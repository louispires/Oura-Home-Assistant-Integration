"""A rejected refresh token must escape the heart rate endpoint.

`async_get_data` already re-raises OAuth2TokenRequestReauthError out of the
gather, so the coordinator can turn it into ConfigEntryAuthFailed. But that
guard only sees exceptions the endpoint methods let out, and
`_async_get_heartrate` catches broadly inside its own paging loop -- so a
rejected token there was absorbed as an ordinary per-batch outage and the
integration went on serving stale data instead of asking for reauth.
"""
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiohttp import RequestInfo
from homeassistant.helpers.config_entry_oauth2_flow import (
    OAuth2TokenRequestReauthError,
)
from multidict import CIMultiDict, CIMultiDictProxy
from yarl import URL

from custom_components.oura.api import OuraApiClient

_TOKEN_URL = URL("https://api.ouraring.com/oauth/token")


def _reauth_error() -> OAuth2TokenRequestReauthError:
    """Build a real one -- it subclasses ClientResponseError and needs the lot.

    Raising the bare class instead would blow up as a TypeError, which the
    broad `except` absorbs, and the test would pass for the wrong reason.
    """
    request_info = RequestInfo(
        _TOKEN_URL, "POST", CIMultiDictProxy(CIMultiDict()), _TOKEN_URL
    )
    return OAuth2TokenRequestReauthError(
        domain="oura", request_info=request_info, history=(), status=400
    )


def _client() -> OuraApiClient:
    hass = MagicMock()
    hass.config.time_zone = "UTC"
    return OuraApiClient(hass, MagicMock(), MagicMock())


@pytest.mark.anyio
async def test_reauth_escapes_the_batched_path():
    """Ranges over 30 days go through the batching loop."""
    client = _client()
    client._async_get_all_pages = AsyncMock(side_effect=_reauth_error())

    with pytest.raises(OAuth2TokenRequestReauthError):
        await client._async_get_heartrate(date(2026, 1, 1), date(2026, 3, 31))


@pytest.mark.anyio
async def test_reauth_escapes_the_short_path():
    """Ranges of 30 days or less skip the loop entirely."""
    client = _client()
    client._async_get_all_pages = AsyncMock(side_effect=_reauth_error())

    with pytest.raises(OAuth2TokenRequestReauthError):
        await client._async_get_heartrate(date(2026, 3, 1), date(2026, 3, 15))


@pytest.mark.anyio
async def test_an_ordinary_failure_is_still_absorbed():
    """The point is to single out reauth, not to stop tolerating outages."""
    client = _client()
    client._async_get_all_pages = AsyncMock(side_effect=TimeoutError("upstream down"))

    assert await client._async_get_heartrate(date(2026, 3, 1), date(2026, 3, 15)) == {
        "data": []
    }


@pytest.mark.anyio
async def test_an_ordinary_failure_is_still_absorbed_when_batching():
    """A dead batch must not abort the batches that follow it."""
    client = _client()
    client._async_get_all_pages = AsyncMock(
        side_effect=[TimeoutError("upstream down"), [{"bpm": 60}], [{"bpm": 61}]]
    )

    result = await client._async_get_heartrate(date(2026, 1, 1), date(2026, 3, 31))

    assert result == {"data": [{"bpm": 60}, {"bpm": 61}]}


@pytest.mark.anyio
async def test_reauth_reaches_async_get_data_through_the_gather():
    """End to end: the outer guard can only fire if the inner one lets go."""
    client = _client()
    for name in (
        "_async_get_sleep", "_async_get_readiness", "_async_get_activity",
        "_async_get_sleep_detail", "_async_get_stress", "_async_get_resilience",
        "_async_get_spo2", "_async_get_vo2_max", "_async_get_cardiovascular_age",
        "_async_get_sleep_time", "_async_get_workout", "_async_get_session",
        "_async_get_tag", "_async_get_enhanced_tag", "_async_get_rest_mode",
        "_async_get_ring_battery_level", "_async_get_ring_configuration",
    ):
        setattr(client, name, AsyncMock(return_value={"data": []}))
    client._async_get_all_pages = AsyncMock(side_effect=_reauth_error())

    with pytest.raises(OAuth2TokenRequestReauthError):
        await client.async_get_data(days_back=90)
