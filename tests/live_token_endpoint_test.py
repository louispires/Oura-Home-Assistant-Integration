"""Live test: probe which OAuth token endpoint accepts your app's refresh token.

Useful for confirming whether your Oura app is a legacy-portal or new-portal
app, and verifying that moi.ouraring.com (the primary endpoint since v2.10.0)
works for your credentials.

Usage:
    Set the three environment variables below, then run:

        python tests/live_token_endpoint_test.py

    OURA_CLIENT_ID      — OAuth client ID from your Oura developer app
    OURA_CLIENT_SECRET  — OAuth client secret
    OURA_REFRESH_TOKEN  — refresh_token from an existing OAuth session
                          (copy from HA storage, or capture from a fresh auth flow)

How to find your refresh_token in Home Assistant:
    1. Open the HA file system (e.g. Studio Code Server, SSH, or Samba).
    2. Look in .storage/core.config_entries — find the "oura" entry and copy the
       token.refresh_token value.

What this script does:
    1. Tries the primary endpoint (moi.ouraring.com/oauth/v2/ext/oauth-token).
    2. Tries the legacy endpoint (api.ouraring.com/oauth/token).
    3. Reports which one(s) returned a new access token and which failed.

Expected results:
    Most apps (new- and legacy-portal): moi ✅, legacy may or may not also work.
    Legacy-only app: moi ❌, legacy ✅ — the fallback in application_credentials.py
    covers this case automatically.
"""
import asyncio
import json
import os
import sys

try:
    import aiohttp
except ImportError:
    print("ERROR: aiohttp not installed. Run: pip install aiohttp")
    sys.exit(1)

PRIMARY_ENDPOINT = "https://moi.ouraring.com/oauth/v2/ext/oauth-token"
LEGACY_ENDPOINT = "https://api.ouraring.com/oauth/token"


def _require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"ERROR: environment variable {name} is not set.")
        sys.exit(1)
    return value


async def try_refresh(
    session: aiohttp.ClientSession,
    endpoint: str,
    client_id: str,
    client_secret: str,
    refresh_token: str,
) -> None:
    label = endpoint.split("/")[2]  # hostname only, for readability
    print(f"\n{'─' * 60}")
    print(f"Endpoint : {endpoint}")
    payload = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }
    try:
        async with session.post(endpoint, data=payload) as resp:
            body = await resp.text()
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                data = {}

            if resp.status == 200 and "access_token" in data:
                token_preview = data["access_token"][:12] + "..."
                expires_in = data.get("expires_in", "?")
                print(f"Result   : ✅ SUCCESS (HTTP 200)")
                print(f"Token    : {token_preview}  expires_in={expires_in}s")
                if "refresh_token" in data:
                    print("Note     : A new refresh_token was also issued (rotate it).")
            else:
                error = data.get("error", "?")
                description = data.get("error_description", body[:120])
                print(f"Result   : ❌ FAILED (HTTP {resp.status})")
                print(f"Error    : {error}: {description}")
    except aiohttp.ClientConnectorError as exc:
        print(f"Result   : ❌ CONNECTION ERROR — {exc}")


async def main() -> None:
    client_id = _require_env("OURA_CLIENT_ID")
    client_secret = _require_env("OURA_CLIENT_SECRET")
    refresh_token = _require_env("OURA_REFRESH_TOKEN")

    print("Oura token endpoint probe")
    print(f"client_id : {client_id[:8]}...{client_id[-4:]}")
    print(f"refresh   : {refresh_token[:8]}...{refresh_token[-4:]}")

    async with aiohttp.ClientSession() as session:
        await try_refresh(session, PRIMARY_ENDPOINT, client_id, client_secret, refresh_token)
        await try_refresh(session, LEGACY_ENDPOINT, client_id, client_secret, refresh_token)

    print(f"\n{'─' * 60}")
    print(
        "\nInterpretation:\n"
        "  moi ✅                  → no action needed, this is what v2.10.0 uses by default\n"
        "  moi ❌ / legacy ✅      → legacy-portal app; the built-in fallback handles this\n"
        "  Both ❌               → credentials are wrong or tokens have expired"
    )


if __name__ == "__main__":
    asyncio.run(main())
