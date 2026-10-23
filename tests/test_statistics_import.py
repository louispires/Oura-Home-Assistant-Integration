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
async def test_import_statistics_leaves_sleep_sums_to_the_recorder(
    mock_hass: HomeAssistant, mock_config_entry: ConfigEntry
):
    """Sleep duration sums are not imported (#86); per-night means still come from long_sleep."""

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

        imported = {
            call.args[1]["statistic_id"]: call.args[2] for call in mock_import_ha.call_args_list
        }

    assert "sensor.oura_ring_total_sleep_duration" not in imported
    assert "sensor.oura_ring_deep_sleep_duration" not in imported
    assert imported["sensor.oura_ring_sleep_efficiency"][0]["mean"] == 90
