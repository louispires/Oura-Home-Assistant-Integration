"""DataUpdateCoordinator for Oura Ring."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OuraApiClient
from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL
from .statistics import async_import_statistics

_LOGGER = logging.getLogger(__name__)


class OuraDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Oura Ring data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_client: OuraApiClient,
        entry: ConfigEntry,
        update_interval_minutes: int = DEFAULT_UPDATE_INTERVAL,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=update_interval_minutes),
        )
        self.api_client = api_client
        self.entry = entry
        self.historical_data_loaded = False

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via API."""
        try:
            # For regular updates, only fetch 1 day of data
            data = await self.api_client.async_get_data(days_back=1)
            processed_data = self._process_data(data)

            # Check if we got any actual data back
            # If all endpoints failed, processed_data will be empty
            if not processed_data:
                _LOGGER.warning(
                    "No data returned from API (all endpoints failed). "
                    "Keeping existing data if available. Will retry in %s minutes.",
                    self.update_interval.total_seconds() / 60,
                )
                # If we have existing data, keep it
                if self.data:
                    return self.data
                # If no existing data, this is a problem
                raise UpdateFailed("No data available from API")

            return processed_data

        except Exception as err:
            # Log the error but keep existing data to maintain sensor states
            # This handles transient network issues gracefully
            _LOGGER.warning(
                "Error communicating with API (will retry in %s minutes): %s",
                self.update_interval.total_seconds() / 60,
                err
            )

            # If we have existing data, return it to keep sensors showing last known values
            if self.data:
                _LOGGER.debug("Keeping existing data due to transient error")
                return self.data

            # If no existing data (first run), raise the error
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def async_load_historical_data(self, days: int) -> None:
        """Load historical data on first setup.

        Args:
            days: Number of days of historical data to fetch
        """
        try:
            _LOGGER.info("Loading %d days of historical data...", days)
            historical_data = await self.api_client.async_get_data(days_back=days)

            # Import historical data as long-term statistics
            try:
                await async_import_statistics(self.hass, historical_data, self.entry)
                _LOGGER.info("Historical data loaded successfully")
            except Exception as stats_err:
                _LOGGER.error("Failed to import statistics: %s", stats_err)
                raise

            # Process and store the LATEST day's data for current sensor states
            processed_data = self._process_data(historical_data)

            # Update the coordinator's data with current information
            self.data = processed_data
            self.historical_data_loaded = True
        except Exception as err:
            _LOGGER.error("Failed to fetch historical data: %s", err)
            raise

    def _process_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process the raw API data into sensor values.

        Orchestrates processing of all data sources by delegating to specialized methods.
        """
        processed = {}

        # Process each data type using specialized methods
        self._process_sleep_scores(data, processed)
        self._process_sleep_details(data, processed)
        self._process_readiness(data, processed)
        self._process_activity(data, processed)
        self._process_heart_rate(data, processed)
        self._process_stress(data, processed)
        self._process_resilience(data, processed)
        self._process_spo2(data, processed)
        self._process_vo2_max(data, processed)
        self._process_cardiovascular_age(data, processed)
        self._process_sleep_time(data, processed)

        return processed

    def _process_sleep_scores(self, data: dict[str, Any], processed: dict[str, Any]) -> None:
        """Process sleep scores (contribution scores, not durations)."""
        if sleep_data := data.get("sleep", {}).get("data"):
            if sleep_data and len(sleep_data) > 0:
                latest_sleep = sleep_data[-1]
                processed["sleep_score"] = latest_sleep.get("score")
                # Store the data date for verification
                if day := latest_sleep.get("day"):
                    processed["_data_date"] = day
                if contributors := latest_sleep.get("contributors"):
                    processed["sleep_efficiency"] = contributors.get("efficiency")
                    processed["restfulness"] = contributors.get("restfulness")
                    processed["sleep_timing"] = contributors.get("timing")

    def _process_sleep_details(self, data: dict[str, Any], processed: dict[str, Any]) -> None:
        """Process detailed sleep data (actual durations and HRV)."""
        if sleep_detail_data := data.get("sleep_detail", {}).get("data"):
            if sleep_detail_data and len(sleep_detail_data) > 0:
                latest_sleep_detail = sleep_detail_data[-1]

                # Extract duration values
                total_sleep_seconds = latest_sleep_detail.get("total_sleep_duration")
                deep_sleep_seconds = latest_sleep_detail.get("deep_sleep_duration")
                rem_sleep_seconds = latest_sleep_detail.get("rem_sleep_duration")
                light_sleep_seconds = latest_sleep_detail.get("light_sleep_duration")

                # Convert durations from seconds to hours
                if total_sleep_seconds:
                    processed["total_sleep_duration"] = total_sleep_seconds / 3600
                if deep_sleep_seconds:
                    processed["deep_sleep_duration"] = deep_sleep_seconds / 3600
                if rem_sleep_seconds:
                    processed["rem_sleep_duration"] = rem_sleep_seconds / 3600
                if light_sleep_seconds:
                    processed["light_sleep_duration"] = light_sleep_seconds / 3600
                if awake := latest_sleep_detail.get("awake_time"):
                    processed["awake_time"] = awake / 3600
                if latency := latest_sleep_detail.get("latency"):
                    processed["sleep_latency"] = latency / 60  # Convert to minutes
                if time_in_bed := latest_sleep_detail.get("time_in_bed"):
                    processed["time_in_bed"] = time_in_bed / 3600

                # Calculate sleep stage percentages
                if total_sleep_seconds and total_sleep_seconds > 0:
                    if deep_sleep_seconds is not None:
                        processed["deep_sleep_percentage"] = round(
                            (deep_sleep_seconds / total_sleep_seconds) * 100, 1
                        )
                    if rem_sleep_seconds is not None:
                        processed["rem_sleep_percentage"] = round(
                            (rem_sleep_seconds / total_sleep_seconds) * 100, 1
                        )

                # HRV during sleep
                if average_hrv := latest_sleep_detail.get("average_hrv"):
                    processed["average_sleep_hrv"] = average_hrv

                # Bedtime timestamps (when you went to sleep and woke up)
                # Parse ISO 8601 datetime strings (e.g., "2024-01-15T23:30:00+00:00") to datetime objects
                if bedtime_start := latest_sleep_detail.get("bedtime_start"):
                    try:
                        processed["bedtime_start"] = datetime.fromisoformat(bedtime_start.replace('Z', '+00:00'))
                    except (ValueError, AttributeError) as e:
                        _LOGGER.debug("Error parsing bedtime_start '%s': %s", bedtime_start, e)

                if bedtime_end := latest_sleep_detail.get("bedtime_end"):
                    try:
                        processed["bedtime_end"] = datetime.fromisoformat(bedtime_end.replace('Z', '+00:00'))
                    except (ValueError, AttributeError) as e:
                        _LOGGER.debug("Error parsing bedtime_end '%s': %s", bedtime_end, e)


                if lowest_heart_rate := latest_sleep_detail.get("lowest_heart_rate"):
                    processed["lowest_sleep_heart_rate"] = lowest_heart_rate
                if average_heart_rate := latest_sleep_detail.get("average_heart_rate"):
                    processed["average_sleep_heart_rate"] = average_heart_rate

                # Low battery alert flag (always set, defaults to False)
                processed["low_battery_alert"] = latest_sleep_detail.get("low_battery_alert", False)

    def _process_readiness(self, data: dict[str, Any], processed: dict[str, Any]) -> None:
        """Process readiness data (contributors are scores 1-100)."""
        if readiness_data := data.get("readiness", {}).get("data"):
            if readiness_data and len(readiness_data) > 0:
                latest_readiness = readiness_data[-1]
                processed["readiness_score"] = latest_readiness.get("score")
                processed["temperature_deviation"] = latest_readiness.get("temperature_deviation")

                if contributors := latest_readiness.get("contributors"):
                    processed["resting_heart_rate"] = contributors.get("resting_heart_rate")
                    processed["hrv_balance"] = contributors.get("hrv_balance")
                    processed["sleep_regularity"] = contributors.get("sleep_regularity")

    def _process_activity(self, data: dict[str, Any], processed: dict[str, Any]) -> None:
        """Process activity data (steps, calories, MET minutes)."""
        if activity_data := data.get("activity", {}).get("data"):
            if activity_data and len(activity_data) > 0:
                latest_activity = activity_data[-1]
                processed["activity_score"] = latest_activity.get("score")
                processed["steps"] = latest_activity.get("steps")
                processed["active_calories"] = latest_activity.get("active_calories")
                processed["total_calories"] = latest_activity.get("total_calories")
                processed["target_calories"] = latest_activity.get("target_calories")
                processed["met_min_high"] = latest_activity.get("high_activity_met_minutes")
                processed["met_min_medium"] = latest_activity.get("medium_activity_met_minutes")
                processed["met_min_low"] = latest_activity.get("low_activity_met_minutes")

    def _process_heart_rate(self, data: dict[str, Any], processed: dict[str, Any]) -> None:
        """Process heart rate data with aggregation from recent readings."""
        if heartrate_data := data.get("heartrate", {}).get("data"):
            if heartrate_data and len(heartrate_data) > 0:
                # Latest reading
                latest_hr = heartrate_data[-1]
                processed["current_heart_rate"] = latest_hr.get("bpm")
                processed["heart_rate_timestamp"] = latest_hr.get("timestamp")

                # Aggregate recent readings
                recent_readings = [hr.get("bpm") for hr in heartrate_data[-10:] if hr.get("bpm")]
                if recent_readings:
                    processed["average_heart_rate"] = sum(recent_readings) / len(recent_readings)
                    processed["min_heart_rate"] = min(recent_readings)
                    processed["max_heart_rate"] = max(recent_readings)

    def _process_stress(self, data: dict[str, Any], processed: dict[str, Any]) -> None:
        """Process stress data (durations and day summary)."""
        if stress_data := data.get("stress", {}).get("data"):
            if stress_data and len(stress_data) > 0:
                latest_stress = stress_data[-1]
                if (stress_high := latest_stress.get("stress_high")) is not None:
                    processed["stress_high_duration"] = stress_high / 60
                if (recovery_high := latest_stress.get("recovery_high")) is not None:
                    processed["recovery_high_duration"] = recovery_high / 60
                processed["stress_day_summary"] = latest_stress.get("day_summary")

    def _process_resilience(self, data: dict[str, Any], processed: dict[str, Any]) -> None:
        """Process resilience data (level and recovery scores)."""
        if resilience_data := data.get("resilience", {}).get("data"):
            if resilience_data and len(resilience_data) > 0:
                latest_resilience = resilience_data[-1]
                processed["resilience_level"] = latest_resilience.get("level")

                if contributors := latest_resilience.get("contributors"):
                    processed["sleep_recovery_score"] = contributors.get("sleep_recovery")
                    processed["daytime_recovery_score"] = contributors.get("daytime_recovery")
                    processed["stress_resilience_score"] = contributors.get("stress")

    def _process_spo2(self, data: dict[str, Any], processed: dict[str, Any]) -> None:
        """Process SpO2 data (blood oxygen - Gen3 and Oura Ring 4 only)."""
        if spo2_data := data.get("spo2", {}).get("data"):
            if spo2_data and len(spo2_data) > 0:
                latest_spo2 = spo2_data[-1]
                if spo2_percentage := latest_spo2.get("spo2_percentage"):
                    processed["spo2_average"] = spo2_percentage.get("average")
                processed["breathing_disturbance_index"] = latest_spo2.get("breathing_disturbance_index")

    def _process_vo2_max(self, data: dict[str, Any], processed: dict[str, Any]) -> None:
        """Process VO2 Max fitness data."""
        if vo2_max_data := data.get("vo2_max", {}).get("data"):
            if vo2_max_data and len(vo2_max_data) > 0:
                latest_vo2 = vo2_max_data[-1]
                processed["vo2_max"] = latest_vo2.get("vo2_max")

    def _process_cardiovascular_age(self, data: dict[str, Any], processed: dict[str, Any]) -> None:
        """Process cardiovascular age data."""
        if cardiovascular_age_data := data.get("cardiovascular_age", {}).get("data"):
            if cardiovascular_age_data and len(cardiovascular_age_data) > 0:
                latest_cv_age = cardiovascular_age_data[-1]
                processed["cardiovascular_age"] = latest_cv_age.get("vascular_age")

    def _process_sleep_time(self, data: dict[str, Any], processed: dict[str, Any]) -> None:
        """Process sleep time recommendations (optimal bedtime windows)."""
        if sleep_time_data := data.get("sleep_time", {}).get("data"):
            if sleep_time_data and len(sleep_time_data) > 0:
                latest_sleep_time = sleep_time_data[-1]

                if optimal_bedtime := latest_sleep_time.get("optimal_bedtime"):
                    # Offsets are in seconds from midnight
                    # We need to convert them to a timestamp or time string
                    # For now, let's store the raw offsets or convert if needed
                    # The sensor definition expects a timestamp device class, but that requires a full datetime
                    # Given these are offsets from midnight of the 'day', we can construct a datetime

                    day_str = latest_sleep_time.get("day")
                    day_tz = optimal_bedtime.get("day_tz", 0)
                    start_offset = optimal_bedtime.get("start_offset")
                    end_offset = optimal_bedtime.get("end_offset")

                    if day_str and start_offset is not None:
                        # Construct approximate datetime for start
                        # Note: This is a simplification. Ideally we'd use the timezone info.
                        # But for Home Assistant timestamp sensor, we usually want a UTC ISO string.
                        # Since we don't have easy timezone handling here without external libs,
                        # and the offsets are from midnight, we might need to be careful.
                        # However, the previous implementation expected a value.
                        # Let's try to provide the offset in seconds if the sensor supports it,
                        # or maybe just the raw value if that's what was intended.
                        # Looking at const.py, device_class is "timestamp".

                        # Let's try to construct a proper ISO string if possible,
                        # or just pass the offset if we can't.
                        # Actually, let's look at how we can make this useful.
                        # If we just return the offset, it's not a timestamp.

                        # Let's parse the day
                        from datetime import datetime
                        try:
                            date_obj = datetime.strptime(day_str, "%Y-%m-%d")
                            # Add offsets (which are seconds from midnight)
                            # Note: day_tz is offset from GMT.
                            # If we want UTC time: Local = GMT + offset => GMT = Local - offset
                            # The offsets are from midnight local time?
                            # "Start offset from midnight in second"
                            # If I have 2025-11-10 00:00:00 Local
                            # And start_offset is -3600 (23:00 previous day)
                            # Then local start is 2025-11-09 23:00:00
                            # To get UTC, we subtract the timezone offset.

                            start_dt = date_obj + timedelta(seconds=start_offset) - timedelta(seconds=day_tz)
                            end_dt = date_obj + timedelta(seconds=end_offset) - timedelta(seconds=day_tz)

                            # Ensure we have timezone aware datetime for HA
                            # Since we calculated UTC, set it to UTC
                            from datetime import timezone
                            start_dt = start_dt.replace(tzinfo=timezone.utc)
                            end_dt = end_dt.replace(tzinfo=timezone.utc)

                            processed["optimal_bedtime_start"] = start_dt
                            processed["optimal_bedtime_end"] = end_dt
                        except Exception as e:
                            _LOGGER.warning("Error calculating sleep time: %s", e)
