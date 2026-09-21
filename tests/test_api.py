"""Tests for Oura API client date window handling."""
import logging
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientResponseError, RequestInfo
from multidict import CIMultiDict, CIMultiDictProxy
from yarl import URL

from custom_components.oura.api import OuraApiClient


class _FrozenDateTime(datetime):
    """Frozen datetime for deterministic timezone-aware date calculations."""

    @classmethod
    def now(cls, tz=None):
        """Return a fixed local time and require timezone-aware calls."""
        assert tz is not None
        return cls(2026, 3, 23, 1, 30, tzinfo=tz)


@pytest.mark.anyio
async def test_async_get_data_uses_local_date_and_exclusive_end_date():
    """Test timezone-aware date range and +1 day exclusive end date handling."""
    hass = MagicMock()
    hass.config.time_zone = "America/Denver"
    session = MagicMock()
    entry = MagicMock()
    client = OuraApiClient(hass, session, entry)

    endpoint_methods = [
        "_async_get_sleep",
        "_async_get_readiness",
        "_async_get_activity",
        "_async_get_heartrate",
        "_async_get_sleep_detail",
        "_async_get_stress",
        "_async_get_resilience",
        "_async_get_spo2",
        "_async_get_vo2_max",
        "_async_get_cardiovascular_age",
        "_async_get_sleep_time",
        "_async_get_workout",
        "_async_get_session",
        "_async_get_tag",
        "_async_get_enhanced_tag",
        "_async_get_rest_mode",
        "_async_get_ring_battery_level",
        "_async_get_ring_configuration",
    ]
    for method_name in endpoint_methods:
        setattr(client, method_name, AsyncMock(return_value={"data": []}))

    with patch("custom_components.oura.api.datetime", _FrozenDateTime):
        await client.async_get_data(days_back=1)

    expected_start = date(2026, 3, 22)
    expected_end = date(2026, 3, 24)
    for method_name in endpoint_methods:
        mocked_method = getattr(client, method_name)
        assert mocked_method.await_count == 1
        assert mocked_method.await_args.args == (expected_start, expected_end)


@pytest.mark.anyio
async def test_async_get_data_counts_absorbed_heartrate_outage(caplog):
    """Absorbed heart-rate outages should still count as endpoint failures."""
    hass = MagicMock()
    hass.config.time_zone = "UTC"
    client = OuraApiClient(hass, MagicMock(), MagicMock())

    endpoint_methods = [
        "_async_get_sleep",
        "_async_get_readiness",
        "_async_get_activity",
        "_async_get_sleep_detail",
        "_async_get_stress",
        "_async_get_resilience",
        "_async_get_spo2",
        "_async_get_vo2_max",
        "_async_get_cardiovascular_age",
        "_async_get_sleep_time",
        "_async_get_workout",
        "_async_get_session",
        "_async_get_tag",
        "_async_get_enhanced_tag",
        "_async_get_rest_mode",
        "_async_get_ring_battery_level",
        "_async_get_ring_configuration",
    ]

    failing_methods = endpoint_methods[:8]
    for method_name in endpoint_methods:
        if method_name in failing_methods:
            setattr(client, method_name, AsyncMock(side_effect=TimeoutError("network outage")))
        else:
            setattr(client, method_name, AsyncMock(return_value={"data": []}))

    client._async_get_all_pages = AsyncMock(side_effect=TimeoutError("heart rate outage"))

    with caplog.at_level(logging.WARNING):
        data = await client.async_get_data(days_back=1)

    assert data["heartrate"] == {"data": []}
    assert any(
        "Network connectivity issue: 9/18 API endpoints failed" in record.getMessage()
        for record in caplog.records
    )


def _client_response_error(status: int, headers: dict | None = None) -> ClientResponseError:
    url = URL("https://api.ouraring.com/v2/usercollection/daily_activity")
    request_info = RequestInfo(url, "GET", CIMultiDictProxy(CIMultiDict()), url)
    return ClientResponseError(
        request_info=request_info, history=(), status=status, headers=headers or {}
    )


def _make_client_with_mock_http() -> OuraApiClient:
    """Build a client with a mocked OAuth2Session and cached aiohttp session."""
    hass = MagicMock()
    session = MagicMock()
    session.async_ensure_token_valid = AsyncMock()
    session.valid_token = True
    session.token = {"access_token": "tok"}
    client = OuraApiClient(hass, session, MagicMock())
    client._client_session = MagicMock()  # bypasses async_get_clientsession(hass)
    return client


