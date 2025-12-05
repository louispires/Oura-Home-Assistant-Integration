"""Config flow for Oura Ring integration."""
from __future__ import annotations

import logging
from typing import Any

from aiohttp import ClientError
from homeassistant import config_entries
from homeassistant.config_entries import SOURCE_REAUTH
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol

from .const import (
    DOMAIN,
    OAUTH2_SCOPES,
    CONF_UPDATE_INTERVAL,
    CONF_HISTORICAL_MONTHS,
    CONF_HISTORICAL_DATA_IMPORTED,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_HISTORICAL_MONTHS,
    MIN_UPDATE_INTERVAL,
    MAX_UPDATE_INTERVAL,
    MIN_HISTORICAL_MONTHS,
    MAX_HISTORICAL_MONTHS,
)

_LOGGER = logging.getLogger(__name__)


class OuraFlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Handle a config flow for Oura Ring."""

    DOMAIN = DOMAIN
    VERSION = 1

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return _LOGGER
    
    @property
    def extra_authorize_data(self) -> dict[str, Any]:
        """Extra data that needs to be appended to the authorize url."""
        return {
            "scope": " ".join(OAUTH2_SCOPES)
        }

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        # Don't set unique_id here - we'll set it in async_oauth_create_entry
        # after we get the user's Oura account ID
        return await super().async_step_user(user_input)

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> config_entries.FlowResult:
        """Handle re-authentication."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Confirm re-authentication."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=vol.Schema({}),
            )
        return await self.async_step_user()

    async def async_oauth_create_entry(self, data: dict[str, Any]) -> config_entries.FlowResult:
        """Create an entry for Oura Ring."""
        # Get user info from Oura API to get unique user ID
        try:
            user_info = await self._async_get_user_info(data)
        except ClientError as err:
            _LOGGER.error("Failed to get user info: %s", err)
            return self.async_abort(reason="cannot_connect")
        except Exception as err:
            _LOGGER.exception("Unexpected error getting user info: %s", err)
            return self.async_abort(reason="unknown")

        user_id = user_info.get("id")
        if not user_id:
            _LOGGER.error("No user ID in response: %s", user_info)
            return self.async_abort(reason="invalid_user_info")

        email = user_info.get("email")
        title = email if email else "Oura Ring"

        await self.async_set_unique_id(user_id)

        if self.source == SOURCE_REAUTH:
            self._abort_if_unique_id_mismatch(reason="wrong_account")
            return self.async_update_reload_and_abort(
                self._get_reauth_entry(), data=data
            )

        self._abort_if_unique_id_configured()

        _LOGGER.info("Successfully authenticated user: %s", title)
        return self.async_create_entry(title=title, data=data)

    async def _async_get_user_info(self, data: dict[str, Any]) -> dict[str, Any]:
        """Get user info from Oura API."""
        access_token = data["token"]["access_token"]
        session = async_get_clientsession(self.hass)

        async with session.get(
            "https://api.ouraring.com/v2/usercollection/personal_info",
            headers={"Authorization": f"Bearer {access_token}"},
        ) as response:
            response.raise_for_status()
            return await response.json()

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OuraOptionsFlowHandler:
        """Get the options flow for this handler."""
        return OuraOptionsFlowHandler()


class OuraOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Oura Ring options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                        ),
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_UPDATE_INTERVAL, max=MAX_UPDATE_INTERVAL),
                    ),
                    vol.Optional(
                        CONF_HISTORICAL_MONTHS,
                        default=self.config_entry.options.get(
                            CONF_HISTORICAL_MONTHS, DEFAULT_HISTORICAL_MONTHS
                        ),
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_HISTORICAL_MONTHS, max=MAX_HISTORICAL_MONTHS),
                    ),
                    vol.Optional(
                        CONF_HISTORICAL_DATA_IMPORTED,
                        default=self.config_entry.options.get(
                            CONF_HISTORICAL_DATA_IMPORTED, True
                        ),
                    ): bool,
                }
            ),
        )
