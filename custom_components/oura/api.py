"""API client for Oura Ring."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import logging
from typing import Any
from zoneinfo import ZoneInfo

from aiohttp import ClientSession, ClientResponseError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.config_entry_oauth2_flow import OAuth2Session
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import API_BASE_URL

_LOGGER = logging.getLogger(__name__)

API_ENDPOINTS: dict[str, str] = {
    "sleep": "_async_get_sleep",
    "readiness": "_async_get_readiness",
    "activity": "_async_get_activity",
    "heartrate": "_async_get_heartrate",
    "sleep_detail": "_async_get_sleep_detail",
    "stress": "_async_get_stress",
    "resilience": "_async_get_resilience",
    "spo2": "_async_get_spo2",
    "vo2_max": "_async_get_vo2_max",
    "cardiovascular_age": "_async_get_cardiovascular_age",
    "sleep_time": "_async_get_sleep_time",
    "workout": "_async_get_workout",
    "session": "_async_get_session",
    "tag": "_async_get_tag",
    "enhanced_tag": "_async_get_enhanced_tag",
    "rest_mode": "_async_get_rest_mode",
}


class OuraApiClient:
    """Oura API client."""

    def __init__(self, hass: HomeAssistant, session: OAuth2Session, entry: ConfigEntry) -> None:
        """Initialize the API client."""
        self.hass = hass
        self.session = session
        self.entry = entry
        self._client_session: ClientSession | None = None

    @property
    def client_session(self) -> ClientSession:
        """Get aiohttp client session."""
        if self._client_session is None:
            self._client_session = async_get_clientsession(self.hass)
        return self._client_session

    async def async_get_data(self, days_back: int = 1) -> dict[str, Any]:
        """Get data from Oura API.
        
        Args:
            days_back: Number of days of historical data to fetch (default: 1)
        """
        local_tz = ZoneInfo(self.hass.config.time_zone)
        today = datetime.now(tz=local_tz).date()
        end_date = today + timedelta(days=1)  # Oura API end_date is exclusive
        start_date = today - timedelta(days=days_back)

        results = await asyncio.gather(
            *(getattr(self, method_name)(start_date, end_date) for method_name in API_ENDPOINTS.values()),
            return_exceptions=True,
        )

        data: dict[str, Any] = {}
        failed_endpoints = 0
        total_endpoints = len(API_ENDPOINTS)

        for (key, _), result in zip(API_ENDPOINTS.items(), results):
            if isinstance(result, Exception):
                failed_endpoints += 1
                _LOGGER.debug("Error fetching %s data: %s", key, result)
                data[key] = {}
            else:
                data[key] = result

        if failed_endpoints >= total_endpoints * 0.5:
            _LOGGER.warning(
                "Network connectivity issue: %d/%d API endpoints failed. "
                "Will retry on next update cycle.",
                failed_endpoints, total_endpoints
            )

        return data

    async def _async_get_sleep(self, start_date: datetime.date, end_date: datetime.date) -> dict[str, Any]:
        """Get sleep data."""
        url = f"{API_BASE_URL}/daily_sleep"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        return await self._async_get(url, params)

    async def _async_get_readiness(self, start_date: datetime.date, end_date: datetime.date) -> dict[str, Any]:
        """Get readiness data."""
        url = f"{API_BASE_URL}/daily_readiness"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        return await self._async_get(url, params)

    async def _async_get_activity(self, start_date: datetime.date, end_date: datetime.date) -> dict[str, Any]:
        """Get activity data."""
        url = f"{API_BASE_URL}/daily_activity"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        return await self._async_get(url, params)

    async def _async_get_heartrate(self, start_date: datetime.date, end_date: datetime.date) -> dict[str, Any]:
        """Get heart rate data.
        
        Note: The heartrate endpoint has a maximum range of 30 days.
        For historical data requests, we'll batch the requests.
        """
        url = f"{API_BASE_URL}/heartrate"
        
        # Calculate the number of days in the range
        days_range = (end_date - start_date).days
        
        # If range is > 30 days, batch the requests
        if days_range > 30:
            all_data = []
            current_start = start_date
            
            while current_start < end_date:
                current_end = min(current_start + timedelta(days=30), end_date)
                params = {
                    "start_datetime": f"{current_start.isoformat()}T00:00:00",
                    "end_datetime": f"{current_end.isoformat()}T23:59:59",
                }
                
                try:
                    batch_data = await self._async_get(url, params)
                    if batch_data and "data" in batch_data:
                        all_data.extend(batch_data["data"])
                except Exception as err:
                    _LOGGER.warning(
                        "Failed to fetch heart rate data for %s to %s: %s",
                        current_start, current_end, err
                    )
                
                current_start = current_end + timedelta(days=1)
            
            return {"data": all_data}
        else:
            # Range is 30 days or less, single request
            params = {
                "start_datetime": f"{start_date.isoformat()}T00:00:00",
                "end_datetime": f"{end_date.isoformat()}T23:59:59",
            }
            
            try:
                return await self._async_get(url, params)
            except Exception as err:
                _LOGGER.debug("Heart rate endpoint failed: %s", err)
                # Return empty data instead of failing completely
                return {"data": []}

    async def _async_get_sleep_detail(self, start_date: datetime.date, end_date: datetime.date) -> dict[str, Any]:
        """Get detailed sleep data including HRV."""
        url = f"{API_BASE_URL}/sleep"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        return await self._async_get(url, params)

    async def _async_get_stress(self, start_date: datetime.date, end_date: datetime.date) -> dict[str, Any]:
        """Get daily stress data."""
        url = f"{API_BASE_URL}/daily_stress"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        return await self._async_get(url, params)

    async def _async_get_resilience(self, start_date: datetime.date, end_date: datetime.date) -> dict[str, Any]:
        """Get daily resilience data.
        
        Note: This endpoint may return 401 if the user hasn't authorized the required scope
        or if their ring/subscription doesn't support this feature.
        """
        url = f"{API_BASE_URL}/daily_resilience"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        try:
            return await self._async_get(url, params)
        except ClientResponseError as err:
            if err.status == 401:  # Feature not available
                return {"data": []}
            raise

    async def _async_get_spo2(self, start_date: datetime.date, end_date: datetime.date) -> dict[str, Any]:
        """Get daily SpO2 (blood oxygen) data. Available for Gen3 and Oura Ring 4.
        
        Note: This endpoint may return 401 if the user hasn't authorized the spo2Daily scope
        or if their ring doesn't support SpO2 (only Gen3 and Ring 4).
        """
        url = f"{API_BASE_URL}/daily_spo2"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        try:
            return await self._async_get(url, params)
        except ClientResponseError as err:
            if err.status == 401:  # Feature not available (Gen3/Ring4 only)
                return {"data": []}
            raise

    async def _async_get_vo2_max(self, start_date: datetime.date, end_date: datetime.date) -> dict[str, Any]:
        """Get VO2 Max fitness data.
        
        Note: This endpoint may return 401 if the user hasn't authorized the required scope
        or if their ring/subscription doesn't support this feature.
        """
        url = f"{API_BASE_URL}/vO2_max"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        try:
            return await self._async_get(url, params)
        except ClientResponseError as err:
            if err.status == 401:  # Feature not available
                return {"data": []}
            raise

    async def _async_get_cardiovascular_age(self, start_date: datetime.date, end_date: datetime.date) -> dict[str, Any]:
        """Get daily cardiovascular age data.
        
        Note: This endpoint may return 401 if the user hasn't authorized the required scope
        or if their ring/subscription doesn't support this feature.
        """
        url = f"{API_BASE_URL}/daily_cardiovascular_age"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        try:
            return await self._async_get(url, params)
        except ClientResponseError as err:
            if err.status == 401:  # Feature not available
                return {"data": []}
            raise

    async def _async_get_sleep_time(self, start_date: datetime.date, end_date: datetime.date) -> dict[str, Any]:
        """Get optimal sleep time recommendations."""
        url = f"{API_BASE_URL}/sleep_time"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        return await self._async_get(url, params)

    async def _async_get_workout(self, start_date: datetime.date, end_date: datetime.date) -> dict[str, Any]:
        """Get workout data."""
        url = f"{API_BASE_URL}/workout"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        try:
            return await self._async_get(url, params)
        except ClientResponseError as err:
            if err.status == 401:
                return {"data": []}
            raise

    async def _async_get_session(self, start_date: datetime.date, end_date: datetime.date) -> dict[str, Any]:
        """Get session data."""
        url = f"{API_BASE_URL}/session"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        try:
            return await self._async_get(url, params)
        except ClientResponseError as err:
            if err.status == 401:
                return {"data": []}
            raise

    async def _async_get_tag(self, start_date: datetime.date, end_date: datetime.date) -> dict[str, Any]:
        """Get tag data."""
        url = f"{API_BASE_URL}/tag"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        try:
            return await self._async_get(url, params)
        except ClientResponseError as err:
            if err.status == 401:
                return {"data": []}
            raise

    async def _async_get_enhanced_tag(self, start_date: datetime.date, end_date: datetime.date) -> dict[str, Any]:
        """Get enhanced tag data."""
        url = f"{API_BASE_URL}/enhanced_tag"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        try:
            return await self._async_get(url, params)
        except ClientResponseError as err:
            if err.status == 401:
                return {"data": []}
            raise

    async def _async_get_rest_mode(self, start_date: datetime.date, end_date: datetime.date) -> dict[str, Any]:
        """Get rest mode period data."""
        url = f"{API_BASE_URL}/rest_mode_period"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        try:
            return await self._async_get(url, params)
        except ClientResponseError as err:
            if err.status == 401:
                return {"data": []}
            raise

    async def _async_get(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make GET request to Oura API."""
        try:
            # Ensure token is valid and get the token data
            await self.session.async_ensure_token_valid()

            # Access the token directly from the session
            if not self.session.valid_token or not self.session.token:
                _LOGGER.error(
                    "OAuth session has no valid token. Valid: %s, Token exists: %s",
                    self.session.valid_token,
                    self.session.token is not None
                )
                raise ValueError("Failed to get valid OAuth token")

            token = self.session.token

            if 'access_token' not in token:
                _LOGGER.error("Token missing access_token. Token keys: %s", list(token.keys()))
                raise ValueError("OAuth token missing access_token")

            headers = {
                "Authorization": f"Bearer {token['access_token']}",
            }

            async with self.client_session.get(url, headers=headers, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except ClientResponseError as err:
            if err.status != 401:  # 401 handled gracefully by callers for optional features
                _LOGGER.error("Error fetching data from %s: %s", url, err)
            raise
        except (TypeError, KeyError) as err:
            # Handle token validation failures
            _LOGGER.error("Token error fetching data from %s: %s", url, err)
            raise
        except Exception as err:
            # Use warning for connection errors, error for other issues
            log_msg = "Unexpected error fetching data from %s: %s"
            if "Cannot connect" in str(err) or "Domain name not found" in str(err) or "Timeout" in str(err):
                _LOGGER.warning(log_msg, url, err)
            else:
                _LOGGER.error(log_msg, url, err)
            raise
