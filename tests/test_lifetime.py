"""Tests for the lifetime counters (#86)."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from zoneinfo import ZoneInfo

import pytest
from homeassistant.util import dt as dt_util

from custom_components.oura import async_remove_entry
from custom_components.oura.const import LIFETIME_PREFIX, LIFETIME_SOURCE_KEYS, SENSOR_TYPES
from custom_components.oura.coordinator import OuraDataUpdateCoordinator
from custom_components.oura.lifetime import OuraLifetimeCounters, day_anchor
from custom_components.oura.sensor import OuraSensor
from custom_components.oura.statistics import STATISTICS_METADATA, daily_sum_values

NOW = datetime(2026, 10, 20, 15, 2, 0, tzinfo=timezone.utc)
PERIOD = datetime(2026, 10, 20, 15, 0, 0, tzinfo=timezone.utc)
SID = "sensor.oura_ring_lifetime_steps"


def _activity(*days: tuple[str, int]) -> dict:
    return {"activity": {"data": [{"day": day, "steps": steps} for day, steps in days]}}


@pytest.fixture
def frozen_now():
    with patch("custom_components.oura.lifetime.dt_util.utcnow", return_value=NOW), \
         patch("custom_components.oura.lifetime.dt_util.now", return_value=NOW):
        yield


@pytest.fixture
def store():
    store = MagicMock()
    store.async_load = AsyncMock(return_value=None)
    store.async_save = AsyncMock()
    with patch("custom_components.oura.lifetime.Store", return_value=store):
        yield store


@pytest.fixture
def registry():
    with patch("custom_components.oura.lifetime.er.async_get") as get:
        get.return_value.async_get_entity_id.side_effect = (
            lambda _domain, _platform, unique_id: "sensor.oura_ring_"
            + unique_id.removeprefix("mock_entry_id_")
        )
        yield get.return_value


@pytest.fixture
def recorder():
    recorder = MagicMock()
    recorder.async_add_executor_job = AsyncMock(return_value={})
    with patch("custom_components.oura.lifetime.get_instance", return_value=recorder):
        yield recorder


@pytest.fixture
def import_ha():
    with patch("custom_components.oura.lifetime.async_import_statistics_ha") as mock_import:
        yield mock_import


def _latest_row(recorder: MagicMock, rows: dict[str, dict]) -> None:
    async def _job(_func, _hass, _count, statistic_id, _convert, _types):
        return {statistic_id: [rows[statistic_id]]} if statistic_id in rows else {}

    recorder.async_add_executor_job = AsyncMock(side_effect=_job)


async def _counters(mock_hass, mock_config_entry, data, joined=()) -> OuraLifetimeCounters:
    counters = OuraLifetimeCounters(mock_hass, mock_config_entry)
    await counters.async_initialize(data)
    counters._data["joined"] = list(joined)
    return counters


def test_lifetime_keys_are_the_entity_sum_sensors():
    """Every entity whose sum the recorder now owns has a counter carrying its history."""
    entity_sums = {
        key
        for key, meta in STATISTICS_METADATA.items()
        if meta["has_sum"] and key in SENSOR_TYPES
    }
    assert set(LIFETIME_SOURCE_KEYS) == entity_sums


def test_lifetime_sensors_are_never_resetting_totals():
    for key in LIFETIME_SOURCE_KEYS:
        info = SENSOR_TYPES[f"{LIFETIME_PREFIX}{key}"]
        assert info["state_class"] == "total"
        assert info["unit"] == SENSOR_TYPES[key]["unit"]
        assert info["name"] == f"Lifetime {SENSOR_TYPES[key]['name']}"
        assert f"{LIFETIME_PREFIX}{key}" not in STATISTICS_METADATA


def test_lifetime_sensor_has_no_last_reset():
    """A last_reset would make the recorder start a new cycle; the counter never resets."""
    coordinator = MagicMock()
    coordinator.data = {"lifetime_steps": 1000.0, "_day_activity": date(2026, 10, 20)}
    sensor = OuraSensor(coordinator, "lifetime_steps", SENSOR_TYPES["lifetime_steps"])

    assert sensor.last_reset is None
    assert sensor.native_value == 1000.0


def test_daily_sum_values_per_day():
    data = {
        "activity": {"data": [
            {"day": "2026-10-19", "steps": 1000, "resting_time": 3600, "equivalent_walking_distance": 800},
            {"day": "2026-10-20", "steps": 200},
            {"day": None, "steps": 5},
        ]},
        "stress": {"data": [{"day": "2026-10-19", "stress_high": 1800, "recovery_high": None}]},
        "sleep_detail": {"data": [
            {"day": "2026-10-20", "type": "long_sleep", "total_sleep_duration": 25200, "deep_sleep_duration": 3600},
            {"day": "2026-10-20", "type": "late_nap", "total_sleep_duration": 1800, "deep_sleep_duration": 600},
        ]},
    }

    values = daily_sum_values(data)

    assert values["steps"] == {"2026-10-19": 1000.0, "2026-10-20": 200.0}
    assert values["resting_time"] == {"2026-10-19": 60.0}
    assert values["equivalent_walking_distance"] == {"2026-10-19": 800.0}
    assert values["stress_high_duration"] == {"2026-10-19": 30.0}
    assert values["recovery_high_duration"] == {}
    # Total sleep counts the nap too; the other sleep sums come from the long_sleep record.
    assert values["total_sleep_duration"] == {"2026-10-20": 7.5}
    assert values["deep_sleep_duration"] == {"2026-10-20": 1.0}


@pytest.mark.parametrize(
    ("zone", "expected"),
    [
        ("UTC", datetime(2026, 10, 20, 12, tzinfo=timezone.utc)),
        ("America/Los_Angeles", datetime(2026, 10, 20, 19, tzinfo=timezone.utc)),
        ("Asia/Kolkata", datetime(2026, 10, 20, 6, tzinfo=timezone.utc)),
    ],
)
def test_day_anchor_is_local_noon_on_an_hour(zone, expected):
    original = dt_util.DEFAULT_TIME_ZONE
    dt_util.set_default_time_zone(ZoneInfo(zone))
    try:
        assert day_anchor(date(2026, 10, 20)) == expected
    finally:
        dt_util.set_default_time_zone(original)


@pytest.mark.anyio
async def test_initialize_imports_finished_days_as_history(
    mock_hass, mock_config_entry, frozen_now, store, registry, recorder, import_ha
):
    data = _activity(("2026-10-18", 100), ("2026-10-19", 200), ("2026-10-20", 50))

    counters = await _counters(mock_hass, mock_config_entry, data)

    assert counters.initialized
    assert counters.values()["lifetime_steps"] == 350
    store.async_save.assert_awaited_once()
    assert counters._data["live_since"] == PERIOD.isoformat()

    calls = {call.args[1]["statistic_id"]: call.args for call in import_ha.call_args_list}
    assert set(calls) == {SID}
    _, metadata, rows = calls[SID]
    assert metadata["has_sum"] is True and metadata["source"] == "recorder"
    assert metadata["unit_of_measurement"] == "steps"
    # Today is still running; the recorder counts it from the counter's state.
    assert [(row["start"], row["state"], row["sum"]) for row in rows] == [
        (datetime(2026, 10, 18, 12, tzinfo=timezone.utc), 100, 100),
        (datetime(2026, 10, 19, 12, tzinfo=timezone.utc), 300, 300),
    ]


@pytest.mark.anyio
async def test_initialize_folds_old_days_into_base(
    mock_hass, mock_config_entry, frozen_now, store, registry, recorder, import_ha
):
    old_day = (NOW.date() - timedelta(days=70)).isoformat()
    counters = await _counters(
        mock_hass, mock_config_entry, _activity((old_day, 1000), ("2026-10-20", 5))
    )

    assert counters.values()["lifetime_steps"] == 1005
    assert counters._data["base"]["steps"] == 1000
    assert old_day not in counters._data["days"]["steps"]


@pytest.mark.anyio
async def test_update_today_changes_state_without_move(
    mock_hass, mock_config_entry, frozen_now, store, registry, recorder, import_ha
):
    counters = await _counters(
        mock_hass, mock_config_entry, _activity(("2026-10-19", 200), ("2026-10-20", 50)), joined=LIFETIME_SOURCE_KEYS
    )
    store.async_save.reset_mock()

    await counters.async_update(_activity(("2026-10-20", 80)))

    assert counters.values()["lifetime_steps"] == 280
    assert counters._data["pending"] == []
    store.async_save.assert_not_awaited()
    store.async_delay_save.assert_called_once()
    recorder.async_adjust_statistics.assert_not_called()


@pytest.mark.anyio
async def test_update_late_data_records_move_and_saves_first(
    mock_hass, mock_config_entry, frozen_now, store, registry, recorder, import_ha
):
    counters = await _counters(
        mock_hass, mock_config_entry, _activity(("2026-10-19", 200), ("2026-10-20", 50)), joined=LIFETIME_SOURCE_KEYS
    )
    store.async_save.reset_mock()

    await counters.async_update(_activity(("2026-10-19", 260), ("2026-10-20", 50)))

    assert counters.values()["lifetime_steps"] == 310
    assert counters._data["pending"] == [
        {"key": "steps", "day": "2026-10-19", "delta": 60, "period": PERIOD.isoformat()}
    ]
    store.async_save.assert_awaited_once()
    recorder.async_adjust_statistics.assert_not_called()


@pytest.mark.anyio
async def test_update_late_data_before_join_stays_on_arrival_hour(
    mock_hass, mock_config_entry, frozen_now, store, registry, recorder, import_ha
):
    counters = await _counters(mock_hass, mock_config_entry, _activity(("2026-10-19", 200)))

    await counters.async_update(_activity(("2026-10-19", 260)))

    assert counters.values()["lifetime_steps"] == 260
    assert counters._data["pending"] == []


@pytest.mark.anyio
async def test_update_ignores_days_before_retention(
    mock_hass, mock_config_entry, frozen_now, store, registry, recorder, import_ha
):
    counters = await _counters(mock_hass, mock_config_entry, _activity(("2026-10-20", 50)), joined=LIFETIME_SOURCE_KEYS)
    old_day = (NOW.date() - timedelta(days=90)).isoformat()

    await counters.async_update(_activity((old_day, 999)))

    assert counters.values()["lifetime_steps"] == 50
    assert counters._data["pending"] == []


@pytest.mark.anyio
async def test_update_close_to_period_boundary_waits_for_next_period(
    mock_hass, mock_config_entry, store, registry, recorder, import_ha
):
    late = datetime(2026, 10, 20, 15, 4, 55, tzinfo=timezone.utc)
    with patch("custom_components.oura.lifetime.dt_util.utcnow", return_value=late), \
         patch("custom_components.oura.lifetime.dt_util.now", return_value=late), \
         patch("custom_components.oura.lifetime.asyncio.sleep", new=AsyncMock()) as mock_sleep:
        counters = await _counters(
            mock_hass, mock_config_entry, _activity(("2026-10-19", 200)), joined=LIFETIME_SOURCE_KEYS
        )
        await counters.async_update(_activity(("2026-10-19", 210)))

    mock_sleep.assert_awaited_once()
    assert counters._data["pending"][0]["period"] == "2026-10-20T15:05:00+00:00"


@pytest.mark.anyio
async def test_join_lifts_recorder_chain_onto_history_once(
    mock_hass, mock_config_entry, frozen_now, store, registry, recorder, import_ha
):
    counters = await _counters(mock_hass, mock_config_entry, _activity(("2026-10-19", 300), ("2026-10-20", 50)))
    _latest_row(recorder, {SID: {"start": PERIOD.timestamp(), "state": 350.0, "sum": 0.0}})

    await counters.async_update({})
    await counters.async_update({})

    recorder.async_adjust_statistics.assert_called_once_with(SID, PERIOD, 350.0, "steps")
    assert "steps" not in counters._data["joined"]

    _latest_row(recorder, {SID: {"start": PERIOD.timestamp(), "state": 350.0, "sum": 350.0}})
    store.async_save.reset_mock()
    await counters.async_update({})

    assert "steps" in counters._data["joined"]
    store.async_save.assert_awaited_once()
    recorder.async_adjust_statistics.assert_called_once()


@pytest.mark.anyio
async def test_join_repeated_after_restart_if_adjustment_was_lost(
    mock_hass, mock_config_entry, frozen_now, store, registry, recorder, import_ha
):
    counters = await _counters(mock_hass, mock_config_entry, _activity(("2026-10-20", 50)))
    _latest_row(recorder, {SID: {"start": PERIOD.timestamp(), "state": 50.0, "sum": 0.0}})
    await counters.async_update({})

    restarted = OuraLifetimeCounters(mock_hass, mock_config_entry)
    restarted._data = counters._data
    await restarted.async_update({})

    assert recorder.async_adjust_statistics.call_count == 2


@pytest.mark.anyio
async def test_pending_move_applied_once_recorder_compiled_its_period(
    mock_hass, mock_config_entry, frozen_now, store, registry, recorder, import_ha
):
    counters = await _counters(mock_hass, mock_config_entry, _activity(("2026-10-19", 200)), joined=LIFETIME_SOURCE_KEYS)
    move = {"key": "steps", "day": "2026-10-19", "delta": 60.0, "period": PERIOD.isoformat()}
    counters._data["pending"] = [dict(move)]

    _latest_row(recorder, {SID: {"start": (PERIOD - timedelta(minutes=5)).timestamp(), "state": 0.0, "sum": 0.0}})
    await counters.async_update({})
    recorder.async_adjust_statistics.assert_not_called()
    assert counters._data["pending"] == [move]

    _latest_row(recorder, {SID: {"start": PERIOD.timestamp(), "state": 0.0, "sum": 0.0}})
    store.async_save.reset_mock()
    await counters.async_update({})

    assert counters._data["pending"] == []
    store.async_save.assert_awaited_once()
    assert [call.args for call in recorder.async_adjust_statistics.call_args_list] == [
        (SID, datetime(2026, 10, 19, 12, tzinfo=timezone.utc), 60.0, "steps"),
        (SID, PERIOD, -60.0, "steps"),
    ]


@pytest.mark.anyio
async def test_stale_pending_move_is_dropped(
    mock_hass, mock_config_entry, frozen_now, store, registry, recorder, import_ha
):
    counters = await _counters(mock_hass, mock_config_entry, {}, joined=LIFETIME_SOURCE_KEYS)
    counters._data["pending"] = [
        {"key": "steps", "day": "2026-10-15", "delta": 10.0, "period": (NOW - timedelta(days=3)).isoformat()}
    ]

    await counters.async_update({})

    assert counters._data["pending"] == []
    recorder.async_adjust_statistics.assert_not_called()


@pytest.mark.anyio
async def test_remove_entry_deletes_counter_state(mock_hass, mock_config_entry, store):
    store.async_remove = AsyncMock()

    await async_remove_entry(mock_hass, mock_config_entry)

    store.async_remove.assert_awaited_once()


@pytest.mark.anyio
async def test_poll_adds_lifetime_values(mock_hass, mock_config_entry, mock_oura_api_data):
    coordinator = OuraDataUpdateCoordinator.__new__(OuraDataUpdateCoordinator)
    coordinator.hass = mock_hass
    coordinator.entry = mock_config_entry
    coordinator.data = None
    coordinator._last_reconcile_day = dt_util.now().date()
    coordinator._lifetime_retry_days = None
    coordinator.api_client = MagicMock()
    coordinator.api_client.async_get_data = AsyncMock(return_value=mock_oura_api_data)
    coordinator.lifetime = MagicMock(initialized=True)
    coordinator.lifetime.async_update = AsyncMock()
    coordinator.lifetime.values.return_value = {"lifetime_steps": 12345.0}

    processed = await coordinator._async_update_data()

    coordinator.lifetime.async_update.assert_awaited_once_with(mock_oura_api_data)
    assert processed["lifetime_steps"] == 12345.0


@pytest.mark.anyio
async def test_lifetime_init_failure_retried_with_daily_reconcile(
    mock_hass, mock_config_entry, mock_oura_api_data
):
    coordinator = OuraDataUpdateCoordinator.__new__(OuraDataUpdateCoordinator)
    coordinator.hass = mock_hass
    coordinator.entry = mock_config_entry
    coordinator.data = None
    coordinator._last_reconcile_day = None
    coordinator._lifetime_retry_days = None
    coordinator.api_client = MagicMock()
    coordinator.api_client.async_get_data = AsyncMock(side_effect=RuntimeError("boom"))
    coordinator.lifetime = MagicMock(initialized=False)
    coordinator.lifetime.async_initialize = AsyncMock()

    await coordinator.async_initialize_lifetime(90)
    assert coordinator._lifetime_retry_days == 90

    coordinator.api_client.async_get_data = AsyncMock(return_value=mock_oura_api_data)
    with patch("custom_components.oura.coordinator.async_import_statistics", new=AsyncMock()):
        await coordinator._async_update_data()

    coordinator.lifetime.async_initialize.assert_awaited_once_with(mock_oura_api_data)
    assert coordinator._lifetime_retry_days is None
