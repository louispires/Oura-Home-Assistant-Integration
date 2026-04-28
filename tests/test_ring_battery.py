"""Tests for ring battery level and ring configuration functionality."""
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.oura.coordinator import OuraDataUpdateCoordinator


# ---------------------------------------------------------------------------
# Coordinator: ring battery level processing
# ---------------------------------------------------------------------------

class TestProcessRingBatteryLevel:
    """Tests for _process_ring_battery_level."""

    def _make_coordinator(self):
        coordinator = MagicMock(spec=OuraDataUpdateCoordinator)
        coordinator.data = None
        return coordinator

    def test_battery_level_and_not_charging(self):
        """Battery level and charging=False are extracted correctly."""
        coordinator = OuraDataUpdateCoordinator.__new__(OuraDataUpdateCoordinator)
        data = {
            "ring_battery_level": {
                "data": [
                    {
                        "timestamp": "2024-01-15T08:00:00+00:00",
                        "timestamp_unix": 1705312800000,
                        "level": 72,
                        "charging": False,
                        "in_charger": False,
                    }
                ]
            }
        }
        processed = {}
        coordinator._process_ring_battery_level(data, processed)

        assert processed["ring_battery_level"] == 72
        assert processed["ring_battery_charging"] is False

    def test_battery_level_while_charging(self):
        """Battery level and charging=True are extracted correctly."""
        coordinator = OuraDataUpdateCoordinator.__new__(OuraDataUpdateCoordinator)
        data = {
            "ring_battery_level": {
                "data": [
                    {
                        "timestamp": "2024-01-15T10:00:00+00:00",
                        "timestamp_unix": 1705320000000,
                        "level": 85,
                        "charging": True,
                        "in_charger": True,
                    }
                ]
            }
        }
        processed = {}
        coordinator._process_ring_battery_level(data, processed)

        assert processed["ring_battery_level"] == 85
        assert processed["ring_battery_charging"] is True

    def test_charging_none_when_field_missing(self):
        """charging key becomes None when not present in API response."""
        coordinator = OuraDataUpdateCoordinator.__new__(OuraDataUpdateCoordinator)
        data = {
            "ring_battery_level": {
                "data": [{"timestamp": "2024-01-15T08:00:00+00:00", "timestamp_unix": 1705312800000, "level": 60}]
            }
        }
        processed = {}
        coordinator._process_ring_battery_level(data, processed)

        assert processed["ring_battery_level"] == 60
        assert processed["ring_battery_charging"] is None

    def test_empty_data_sets_nothing(self):
        """Empty data list does not set any battery keys."""
        coordinator = OuraDataUpdateCoordinator.__new__(OuraDataUpdateCoordinator)
        data = {"ring_battery_level": {"data": []}}
        processed = {}
        coordinator._process_ring_battery_level(data, processed)

        assert "ring_battery_level" not in processed
        assert "ring_battery_charging" not in processed

    def test_missing_key_sets_nothing(self):
        """Missing ring_battery_level key does not set any battery keys."""
        coordinator = OuraDataUpdateCoordinator.__new__(OuraDataUpdateCoordinator)
        processed = {}
        coordinator._process_ring_battery_level({}, processed)

        assert "ring_battery_level" not in processed

    def test_latest_reading_is_used(self):
        """The last entry in the data list is used as the current value."""
        coordinator = OuraDataUpdateCoordinator.__new__(OuraDataUpdateCoordinator)
        data = {
            "ring_battery_level": {
                "data": [
                    {"timestamp": "2024-01-15T06:00:00+00:00", "timestamp_unix": 1705305600000, "level": 20, "charging": False},
                    {"timestamp": "2024-01-15T10:00:00+00:00", "timestamp_unix": 1705320000000, "level": 95, "charging": True},
                ]
            }
        }
        processed = {}
        coordinator._process_ring_battery_level(data, processed)

        assert processed["ring_battery_level"] == 95
        assert processed["ring_battery_charging"] is True


# ---------------------------------------------------------------------------
# Coordinator: ring configuration processing
# ---------------------------------------------------------------------------

