"""Tests for Oura Ring sensor platform."""
from datetime import date
from unittest.mock import MagicMock, Mock

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ID
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.util import dt as dt_util

from custom_components.oura.const import DOMAIN, SENSOR_TYPES
from custom_components.oura.binary_sensor import OuraRestModeBinarySensor
from custom_components.oura.coordinator import OuraDataUpdateCoordinator
from custom_components.oura.sensor import OuraSensor


@pytest.fixture
def mock_coordinator():
    """Create a mock coordinator."""
    coordinator = MagicMock(spec=OuraDataUpdateCoordinator)
    coordinator.data = {"sleep_score": 85, "readiness_score": 90}
    coordinator.last_update_success = True
    
    # Mock the config entry
    mock_entry = MagicMock(spec=ConfigEntry)
    mock_entry.entry_id = "test_entry_id_12345"
    coordinator.entry = mock_entry
    
    return coordinator


def test_sensor_device_info(mock_coordinator):
    """Test that sensor returns correct DeviceInfo."""
    sensor = OuraSensor(
        coordinator=mock_coordinator,
        sensor_type="sleep_score",
        sensor_info=SENSOR_TYPES["sleep_score"],
    )
    
    device_info = sensor.device_info
    
    assert device_info is not None
    assert device_info["identifiers"] == {(DOMAIN, "test_entry_id_12345")}
    assert device_info["name"] == "Oura Ring"
    assert device_info["manufacturer"] == "Oura"
    assert device_info["model"] == "Oura Ring"
    assert device_info["entry_type"] == DeviceEntryType.SERVICE


def test_sensor_unique_id_includes_entry(mock_coordinator):
    """Test that unique_id includes entry_id."""
    sensor = OuraSensor(
        coordinator=mock_coordinator,
        sensor_type="sleep_score",
        sensor_info=SENSOR_TYPES["sleep_score"],
    )
    
    assert sensor.unique_id == "test_entry_id_12345_sleep_score"


def test_sensor_has_entity_name(mock_coordinator):
    """Test that has_entity_name attribute is set to True."""
    sensor = OuraSensor(
        coordinator=mock_coordinator,
        sensor_type="sleep_score",
        sensor_info=SENSOR_TYPES["sleep_score"],
    )
    
    assert sensor.has_entity_name is True


def test_sensor_translation_key(mock_coordinator):
    """Test that translation_key is properly set."""
    sensor = OuraSensor(
        coordinator=mock_coordinator,
        sensor_type="sleep_score",
        sensor_info=SENSOR_TYPES["sleep_score"],
    )
    
    assert sensor.translation_key == "sleep_score"


def test_sensor_native_value(mock_coordinator):
    """Test that native_value returns correct data from coordinator."""
    sensor = OuraSensor(
        coordinator=mock_coordinator,
        sensor_type="sleep_score",
        sensor_info=SENSOR_TYPES["sleep_score"],
    )
    
    assert sensor.native_value == 85


def test_sensor_available_when_data_exists(mock_coordinator):
    """Test sensor is available when data exists."""
    sensor = OuraSensor(
        coordinator=mock_coordinator,
        sensor_type="sleep_score",
        sensor_info=SENSOR_TYPES["sleep_score"],
    )
    
    assert sensor.available is True


def test_sensor_unavailable_when_data_missing(mock_coordinator):
    """Test sensor is unavailable when data is missing."""
    mock_coordinator.data = {}
    
    sensor = OuraSensor(
        coordinator=mock_coordinator,
        sensor_type="sleep_score",
        sensor_info=SENSOR_TYPES["sleep_score"],
    )
    
    assert sensor.available is False


def test_boolean_sensor_true_value(mock_coordinator):
    """Test that boolean sensor correctly exposes True value."""
    mock_coordinator.data = {"low_battery_alert": True}
    
    sensor = OuraSensor(
        coordinator=mock_coordinator,
        sensor_type="low_battery_alert",
        sensor_info=SENSOR_TYPES["low_battery_alert"],
    )
    
    assert sensor.native_value is True
    assert sensor.available is True


def test_boolean_sensor_false_value(mock_coordinator):
    """Test that boolean sensor correctly exposes False value."""
    mock_coordinator.data = {"low_battery_alert": False}
    
    sensor = OuraSensor(
        coordinator=mock_coordinator,
        sensor_type="low_battery_alert",
        sensor_info=SENSOR_TYPES["low_battery_alert"],
    )
    
    assert sensor.native_value is False
    assert sensor.available is True


def test_tags_sensor_exposes_tag_attributes(mock_coordinator):
    """Test tags sensor exposes structured tag attributes."""
    mock_coordinator.data = {
        "tags_today": "coffee, travel",
        "_tags_today_list": ["coffee", "travel"],
        "_enhanced_tags_today": [{"tag_type_code": "coffee", "comment": "Morning coffee"}],
    }

    sensor = OuraSensor(
        coordinator=mock_coordinator,
        sensor_type="tags_today",
        sensor_info=SENSOR_TYPES["tags_today"],
    )

    assert sensor.native_value == "coffee, travel"
    assert sensor.extra_state_attributes == {
        "tags": ["coffee", "travel"],
        "enhanced_tags": [{"tag_type_code": "coffee", "comment": "Morning coffee"}],
    }


