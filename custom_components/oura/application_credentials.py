"""Application credentials platform for Oura Ring."""
import logging

from aiohttp import ClientResponseError
from homeassistant.components.application_credentials import (
    AuthImplementation,
    AuthorizationServer,
    ClientCredential,
)
from homeassistant.core import HomeAssistant

from .const import OAUTH2_AUTHORIZE, OAUTH2_TOKEN, OAUTH2_TOKEN_FALLBACK

_LOGGER = logging.getLogger(__name__)

# Statuses the legacy endpoint returns for new-portal apps: 400 on refresh,
# 401 on the initial authorization_code exchange.
_FALLBACK_STATUSES = (400, 401)


class OuraOAuth2Implementation(AuthImplementation):
    """OAuth2 impl with automatic fallback to the new-portal token endpoint.

    Apps registered on developer.ouraring.com are rejected by the legacy
    api.ouraring.com/oauth/token endpoint: refreshes fail with 400, and the
    initial authorization_code exchange fails with 401. HA wraps both as
    ClientResponseError (400/401 refreshes are further wrapped as
    OAuth2TokenRequestReauthError, which subclasses it). On first rejection we
    transparently retry against the new endpoint and update self.token_url so
    all subsequent requests go there directly.
    """

    async def _token_request(self, data: dict) -> dict:
        """Make a token request, falling back to the new endpoint on 400/401."""
        try:
            return await super()._token_request(data)
        except ClientResponseError as err:
            if self.token_url == OAUTH2_TOKEN_FALLBACK or err.status not in _FALLBACK_STATUSES:
                raise
            _LOGGER.debug(
                "Legacy token endpoint rejected the request (%s); retrying against %s",
                err.status,
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
