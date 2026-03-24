"""Tests for Oura Ring sensor platform."""
from unittest.mock import MagicMock, Mock

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ID
from homeassistant.helpers.device_registry import DeviceEntryType

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


def test_rest_mode_binary_sensor(mock_coordinator):
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

