# Oura Ring v2 Custom Component - Project Summary

## Overview

Home Assistant custom integration for Oura Ring v2 API using OAuth2.

Current release baseline in repository:

- **Version**: 2.9.0
- **Entity model**: 71 sensors + 2 binary sensors
- **Architecture**: DataUpdateCoordinator + configuration-driven sensor definitions
- **Testing**: 132 tests passing in Docker test harness

## Core Architecture

### Main flow

1. `custom_components/oura/__init__.py`
   - Sets up OAuth2 session
   - Creates API client + coordinator
   - Forwards platforms
   - Registers integration services

2. `custom_components/oura/api.py`
   - Fetches Oura endpoints in parallel
   - Handles endpoint-specific fallback behavior
   - Preserves reauth propagation for OAuth failures

3. `custom_components/oura/coordinator.py`
   - Normalizes raw API responses into `coordinator.data`
   - Contains modular processing methods per data category
   - Includes latest-sleep-session processing and reconciliation integration

4. `custom_components/oura/sensor.py` and `custom_components/oura/binary_sensor.py`
   - Entities driven by metadata in `const.py`
   - Entry-scoped unique IDs
   - Translation keys and entity categories

5. `custom_components/oura/statistics.py`
   - Historical import into long-term statistics
   - Daily reconciliation support for late-arriving data
   - Sum-baseline continuity for cumulative statistics

6. `custom_components/oura/const.py`
   - Single source of truth for sensor metadata (`SENSOR_TYPES`)
   - API URLs, defaults, options constants

## Feature Snapshot

- OAuth2 authentication via Home Assistant Application Credentials
- Multi-account support (entry-scoped IDs)
- Expanded Oura coverage (sleep, readiness, activity, heart, stress, resilience, SpO2, cardio, workouts, sessions, tags, rest mode, ring battery)
- Latest bedtime sensors for most-recent sleep session tracking (including naps)
- Daily statistics reconciliation + on-demand `oura.reconcile_statistics` service
- Historical import options with persistent import-state tracking

## Documentation Map

- `README.md`: full user-facing guide and examples
- `docs/INSTALLATION.md`: installation and setup
- `docs/FIXING_REDIRECT_URI.md`: OAuth redirect troubleshooting
- `docs/TROUBLESHOOTING.md`: operational troubleshooting
- `docs/CONTRIBUTING.md`: contribution workflow and test commands
- `docs/QUICKREF.md`: concise operator reference

## Testing Snapshot

Current test suite includes:

- API behavior and reauth propagation
- Config flow/options flow
- Coordinator processing logic
- Sensor and binary sensor behavior
- Statistics import/reconciliation logic
- Integration setup/lifecycle
- Ring battery + charging diagnostics

Run tests:

```bash
# Full suite

docker compose -f docker-compose.test.yml run --rm test

# Single file

docker compose -f docker-compose.test.yml run --rm test pytest tests/test_sensor.py -v
```

## Maintenance Notes

- Keep sensor metadata changes in `const.py` and processing changes in `coordinator.py` aligned.
- Any new sensor key must include translation updates (`strings.json` + `translations/*.json`).
- If OAuth behavior changes, update both docs and tests (especially fallback/reauth paths).
- Keep this summary concise; use README for deep user documentation.

---

**Status**: Active, production-ready, and aligned with current repository state.
