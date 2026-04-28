"""Tests for Oura API client date window handling."""
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.oura.api import OuraApiClient


class _FrozenDateTime(datetime):
    """Frozen datetime for deterministic timezone-aware date calculations."""

    @classmethod
    def now(cls, tz=None):
        """Return a fixed local time and require timezone-aware calls."""
        assert tz is not None
        return cls(2026, 3, 23, 1, 30, tzinfo=tz)


@pytest.mark.asyncio
async def test_async_get_data_uses_local_date_and_exclusive_end_date():
    """Test timezone-aware date range and +1 day exclusive end date handling."""
    hass = MagicMock()
    hass.config.time_zone = "America/Denver"
    session = MagicMock()
    entry = MagicMock()
    client = OuraApiClient(hass, session, entry)

    endpoint_methods = [
        "_async_get_sleep",
        "_async_get_readiness",
        "_async_get_activity",
        "_async_get_heartrate",
        "_async_get_sleep_detail",
        "_async_get_stress",
        "_async_get_resilience",
        "_async_get_spo2",
        "_async_get_vo2_max",
        "_async_get_cardiovascular_age",
        "_async_get_sleep_time",
        "_async_get_workout",
        "_async_get_session",
        "_async_get_tag",
        "_async_get_enhanced_tag",
        "_async_get_rest_mode",
        "_async_get_ring_battery_level",
        "_async_get_ring_configuration",
    ]
    for method_name in endpoint_methods:
        setattr(client, method_name, AsyncMock(return_value={"data": []}))

    with patch("custom_components.oura.api.datetime", _FrozenDateTime):
        await client.async_get_data(days_back=1)

    expected_start = date(2026, 3, 22)
    expected_end = date(2026, 3, 24)
    for method_name in endpoint_methods:
        mocked_method = getattr(client, method_name)
        assert mocked_method.await_count == 1
        assert mocked_method.await_args.args == (expected_start, expected_end)
