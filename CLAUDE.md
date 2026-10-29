# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Home Assistant custom integration for Oura Ring (v2 API, OAuth2). Domain: `oura`. Distributed via HACS. Single component lives at `custom_components/oura/`.

## Build / Test

Tests run inside the Home Assistant container — the local `.venv` does not have HA test deps. Always use Docker for verification.

```bash
# Full test suite (authoritative)
docker compose -f docker-compose.test.yml run --rm test

# Single test file
docker compose -f docker-compose.test.yml run --rm test pytest tests/test_sensor.py -v

# Single test
docker compose -f docker-compose.test.yml run --rm test pytest tests/test_sensor.py::test_sensor_device_info -v
```

Test image pinned to `homeassistant/home-assistant:2026.9` (Python 3.14). pytest reads `pytest.ini` (the `[tool.pytest.ini_options]` block in `pyproject.toml` is ignored). Async tests use `@pytest.mark.anyio` (anyio plugin, asyncio backend via the `anyio_backend` fixture in `tests/conftest.py`); pytest-asyncio is not installed.

No local lint/format command is configured. CI (`.github/workflows/validate.yml`) runs hassfest, HACS validation, and a non-blocking flake8.

Minimum Home Assistant: 2026.3.0 (`OAuth2TokenRequestReauthError` import); keep `hacs.json` in sync.

## Architecture

```
custom_components/oura/
├── __init__.py                  # Setup: OAuth2 session → OuraApiClient → Coordinator → forward platforms
├── api.py                       # OuraApiClient: 18 endpoints fetched in parallel via asyncio.gather
├── coordinator.py               # OuraDataUpdateCoordinator: modular _process_* methods per data category
├── sensor.py                    # OuraSensor: CoordinatorEntity, driven by SENSOR_TYPES dict
├── binary_sensor.py             # Rest mode + ring charging binary sensors
├── statistics.py                # Historical import + daily reconcile as HA long-term statistics (means + statistics-only sums)
├── lifetime.py                  # Lifetime counters: history of entity sums, recorder-owned statistics, late-data moves (#86)
├── config_flow.py               # OAuth2 + options flow (update interval, historical months, reconcile days, re-import toggle)
├── const.py                     # SENSOR_TYPES (single source of truth), API URLs, scopes, defaults
├── application_credentials.py   # OAuth2 credential provider (moi.ouraring.com primary, legacy fallback)
├── services.yaml                # oura.reconcile_statistics action
├── strings.json                 # en source; translations/ has de, en, es, fr
```

**Data flow**: `api.py` fetches all Oura endpoints in parallel → `coordinator.py` `_process_*` methods normalize each category into `coordinator.data[key]` → entities read by key.

**Sensors are config-driven.** `SENSOR_TYPES` in `const.py` is the single source of truth (name, icon, unit, device_class, state_class, entity_category, data_category). To add a sensor:
1. Add entry to `SENSOR_TYPES` in `const.py`
2. Add matching translation key in `strings.json` (+ all `translations/*.json`; `tests/test_translations.py` enforces parity)
3. Ensure coordinator `_process_*` populates `coordinator.data[key]`
4. Add `STATISTICS_METADATA` + `DATA_SOURCE_CONFIG` mapping in `statistics.py` unless the sensor is intentionally excluded (timestamps, text, "last workout" style). A daily sum with an entity (`has_sum`) is never imported into its own statistic (the recorder owns it, #86); add its key to `LIFETIME_SOURCE_KEYS` in `const.py` instead so it gets a lifetime counter
5. Add a row to `docs/SENSORS.md` and bump the sensor counts in README, `docs/SENSORS.md`, `docs/QUICKREF.md`, `docs/INSTALLATION.md`, `docs/PROJECT_SUMMARY.md`, `info.md`

To add an API endpoint: add to `API_ENDPOINTS` dict in `api.py`, add `_async_get_*` method, include in the `asyncio.gather` call, add a `_process_*` step in coordinator.

## Conventions

- **Config entry only** — no YAML configuration (`config_entry_only_config_schema`)
- All entities use `CoordinatorEntity`, `_attr_has_entity_name = True`, `_attr_translation_key`
- One shared device per config entry (`Oura Ring` / `Oura` / `SERVICE`)
- Availability gate: coordinator has data AND key exists AND value is not None
- 401/403 on optional/Gen3/subscription-limited endpoints → empty data, not errors. 429 retried once honouring `Retry-After`. Transient failures preserve last known data.
- Diagnostic sensors get `EntityCategory.DIAGNOSTIC` in `const.py`
- One-time historical import gated by `CONF_HISTORICAL_DATA_IMPORTED` flag in entry options — survives restarts
- Heart rate API is 30-day-chunked; `api.py` auto-batches longer ranges
- OAuth token refresh handled by HA's `OAuth2Session` — never refresh manually
- Multi-account supported via entry-scoped unique IDs

## Reference docs in repo

- `.github/copilot-instructions.md` — same scope as this file, kept in sync
- `docs/INSTALLATION.md`, `docs/SENSORS.md`, `docs/DASHBOARDS.md`, `docs/TROUBLESHOOTING.md`, `docs/CONTRIBUTING.md`, `docs/PROJECT_SUMMARY.md`
- `docs/Oura API/` — OpenAPI schemas 1.27 → 1.43 (latest: `openapi-1.43.json`)
- `plans/` — phase-completion notes from past modernization passes (historical context, not active TODOs)
