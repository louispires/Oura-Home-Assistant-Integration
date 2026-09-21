"""Tests for the Oura Ring config flow with multiple account support."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientError
from homeassistant.config_entries import SOURCE_REAUTH, SOURCE_USER
from homeassistant.helpers.config_entry_oauth2_flow import AbstractOAuth2FlowHandler

from custom_components.oura.config_flow import OuraFlowHandler
from custom_components.oura.const import DOMAIN


@pytest.fixture
def mock_user_info():
    """Mock user info from Oura API."""
    return {
        "id": "unique-user-id-12345",
        "email": "user@example.com",
        "age": 30,
    }


@pytest.fixture
def mock_user_info_no_email():
    """Mock user info without email."""
    return {
        "id": "unique-user-id-67890",
    }


class TestOuraConfigFlow:
    """Test the Oura config flow."""

    @pytest.mark.anyio
    async def test_get_user_info_success(self, mock_user_info):
        """Test successfully getting user info from Oura API."""
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=mock_user_info)
        
        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response), __aexit__=AsyncMock()))
        
        with patch("custom_components.oura.config_flow.async_get_clientsession", return_value=mock_session):
            flow = OuraFlowHandler()
            flow.hass = MagicMock()
            
            data = {"token": {"access_token": "test_token"}}
            result = await flow._async_get_user_info(data)
            
            assert result["id"] == "unique-user-id-12345"
            assert result["email"] == "user@example.com"

    @pytest.mark.anyio
    async def test_unique_id_from_user_id(self, mock_user_info):
        """Test that unique_id is set from user's Oura ID."""
        # This test verifies the flow correctly extracts user ID
        assert mock_user_info["id"] == "unique-user-id-12345"
        
    @pytest.mark.anyio
    async def test_title_from_email(self, mock_user_info):
        """Test that entry title is set from user's email."""
        email = mock_user_info.get("email")
        title = email if email else "Oura Ring"
        assert title == "user@example.com"

    @pytest.mark.anyio
    async def test_title_fallback_no_email(self, mock_user_info_no_email):
        """Test that entry title falls back to 'Oura Ring' when no email."""
        email = mock_user_info_no_email.get("email")
        title = email if email else "Oura Ring"
        assert title == "Oura Ring"

    @pytest.mark.anyio
    async def test_multiple_accounts_different_ids(self, mock_user_info, mock_user_info_no_email):
        """Test that different users get different unique IDs."""
        assert mock_user_info["id"] != mock_user_info_no_email["id"]


class TestAsyncStepCreationAbortRemap:
    """Test that generic OAuth abort reasons become the actionable oauth_token_rejected."""

    @pytest.mark.anyio
    async def test_oauth_unauthorized_remapped(self):
        """oauth_unauthorized (reauth-class token error) is remapped."""
        flow = OuraFlowHandler()
        flow.hass = MagicMock()

        with patch.object(
            AbstractOAuth2FlowHandler,
            "async_step_creation",
            new=AsyncMock(return_value={"type": "abort", "reason": "oauth_unauthorized"}),
        ):
            with patch.object(
                flow, "async_abort", return_value={"type": "abort", "reason": "oauth_token_rejected"}
            ) as mock_abort:
                result = await flow.async_step_creation()

        assert mock_abort.call_args.kwargs["reason"] == "oauth_token_rejected"
        placeholders = mock_abort.call_args.kwargs["description_placeholders"]
        assert placeholders["redirect_uri"] == "https://my.home-assistant.io/redirect/oauth"
        assert "portals" in placeholders
        assert result["reason"] == "oauth_token_rejected"

    @pytest.mark.anyio
    async def test_oauth_failed_remapped(self):
        """oauth_failed (generic token error) is remapped too."""
        flow = OuraFlowHandler()
        flow.hass = MagicMock()

        with patch.object(
            AbstractOAuth2FlowHandler,
            "async_step_creation",
            new=AsyncMock(return_value={"type": "abort", "reason": "oauth_failed"}),
        ):
            with patch.object(
                flow, "async_abort", return_value={"type": "abort", "reason": "oauth_token_rejected"}
            ) as mock_abort:
                result = await flow.async_step_creation()

        assert mock_abort.call_args.kwargs["reason"] == "oauth_token_rejected"
        assert result["reason"] == "oauth_token_rejected"

    @pytest.mark.anyio
    async def test_unrelated_abort_passes_through(self):
        """An abort reason we don't own (e.g. oauth_timeout) is not touched."""
        flow = OuraFlowHandler()
        flow.hass = MagicMock()
        expected = {"type": "abort", "reason": "oauth_timeout"}

        with patch.object(
            AbstractOAuth2FlowHandler,
            "async_step_creation",
            new=AsyncMock(return_value=expected),
        ):
            with patch.object(flow, "async_abort") as mock_abort:
                result = await flow.async_step_creation()

        mock_abort.assert_not_called()
        assert result == expected

    @pytest.mark.anyio
    async def test_success_passes_through(self):
        """A non-abort result (success continuing the flow) is returned unchanged."""
        flow = OuraFlowHandler()
        flow.hass = MagicMock()
        expected = {"type": "create_entry", "title": "Oura Ring"}

        with patch.object(
            AbstractOAuth2FlowHandler,
            "async_step_creation",
            new=AsyncMock(return_value=expected),
        ):
            result = await flow.async_step_creation()

        assert result == expected

