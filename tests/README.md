# Test Suite Documentation

This directory contains the automated test suite and live diagnostic scripts for the Oura Ring Home Assistant integration.

## Test Structure

### Automated Tests (230 tests)

- **`test_api.py`** (9 tests)
  - Timezone-aware date window and exclusive end-date construction
  - Absorbed heart rate outage counted in aggregate failure totals
  - 429 handling: one retry honouring `Retry-After`, give up after second 429, capped default without the header
  - Resilience endpoint: 403 → empty data, other statuses propagate
  - Heart rate requests only `timestamp,bpm` fields (single and batched paths)

- **`test_api_reauth_propagation.py`** (5 tests)
  - `OAuth2TokenRequestReauthError` escapes the batched heart rate fetch path
  - `OAuth2TokenRequestReauthError` escapes the short-range heart rate fetch path
  - Ordinary non-auth failures are still absorbed (graceful degradation preserved)
  - Ordinary failures absorbed in the batched path too
  - Reauth error propagates through `asyncio.gather` to the coordinator

- **`test_application_credentials.py`** (7 tests)
  - Primary (`moi.ouraring.com`) endpoint succeeds → no fallback, `token_url` unchanged
  - Primary 400 on refresh → retry against legacy endpoint → success, `token_url` updated
  - Primary 401 on code exchange → retry against legacy endpoint → success (#75 regression guard)
  - Already on legacy and rejected → `OAuth2TokenRequestReauthError` propagates to coordinator
  - Non-fallback status (e.g. 500) propagates without retry
  - Already on legacy endpoint → succeeds in one call, no extra retry
  - Failure logging includes host/grant/status but never tokens or secrets

- **`test_config_flow.py`** (9 tests)
  - Personal info fetch success and token plumbing
  - Unique ID derived from Oura user ID
  - Config entry title from email address
  - Title fallback when email is absent
  - Multiple accounts with different IDs accepted
  - `oauth_unauthorized` / `oauth_failed` aborts remapped to `oauth_token_rejected`
  - Unrelated aborts and successful results pass through unchanged

- **`test_coordinator.py`** (41 tests)
  - Processing methods for every data category: sleep scores, sleep details, readiness, activity, heart rate, stress, resilience, SpO2, VO2 Max, cardiovascular age, sleep time, workout, session, tags, rest mode
  - Workouts: today-only count/list, latest workout fields (incl. source), carry-forward when no new data, replacement by new data
  - Bedtime selection: in-progress records filtered, longest sleep preferred, fallback to existing when no completed record
  - Latest bedtime: most recent session incl. naps, in-progress end unavailable, deleted/rest ignored
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

- **`test_sensor.py`** (16 tests)
  - Device info, unique IDs, `has_entity_name`, translation keys
  - `native_value` and availability gating
  - Boolean sensors, tags attributes, workout attributes, `workouts_today` list (and absence on other sensors)
  - `last_workout_source` accepts values outside the documented Oura enum
  - Rest mode binary sensor

- **`test_setup_order.py`** (5 tests)
  - Fresh install imports history after platforms are set up
  - Import failure resets the reconcile marker
  - Existing install skips the historical import
  - Reconcile skipped on the marked day, runs again after the marker is reset

- **`test_statistics.py`** (39 tests)
  - Metadata completeness, OpenAPI 1.39 sensor coverage, data source config structure, state class alignment
  - Sleep efficiency mapping, bedtime timestamps excluded
  - Sleep detail collapse (prefers `long_sleep`, falls back to longest); total sleep duration summed across naps, invalid types ignored
  - Timestamp parsing, value transforms, percentage computation, nested value extraction
  - Cumulative sums: accumulation, baseline seeding, hourly baseline lookup
  - Unfinished-hour guard and heart rate grouping by local day
  - Recorder flush before baseline reads; startup/running/stopping recorder-wait behaviour and multi-entry isolation
  - Warning when an entity-backed sensor is imported before registration

- **`test_statistics_import.py`** (3 tests)
  - Statistics import when entity exists
  - Statistics import when entity is missing
  - Total sleep duration summed across sessions

- **`test_translations.py`** (14 tests)
  - `strings.json` has a name for every sensor
  - Sensor and abort keys match `strings.json` in every locale (de, en, es, fr)
  - Abort strings contain no inline URLs (hassfest rule)

## Live / Diagnostic Scripts

These scripts run against real Oura credentials and are not part of the automated suite. They are not collected by pytest.

- **`live_heartrate_test.py`** — fetches live heart rate data and reports freshness and pagination. Requires `OURA_TOKEN` (OAuth2 access token; personal access tokens were deprecated in December 2025).
- **`live_token_endpoint_test.py`** — probes both OAuth token endpoints to determine which one accepts your app's refresh token (useful for diagnosing new-portal vs legacy-portal apps). Requires `OURA_CLIENT_ID`, `OURA_CLIENT_SECRET`, `OURA_REFRESH_TOKEN`.
- **`get_refresh_token.py`** — runs a local OAuth2 authorization code flow to obtain a refresh token from scratch. Requires `OURA_CLIENT_ID`, `OURA_CLIENT_SECRET`, and `http://localhost:8765/callback` registered as a redirect URI in your Oura app.

## Test Fixtures (`conftest.py`)

- **`anyio_backend`** — runs `@pytest.mark.anyio` tests on the asyncio backend
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
$env:OURA_TOKEN = "your-oauth2-access-token"
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

1. Match the existing async pattern: mark async tests with `@pytest.mark.anyio` (anyio plugin; the `anyio_backend` fixture in `conftest.py` selects asyncio). pytest-asyncio is not installed, and pytest reads `pytest.ini`, not `pyproject.toml`
2. Use fixtures from `conftest.py` to reduce boilerplate
3. Test files must start with `test_`; live/diagnostic scripts must not (to avoid pytest collection)
4. Run via Docker to verify — the local venv does not have HA test dependencies
