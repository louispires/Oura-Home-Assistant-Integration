# Project Guidelines

Home Assistant custom integration for Oura Ring (v2 API, OAuth2). Domain: `oura`.

## Architecture

```
custom_components/oura/
├── __init__.py          # Entry setup: OAuth2 session → API client → Coordinator → platforms
├── api.py               # OuraApiClient: 16 endpoints fetched in parallel via asyncio.gather
├── coordinator.py       # OuraDataUpdateCoordinator: modular _process_* methods per data category
├── sensor.py            # OuraSensor: CoordinatorEntity, config-driven from SENSOR_TYPES
├── binary_sensor.py     # OuraRestModeBinarySensor: single rest-mode entity
├── statistics.py        # Historical data import as HA long-term statistics
├── config_flow.py       # OAuth2 flow + options flow (update interval, historical months)
├── const.py             # All sensor definitions, API URLs, scopes, defaults
├── application_credentials.py  # OAuth2 credential provider
└── strings.json         # Translation source (en); translations/ has de, es, fr
```

**Data flow**: `api.py` fetches all endpoints → `coordinator.py` processes raw data via `_process_*` methods → entities read from `coordinator.data[key]`.

**Key pattern**: Sensors are **configuration-driven** — defined in `SENSOR_TYPES` dict in `const.py` (name, icon, unit, device_class, state_class, entity_category, data_category). Adding a sensor means adding an entry there + a processing method in the coordinator.

## Build and Test

```bash
# Run tests (authoritative — use Docker, not bare Python)
docker compose -f docker-compose.test.yml run --rm test

# Run a single test file
docker compose -f docker-compose.test.yml run --rm test pytest tests/test_sensor.py -v
```

Test image: `homeassistant/home-assistant:2025.11`. Tests use `pytest` + `pytest-asyncio` (async throughout).

## Conventions

- **Config entry only** — no YAML configuration support
- **All entities** use `CoordinatorEntity`, `_attr_has_entity_name = True`, `_attr_translation_key`
- **Device info**: shared device per config entry (`Oura Ring` / `Oura` / `SERVICE`)
- **Availability**: entity is available only when coordinator has data AND the sensor key exists AND value is not None
- **API resilience**: 401s on optional endpoints (Gen3-only, subscription-limited) return empty data, not errors. Transient failures preserve existing data.
- **Entity categories**: diagnostic sensors use `EntityCategory.DIAGNOSTIC` (see `const.py`)
- **Translation keys**: every sensor has a translation key matching its `const.py` key; update `strings.json` + `translations/` when adding sensors
- **Historical import**: one-time import tracked via `CONF_HISTORICAL_DATA_IMPORTED` persistent flag in config entry
- **Heart rate batching**: API limits to 30-day chunks; `api.py` auto-batches

## Pitfalls

- Local Python env lacks HA test deps — always verify via Docker test harness
- `SENSOR_TYPES` in `const.py` is the single source of truth for sensor metadata; don't define sensor attributes in `sensor.py`
- OAuth token refresh is handled by HA's `OAuth2Session` — don't manage tokens manually
- When adding API endpoints: add to `API_ENDPOINTS` dict, add `_async_get_*` method, include in `asyncio.gather` call, add `_process_*` in coordinator

## Documentation

See [docs/](../docs/) for detailed guides:
- [INSTALLATION.md](../docs/INSTALLATION.md) — setup and prerequisites
- [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md) — common issues
- [CONTRIBUTING.md](../docs/CONTRIBUTING.md) — contribution workflow
- [PROJECT_SUMMARY.md](../docs/PROJECT_SUMMARY.md) — component overview
- [Oura API specs](../docs/Oura%20API/) — OpenAPI 1.27/1.28 schemas
