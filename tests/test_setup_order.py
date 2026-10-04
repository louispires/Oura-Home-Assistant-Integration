"""Setup ordering for the one-time historical import (issues #80 / #81)."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.oura import async_setup_entry
from custom_components.oura.const import CONF_HISTORICAL_DATA_IMPORTED
from custom_components.oura.coordinator import OuraDataUpdateCoordinator


def _make_entry(imported: bool) -> MagicMock:
    entry = MagicMock()
    entry.entry_id = "mock_entry_id"
    entry.data = {}
    entry.options = {"historical_months": 3, CONF_HISTORICAL_DATA_IMPORTED: imported}
    return entry


def _make_coordinator() -> MagicMock:
    coordinator = MagicMock()
    coordinator.async_config_entry_first_refresh = AsyncMock()
    coordinator.async_load_historical_data = AsyncMock()
    return coordinator


async def _run_setup(mock_hass, entry, coordinator) -> tuple[bool, MagicMock]:
    manager = MagicMock()
    manager.attach_mock(coordinator.mark_reconciled_today, "mark_reconciled_today")
    manager.attach_mock(coordinator.reset_reconcile_marker, "reset_reconcile_marker")
    manager.attach_mock(coordinator.async_config_entry_first_refresh, "first_refresh")
    manager.attach_mock(coordinator.async_load_historical_data, "load_historical")
    manager.attach_mock(mock_hass.config_entries.async_forward_entry_setups, "forward")
    manager.attach_mock(mock_hass.config_entries.async_update_entry, "update_entry")
    manager.attach_mock(entry.add_update_listener, "add_update_listener")

    with patch(
        "custom_components.oura.config_entry_oauth2_flow.async_get_config_entry_implementation",
        new=AsyncMock(),
    ), patch("custom_components.oura.config_entry_oauth2_flow.OAuth2Session"), \
         patch("custom_components.oura.OuraApiClient"), \
         patch("custom_components.oura.OuraDataUpdateCoordinator", return_value=coordinator), \
         patch("custom_components.oura._async_register_services"):
        result = await async_setup_entry(mock_hass, entry)

    return result, manager


def _call_names(manager: MagicMock) -> list[str]:
    return [call[0] for call in manager.mock_calls if "." not in call[0] and call[0]]


@pytest.mark.anyio
async def test_fresh_install_imports_history_after_platforms(mock_hass):
    """Entities must be registered before the import so statistic IDs match (#81)."""
    entry = _make_entry(imported=False)
    coordinator = _make_coordinator()

    result, manager = await _run_setup(mock_hass, entry, coordinator)

    assert result is True
    assert _call_names(manager) == [
        "mark_reconciled_today",
        "first_refresh",
        "forward",
        "load_historical",
        "update_entry",
        "add_update_listener",
    ]
    coordinator.async_load_historical_data.assert_awaited_once_with(90)
    new_options = mock_hass.config_entries.async_update_entry.call_args.kwargs["options"]
    assert new_options[CONF_HISTORICAL_DATA_IMPORTED] is True


@pytest.mark.anyio
async def test_fresh_install_import_failure_resets_reconcile(mock_hass):
    """A failed import leaves the flag unset and lets the next poll reconcile."""
    entry = _make_entry(imported=False)
    coordinator = _make_coordinator()
    coordinator.async_load_historical_data.side_effect = RuntimeError("boom")

    result, manager = await _run_setup(mock_hass, entry, coordinator)

    assert result is True
    names = _call_names(manager)
    assert "update_entry" not in names
    assert names.index("reset_reconcile_marker") < names.index("add_update_listener")


@pytest.mark.anyio
async def test_existing_install_skips_import(mock_hass):
    """Already-imported entries do no historical work and keep the daily reconcile."""
    entry = _make_entry(imported=True)
    coordinator = _make_coordinator()

    result, manager = await _run_setup(mock_hass, entry, coordinator)

    assert result is True
    assert _call_names(manager) == ["first_refresh", "forward", "add_update_listener"]


def _bare_coordinator(mock_hass, mock_config_entry, api_data) -> OuraDataUpdateCoordinator:
    coordinator = OuraDataUpdateCoordinator.__new__(OuraDataUpdateCoordinator)
    coordinator.hass = mock_hass
    coordinator.entry = mock_config_entry
    coordinator.api_client = MagicMock()
    coordinator.api_client.async_get_data = AsyncMock(return_value=api_data)
    coordinator.data = None
    coordinator._last_reconcile_day = None
    return coordinator


@pytest.mark.anyio
async def test_marked_day_skips_reconcile_on_poll(
    mock_hass, mock_config_entry, mock_oura_api_data
):
    """First refresh after a fresh install must not reconcile ahead of the import (#80)."""
    coordinator = _bare_coordinator(mock_hass, mock_config_entry, mock_oura_api_data)
    coordinator.mark_reconciled_today()

    with patch(
        "custom_components.oura.coordinator.async_import_statistics", new=AsyncMock()
    ) as mock_import:
        await coordinator._async_update_data()

    assert not mock_import.called
    coordinator.api_client.async_get_data.assert_awaited_once_with(days_back=1)


@pytest.mark.anyio
async def test_reset_marker_reconciles_on_next_poll(
    mock_hass, mock_config_entry, mock_oura_api_data
):
    """After a reset, the next poll runs the daily reconcile again."""
    coordinator = _bare_coordinator(mock_hass, mock_config_entry, mock_oura_api_data)
    coordinator.mark_reconciled_today()
    coordinator.reset_reconcile_marker()

    with patch(
        "custom_components.oura.coordinator.async_import_statistics", new=AsyncMock()
    ) as mock_import:
        await coordinator._async_update_data()

    assert mock_import.called
