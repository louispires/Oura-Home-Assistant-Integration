"""Integration tests for Oura Ring component setup."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.oura.const import DOMAIN


def test_config_entry_fixture(mock_config_entry: ConfigEntry):
    """Test that config entry fixture is properly configured."""
    assert mock_config_entry.domain == DOMAIN
    assert mock_config_entry.title == "Oura Ring"
    assert "token" in mock_config_entry.data
    assert mock_config_entry.data["token"]["access_token"] == "mock_access_token"
    assert mock_config_entry.options["update_interval"] == 5
    assert mock_config_entry.options["historical_months"] == 3
    assert mock_config_entry.options["historical_data_imported"] is True
    assert mock_config_entry.unique_id == "mock_unique_id"


def test_mock_hass_fixture(mock_hass: HomeAssistant):
    """Test that hass fixture is properly configured."""
    assert mock_hass.data == {}
    assert hasattr(mock_hass.config_entries, "async_forward_entry_setups")
    assert hasattr(mock_hass.config_entries, "async_unload_platforms")


def test_mock_oura_api_data_fixture(mock_oura_api_data: dict):
    """Test that API data fixture contains expected data."""
    assert "sleep" in mock_oura_api_data
    assert "sleep_detail" in mock_oura_api_data
    assert "readiness" in mock_oura_api_data
    assert "activity" in mock_oura_api_data
    assert "heartrate" in mock_oura_api_data
    assert "workout" in mock_oura_api_data
    assert "session" in mock_oura_api_data
    assert "tag" in mock_oura_api_data
    assert "enhanced_tag" in mock_oura_api_data
    assert "rest_mode" in mock_oura_api_data
    assert len(mock_oura_api_data["sleep"]["data"]) > 0
    assert mock_oura_api_data["sleep"]["data"][0]["score"] == 85
    assert mock_oura_api_data["sleep_detail"]["data"][0]["efficiency"] == 92


def test_mock_oura_api_client_fixture(mock_oura_api_client: AsyncMock):
    """Test that API client fixture is properly configured."""
    assert hasattr(mock_oura_api_client, "async_get_data")
    assert isinstance(mock_oura_api_client.async_get_data, AsyncMock)


def test_mock_oauth2_session_fixture(mock_oauth2_session: MagicMock):
    """Test that OAuth2 session fixture is properly configured."""
    assert hasattr(mock_oauth2_session, "async_ensure_token_valid")
    assert isinstance(mock_oauth2_session.async_ensure_token_valid, AsyncMock)


def test_mock_coordinator_fixture(mock_coordinator_with_data):
    """Test that coordinator fixture is properly configured."""
    assert mock_coordinator_with_data.data is not None
    assert "sleep_score" in mock_coordinator_with_data.data
    assert mock_coordinator_with_data.data["sleep_score"] == 85
    assert mock_coordinator_with_data.last_update_success is True


def test_mock_empty_api_response_fixture(mock_empty_api_response: dict):
    """Test that empty API response fixture is properly configured."""
    assert "sleep" in mock_empty_api_response
    assert len(mock_empty_api_response["sleep"]["data"]) == 0
    assert len(mock_empty_api_response["activity"]["data"]) == 0

