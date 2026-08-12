"""One-shot OAuth2 flow to obtain a refresh_token from Oura.

Run this once to get your refresh_token, then use it with live_token_endpoint_test.py.

Prerequisites:
    1. In your Oura app at developer.ouraring.com → Edit → Redirect URIs,
       add:  http://localhost:8765/callback
    2. Set environment variables:
           OURA_CLIENT_ID      your client ID
           OURA_CLIENT_SECRET  your client secret
    3. Run:
           python tests/get_refresh_token.py

The script opens your browser, waits for you to authorise, then prints
the access_token and refresh_token. It does not store them anywhere.
"""
import asyncio
import json
import os
import sys
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

try:
    import aiohttp
except ImportError:
    print("ERROR: aiohttp not installed. Run: pip install aiohttp")
    sys.exit(1)

AUTHORIZE_URL = "https://cloud.ouraring.com/oauth/authorize"
TOKEN_URL = "https://api.ouraring.com/oauth/token"
REDIRECT_URI = "http://localhost:8765/callback"
SCOPES = "email personal daily heartrate workout session tag spo2 ring_configuration stress heart_health"

_auth_code: str | None = None


class _CallbackHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # silence access logs
        pass

    def do_GET(self):
        global _auth_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "error" in params:
            error = params["error"][0]
            desc = params.get("error_description", [""])[0]
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"Authorization failed: {error} — {desc}".encode())
            print(f"\nERROR: Oura returned: {error}: {desc}")
        elif "code" in params:
            _auth_code = params["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h2>Authorised. You can close this tab.</h2>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing code parameter.")


def _run_server(server: HTTPServer) -> None:
    server.handle_request()  # serve exactly one request then exit


async def exchange_code(client_id: str, client_secret: str, code: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "redirect_uri": REDIRECT_URI,
            },
        ) as resp:
            body = await resp.text()
            if resp.status != 200:
                print(f"Token exchange failed (HTTP {resp.status}): {body}")
                sys.exit(1)
            return json.loads(body)


def main() -> None:
    client_id = os.environ.get("OURA_CLIENT_ID", "").strip()
    client_secret = os.environ.get("OURA_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        print("ERROR: set OURA_CLIENT_ID and OURA_CLIENT_SECRET environment variables.")
        sys.exit(1)

    params = urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
    })
    auth_url = f"{AUTHORIZE_URL}?{params}"

    server = HTTPServer(("localhost", 8765), _CallbackHandler)
    thread = Thread(target=_run_server, args=(server,), daemon=True)
    thread.start()

    print(f"Opening browser for authorisation...")
    print(f"(If the browser doesn't open, visit this URL manually:)\n{auth_url}\n")
    webbrowser.open(auth_url)

    print("Waiting for Oura to redirect back to localhost:8765 ...")
    thread.join(timeout=120)

    if not _auth_code:
        print("ERROR: No authorisation code received within 2 minutes.")
        sys.exit(1)

    print("Exchanging code for tokens...")
    tokens = asyncio.run(exchange_code(client_id, client_secret, _auth_code))

    access = tokens.get("access_token", "")
    refresh = tokens.get("refresh_token", "")
    expires = tokens.get("expires_in", "?")

    print("\n" + "─" * 60)
    print(f"access_token  : {access[:16]}...  (expires in {expires}s)")
    print(f"refresh_token : {refresh}")
    print("─" * 60)
    print("\nTo run the endpoint probe:")
    print(f'  $env:OURA_CLIENT_ID="{client_id}"')
    print(f'  $env:OURA_CLIENT_SECRET="<your-secret>"')
    print(f'  $env:OURA_REFRESH_TOKEN="{refresh}"')
    print("  python tests/live_token_endpoint_test.py")


if __name__ == "__main__":
    main()
