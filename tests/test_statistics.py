"""Tests for Oura Ring statistics module."""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.oura.statistics import (
    STATISTICS_METADATA,
    DATA_SOURCE_CONFIG,
    _create_statistic,
    _get_baseline_sum,
    _parse_date_to_timestamp,
    _apply_transformation,
    _compute_percentage,
    _get_nested_value,
)


def test_statistics_metadata_completeness():
    """Test that all required sensors have metadata."""
    # These sensors should all have metadata
    required_sensors = [
        "sleep_score",
        "readiness_score",
        "activity_score",
        "steps",
        "vo2_max",
        "cardiovascular_age",
        "daily_workouts",
        "daily_mindfulness_sessions",
        "daily_tag_count",
    ]
    
    for sensor in required_sensors:
        assert sensor in STATISTICS_METADATA
        metadata = STATISTICS_METADATA[sensor]
        assert "name" in metadata
        assert "has_mean" in metadata
        assert "has_sum" in metadata


def test_data_source_config_structure():
    """Test that data source configuration is properly structured."""
    for source_key, config in DATA_SOURCE_CONFIG.items():
        # Either has mappings or a custom processor
        assert "mappings" in config or "custom_processor" in config
        
        if "mappings" in config:
            assert isinstance(config["mappings"], list)
            
            for mapping in config["mappings"]:
                assert "sensor_key" in mapping
                assert "api_path" in mapping
                assert mapping["sensor_key"] in STATISTICS_METADATA


def test_sleep_efficiency_uses_sleep_detail_mapping():
    """Test that sleep efficiency is mapped from detailed sleep data."""
    sleep_mappings = DATA_SOURCE_CONFIG["sleep"]["mappings"]
    sleep_detail_mappings = DATA_SOURCE_CONFIG["sleep_detail"]["mappings"]

    assert all(mapping["sensor_key"] != "sleep_efficiency" for mapping in sleep_mappings)
    assert {"sensor_key": "sleep_efficiency", "api_path": "efficiency"} in sleep_detail_mappings


def test_bedtime_timestamps_excluded_from_statistics():
    """Bedtime Start/End are timestamps and cannot be long-term statistics (issue #73)."""
    sleep_detail_mappings = DATA_SOURCE_CONFIG["sleep_detail"]["mappings"]

    assert all(mapping["sensor_key"] != "bedtime_start" for mapping in sleep_detail_mappings)
    assert all(mapping["sensor_key"] != "bedtime_end" for mapping in sleep_detail_mappings)
    assert "bedtime_start" not in STATISTICS_METADATA
    assert "bedtime_end" not in STATISTICS_METADATA


def test_collapse_sleep_detail_by_day_prefers_long_sleep():
    """Same-day nap + overnight sleep collapse to a single long_sleep record (issue #73)."""
    from custom_components.oura.statistics import _collapse_sleep_detail_by_day

    records = [
        {"day": "2024-01-15", "type": "long_sleep", "total_sleep_duration": 28800},
        {"day": "2024-01-15", "type": "late_nap", "total_sleep_duration": 3600},
        {"day": "2024-01-16", "type": "sleep", "total_sleep_duration": 1800},
    ]

    collapsed = _collapse_sleep_detail_by_day(records)

    by_day = {record["day"]: record for record in collapsed}
    assert len(collapsed) == 2
    assert by_day["2024-01-15"]["type"] == "long_sleep"
    assert by_day["2024-01-16"]["type"] == "sleep"


def test_collapse_sleep_detail_by_day_falls_back_to_longest():
    """Without a long_sleep record, the longest session for the day wins."""
    from custom_components.oura.statistics import _collapse_sleep_detail_by_day

    records = [
        {"day": "2024-01-15", "type": "late_nap", "total_sleep_duration": 1800},
        {"day": "2024-01-15", "type": "sleep", "total_sleep_duration": 3600},
    ]

    collapsed = _collapse_sleep_detail_by_day(records)

    assert len(collapsed) == 1
    assert collapsed[0]["total_sleep_duration"] == 3600


def test_total_sleep_duration_not_in_collapsed_mapping():
    """Total Sleep Duration is summed separately, not read off the single collapsed record (issue #73)."""
    sleep_detail_mappings = DATA_SOURCE_CONFIG["sleep_detail"]["mappings"]

    assert all(mapping["sensor_key"] != "total_sleep_duration" for mapping in sleep_detail_mappings)
    assert "total_sleep_duration" in STATISTICS_METADATA


def test_sum_total_sleep_duration_by_day_includes_naps():
    """Nap + overnight sleep on the same day both contribute to the day's total (issue #73)."""
    from custom_components.oura.statistics import _sum_total_sleep_duration_by_day

    records = [
        {"day": "2024-01-15", "type": "long_sleep", "total_sleep_duration": 18120},  # 5h02m
        {"day": "2024-01-15", "type": "late_nap", "total_sleep_duration": 1800},     # 30m
        {"day": "2024-01-16", "type": "sleep", "total_sleep_duration": 3600},
    ]

    totals = _sum_total_sleep_duration_by_day(records)

    assert totals["2024-01-15"] == 19920  # 5h32m
    assert totals["2024-01-16"] == 3600


