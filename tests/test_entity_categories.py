"""Tests for entity categories and metadata."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "custom_components"))

from custom_components.oura.const import SENSOR_TYPES


def test_entity_categories_assigned():
    """Test that entity categories are properly assigned."""
    diagnostic_sensors = [
        "deep_sleep_percentage",
        "rem_sleep_percentage",
        "target_calories",
        "min_heart_rate",
        "max_heart_rate",
        "breathing_disturbance_index",
        "optimal_bedtime_start",
        "optimal_bedtime_end",
        "low_battery_alert",
    ]
    
    for sensor_key in diagnostic_sensors:
        assert sensor_key in SENSOR_TYPES, f"Sensor {sensor_key} not in SENSOR_TYPES"
        assert SENSOR_TYPES[sensor_key].get("entity_category") == "diagnostic", \
            f"Sensor {sensor_key} should have diagnostic category"


def test_low_battery_alert_metadata():
    """Test that low_battery_alert sensor has correct metadata."""
    assert "low_battery_alert" in SENSOR_TYPES, "low_battery_alert sensor should exist"
    
    sensor_info = SENSOR_TYPES["low_battery_alert"]
    assert sensor_info["name"] == "Low Battery Alert", "Name should be 'Low Battery Alert'"
    assert sensor_info["icon"] == "mdi:battery-alert", "Icon should be battery alert"
    assert sensor_info["unit"] is None, "Boolean sensor should have no unit"
    assert sensor_info["device_class"] is None, "Boolean sensor should have no device_class"
    assert sensor_info["state_class"] is None, "Boolean sensor should have no state_class"
    assert sensor_info.get("entity_category") == "diagnostic", "Should be diagnostic category"


def test_state_classes_improved():
    """Test that state classes are properly assigned for cumulative values."""
    # Total/cumulative sensors should use 'total' or 'total_increasing'
    total_sensors = {
        "total_sleep_duration": "total",
        "deep_sleep_duration": "total",
        "rem_sleep_duration": "total",
        "light_sleep_duration": "total",
        "awake_time": "total",
        "time_in_bed": "total",
        "steps": "total_increasing",
        "active_calories": "total",
        "total_calories": "total",
        "met_min_high": "total",
        "met_min_medium": "total",
        "met_min_low": "total",
        "stress_high_duration": "total",
        "recovery_high_duration": "total",
        "equivalent_walking_distance": "total",
    }
    
    for sensor_key, expected_state_class in total_sensors.items():
        assert sensor_key in SENSOR_TYPES, f"Sensor {sensor_key} not in SENSOR_TYPES"
        actual = SENSOR_TYPES[sensor_key].get("state_class")
        assert actual == expected_state_class, \
            f"Sensor {sensor_key} should have state_class '{expected_state_class}', got '{actual}'"


def test_measurement_state_classes():
    """Test that measurement sensors have correct state class."""
    measurement_sensors = [
        "sleep_score",
        "sleep_efficiency",
        "restfulness",
        "sleep_latency",
        "sleep_timing",
        "readiness_score",
        "temperature_deviation",
        "activity_score",
        "current_heart_rate",
        "average_heart_rate",
        "spo2_average",
        "vo2_max",
    ]
    
    for sensor_key in measurement_sensors:
        assert sensor_key in SENSOR_TYPES, f"Sensor {sensor_key} not in SENSOR_TYPES"
        assert SENSOR_TYPES[sensor_key].get("state_class") == "measurement", \
            f"Sensor {sensor_key} should have state_class 'measurement'"


def test_no_state_class_for_text_sensors():
    """Test that text-based sensors don't have state_class."""
    text_sensors = ["stress_day_summary", "resilience_level", "last_workout_source"]
    
    for sensor_key in text_sensors:
        assert sensor_key in SENSOR_TYPES, f"Sensor {sensor_key} not in SENSOR_TYPES"
        assert SENSOR_TYPES[sensor_key].get("state_class") is None, \
            f"Sensor {sensor_key} should not have a state_class"


def test_all_sensors_have_entity_category_key():
    """Test that all sensors have entity_category key (even if None)."""
    for sensor_key, sensor_info in SENSOR_TYPES.items():
        assert "entity_category" in sensor_info, \
            f"Sensor {sensor_key} missing entity_category key"


def test_primary_sensors_not_diagnostic():
    """Test that primary health sensors are not marked as diagnostic."""
    primary_sensors = [
        "sleep_score",
        "total_sleep_duration",
        "readiness_score",
        "activity_score",
        "steps",
        "current_heart_rate",
        "average_heart_rate",
        "spo2_average",
        "vo2_max",
    ]
    
    for sensor_key in primary_sensors:
        assert sensor_key in SENSOR_TYPES, f"Sensor {sensor_key} not in SENSOR_TYPES"
        assert SENSOR_TYPES[sensor_key].get("entity_category") is None, \
            f"Sensor {sensor_key} should not be diagnostic (primary health metric)"