class TestProcessRingConfiguration:
    """Tests for _process_ring_configuration."""

    def test_all_fields_extracted(self):
        """All ring configuration fields are extracted into processed dict."""
        coordinator = OuraDataUpdateCoordinator.__new__(OuraDataUpdateCoordinator)
        data = {
            "ring_configuration": {
                "data": [
                    {
                        "id": "ring-1",
                        "hardware_type": "gen4",
                        "firmware_version": "2.8.10",
                        "color": "stealth_black",
                        "design": "horizon",
                        "size": 9,
                    }
                ]
            }
        }
        processed = {}
        coordinator._process_ring_configuration(data, processed)

        assert processed["ring_hardware_type"] == "gen4"
        assert processed["ring_firmware_version"] == "2.8.10"
        assert processed["ring_color"] == "stealth_black"
        assert processed["ring_design"] == "horizon"
        assert processed["ring_size"] == 9

    def test_optional_fields_none_when_missing(self):
        """Optional fields default to None when absent from API response."""
        coordinator = OuraDataUpdateCoordinator.__new__(OuraDataUpdateCoordinator)
        data = {
            "ring_configuration": {
                "data": [{"id": "ring-1"}]
            }
        }
        processed = {}
        coordinator._process_ring_configuration(data, processed)

        assert processed["ring_hardware_type"] is None
        assert processed["ring_firmware_version"] is None
        assert processed["ring_color"] is None

    def test_empty_data_sets_nothing(self):
        """Empty data list does not set any ring configuration keys."""
        coordinator = OuraDataUpdateCoordinator.__new__(OuraDataUpdateCoordinator)
        processed = {}
        coordinator._process_ring_configuration({"ring_configuration": {"data": []}}, processed)

        assert "ring_hardware_type" not in processed

    def test_first_config_used_for_multiple_rings(self):
        """First ring configuration entry is used when multiple exist."""
        coordinator = OuraDataUpdateCoordinator.__new__(OuraDataUpdateCoordinator)
        data = {
            "ring_configuration": {
                "data": [
                    {"id": "ring-1", "hardware_type": "gen4", "firmware_version": "2.8.10"},
                    {"id": "ring-2", "hardware_type": "gen3", "firmware_version": "1.5.0"},
                ]
            }
        }
        processed = {}
        coordinator._process_ring_configuration(data, processed)

        assert processed["ring_hardware_type"] == "gen4"


# ---------------------------------------------------------------------------
# API client: ring_battery_level endpoint
# ---------------------------------------------------------------------------

class TestRingBatteryApiMethod:
    """Tests for OuraApiClient._async_get_ring_battery_level."""

    @pytest.mark.anyio
    async def test_uses_latest_param(self):
        """Battery level fetch always uses latest=true parameter."""
        from custom_components.oura.api import OuraApiClient

        hass = MagicMock()
        hass.config.time_zone = "UTC"
        session = MagicMock()
        entry = MagicMock()
        client = OuraApiClient(hass, session, entry)

        expected_response = {"data": [{"level": 80, "charging": False, "timestamp": "2024-01-15T10:00:00+00:00", "timestamp_unix": 1705320000000}]}
        client._async_get = AsyncMock(return_value=expected_response)

        result = await client._async_get_ring_battery_level(date(2024, 1, 15), date(2024, 1, 16))

        client._async_get.assert_awaited_once()
        _, call_params = client._async_get.call_args.args
        assert call_params.get("latest") == "true"
        assert result == expected_response

    @pytest.mark.anyio
    async def test_returns_empty_on_401(self):
        """Battery level returns empty data on 401 (feature not available)."""
        from aiohttp import ClientResponseError
        from custom_components.oura.api import OuraApiClient

        hass = MagicMock()
        session = MagicMock()
        entry = MagicMock()
        client = OuraApiClient(hass, session, entry)

        err = ClientResponseError(request_info=MagicMock(), history=(), status=401)
        client._async_get = AsyncMock(side_effect=err)

        result = await client._async_get_ring_battery_level(date(2024, 1, 15), date(2024, 1, 16))

        assert result == {"data": []}

    @pytest.mark.anyio
    async def test_returns_empty_on_404(self):
        """Battery level returns empty data on 404."""
        from aiohttp import ClientResponseError
        from custom_components.oura.api import OuraApiClient

        hass = MagicMock()
        session = MagicMock()
        entry = MagicMock()
        client = OuraApiClient(hass, session, entry)

        err = ClientResponseError(request_info=MagicMock(), history=(), status=404)
        client._async_get = AsyncMock(side_effect=err)

        result = await client._async_get_ring_battery_level(date(2024, 1, 15), date(2024, 1, 16))

        assert result == {"data": []}