def test_sum_total_sleep_duration_by_day_ignores_invalid_types():
    """Records with a type outside the valid-sleep set don't contribute to the sum."""
    from custom_components.oura.statistics import _sum_total_sleep_duration_by_day

    records = [
        {"day": "2024-01-15", "type": "long_sleep", "total_sleep_duration": 3600},
        {"day": "2024-01-15", "type": "rest", "total_sleep_duration": 999999},
        {"day": "2024-01-15", "total_sleep_duration": 999999},  # missing type
    ]

    totals = _sum_total_sleep_duration_by_day(records)

    assert totals["2024-01-15"] == 3600


def test_timestamp_parsing():
    """Test that date strings are correctly parsed to timestamps."""
    # Test valid date
    timestamp = _parse_date_to_timestamp("2024-01-15")
    assert timestamp is not None
    assert timestamp.year == 2024
    assert timestamp.month == 1
    assert timestamp.day == 15
    assert timestamp.hour == 12  # Should be noon UTC
    assert timestamp.tzinfo == timezone.utc
    
    # Test invalid date
    assert _parse_date_to_timestamp(None) is None
    assert _parse_date_to_timestamp("") is None
    assert _parse_date_to_timestamp("invalid") is None


def test_value_transformations():
    """Test that data transformations work correctly."""
    # Test seconds to hours
    assert _apply_transformation(3600, "seconds_to_hours") == 1.0
    assert _apply_transformation(7200, "seconds_to_hours") == 2.0
    
    # Test seconds to minutes
    assert _apply_transformation(60, "seconds_to_minutes") == 1.0
    assert _apply_transformation(300, "seconds_to_minutes") == 5.0
    
    # Test percentage calculation
    assert _apply_transformation(30, "percentage", total=100) == 30.0
    
    # Test ISO to datetime
    iso_str = "2024-01-15T08:30:00+00:00"
    dt = _apply_transformation(iso_str, "iso_to_datetime")
    assert dt is not None
    assert dt.year == 2024
    assert dt.month == 1
    assert dt.day == 15
    assert dt.hour == 8
    assert dt.minute == 30
    assert dt.tzinfo == timezone.utc

    # Test ISO to datetime with Z
    iso_str_z = "2024-01-15T08:30:00Z"
    dt_z = _apply_transformation(iso_str_z, "iso_to_datetime")
    assert dt_z is not None
    assert dt_z.hour == 8
    assert dt_z.tzinfo == timezone.utc
    
    # Test no transformation
    assert _apply_transformation(42, "unknown") == 42


def test_compute_percentage():
    """Test percentage computation."""
    entry = {
        "total_sleep_duration": 28800,  # 8 hours
        "deep_sleep_duration": 7200,    # 2 hours = 25%
        "rem_sleep_duration": 5760,     # 1.6 hours = 20%
    }
    
    deep_pct = _compute_percentage(entry, "deep_sleep_duration", "total_sleep_duration")
    assert deep_pct == 25.0
    
    rem_pct = _compute_percentage(entry, "rem_sleep_duration", "total_sleep_duration")
    assert rem_pct == 20.0
    
    # Test missing values
    assert _compute_percentage({}, "numerator", "denominator") is None
    assert _compute_percentage({"numerator": 10}, "numerator", "denominator") is None
    assert _compute_percentage({"numerator": 10, "denominator": 0}, "numerator", "denominator") is None


def test_get_nested_value():
    """Test nested value extraction."""
    data = {
        "score": 85,
        "contributors": {
            "efficiency": 90,
            "restfulness": 75,
        },
    }
    
    # Test direct access
    assert _get_nested_value(data, "score") == 85
    
    # Test nested access
    assert _get_nested_value(data, "contributors.efficiency") == 90
    assert _get_nested_value(data, "contributors.restfulness") == 75
    
    # Test missing values
    assert _get_nested_value(data, "missing") is None
    assert _get_nested_value(data, "contributors.missing") is None
    assert _get_nested_value(data, "missing.nested") is None


