"""Pytest fixtures for Oura Ring integration tests."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET
from homeassistant.core import HomeAssistant

from custom_components.oura.const import DOMAIN


@pytest.fixture
def mock_config_entry() -> ConfigEntry:
    """Mock ConfigEntry for testing."""
    return ConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title="Oura Ring",
        data={
            "token": {
                "access_token": "mock_access_token",
                "refresh_token": "mock_refresh_token",
                "expires_in": 3600,
                "expires_at": (datetime.now() + timedelta(hours=1)).timestamp(),
            },
            CONF_CLIENT_ID: "mock_client_id",
            CONF_CLIENT_SECRET: "mock_client_secret",
        },
        options={
            "update_interval": 5,
            "historical_months": 3,
            "historical_data_imported": True,
        },
        entry_id="mock_entry_id",
        source="user",
        unique_id="mock_unique_id",
        discovery_keys={},
        subentries_data={},
    )


@pytest.fixture
def mock_oura_api_data() -> dict[str, Any]:
    """Mock Oura API response data."""
    current_day = datetime.now(timezone.utc).date().isoformat()
    next_day = (datetime.now(timezone.utc).date() + timedelta(days=1)).isoformat()

    return {
        "sleep": {
            "data": [
                {
                    "day": current_day,
                    "score": 85,
                    "contributors": {
                        "efficiency": 90,
                        "restfulness": 80,
                        "timing": 75,
                    },
                }
            ]
        },
        "sleep_detail": {
            "data": [
                {
                    "day": current_day,
                    "efficiency": 92,
                    "total_sleep_duration": 28800,  # 8 hours
                    "deep_sleep_duration": 7200,    # 2 hours
                    "rem_sleep_duration": 7200,     # 2 hours
                    "light_sleep_duration": 14400,  # 4 hours
                    "awake_time": 1800,             # 0.5 hours
                    "latency": 600,                 # 10 minutes
                    "time_in_bed": 30600,           # 8.5 hours
                    "average_hrv": 45,
                    "bedtime_start": "2024-01-15T23:30:00+00:00",
                    "bedtime_end": "2024-01-16T07:30:00+00:00",
                    "average_heart_rate": 61.125,
                    "lowest_heart_rate": 55,
                }
            ]
        },
        "readiness": {
            "data": [
                {
                    "day": current_day,
                    "score": 82,
                    "temperature_deviation": -0.5,
                    "contributors": {
                        "resting_heart_rate": 85,
                        "hrv_balance": 90,
                    },
                }
            ]
        },
        "activity": {
            "data": [
                {
                    "day": current_day,
                    "score": 88,
                    "steps": 12345,
                    "active_calories": 450,
                    "total_calories": 2200,
                    "target_calories": 500,
                    "high_activity_met_minutes": 120,
                    "medium_activity_met_minutes": 180,
                    "low_activity_met_minutes": 240,
                }
            ]
        },
        "heartrate": {
            "data": [
                {"bpm": 55, "timestamp": "2024-01-01T00:00:00"},
                {"bpm": 58, "timestamp": "2024-01-01T00:05:00"},
                {"bpm": 62, "timestamp": "2024-01-01T00:10:00"},
            ]
        },
        "stress": {
            "data": [
                {
                    "day": current_day,
                    "stress_high": 3600,
                    "recovery_high": 1800,
                    "day_summary": "good",
                }
            ]
        },
        "resilience": {
            "data": [
                {
                    "day": current_day,
                    "level": "solid",
                    "contributors": {
                        "sleep_recovery": 85,
                        "daytime_recovery": 78,
                        "stress": 82,
                    },
                }
            ]
        },
        "spo2": {
            "data": [
                {
                    "spo2_percentage": {"average": 96.5},
                    "breathing_disturbance_index": 12,
                }
            ]
        },
        "vo2_max": {"data": [{"vo2_max": 45.2}]},
        "cardiovascular_age": {"data": [{"vascular_age": 28}]},
        "sleep_time": {
            "data": [
                {
                    "day": current_day,
                    "optimal_bedtime": {
                        "day_tz": 0,
                        "start_offset": 79200,
                        "end_offset": 82800,
                    },
                }
            ]
        },
        "workout": {
            "data": [
                {
                    "day": current_day,
                    "activity": "running",
                    "distance": 5000,
                    "calories": 320,
                    "intensity": "moderate",
                    "start_datetime": f"{current_day}T06:30:00+00:00",
                    "end_datetime": f"{current_day}T07:00:00+00:00",
                }
            ]
        },
        "session": {
            "data": [
                {
                    "day": current_day,
                    "type": "meditation",
                    "start_datetime": f"{current_day}T20:00:00+00:00",
                    "end_datetime": f"{current_day}T20:10:00+00:00",
                }
            ]
        },
        "tag": {
            "data": [
                {
                    "day": current_day,
                    "tags": ["coffee", "travel"],
                }
            ]
        },
        "enhanced_tag": {
            "data": [
                {
                    "day": current_day,
                    "tag_type_code": "coffee",
                    "start_time": f"{current_day}T08:00:00+00:00",
                    "end_time": f"{current_day}T08:15:00+00:00",
                    "comment": "Morning coffee",
                }
            ]
        },
        "rest_mode": {
            "data": [
                {
                    "id": "rest-mode-1",
                    "start_day": current_day,
                    "end_day": next_day,
                    "start_time": f"{current_day}T00:00:00+00:00",
                    "end_time": f"{next_day}T23:59:59+00:00",
                }
            ]
        },
    }


@pytest.fixture
def mock_oura_api_client(mock_oura_api_data: dict[str, Any]) -> AsyncMock:
    """Mock OuraApiClient for testing."""
    client = AsyncMock()
    client.async_get_data = AsyncMock(return_value=mock_oura_api_data)
    return client


@pytest.fixture
def mock_oauth2_session() -> MagicMock:
    """Mock OAuth2Session for testing."""
    session = MagicMock()
    session.async_ensure_token_valid = AsyncMock(
        return_value={
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token",
            "expires_in": 3600,
        }
    )
    return session


@pytest.fixture
def mock_hass() -> HomeAssistant:
    """Mock HomeAssistant instance for testing."""
    hass = MagicMock(spec=HomeAssistant)
    hass.data = {}
    hass.config_entries = MagicMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    return hass


@pytest.fixture
def mock_coordinator_with_data(mock_config_entry):
    """Mock OuraDataUpdateCoordinator with data for testing."""
    from custom_components.oura.coordinator import OuraDataUpdateCoordinator

    # Create a mock coordinator without full initialization
    coordinator = MagicMock(spec=OuraDataUpdateCoordinator)
    coordinator.entry = mock_config_entry
    coordinator.data = {
        "sleep_score": 85,
        "total_sleep_duration": 8.0,
        "readiness_score": 82,
        "activity_score": 88,
        "steps": 12345,
        "current_heart_rate": 62,
    }
    coordinator.last_update_success = True
    coordinator.async_refresh = AsyncMock()
    return coordinator


@pytest.fixture
def mock_empty_api_response() -> dict[str, Any]:
    """Mock empty API response for testing unavailable sensors."""
    return {
        "sleep": {"data": []},
        "sleep_detail": {"data": []},
        "readiness": {"data": []},
        "activity": {"data": []},
        "heartrate": {"data": []},
        "stress": {"data": []},
        "resilience": {"data": []},
        "spo2": {"data": []},
        "vo2_max": {"data": []},
        "cardiovascular_age": {"data": []},
        "sleep_time": {"data": []},
        "workout": {"data": []},
        "session": {"data": []},
        "tag": {"data": []},
        "enhanced_tag": {"data": []},
        "rest_mode": {"data": []},
    }
