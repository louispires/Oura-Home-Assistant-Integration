"""Tests for Oura Ring statistics import logic."""
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from custom_components.oura.statistics import async_import_statistics
from custom_components.oura.const import DOMAIN

@pytest.mark.anyio
async def test_import_statistics_entity_exists(mock_hass: HomeAssistant, mock_config_entry: ConfigEntry):
    """Test importing statistics when entity exists (uses recorder source)."""
    
    data = {
        "sleep": {
            "data": [
                {
                    "day": "2024-01-01",
                    "score": 85
                }
            ]
        }
    }
    
    with patch("custom_components.oura.statistics.er.async_get") as mock_er_get, \
         patch("custom_components.oura.statistics.async_import_statistics_ha") as mock_import_ha, \
         patch("custom_components.oura.statistics.async_add_external_statistics") as mock_add_external:
        
        mock_registry = MagicMock()
        mock_er_get.return_value = mock_registry
        # Simulate entity exists
        mock_registry.async_get_entity_id.return_value = "sensor.oura_ring_sleep_score"
        
        await async_import_statistics(mock_hass, data, mock_config_entry)
        
        # Should use async_import_statistics_ha (recorder source)
        assert mock_import_ha.called
        assert not mock_add_external.called
        
        # Check metadata source
        # The call might happen multiple times for different sensors, find the one for sleep_score
        found = False
        for call in mock_import_ha.call_args_list:
            args, _ = call
            metadata = args[1]
            if metadata["statistic_id"] == "sensor.oura_ring_sleep_score":
                assert metadata["source"] == "recorder"
                found = True
                break
        assert found

@pytest.mark.anyio
async def test_import_statistics_entity_missing(mock_hass: HomeAssistant, mock_config_entry: ConfigEntry):
    """Test importing statistics when entity missing (uses recorder source with fallback ID)."""
    
    data = {
        "sleep": {
            "data": [
                {
                    "day": "2024-01-01",
                    "score": 85
                }
            ]
        }
    }
    
    with patch("custom_components.oura.statistics.er.async_get") as mock_er_get, \
         patch("custom_components.oura.statistics.async_import_statistics_ha") as mock_import_ha, \
         patch("custom_components.oura.statistics.async_add_external_statistics") as mock_add_external:
        
        mock_registry = MagicMock()
        mock_er_get.return_value = mock_registry
        # Simulate entity missing
        mock_registry.async_get_entity_id.return_value = None
        
        await async_import_statistics(mock_hass, data, mock_config_entry)
        
        # Should use async_import_statistics_ha (recorder source) because fallback ID is sensor.xxx
        assert mock_import_ha.called
        assert not mock_add_external.called
        
        # Check metadata source
        found = False
        for call in mock_import_ha.call_args_list:
            args, _ = call
            metadata = args[1]
            if metadata["statistic_id"] == "sensor.oura_ring_sleep_score":
                assert metadata["source"] == "recorder"
                found = True
                break
        assert found


@pytest.mark.anyio
async def test_import_statistics_sums_total_sleep_duration_across_sessions(
    mock_hass: HomeAssistant, mock_config_entry: ConfigEntry
):
    """Total Sleep Duration sums nap + long_sleep for the day; other stats stay on long_sleep (issue #73)."""

    data = {
        "sleep_detail": {
            "data": [
                {
                    "day": "2024-01-15",
                    "type": "long_sleep",
                    "total_sleep_duration": 18120,  # 5h02m
                    "deep_sleep_duration": 3600,
                    "efficiency": 90,
                },
                {
                    "day": "2024-01-15",
                    "type": "late_nap",
                    "total_sleep_duration": 1800,  # 30m
                    "deep_sleep_duration": 300,
                    "efficiency": 80,
                },
            ]
        }
    }

    with patch("custom_components.oura.statistics.er.async_get") as mock_er_get, \
         patch("custom_components.oura.statistics.async_import_statistics_ha") as mock_import_ha, \
         patch("custom_components.oura.statistics.async_add_external_statistics") as mock_add_external:

        mock_registry = MagicMock()
        mock_er_get.return_value = mock_registry
        mock_registry.async_get_entity_id.return_value = None

        await async_import_statistics(mock_hass, data, mock_config_entry)

        assert not mock_add_external.called

        total_sleep_points = None
        deep_sleep_points = None
        for call in mock_import_ha.call_args_list:
            args, _ = call
            metadata, statistics = args[1], args[2]
            if metadata["statistic_id"] == "sensor.oura_ring_total_sleep_duration":
                total_sleep_points = statistics
            elif metadata["statistic_id"] == "sensor.oura_ring_deep_sleep_duration":
                deep_sleep_points = statistics

        # Summed across both sessions: (18120 + 1800) / 3600 hours
        assert total_sleep_points is not None
        assert total_sleep_points[0]["state"] == pytest.approx(19920 / 3600)

        # Still sourced from the single long_sleep record, not summed
        assert deep_sleep_points is not None
        assert deep_sleep_points[0]["state"] == pytest.approx(3600 / 3600)
