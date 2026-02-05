"""API client for Oura Ring."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import logging
from typing import Any

from aiohttp import ClientSession, ClientResponseError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.config_entry_oauth2_flow import OAuth2Session
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import API_BASE_URL

_LOGGER = logging.getLogger(__name__)


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
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)

        sleep_data, readiness_data, activity_data, heartrate_data, sleep_detail_data, stress_data, resilience_data, spo2_data, vo2_max_data, cardiovascular_age_data, sleep_time_data = await asyncio.gather(
            self._async_get_sleep(start_date, end_date),
            self._async_get_readiness(start_date, end_date),
            self._async_get_activity(start_date, end_date),
            self._async_get_heartrate(start_date, end_date),
            self._async_get_sleep_detail(start_date, end_date),
            self._async_get_stress(start_date, end_date),
            self._async_get_resilience(start_date, end_date),
            self._async_get_spo2(start_date, end_date),
            self._async_get_vo2_max(start_date, end_date),
            self._async_get_cardiovascular_age(start_date, end_date),
            self._async_get_sleep_time(start_date, end_date),
            return_exceptions=True,
        )

        # Log any exceptions that occurred
        # Count how many endpoints failed to determine if this is a systemic issue
        failed_endpoints = 0
        total_endpoints = 11

        if isinstance(sleep_data, Exception):
            failed_endpoints += 1
        if isinstance(readiness_data, Exception):
            failed_endpoints += 1
        if isinstance(activity_data, Exception):
            failed_endpoints += 1
        if isinstance(heartrate_data, Exception):
            failed_endpoints += 1
        if isinstance(sleep_detail_data, Exception):
            failed_endpoints += 1
        if isinstance(stress_data, Exception):
            failed_endpoints += 1
        if isinstance(resilience_data, Exception):
            failed_endpoints += 1
        if isinstance(spo2_data, Exception):
            failed_endpoints += 1
        if isinstance(vo2_max_data, Exception):
            failed_endpoints += 1
        if isinstance(cardiovascular_age_data, Exception):
            failed_endpoints += 1
        if isinstance(sleep_time_data, Exception):
            failed_endpoints += 1
        
        # If all or most endpoints failed, this is likely a network issue
        if failed_endpoints >= total_endpoints * 0.5:  # 50% or more failed
            _LOGGER.warning(
                "Network connectivity issue: %d/%d API endpoints failed. "
                "Will retry on next update cycle.",
                failed_endpoints, total_endpoints
            )
        else:
            # Log individual endpoint failures at debug level
            if isinstance(sleep_data, Exception):
                _LOGGER.debug("Error fetching sleep data: %s", sleep_data)
            if isinstance(readiness_data, Exception):
                _LOGGER.debug("Error fetching readiness data: %s", readiness_data)
            if isinstance(activity_data, Exception):
                _LOGGER.debug("Error fetching activity data: %s", activity_data)
            if isinstance(heartrate_data, Exception):
                _LOGGER.debug("Error fetching heart rate data: %s", heartrate_data)
            if isinstance(sleep_detail_data, Exception):
                _LOGGER.debug("Error fetching detailed sleep data: %s", sleep_detail_data)
            if isinstance(stress_data, Exception):
                _LOGGER.debug("Error fetching stress data: %s", stress_data)
            if isinstance(resilience_data, Exception):
                _LOGGER.debug("Error fetching resilience data: %s", resilience_data)
            if isinstance(spo2_data, Exception):
                _LOGGER.debug("Error fetching SpO2 data: %s", spo2_data)
            if isinstance(vo2_max_data, Exception):
                _LOGGER.debug("Error fetching VO2 Max data: %s", vo2_max_data)
            if isinstance(cardiovascular_age_data, Exception):
                _LOGGER.debug("Error fetching cardiovascular age data: %s", cardiovascular_age_data)
            if isinstance(sleep_time_data, Exception):
                _LOGGER.debug("Error fetching sleep time data: %s", sleep_time_data)

        return {
            "sleep": sleep_data if not isinstance(sleep_data, Exception) else {},
            "readiness": readiness_data if not isinstance(readiness_data, Exception) else {},
            "activity": activity_data if not isinstance(activity_data, Exception) else {},
            "heartrate": heartrate_data if not isinstance(heartrate_data, Exception) else {},
            "sleep_detail": sleep_detail_data if not isinstance(sleep_detail_data, Exception) else {},
            "stress": stress_data if not isinstance(stress_data, Exception) else {},
            "resilience": resilience_data if not isinstance(resilience_data, Exception) else {},
            "spo2": spo2_data if not isinstance(spo2_data, Exception) else {},
            "vo2_max": vo2_max_data if not isinstance(vo2_max_data, Exception) else {},
            "cardiovascular_age": cardiovascular_age_data if not isinstance(cardiovascular_age_data, Exception) else {},
            "sleep_time": sleep_time_data if not isinstance(sleep_time_data, Exception) else {},
        }

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
