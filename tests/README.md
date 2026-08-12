# Test Suite Documentation

This directory contains the automated test suite and live diagnostic scripts for the Oura Ring Home Assistant integration.

## Test Structure

### Automated Tests (123 tests)

- **`test_api.py`** (2 tests)
  - Timezone-aware date window and exclusive end-date construction
  - Absorbed heart rate outage counted in aggregate failure totals

- **`test_api_reauth_propagation.py`** (5 tests)
  - `OAuth2TokenRequestReauthError` escapes the batched heart rate fetch path
  - `OAuth2TokenRequestReauthError` escapes the short-range heart rate fetch path
  - Ordinary non-auth failures are still absorbed (graceful degradation preserved)
  - Ordinary failures absorbed in the batched path too
  - Reauth error propagates through `asyncio.gather` to the coordinator

- **`test_application_credentials.py`** (4 tests)
  - Legacy endpoint succeeds → fallback never fires, `token_url` unchanged
  - Legacy 400 → retry against new-portal endpoint → success, `token_url` updated
  - Both endpoints 400 → `OAuth2TokenRequestReauthError` propagates to coordinator
  - Already on fallback endpoint → succeeds in one call, no extra retry

- **`test_config_flow.py`** (5 tests)
  - Personal info fetch success and token plumbing
  - Unique ID derived from Oura user ID
  - Config entry title from email address
  - Title fallback when email is absent
  - Multiple accounts with different IDs accepted

- **`test_coordinator.py`** (38 tests)
  - Processing methods for every data category: sleep scores, sleep details, readiness, activity, heart rate, stress, resilience, SpO2, VO2 Max, cardiovascular age, sleep time, workout, session, tags, rest mode
  - Bedtime selection: in-progress records filtered, longest sleep preferred, fallback to existing when no completed record
  - Activity time field presence and absence
  - Heart rate sorting, 24-hour aggregation, and 10-reading fallback
  - Sleep detail date sorting and age filtering
  - Cardiovascular age with and without pulse wave velocity
  - Bedtime tie-breaking by total sleep duration (same day)

- **`test_entity_categories.py`** (7 tests)
  - Entity category assignments (primary vs diagnostic)
  - `low_battery_alert` metadata
  - `total` / `total_increasing` state class assignments
  - Measurement state classes
  - Text sensors have no state class
  - All sensors have an entity category key
  - Primary sensors not marked diagnostic

- **`test_integration_setup.py`** (7 tests)
  - Fixture validation: config entry, hass, API data, API client, OAuth2 session, coordinator, empty response

- **`test_ring_battery.py`** (30 tests)
  - Battery level and charging state processing
  - Edge cases: missing fields, empty data
  - Most-recent ring configuration selection (order-independent, parametrized)
  - Timestamp edge cases: missing, naive, invalid
  - API method: `latest=true` param, 401/404 graceful handling
  - Ring charging binary sensor: `is_on` and availability logic
  - Device info enrichment: hardware type display names, firmware version, fallback

- **`test_sensor.py`** (15 tests)
  - Device info, unique IDs, `has_entity_name`, translation keys
  - `native_value` and availability gating
  - Boolean sensors, tags attributes, workout attributes, `workouts_today` list
  - Rest mode binary sensor

- **`test_statistics.py`** (9 tests)
  - Metadata completeness and state class alignment
  - Sleep efficiency field mapping
  - Timestamp parsing, value transforms, percentage computation, nested value extraction
  - Cumulative sum accumulation

- **`test_statistics_import.py`** (2 tests)
  - Statistics import when entity exists
  - Statistics import when entity is missing

## Live / Diagnostic Scripts

These scripts run against real Oura credentials and are not part of the automated suite. They are not collected by pytest.

- **`live_heartrate_test.py`** — fetches live heart rate data and reports freshness and pagination. Requires `OURA_TOKEN` (Personal Access Token).
- **`live_token_endpoint_test.py`** — probes both OAuth token endpoints to determine which one accepts your app's refresh token (useful for diagnosing new-portal vs legacy-portal apps). Requires `OURA_CLIENT_ID`, `OURA_CLIENT_SECRET`, `OURA_REFRESH_TOKEN`.
- **`get_refresh_token.py`** — runs a local OAuth2 authorization code flow to obtain a refresh token from scratch. Requires `OURA_CLIENT_ID`, `OURA_CLIENT_SECRET`, and `http://localhost:8765/callback` registered as a redirect URI in your Oura app.

## Test Fixtures (`conftest.py`)

- **`mock_config_entry`** — ConfigEntry with OAuth2 token data
- **`mock_hass`** — mocked `HomeAssistant` instance
- **`mock_oura_api_client`** — `AsyncMock` API client with sample responses
- **`mock_oauth2_session`** — mocked OAuth2 session with token refresh
- **`mock_coordinator_with_data`** — coordinator with pre-populated data
- **`mock_oura_api_data`** — complete sample API response covering all data types
- **`mock_empty_api_response`** — empty response for unavailable-sensor testing

## Running Tests

### Using Docker (required — local venv lacks HA test deps)

```bash
# Full suite
docker compose -f docker-compose.test.yml run --rm test

# Single file
docker compose -f docker-compose.test.yml run --rm test pytest tests/test_sensor.py -v

# Single test
docker compose -f docker-compose.test.yml run --rm test pytest tests/test_coordinator.py::test_process_sleep_scores -v
```

### Running Live Scripts

```bash
# Heart rate freshness probe
$env:OURA_TOKEN = "your-personal-access-token"
python tests/live_heartrate_test.py

# Token endpoint probe (which OAuth endpoint accepts your app)
$env:OURA_CLIENT_ID     = "your-client-id"
$env:OURA_CLIENT_SECRET = "your-client-secret"
$env:OURA_REFRESH_TOKEN = "your-refresh-token"
python tests/live_token_endpoint_test.py

# Obtain a refresh token via browser OAuth flow (run once)
$env:OURA_CLIENT_ID     = "your-client-id"
$env:OURA_CLIENT_SECRET = "your-client-secret"
python tests/get_refresh_token.py
```

## Adding New Tests

1. Match the existing async pattern: `@pytest.mark.anyio` with `asyncio_mode = "auto"` (set in `pytest.ini`)
2. Use fixtures from `conftest.py` to reduce boilerplate
3. Test files must start with `test_`; live/diagnostic scripts must not (to avoid pytest collection)
4. Run via Docker to verify — the local venv does not have HA test dependencies
