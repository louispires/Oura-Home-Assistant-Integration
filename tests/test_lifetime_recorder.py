"""Lifetime counter against a real recorder: one sum chain, late data on its own day (#86)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from homeassistant import bootstrap, config_entries, loader
from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.statistics import (
    StatisticData,
    StatisticMeanType,
    StatisticMetaData,
    async_import_statistics,
    statistics_during_period,
)
from homeassistant.components.recorder.tasks import StatisticsTask
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er, recorder as recorder_helper
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util

from custom_components.oura.lifetime import OuraLifetimeCounters

SID = "sensor.oura_ring_lifetime_steps"
ATTRS = {"state_class": "total", "unit_of_measurement": "steps"}
START = datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)


def _activity(*days: tuple[str, int]) -> dict:
    return {"activity": {"data": [{"day": day, "steps": steps} for day, steps in days]}}


@pytest.fixture
async def hass(tmp_path):
    hass = HomeAssistant(str(tmp_path))
    await hass.config.async_set_time_zone("UTC")
    hass.config_entries = config_entries.ConfigEntries(hass, {})
    loader.async_setup(hass)
    assert await bootstrap.async_load_base_functionality(hass)
    recorder_helper.async_initialize_recorder(hass)
    assert await async_setup_component(
        hass, "recorder", {"recorder": {"db_url": f"sqlite:///{tmp_path}/test.db", "commit_interval": 0}}
    )
    assert await async_setup_component(hass, "sensor", {})
    await hass.async_start()
    await hass.async_block_till_done()
    yield hass
    await hass.async_stop(force=True)


async def _compile(hass: HomeAssistant, start: datetime, end: datetime) -> None:
    period = start
    while period < end:
        get_instance(hass).queue_task(StatisticsTask(period, False))
        period += timedelta(minutes=5)
    await get_instance(hass).async_block_till_done()


async def _rows(hass: HomeAssistant, period: str) -> list[tuple[datetime, float, float]]:
    stats = await get_instance(hass).async_add_executor_job(
        statistics_during_period,
        hass,
        datetime(2026, 1, 1, tzinfo=timezone.utc),
        None,
        {SID},
        period,
        None,
        {"state", "sum"},
    )
    return [
        (dt_util.utc_from_timestamp(row["start"]), row["state"], row["sum"])
        for row in stats.get(SID, [])
    ]


@pytest.mark.anyio
async def test_lifetime_counter_single_chain_with_late_data(hass):
    er.async_get(hass).async_get_or_create(
        "sensor", "oura", "eid_lifetime_steps", suggested_object_id="oura_ring_lifetime_steps"
    )
    clock = {"now": START + timedelta(minutes=2)}
    shim = SimpleNamespace(
        utcnow=lambda: clock["now"],
        now=lambda: clock["now"],
        start_of_local_day=dt_util.start_of_local_day,
        as_utc=dt_util.as_utc,
    )
    entry = MagicMock(entry_id="eid")

    with patch("custom_components.oura.lifetime.dt_util", new=shim), \
         patch("custom_components.oura.lifetime.Store") as store_cls:
        store_cls.return_value.async_save = MagicMock(side_effect=_noop)
        counters = OuraLifetimeCounters(hass, entry)

        async def poll(data: dict) -> None:
            await counters.async_update(data)
            hass.states.async_set(
                SID, counters.values()["lifetime_steps"], ATTRS, timestamp=clock["now"].timestamp()
            )
            await hass.async_block_till_done()

        # 10:02 history import; the counter goes live with today's 50 steps so far.
        await counters.async_initialize(
            _activity(("2026-10-18", 100), ("2026-10-19", 200), ("2026-10-20", 50))
        )
        hass.states.async_set(SID, counters.values()["lifetime_steps"], ATTRS, timestamp=clock["now"].timestamp())
        await hass.async_block_till_done()
        await _compile(hass, START, START + timedelta(minutes=5))

        # 10:07 join; today's steps grow to 70.
        clock["now"] = START + timedelta(minutes=7)
        await poll(_activity(("2026-10-20", 70)))
        await get_instance(hass).async_block_till_done()
        await _compile(hass, START + timedelta(minutes=5), START + timedelta(minutes=10))

        # 10:12 late data: yesterday 200 -> 260 arrives today.
        clock["now"] = START + timedelta(minutes=12)
        await poll(_activity(("2026-10-19", 260), ("2026-10-20", 70)))
        await _compile(hass, START + timedelta(minutes=10), START + timedelta(minutes=15))

        # 10:17 the recorder has counted it: the move is applied.
        clock["now"] = START + timedelta(minutes=17)
        await poll(_activity(("2026-10-20", 80)))
        await get_instance(hass).async_block_till_done()
        await _compile(hass, START + timedelta(minutes=15), START + timedelta(hours=1))

    assert "steps" in counters._data["joined"]
    assert counters._data["pending"] == []

    # Daily changes: 10-19 = 360 - 100 = 260 (late data on its own day), today = 80.
    hourly = await _rows(hass, "hour")
    assert [(start, s) for start, _state, s in hourly] == [
        (datetime(2026, 10, 18, 12, tzinfo=timezone.utc), 100),
        (datetime(2026, 10, 19, 12, tzinfo=timezone.utc), 360),
        (START, 440),
    ]
    # From the period the recorder counted the late data in, sum equals state again.
    short = await _rows(hass, "5minute")
    assert len(short) == 12
    assert all(row_sum == pytest.approx(state) for _start, state, row_sum in short[2:])
    assert short[-1][2] == 440


async def _noop(*_args, **_kwargs) -> None:
    return None


@pytest.mark.anyio
async def test_daily_total_new_day_is_a_new_cycle_not_a_decrease(hass):
    """With last_reset the daily drop back to a small value adds to the sum (#86)."""
    entity_id = "sensor.oura_ring_active_calories"
    states = [
        (START + timedelta(minutes=2), 100, "2026-10-19T00:00:00+00:00"),
        (START + timedelta(minutes=7), 150, "2026-10-19T00:00:00+00:00"),
        (START + timedelta(minutes=12), 20, "2026-10-20T00:00:00+00:00"),
    ]
    for moment, value, last_reset in states:
        hass.states.async_set(
            entity_id,
            value,
            {"state_class": "total", "unit_of_measurement": "kcal", "last_reset": last_reset},
            timestamp=moment.timestamp(),
        )
        await hass.async_block_till_done()
    await _compile(hass, START, START + timedelta(minutes=15))

    stats = await get_instance(hass).async_add_executor_job(
        statistics_during_period, hass, START, None, {entity_id}, "5minute", None, {"sum"}
    )
    assert [row["sum"] for row in stats[entity_id]] == [0, 50, 70]


@pytest.mark.anyio
async def test_initialize_replaces_rows_left_by_an_earlier_entry(hass):
    """Removing and re-adding the entry must not leave the old chain under the new history (#86)."""
    er.async_get(hass).async_get_or_create(
        "sensor", "oura", "eid_lifetime_steps", suggested_object_id="oura_ring_lifetime_steps"
    )
    async_import_statistics(
        hass,
        StatisticMetaData(
            has_mean=False,
            has_sum=True,
            mean_type=StatisticMeanType.NONE,
            name=None,
            source="recorder",
            statistic_id=SID,
            unit_class=None,
            unit_of_measurement="steps",
        ),
        [
            StatisticData(start=datetime(2026, 10, 10, 12, tzinfo=timezone.utc), state=5000, sum=5000),
            StatisticData(start=datetime(2026, 10, 19, 12, tzinfo=timezone.utc), state=9000, sum=9000),
        ],
    )
    await get_instance(hass).async_block_till_done()
    assert len(await _rows(hass, "hour")) == 2

    now = START + timedelta(minutes=2)
    shim = SimpleNamespace(
        utcnow=lambda: now,
        now=lambda: now,
        start_of_local_day=dt_util.start_of_local_day,
        as_utc=dt_util.as_utc,
    )
    with patch("custom_components.oura.lifetime.dt_util", new=shim),          patch("custom_components.oura.lifetime.Store") as store_cls:
        store_cls.return_value.async_save = MagicMock(side_effect=_noop)
        counters = OuraLifetimeCounters(hass, MagicMock(entry_id="eid"))
        await counters.async_initialize(
            _activity(("2026-10-18", 100), ("2026-10-19", 200), ("2026-10-20", 50))
        )
    await get_instance(hass).async_block_till_done()

    assert [(start, s) for start, _state, s in await _rows(hass, "hour")] == [
        (datetime(2026, 10, 18, 12, tzinfo=timezone.utc), 100),
        (datetime(2026, 10, 19, 12, tzinfo=timezone.utc), 300),
    ]