def test_statistics_metadata_state_class_alignment():
    """Test that total/total_increasing sensors use sum statistics."""
    sum_sensors = [
        "total_sleep_duration",
        "deep_sleep_duration",
        "rem_sleep_duration",
        "light_sleep_duration",
        "awake_time",
        "time_in_bed",
        "steps",
        "active_calories",
        "total_calories",
        "met_min_high",
        "met_min_medium",
        "met_min_low",
        "stress_high_duration",
        "recovery_high_duration",
        "daily_workouts",
        "daily_workout_distance",
        "daily_workout_calories",
        "daily_workout_duration",
        "daily_mindfulness_sessions",
        "daily_meditation_duration",
        "daily_tag_count",
        "daily_rest_mode_count",
        "daily_rest_mode_duration",
    ]
    for sensor_key in sum_sensors:
        assert STATISTICS_METADATA[sensor_key]["has_sum"] is True
        assert STATISTICS_METADATA[sensor_key]["has_mean"] is False

    mean_sensors = [
        "sleep_score",
        "sleep_efficiency",
        "restfulness",
        "sleep_timing",
        "sleep_latency",
        "deep_sleep_percentage",
        "rem_sleep_percentage",
        "readiness_score",
        "temperature_deviation",
        "resting_heart_rate",
        "hrv_balance",
        "activity_score",
        "target_calories",
        "average_sleep_hrv",
        "lowest_sleep_heart_rate",
        "average_sleep_heart_rate",
        "average_heart_rate",
        "min_heart_rate",
        "max_heart_rate",
        "spo2_average",
        "breathing_disturbance_index",
        "vo2_max",
        "cardiovascular_age",
        "sleep_recovery_score",
        "daytime_recovery_score",
        "stress_resilience_score",
    ]
    for sensor_key in mean_sensors:
        assert STATISTICS_METADATA[sensor_key]["has_mean"] is True
        assert STATISTICS_METADATA[sensor_key]["has_sum"] is False


@pytest.mark.anyio
async def test_create_statistic_builds_cumulative_sum(mock_hass, mock_config_entry):
    """Test that has_sum sensors use sorted data points with cumulative sum."""
    data_points = [
        {"timestamp": datetime(2024, 1, 3, 12, 0, 0, tzinfo=timezone.utc), "value": 300},
        {"timestamp": datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc), "value": 100},
        {"timestamp": datetime(2024, 1, 2, 12, 0, 0, tzinfo=timezone.utc), "value": 200},
    ]

    with patch("custom_components.oura.statistics.er.async_get") as mock_er_get, \
         patch("custom_components.oura.statistics.async_import_statistics_ha") as mock_import_ha:
        mock_registry = MagicMock()
        mock_er_get.return_value = mock_registry
        mock_registry.async_get_entity_id.return_value = "sensor.oura_ring_steps"

        await _create_statistic(mock_hass, "steps", data_points, mock_config_entry)

    assert mock_import_ha.call_count == 1
    _, metadata, statistics = mock_import_ha.call_args.args
    assert metadata["statistic_id"] == "sensor.oura_ring_steps"
    assert [point["start"].day for point in statistics] == [1, 2, 3]
    assert [point["state"] for point in statistics] == [100, 200, 300]
    assert [point["sum"] for point in statistics] == [100, 300, 600]


@pytest.mark.anyio
async def test_create_statistic_seeds_sum_from_baseline(mock_hass, mock_config_entry):
    """Reconciling a recent window continues the cumulative sum from the prior total."""
    data_points = [
        {"timestamp": datetime(2024, 1, 4, 12, 0, 0, tzinfo=timezone.utc), "value": 100},
        {"timestamp": datetime(2024, 1, 5, 12, 0, 0, tzinfo=timezone.utc), "value": 200},
    ]

    with patch("custom_components.oura.statistics.er.async_get") as mock_er_get, \
         patch("custom_components.oura.statistics.async_import_statistics_ha") as mock_import_ha, \
         patch("custom_components.oura.statistics._get_baseline_sum", new=AsyncMock(return_value=1000.0)):
        mock_registry = MagicMock()
        mock_er_get.return_value = mock_registry
        mock_registry.async_get_entity_id.return_value = "sensor.oura_ring_steps"

        await _create_statistic(mock_hass, "steps", data_points, mock_config_entry)

    _, _, statistics = mock_import_ha.call_args.args
    # Sums continue from the 1000.0 baseline instead of restarting at zero
    assert [point["sum"] for point in statistics] == [1100, 1300]


@pytest.mark.anyio
async def test_get_baseline_sum_returns_last_prior_sum(mock_hass):
    """Baseline is the cumulative sum of the most recent row before the window."""
    before = datetime(2024, 1, 5, 12, 0, 0, tzinfo=timezone.utc)
    recorder = MagicMock()
    recorder.async_add_executor_job = AsyncMock(
        return_value={"sensor.oura_ring_steps": [{"sum": 500.0}, {"sum": 900.0}]}
    )

    with patch("custom_components.oura.statistics.get_instance", return_value=recorder):
        baseline = await _get_baseline_sum(mock_hass, "sensor.oura_ring_steps", before)

    assert baseline == 900.0


@pytest.mark.anyio
async def test_get_baseline_sum_zero_when_no_history(mock_hass):
    """No prior statistics → baseline of 0.0 (full historical import behaviour)."""
    before = datetime(2024, 1, 5, 12, 0, 0, tzinfo=timezone.utc)
    recorder = MagicMock()
    recorder.async_add_executor_job = AsyncMock(return_value={})

    with patch("custom_components.oura.statistics.get_instance", return_value=recorder):
        baseline = await _get_baseline_sum(mock_hass, "sensor.oura_ring_steps", before)

    assert baseline == 0.0


