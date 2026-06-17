"""Live test: connect to real Oura API and inspect heart rate data freshness.

Usage:
    Set OURA_TOKEN to a Personal Access Token from cloud.ouraring.com/personal-access-tokens

    python tests/live_heartrate_test.py

The script prints every heart rate reading returned by the API for the current
window, shows how stale the latest reading is, and reports what the integration
would show as current_heart_rate / average_heart_rate.
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone

try:
    import aiohttp
except ImportError:
    print("ERROR: aiohttp not installed. Run: pip install aiohttp")
    sys.exit(1)


API_BASE = "https://api.ouraring.com/v2/usercollection"


def _parse_iso(ts: str) -> datetime | None:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


async def fetch_heartrate_page(session: aiohttp.ClientSession, token: str, params: dict) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    async with session.get(f"{API_BASE}/heartrate", headers=headers, params=params) as resp:
        resp.raise_for_status()
        return await resp.json()


async def fetch_heartrate(token: str, start_dt: str, end_dt: str) -> tuple[list[dict], int]:
    """Fetch all pages of heart rate data. Returns (readings, page_count)."""
    base_params = {"start_datetime": start_dt, "end_datetime": end_dt}
    all_readings: list[dict] = []
    page = 0

    async with aiohttp.ClientSession() as session:
        params = dict(base_params)
        while True:
            page += 1
            raw = await fetch_heartrate_page(session, token, params)
            readings = raw.get("data", [])
            all_readings.extend(readings)
            next_token = raw.get("next_token")
            print(f"  Page {page}: {len(readings)} readings, next_token={'YES' if next_token else 'no'}")
            if not next_token:
                break
            params = {"next_token": next_token}

    return all_readings, page


def analyse(readings: list[dict]) -> None:
    now_utc = datetime.now(timezone.utc)
    print(f"\nCurrent UTC time : {now_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Total readings   : {len(readings)}\n")

    if not readings:
        print("No heart rate readings returned by API.")
        return

    sorted_readings = sorted(readings, key=lambda x: x.get("timestamp", ""))

    print(f"{'Timestamp (UTC)':<30}  {'BPM':>4}  {'Source':<20}  Lag")
    print("-" * 75)
    for hr in sorted_readings:
        ts_str = hr.get("timestamp", "")
        bpm = hr.get("bpm", "?")
        source = hr.get("source", "")
        parsed = _parse_iso(ts_str)
        lag = f"{int((now_utc - parsed).total_seconds() / 60)} min ago" if parsed else "?"
        print(f"  {ts_str:<28}  {bpm:>4}  {source:<20}  {lag}")

    latest = sorted_readings[-1]
    latest_ts = _parse_iso(latest.get("timestamp", ""))
    latest_bpm = latest.get("bpm")
    lag_seconds = (now_utc - latest_ts).total_seconds() if latest_ts else None

    print()
    print("=== Integration would report ===")
    print(f"  current_heart_rate  : {latest_bpm} bpm")
    if latest_ts:
        print(f"  heart_rate_timestamp: {latest_ts.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"  Data lag            : {lag_seconds / 60:.1f} minutes old")

    cutoff = now_utc - timedelta(hours=24)
    recent_bpms = [
        r["bpm"] for r in sorted_readings
        if r.get("bpm") and (_parse_iso(r.get("timestamp", "")) or datetime.min.replace(tzinfo=timezone.utc)) > cutoff
    ]
    if not recent_bpms:
        recent_bpms = [r["bpm"] for r in sorted_readings[-10:] if r.get("bpm")]
        print(f"  average_heart_rate  : {sum(recent_bpms)/len(recent_bpms):.1f} bpm (last 10 readings, no 24h data)")
    else:
        print(f"  average_heart_rate  : {sum(recent_bpms)/len(recent_bpms):.1f} bpm ({len(recent_bpms)} readings in last 24h)")
        print(f"  min_heart_rate      : {min(recent_bpms)} bpm")
        print(f"  max_heart_rate      : {max(recent_bpms)} bpm")

    print()
    if lag_seconds is not None and lag_seconds > 3600:
        print(f"WARNING: Latest reading is {lag_seconds/3600:.1f} hours old.")
        print("         This means the ring has not synced with Oura servers recently.")
        print("         The integration can only report data that Oura has received.")
    elif lag_seconds is not None and lag_seconds > 600:
        print(f"NOTE: Latest reading is {lag_seconds/60:.0f} minutes old (ring may not have synced yet).")
    else:
        print("Data appears fresh (< 10 minutes old).")


async def main() -> None:
    token = os.environ.get("OURA_TOKEN", "").strip()
    if not token:
        print(
            "ERROR: Set OURA_TOKEN environment variable to your Oura Personal Access Token.\n"
            "  Get one at: https://cloud.ouraring.com/personal-access-tokens\n"
            "\n"
            "  Windows PowerShell:  $env:OURA_TOKEN = 'your_token_here'\n"
            "  bash/zsh:            export OURA_TOKEN=your_token_here\n"
        )
        sys.exit(1)

    now_utc = datetime.now(timezone.utc)
    # Match exactly what the integration fetches: yesterday through tomorrow
    start_date = (now_utc - timedelta(days=1)).date()
    end_date = (now_utc + timedelta(days=1)).date()
    start_dt = f"{start_date.isoformat()}T00:00:00"
    end_dt = f"{end_date.isoformat()}T23:59:59"

    print(f"Fetching heartrate from {start_dt} to {end_dt} ...")

    try:
        readings, pages = await fetch_heartrate(token, start_dt, end_dt)
    except aiohttp.ClientResponseError as err:
        print(f"API error {err.status}: {err.message}")
        if err.status == 401:
            print("Token is invalid or expired. Generate a new one at cloud.ouraring.com/personal-access-tokens")
        sys.exit(1)

    print(f"Total pages fetched: {pages}\n")
    analyse(readings)


if __name__ == "__main__":
    asyncio.run(main())
