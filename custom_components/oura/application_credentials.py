"""Application credentials platform for Oura Ring."""
import logging

from aiohttp import ClientResponseError
from homeassistant.components.application_credentials import (
    AuthImplementation,
    AuthorizationServer,
    ClientCredential,
)
from homeassistant.core import HomeAssistant

from .const import OAUTH2_AUTHORIZE, OAUTH2_TOKEN, OAUTH2_TOKEN_LEGACY

_LOGGER = logging.getLogger(__name__)

# Statuses that mean "wrong token endpoint for this client", worth a same-request retry.
_FALLBACK_STATUSES = (400, 401)


class OuraOAuth2Implementation(AuthImplementation):
    """OAuth2 impl with automatic fallback to the legacy token endpoint.

    moi.ouraring.com/oauth/v2/ext/oauth-token is the live token endpoint for
    essentially all apps today; api.ouraring.com/oauth/token only still works
    for a shrinking set of legacy-portal apps. Trying the legacy endpoint
    first is what caused issue #75: a rejected authorization_code exchange
    burns the single-use code (RFC 6749 4.1.2), so the fallback retry against
    moi then also fails even though moi would have accepted the original code.
    Trying moi first avoids that entirely; the legacy retry only fires for the
    rare app that moi itself rejects, and a refresh_token grant is never
    single-use so that retry is always safe.
    """

    async def _token_request(self, data: dict) -> dict:
        """Make a token request, falling back to the legacy endpoint on 400/401."""
        try:
            return await super()._token_request(data)
        except ClientResponseError as err:
            # HA only logs the parsed error/error_description body at DEBUG; re-reading
            # the body ourselves would mean a second HTTP call, so we log what the
            # exception carries (host, grant, status) at ERROR for #75-style reports.
            _LOGGER.error(
                "Token request to %s failed (grant_type=%s, status=%s): %s",
                self.token_url,
                data.get("grant_type", "unknown"),
                err.status,
                err.message,
            )
            if self.token_url == OAUTH2_TOKEN_LEGACY or err.status not in _FALLBACK_STATUSES:
                raise
            _LOGGER.debug(
                "Token endpoint %s rejected the request (%s); retrying against %s",
                self.token_url,
                err.status,
                OAUTH2_TOKEN_LEGACY,
            )
            self.token_url = OAUTH2_TOKEN_LEGACY
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
