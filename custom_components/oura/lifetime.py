"""Lifetime counters for the daily Oura sums (#86).

Each counter's long-term statistic has a single writer: the history is imported once,
after that only the recorder writes rows and this module only shifts their sums.
"""
from __future__ import annotations

import asyncio
from datetime import date, datetime, timedelta
import logging
from typing import Any

from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.statistics import (
    StatisticData,
    StatisticMeanType,
    StatisticMetaData,
    async_import_statistics as async_import_statistics_ha,
    get_last_short_term_statistics,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import DOMAIN, LIFETIME_PREFIX, LIFETIME_SOURCE_KEYS, SENSOR_TYPES
from .statistics import _get_unit_class, daily_sum_values

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 1
# Days kept one by one so late data can still be moved to its day; older ones fold into the base.
RETENTION_DAYS = 60
# A move whose recorder period never appears (entity not recorded) is dropped after this.
PENDING_MAX_AGE = timedelta(days=2)
SHORT_TERM_PERIOD = timedelta(minutes=5)
# Close to a period boundary the state write could land in the next period.
PERIOD_GUARD = timedelta(seconds=10)
_TOLERANCE = 1e-6


def storage_key(entry_id: str) -> str:
    """Return the storage key of an entry's lifetime counters."""
    return f"{DOMAIN}.lifetime.{entry_id}"


async def async_remove_store(hass: HomeAssistant, entry_id: str) -> None:
    """Delete an entry's lifetime counter state."""
    await Store(hass, STORAGE_VERSION, storage_key(entry_id)).async_remove()


def day_anchor(day: date) -> datetime:
    """Return the UTC hour that holds a day's value: local noon, floored to the hour."""
    noon = dt_util.start_of_local_day(day) + timedelta(hours=12)
    return dt_util.as_utc(noon).replace(minute=0, second=0, microsecond=0)


def _period_start(moment: datetime) -> datetime:
    return moment.replace(minute=moment.minute - moment.minute % 5, second=0, microsecond=0)


def _is_zero(value: float, scale: float) -> bool:
    return abs(value) <= _TOLERANCE * max(1.0, abs(scale))


class OuraLifetimeCounters:
    """Never-resetting totals of the daily sums, one recorder-owned statistic each."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.hass = hass
        self.entry = entry
        self._store: Store[dict[str, Any]] = Store(
            hass, STORAGE_VERSION, storage_key(entry.entry_id)
        )
        self._data: dict[str, Any] | None = None
        # A poll and the reconcile action may overlap; both must not apply the same move.
        self._lock = asyncio.Lock()

    async def async_load(self) -> None:
        """Load the stored counter state."""
        data = await self._store.async_load()
        if data is not None:
            data.setdefault("join_pending", {})
        self._data = data

    @property
    def initialized(self) -> bool:
        """Return True once the history has been loaded."""
        return self._data is not None

    def values(self) -> dict[str, float]:
        """Return the counter states keyed by sensor key."""
        if self._data is None:
            return {}
        return {
            f"{LIFETIME_PREFIX}{key}": self._data["base"].get(key, 0.0)
            + sum(self._data["days"].get(key, {}).values())
            for key in LIFETIME_SOURCE_KEYS
        }

    async def async_initialize(self, data: dict[str, Any]) -> None:
        """Start the counters from ``data`` and import its finished days as their history."""
        async with self._lock:
            await self._async_initialize(data)

    async def _async_initialize(self, data: dict[str, Any]) -> None:
        today = dt_util.now().date()
        today_iso = today.isoformat()
        daily = {
            key: {day_iso: value for day_iso, value in values.items() if day_iso <= today_iso}
            for key, values in daily_sum_values(data).items()
        }
        self._data = {
            "live_since": dt_util.utcnow()
            .replace(minute=0, second=0, microsecond=0)
            .isoformat(),
            "base": {key: 0.0 for key in LIFETIME_SOURCE_KEYS},
            "days": daily,
            "joined": [],
            "join_pending": {},
            "pending": [],
        }
        # Rows left by an earlier entry or a lost store would sit under the new history.
        # The recorder runs the clear before the imports queued below.
        if statistic_ids := [
            statistic_id
            for key in LIFETIME_SOURCE_KEYS
            if (statistic_id := self._statistic_id(key)) is not None
        ]:
            get_instance(self.hass).async_clear_statistics(statistic_ids)
        for key in LIFETIME_SOURCE_KEYS:
            self._import_history(key, daily[key], today)
            self._compact(key, today)
        try:
            await self._store.async_save(self._data)
        except Exception:
            self._data = None
            raise
        _LOGGER.info("Lifetime counters initialised from %d days of history", len(daily["steps"]))

    async def async_update(self, data: dict[str, Any]) -> None:
        """Take in new and late data; late data's statistics are moved onto its own day."""
        async with self._lock:
            if self._data is not None:
                await self._async_update(data)

    async def _async_update(self, data: dict[str, Any]) -> None:
        await self._async_join()
        await self._async_apply_pending()

        today = dt_util.now().date()
        today_iso = today.isoformat()
        cutoff = (today - timedelta(days=RETENTION_DAYS)).isoformat()
        joined = set(self._data["joined"])
        moves: list[dict[str, Any]] = []
        changed = False
        for key, values in daily_sum_values(data).items():
            days = self._data["days"].setdefault(key, {})
            for day_iso, value in values.items():
                # Oura dates an evening session to the next day; it is counted once that day starts.
                if day_iso < cutoff or day_iso > today_iso:
                    continue
                delta = value - days.get(day_iso, 0.0)
                if abs(delta) < 1e-9:
                    continue
                days[day_iso] = value
                changed = True
                if day_iso < today_iso and key in joined:
                    moves.append({"key": key, "day": day_iso, "delta": delta})
            self._compact(key, today)

        if moves:
            now = dt_util.utcnow()
            period = _period_start(now)
            if period + SHORT_TERM_PERIOD - now < PERIOD_GUARD:
                await asyncio.sleep((period + SHORT_TERM_PERIOD - now).total_seconds() + 0.5)
                period += SHORT_TERM_PERIOD
            for move in moves:
                move["period"] = period.isoformat()
            self._data["pending"].extend(moves)
        if changed:
            # A change lost in a crash comes back as late data on the next start and is counted twice.
            await self._store.async_save(self._data)

    def _compact(self, key: str, today: date) -> None:
        cutoff = (today - timedelta(days=RETENTION_DAYS)).isoformat()
        days = self._data["days"].setdefault(key, {})
        for day_iso in [day_iso for day_iso in days if day_iso < cutoff]:
            self._data["base"][key] = self._data["base"].get(key, 0.0) + days.pop(day_iso)

    def _statistic_id(self, key: str) -> str | None:
        return er.async_get(self.hass).async_get_entity_id(
            "sensor", DOMAIN, f"{self.entry.entry_id}_{LIFETIME_PREFIX}{key}"
        )

    @staticmethod
    def _unit(key: str) -> str | None:
        return SENSOR_TYPES[f"{LIFETIME_PREFIX}{key}"]["unit"]

    def _import_history(self, key: str, values: dict[str, float], today: date) -> None:
        if (statistic_id := self._statistic_id(key)) is None:
            return
        total = 0.0
        rows: list[StatisticData] = []
        for day_iso in sorted(values):
            day = date.fromisoformat(day_iso)
            if day >= today:
                break
            total += values[day_iso]
            rows.append(StatisticData(start=day_anchor(day), state=total, sum=total))
        if not rows:
            return
        unit = self._unit(key)
        async_import_statistics_ha(
            self.hass,
            StatisticMetaData(
                has_mean=False,
                has_sum=True,
                mean_type=StatisticMeanType.NONE,
                name=None,
                source="recorder",
                statistic_id=statistic_id,
                unit_class=_get_unit_class(unit),
                unit_of_measurement=unit,
            ),
            rows,
        )

    async def _async_latest_short_term(self, statistic_id: str) -> dict[str, Any] | None:
        try:
            result = await get_instance(self.hass).async_add_executor_job(
                get_last_short_term_statistics,
                self.hass,
                1,
                statistic_id,
                False,
                {"state", "sum"},
            )
        except Exception as err:  # recorder not ready
            _LOGGER.debug("Could not read latest statistics of %s: %s", statistic_id, err)
            return None
        rows = result.get(statistic_id)
        return rows[0] if rows else None

    async def _async_join(self) -> None:
        """Lift the recorder's chain, which starts at 0, onto the imported history."""
        live_since = datetime.fromisoformat(self._data["live_since"])
        joined: list[str] = self._data["joined"]
        requested: dict[str, dict[str, Any]] = self._data["join_pending"]
        now = dt_util.utcnow()
        changed = False
        for key in LIFETIME_SOURCE_KEYS:
            if key in joined or (statistic_id := self._statistic_id(key)) is None:
                continue
            if (row := await self._async_latest_short_term(statistic_id)) is None:
                continue
            state = row.get("state") or 0.0
            offset = state - (row.get("sum") or 0.0)
            if _is_zero(offset, state):
                joined.append(key)
                requested.pop(key, None)
                changed = True
                continue
            # The offset holds until the queued adjustment lands, also across a reload;
            # asking again while it is queued would add it twice. Past the max age it was lost.
            if (
                (request := requested.get(key)) is not None
                and _is_zero(offset - request["offset"], state)
                and now - datetime.fromisoformat(request["at"]) < PENDING_MAX_AGE
            ):
                continue
            get_instance(self.hass).async_adjust_statistics(
                statistic_id, live_since, offset, self._unit(key)
            )
            requested[key] = {"offset": offset, "at": now.isoformat()}
            changed = True
        if changed:
            await self._store.async_save(self._data)

    async def _async_apply_pending(self) -> None:
        """Move late data from the period the recorder counted it in onto its own day."""
        pending: list[dict[str, Any]] = self._data["pending"]
        if not pending:
            return
        now = dt_util.utcnow()
        latest_start: dict[str, float | None] = {}
        keep: list[dict[str, Any]] = []
        ready: list[tuple[str, dict[str, Any]]] = []
        for move in pending:
            if (statistic_id := self._statistic_id(move["key"])) is None:
                continue
            period = datetime.fromisoformat(move["period"])
            if statistic_id not in latest_start:
                row = await self._async_latest_short_term(statistic_id)
                start = row.get("start") if row else None
                latest_start[statistic_id] = (
                    start.timestamp() if isinstance(start, datetime) else start
                )
            # Adjusting before the recorder compiled that period would count the move twice.
            if (start := latest_start[statistic_id]) is not None and start >= period.timestamp():
                ready.append((statistic_id, move))
            elif now - period < PENDING_MAX_AGE:
                keep.append(move)
        if len(keep) == len(pending):
            return

        self._data["pending"] = keep
        # Save first: a lost move leaves late data on its arrival hour, a repeated one breaks the sum.
        await self._store.async_save(self._data)
        recorder = get_instance(self.hass)
        for statistic_id, move in ready:
            anchor = day_anchor(date.fromisoformat(move["day"]))
            period = datetime.fromisoformat(move["period"])
            if anchor >= period:
                continue
            unit = self._unit(move["key"])
            recorder.async_adjust_statistics(statistic_id, anchor, move["delta"], unit)
            recorder.async_adjust_statistics(statistic_id, period, -move["delta"], unit)