# ---------------------------------------------------------------------------
# Binary sensor: OuraRingChargingBinarySensor
# ---------------------------------------------------------------------------

class TestOuraRingChargingBinarySensor:
    """Tests for OuraRingChargingBinarySensor."""

    def _make_sensor(self, coordinator_data):
        from custom_components.oura.binary_sensor import OuraRingChargingBinarySensor

        coordinator = MagicMock()
        coordinator.data = coordinator_data
        entry = MagicMock()
        entry.entry_id = "test_entry"
        coordinator.entry = entry

        sensor = OuraRingChargingBinarySensor.__new__(OuraRingChargingBinarySensor)
        sensor.coordinator = coordinator
        sensor._attr_unique_id = f"{entry.entry_id}_ring_battery_charging"
        return sensor

    def test_is_on_true_when_charging(self):
        """is_on returns True when ring is charging."""
        sensor = self._make_sensor({"ring_battery_charging": True})
        assert sensor.is_on is True

    def test_is_on_false_when_not_charging(self):
        """is_on returns False when ring is not charging."""
        sensor = self._make_sensor({"ring_battery_charging": False})
        assert sensor.is_on is False

    def test_is_on_none_when_no_data(self):
        """is_on returns None when coordinator has no data."""
        sensor = self._make_sensor(None)
        assert sensor.is_on is None

    def test_available_true_when_data_present(self):
        """available returns True when charging data is present."""
        sensor = self._make_sensor({"ring_battery_charging": True})
        assert sensor.available is True

    def test_available_false_when_charging_none(self):
        """available returns False when charging value is None (not yet loaded)."""
        sensor = self._make_sensor({"ring_battery_charging": None})
        assert sensor.available is False

    def test_available_false_when_key_missing(self):
        """available returns False when ring_battery_charging key is absent."""
        sensor = self._make_sensor({"sleep_score": 85})
        assert sensor.available is False

    def test_available_false_when_coordinator_data_none(self):
        """available returns False when coordinator.data is None."""
        sensor = self._make_sensor(None)
        assert sensor.available is False


# ---------------------------------------------------------------------------
# Device info: ring config enriches model and sw_version
# ---------------------------------------------------------------------------

class TestDeviceInfoEnrichment:
    """Tests for device info enrichment from ring configuration."""

    def _make_sensor_entity(self, coordinator_data):
        from custom_components.oura.sensor import OuraSensor
        from custom_components.oura.const import SENSOR_TYPES

        coordinator = MagicMock()
        coordinator.data = coordinator_data
        entry = MagicMock()
        entry.entry_id = "test_entry"
        coordinator.entry = entry

        sensor_type = "ring_battery_level"
        sensor = OuraSensor.__new__(OuraSensor)
        sensor.coordinator = coordinator
        sensor._sensor_type = sensor_type
        return sensor

    def test_model_uses_hardware_type(self):
        """device_info model is 'Oura Ring Gen4' when hardware_type=gen4."""
        sensor = self._make_sensor_entity({"ring_hardware_type": "gen4", "ring_firmware_version": "2.8.10"})
        info = sensor.device_info
        assert info["model"] == "Oura Ring Gen4"

    def test_sw_version_uses_firmware_version(self):
        """device_info sw_version is set from ring firmware_version."""
        sensor = self._make_sensor_entity({"ring_hardware_type": "gen4", "ring_firmware_version": "2.8.10"})
        info = sensor.device_info
        assert info["sw_version"] == "2.8.10"

    def test_model_defaults_when_no_config(self):
        """device_info model falls back to 'Oura Ring' when no ring config available."""
        sensor = self._make_sensor_entity({})
        info = sensor.device_info
        assert info["model"] == "Oura Ring"

    def test_sw_version_none_when_no_firmware(self):
        """device_info sw_version is None when firmware_version not available."""
        sensor = self._make_sensor_entity({"ring_hardware_type": "gen3"})
        info = sensor.device_info
        assert info.get("sw_version") is None

    def test_model_defaults_when_coordinator_data_none(self):
        """device_info model falls back to 'Oura Ring' when coordinator.data is None."""
        sensor = self._make_sensor_entity(None)
        info = sensor.device_info
        assert info["model"] == "Oura Ring"