def test_workout_sensor_exposes_raw_workout_attribute(mock_coordinator):
    """Test workout summary sensors expose the last workout payload."""
    mock_coordinator.data = {
        "last_workout_type": "running",
        "_last_workout_raw": {"activity": "running", "distance": 5000},
    }

    sensor = OuraSensor(
        coordinator=mock_coordinator,
        sensor_type="last_workout_type",
        sensor_info=SENSOR_TYPES["last_workout_type"],
    )

    assert sensor.extra_state_attributes == {"workout": {"activity": "running", "distance": 5000}}


def test_last_workout_source_accepts_unlisted_values(mock_coordinator):
    """Test workout source is plain text so new Oura source values don't break the entity."""
    mock_coordinator.data = {"last_workout_source": "some_future_source"}

    sensor = OuraSensor(
        coordinator=mock_coordinator,
        sensor_type="last_workout_source",
        sensor_info=SENSOR_TYPES["last_workout_source"],
    )

    assert sensor.device_class is None
    assert sensor.native_value == "some_future_source"


def test_workouts_today_sensor_exposes_workout_list(mock_coordinator):
    """Test workouts_today sensor exposes the full list of today's workouts."""
    workouts = [
        {"activity": "strength_training", "start_datetime": "2026-03-24T06:00:00+00:00"},
        {"activity": "cycling", "start_datetime": "2026-03-24T07:00:00+00:00"},
    ]
    mock_coordinator.data = {
        "workouts_today": 2,
        "_workouts_today_list": workouts,
    }

    sensor = OuraSensor(
        coordinator=mock_coordinator,
        sensor_type="workouts_today",
        sensor_info=SENSOR_TYPES["workouts_today"],
    )

    assert sensor.native_value == 2
    assert sensor.extra_state_attributes == {"workouts": workouts}


def test_workouts_attribute_not_on_other_sensors(mock_coordinator):
    """Test that other sensors don't pick up the workouts attribute."""
    mock_coordinator.data = {
        "sleep_score": 82,
        "workouts_today": 1,
        "_workouts_today_list": [{"activity": "running"}],
    }

    sensor = OuraSensor(
        coordinator=mock_coordinator,
        sensor_type="sleep_score",
        sensor_info=SENSOR_TYPES["sleep_score"],
    )

    assert sensor.native_value == 82
    assert sensor.extra_state_attributes is None


def test_workouts_today_sensor_without_list(mock_coordinator):
    """Test workouts_today attributes when no list has been published."""
    mock_coordinator.data = {"workouts_today": 0}

    sensor = OuraSensor(
        coordinator=mock_coordinator,
        sensor_type="workouts_today",
        sensor_info=SENSOR_TYPES["workouts_today"],
    )

    assert sensor.native_value == 0
    assert sensor.extra_state_attributes is None


@pytest.mark.parametrize(
    ("sensor_type", "day_key"),
    [
        ("active_calories", "_day_activity"),
        ("equivalent_walking_distance", "_day_activity"),
        ("total_sleep_duration", "_day_sleep_detail"),
        ("stress_high_duration", "_day_stress"),
        ("workouts_today", "_day_workout"),
        ("meditation_duration_today", "_day_session"),
        ("tag_count_today", "_day_tag"),
    ],
)
def test_daily_total_sensor_last_reset_is_start_of_its_day(mock_coordinator, sensor_type, day_key):
    """Daily totals report last_reset so the recorder sees a new day as a new cycle (#86)."""
    mock_coordinator.data = {sensor_type: 10, day_key: date(2026, 10, 20)}
    sensor = OuraSensor(mock_coordinator, sensor_type, SENSOR_TYPES[sensor_type])

    assert sensor.last_reset == dt_util.start_of_local_day(date(2026, 10, 20))
    assert sensor.state_attributes == {"last_reset": sensor.last_reset.isoformat()}

    mock_coordinator.data[day_key] = date(2026, 10, 21)
    assert sensor.last_reset == dt_util.start_of_local_day(date(2026, 10, 21))


def test_daily_total_sensor_last_reset_none_without_day(mock_coordinator):
    """No day known means no last_reset."""
    mock_coordinator.data = {"active_calories": 300}
    sensor = OuraSensor(mock_coordinator, "active_calories", SENSOR_TYPES["active_calories"])

    assert sensor.last_reset is None


@pytest.mark.parametrize("sensor_type", ["steps", "activity_score"])
def test_non_total_sensor_has_no_last_reset(mock_coordinator, sensor_type):
    """HA only accepts last_reset on state_class total."""
    mock_coordinator.data = {sensor_type: 100, "_day_activity": date(2026, 10, 20)}
    sensor = OuraSensor(mock_coordinator, sensor_type, SENSOR_TYPES[sensor_type])

    assert sensor.last_reset is None

    """Test rest mode binary sensor state and attributes."""
    mock_coordinator.data = {
        "rest_mode_active": True,
        "_active_rest_mode_raw": {
            "id": "rest-mode-1",
            "start_day": "2026-03-24",
            "end_day": "2026-03-25",
        },
    }

    sensor = OuraRestModeBinarySensor(mock_coordinator)

    assert sensor.is_on is True
    assert sensor.available is True
    assert sensor.extra_state_attributes == {
        "id": "rest-mode-1",
        "start_day": "2026-03-24",
        "end_day": "2026-03-25",
    }

