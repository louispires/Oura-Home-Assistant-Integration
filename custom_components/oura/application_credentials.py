"""Application credentials platform for Oura Ring."""
import logging

from homeassistant.components.application_credentials import (
    AuthImplementation,
    AuthorizationServer,
    ClientCredential,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_entry_oauth2_flow import OAuth2TokenRequestReauthError

from .const import OAUTH2_AUTHORIZE, OAUTH2_TOKEN, OAUTH2_TOKEN_FALLBACK

_LOGGER = logging.getLogger(__name__)


class OuraOAuth2Implementation(AuthImplementation):
    """OAuth2 impl with automatic fallback to the new-portal token endpoint.

    Apps registered on developer.ouraring.com return 400 invalid_request when
    refreshing against the legacy api.ouraring.com/oauth/token endpoint. On the
    first such rejection we transparently retry against the new endpoint and
    update self.token_url so all subsequent requests go there directly.
    """

    async def _token_request(self, data: dict) -> dict:
        """Make a token request, falling back to the new endpoint on 400."""
        try:
            return await super()._token_request(data)
        except OAuth2TokenRequestReauthError:
            if self.token_url == OAUTH2_TOKEN_FALLBACK:
                raise
            _LOGGER.debug(
                "Legacy token endpoint rejected the request; retrying against %s",
                OAUTH2_TOKEN_FALLBACK,
            )
            self.token_url = OAUTH2_TOKEN_FALLBACK
            return await super()._token_request(data)


async def async_get_authorization_server(hass: HomeAssistant) -> AuthorizationServer:
    """Return authorization server (used by the default impl path)."""
    return AuthorizationServer(
        authorize_url=OAUTH2_AUTHORIZE,
        token_url=OAUTH2_TOKEN,
    )


async def async_get_auth_implementation(
    hass: HomeAssistant,
    auth_domain: str,
    credential: ClientCredential,
) -> OuraOAuth2Implementation:
    """Return the custom impl that handles the new-portal token endpoint."""
    return OuraOAuth2Implementation(
        hass,
        auth_domain,
        credential,
        AuthorizationServer(
            authorize_url=OAUTH2_AUTHORIZE,
            token_url=OAUTH2_TOKEN,
        ),
    )