def _mock_get_sequence(client: OuraApiClient, responses: list) -> None:
    """Queue a sequence of (raise_for_status side effect, json payload) responses."""

    def _get(*args, **kwargs):
        raise_effect, json_payload = responses.pop(0)
        response = MagicMock()
        response.raise_for_status = MagicMock(side_effect=raise_effect)
        response.json = AsyncMock(return_value=json_payload)
        cm = AsyncMock()
        cm.__aenter__ = AsyncMock(return_value=response)
        cm.__aexit__ = AsyncMock(return_value=False)
        return cm

    client.client_session.get = MagicMock(side_effect=_get)


@pytest.mark.anyio
async def test_async_get_retries_once_on_429_then_succeeds():
    """A 429 with Retry-After is retried once and the retry succeeds."""
    client = _make_client_with_mock_http()
    _mock_get_sequence(
        client,
        [
            (_client_response_error(429, headers={"Retry-After": "0"}), None),
            (None, {"data": [{"ok": True}]}),
        ],
    )

    result = await client._async_get("https://api.ouraring.com/v2/usercollection/daily_activity")

    assert result == {"data": [{"ok": True}]}
    assert client.client_session.get.call_count == 2


@pytest.mark.anyio
async def test_async_get_gives_up_after_second_429():
    """A second consecutive 429 propagates instead of retrying forever."""
    client = _make_client_with_mock_http()
    _mock_get_sequence(
        client,
        [
            (_client_response_error(429, headers={"Retry-After": "0"}), None),
            (_client_response_error(429, headers={"Retry-After": "0"}), None),
        ],
    )

    with pytest.raises(ClientResponseError) as exc_info:
        await client._async_get("https://api.ouraring.com/v2/usercollection/daily_activity")

    assert exc_info.value.status == 429
    assert client.client_session.get.call_count == 2


@pytest.mark.anyio
async def test_async_get_429_without_retry_after_uses_capped_default(monkeypatch):
    """Missing Retry-After falls back to the capped default wait, not an unbounded one."""
    client = _make_client_with_mock_http()
    _mock_get_sequence(
        client,
        [
            (_client_response_error(429), None),
            (None, {"data": []}),
        ],
    )
    sleep_calls = []

    async def _fake_sleep(seconds):
        sleep_calls.append(seconds)

    monkeypatch.setattr("custom_components.oura.api.asyncio.sleep", _fake_sleep)

    await client._async_get("https://api.ouraring.com/v2/usercollection/daily_activity")

    assert sleep_calls == [30]


@pytest.mark.anyio
async def test_resilience_endpoint_returns_empty_on_403():
    """403 (subscription expired) on an optional endpoint yields empty data, not an error."""
    client = _make_client_with_mock_http()
    _mock_get_sequence(client, [(_client_response_error(403), None)])

    result = await client._async_get_resilience(date(2026, 1, 1), date(2026, 1, 2))

    assert result == {"data": []}


@pytest.mark.anyio
async def test_resilience_endpoint_propagates_other_statuses():
    """A status outside (401, 403) on an optional endpoint still propagates."""
    client = _make_client_with_mock_http()
    _mock_get_sequence(client, [(_client_response_error(500), None)])

    with pytest.raises(ClientResponseError):
        await client._async_get_resilience(date(2026, 1, 1), date(2026, 1, 2))


@pytest.mark.anyio
async def test_heartrate_requests_only_consumed_fields():
    """Heart rate only needs timestamp+bpm; requesting them shrinks the 5-minute poll payload."""
    client = _make_client_with_mock_http()
    client._async_get_all_pages = AsyncMock(return_value=[])

    await client._async_get_heartrate(date(2026, 1, 1), date(2026, 1, 2))

    params = client._async_get_all_pages.await_args.args[1]
    assert params["fields"] == "timestamp,bpm"


@pytest.mark.anyio
async def test_heartrate_batched_requests_only_consumed_fields():
    """The >30-day batching path also requests the trimmed field set for every batch."""
    client = _make_client_with_mock_http()
    client._async_get_all_pages = AsyncMock(return_value=[])

    await client._async_get_heartrate(date(2026, 1, 1), date(2026, 3, 1))

    assert client._async_get_all_pages.await_count > 1
    for call in client._async_get_all_pages.await_args_list:
        assert call.args[1]["fields"] == "timestamp,bpm"
