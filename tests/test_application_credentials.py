"""Tests for the legacy token endpoint fallback in application_credentials.py.

moi.ouraring.com/oauth/v2/ext/oauth-token is the primary token endpoint (works for
both legacy- and new-portal apps); api.ouraring.com/oauth/token is kept only as a
fallback for the shrinking set of legacy-portal apps still rejected by moi.
Trying moi first avoids the issue-#75 failure mode: a rejected authorization_code
exchange burns the single-use code, so an endpoint tried second never gets a
chance to redeem it even if it would have accepted it.
OuraOAuth2Implementation transparently retries against the legacy endpoint on
first rejection and updates token_url for all subsequent requests.
"""
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientResponseError, RequestInfo
from multidict import CIMultiDict, CIMultiDictProxy
from yarl import URL

from homeassistant.components.application_credentials import (
    AuthorizationServer,
    ClientCredential,
)
from homeassistant.helpers.config_entry_oauth2_flow import OAuth2TokenRequestReauthError

from custom_components.oura.application_credentials import OuraOAuth2Implementation
from custom_components.oura.const import OAUTH2_AUTHORIZE, OAUTH2_TOKEN, OAUTH2_TOKEN_LEGACY


def _reauth_error(token_url: str = OAUTH2_TOKEN, status: int = 400) -> OAuth2TokenRequestReauthError:
    url = URL(token_url)
    request_info = RequestInfo(url, "POST", CIMultiDictProxy(CIMultiDict()), url)
    return OAuth2TokenRequestReauthError(
        domain="oura", request_info=request_info, history=(), status=status
    )


def _client_response_error(token_url: str = OAUTH2_TOKEN, status: int = 401) -> ClientResponseError:
    url = URL(token_url)
    request_info = RequestInfo(url, "POST", CIMultiDictProxy(CIMultiDict()), url)
    return ClientResponseError(request_info=request_info, history=(), status=status)


def _make_impl() -> OuraOAuth2Implementation:
    hass = MagicMock()
    credential = ClientCredential(client_id="test_id", client_secret="test_secret")
    auth_server = AuthorizationServer(
        authorize_url=OAUTH2_AUTHORIZE,
        token_url=OAUTH2_TOKEN,
    )
    return OuraOAuth2Implementation(hass, "oura.test_id", credential, auth_server)


@pytest.mark.anyio
async def test_primary_success_no_fallback():
    """Happy path: moi endpoint works → token_url stays on moi."""
    impl = _make_impl()
    expected = {"access_token": "tok", "expires_in": 3600}

    with patch.object(
        impl.__class__.__bases__[0],
        "_token_request",
        new=AsyncMock(return_value=expected),
    ) as mock_super:
        result = await impl._token_request({"grant_type": "refresh_token"})

    assert result == expected
    assert impl.token_url == OAUTH2_TOKEN
    mock_super.assert_called_once()


@pytest.mark.anyio
async def test_primary_400_retries_legacy_and_succeeds():
    """Legacy-portal app: moi 400 on refresh → retry against legacy → success, url updated."""
    impl = _make_impl()
    expected = {"access_token": "new_tok", "expires_in": 3600}
    call_count = 0

    async def _side_effect(self_inner, data):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise _reauth_error(OAUTH2_TOKEN)
        return expected

    with patch.object(impl.__class__.__bases__[0], "_token_request", new=_side_effect):
        result = await impl._token_request({"grant_type": "refresh_token"})

    assert result == expected
    assert impl.token_url == OAUTH2_TOKEN_LEGACY
    assert call_count == 2


@pytest.mark.anyio
async def test_legacy_400_propagates_reauth_error():
    """Both endpoints 400 → OAuth2TokenRequestReauthError propagates to coordinator."""
    impl = _make_impl()
    impl.token_url = OAUTH2_TOKEN_LEGACY  # already on the fallback

    with patch.object(
        impl.__class__.__bases__[0],
        "_token_request",
        new=AsyncMock(side_effect=_reauth_error(OAUTH2_TOKEN_LEGACY)),
    ):
        with pytest.raises(OAuth2TokenRequestReauthError):
            await impl._token_request({"grant_type": "refresh_token"})


@pytest.mark.anyio
async def test_primary_401_retries_legacy_and_succeeds():
    """Legacy-portal app: initial code exchange 401 on moi → retry legacy → success.

    Regression guard for #75: the authorization_code grant must hit the endpoint
    that actually owns the client on the FIRST attempt whenever possible, since a
    rejected code exchange burns the single-use code.
    """
    impl = _make_impl()
    expected = {"access_token": "new_tok", "expires_in": 3600}
    call_count = 0

    async def _side_effect(self_inner, data):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise _client_response_error(OAUTH2_TOKEN, status=401)
        return expected

    with patch.object(impl.__class__.__bases__[0], "_token_request", new=_side_effect):
        result = await impl._token_request({"grant_type": "authorization_code"})

    assert result == expected
    assert impl.token_url == OAUTH2_TOKEN_LEGACY
    assert call_count == 2


@pytest.mark.anyio
async def test_non_fallback_status_propagates_without_retry():
    """A status outside (400, 401), e.g. 500, is not retried against the legacy endpoint."""
    impl = _make_impl()

    with patch.object(
        impl.__class__.__bases__[0],
        "_token_request",
        new=AsyncMock(side_effect=_client_response_error(OAUTH2_TOKEN, status=500)),
    ):
        with pytest.raises(ClientResponseError):
            await impl._token_request({"grant_type": "refresh_token"})

    assert impl.token_url == OAUTH2_TOKEN


@pytest.mark.anyio
async def test_already_on_legacy_succeeds_in_one_call():
    """Once token_url is on the legacy endpoint, requests go through with a single call."""
    impl = _make_impl()
    impl.token_url = OAUTH2_TOKEN_LEGACY  # simulates state after a previous switch
    expected = {"access_token": "tok2", "expires_in": 3600}
    call_count = 0

    async def _side_effect(self_inner, data):
        nonlocal call_count
        call_count += 1
        return expected

    with patch.object(impl.__class__.__bases__[0], "_token_request", new=_side_effect):
        result = await impl._token_request({"grant_type": "refresh_token"})

    assert result == expected
    assert call_count == 1  # no extra retry attempt
    assert impl.token_url == OAUTH2_TOKEN_LEGACY


@pytest.mark.anyio
async def test_failure_logs_no_secret_material(caplog):
    """Error logging must include host/grant/status but never tokens or secrets."""
    impl = _make_impl()

    with patch.object(
        impl.__class__.__bases__[0],
        "_token_request",
        new=AsyncMock(side_effect=_client_response_error(OAUTH2_TOKEN, status=500)),
    ):
        with caplog.at_level(logging.ERROR):
            with pytest.raises(ClientResponseError):
                await impl._token_request(
                    {
                        "grant_type": "refresh_token",
                        "refresh_token": "super-secret-refresh-token",
                        "client_secret": "super-secret-client-secret",
                    }
                )

    log_text = "\n".join(caplog.messages)
    assert "super-secret-refresh-token" not in log_text
    assert "super-secret-client-secret" not in log_text
    assert OAUTH2_TOKEN in log_text
    assert "refresh_token" in log_text
