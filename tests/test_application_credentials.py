"""Tests for the new-portal token endpoint fallback in application_credentials.py.

Apps registered on developer.ouraring.com are rejected by the legacy
api.ouraring.com/oauth/token endpoint: refreshes fail with 400, and the
initial authorization_code exchange fails with 401.
OuraOAuth2Implementation transparently retries against the new-portal endpoint
on first rejection and updates token_url for all subsequent requests.
"""
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
from custom_components.oura.const import OAUTH2_AUTHORIZE, OAUTH2_TOKEN, OAUTH2_TOKEN_FALLBACK


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
async def test_legacy_success_no_fallback():
    """Happy path: legacy endpoint works → token_url stays legacy."""
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
async def test_legacy_400_retries_fallback_and_succeeds():
    """New-portal app: legacy 400 → retry against fallback → success, url updated."""
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
    assert impl.token_url == OAUTH2_TOKEN_FALLBACK
    assert call_count == 2


@pytest.mark.anyio
async def test_fallback_400_propagates_reauth_error():
    """Both endpoints 400 → OAuth2TokenRequestReauthError propagates to coordinator."""
    impl = _make_impl()
    impl.token_url = OAUTH2_TOKEN_FALLBACK  # already on fallback

    with patch.object(
        impl.__class__.__bases__[0],
        "_token_request",
        new=AsyncMock(side_effect=_reauth_error(OAUTH2_TOKEN_FALLBACK)),
    ):
        with pytest.raises(OAuth2TokenRequestReauthError):
            await impl._token_request({"grant_type": "refresh_token"})


@pytest.mark.anyio
async def test_legacy_401_retries_fallback_and_succeeds():
    """New-portal app: initial code exchange 401 → retry against fallback → success."""
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
    assert impl.token_url == OAUTH2_TOKEN_FALLBACK
    assert call_count == 2


@pytest.mark.anyio
async def test_non_fallback_status_propagates_without_retry():
    """A status outside (400, 401), e.g. 500, is not retried against the fallback."""
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
async def test_already_on_fallback_succeeds_in_one_call():
    """Once token_url is on the fallback endpoint, requests go through with a single call."""
    impl = _make_impl()
    impl.token_url = OAUTH2_TOKEN_FALLBACK  # simulates state after a previous switch
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
    assert impl.token_url == OAUTH2_TOKEN_FALLBACK
