# Quick Reference Guide

## Configuration URLs

- **Oura Developer Portal**: <https://developer.ouraring.com>
- **OAuth Applications**: <https://developer.ouraring.com/applications>
- **API Documentation**: <https://cloud.ouraring.com/v2/docs>

## Home Assistant Paths

- **Application Credentials**: Settings -> Devices & Services -> Application Credentials
- **Add Integration**: Settings -> Devices & Services -> Add Integration
- **Configure Integration Options**: Settings -> Devices & Services -> Oura Ring -> Configure
- **Logs**: Settings -> System -> Logs
- **Developer Tools**: Developer Tools -> States

## Redirect URI (Important)

Use this exact URI in Oura app settings:

```text
https://my.home-assistant.io/redirect/oauth
```

Do **not** register your local URL, DuckDNS URL, or Nabu Casa URL as Redirect URI for this integration.

## Required OAuth Scopes

- `email`
- `personal`
- `daily`
- `heartrate`
- `workout`
- `session`
- `tag`
- `spo2`
- `ring_configuration`
- `stress`
- `heart_health`

## Entity Summary

- **Sensors**: 99
- **Binary sensors**: 2
- **Total entities**: 100

## Key Entity IDs

### Sleep

```text
sensor.oura_ring_sleep_score
sensor.oura_ring_bedtime_start
sensor.oura_ring_bedtime_end
sensor.oura_ring_latest_bedtime_start
sensor.oura_ring_latest_bedtime_end
sensor.oura_ring_sleep_analysis_reason
sensor.oura_ring_low_battery_alert
```

### Readiness / Activity

```text
sensor.oura_ring_readiness_score
sensor.oura_ring_temperature_deviation
sensor.oura_ring_activity_score
sensor.oura_ring_steps
sensor.oura_ring_active_calories
sensor.oura_ring_total_calories
sensor.oura_ring_target_calories
sensor.oura_ring_high_activity_met_minutes
sensor.oura_ring_medium_activity_met_minutes
sensor.oura_ring_low_activity_met_minutes
```

### Heart / Recovery

```text
sensor.oura_ring_current_heart_rate
sensor.oura_ring_average_heart_rate
sensor.oura_ring_minimum_heart_rate
sensor.oura_ring_maximum_heart_rate
sensor.oura_ring_last_heart_rate_reading
sensor.oura_ring_average_sleep_hrv
```

### Workout / Session / Tag / Rest Mode

```text
sensor.oura_ring_workouts_today
sensor.oura_ring_last_workout_type
sensor.oura_ring_last_workout_distance
sensor.oura_ring_last_workout_source
sensor.oura_ring_mindfulness_sessions_today
sensor.oura_ring_meditation_duration_today
sensor.oura_ring_tags_today
sensor.oura_ring_tag_count_today
sensor.oura_ring_rest_mode_start
sensor.oura_ring_rest_mode_end
binary_sensor.oura_ring_rest_mode
binary_sensor.oura_ring_ring_charging
```

### Ring Battery

```text
sensor.oura_ring_ring_battery_level
sensor.oura_ring_ring_last_sync
```

For the complete list, see the [Sensor Reference](SENSORS.md).

## Statistics Reconciliation

To backfill late-arriving data into long-term statistics:

```yaml
action: oura.reconcile_statistics
data:
  days: 14  # optional, 1-1440
```

Also configurable via integration options: **Statistics Reconcile Window**.

## Test Commands

```bash
# Full suite

docker compose -f docker-compose.test.yml run --rm test

# Single file

docker compose -f docker-compose.test.yml run --rm test pytest tests/test_sensor.py -v
```

## Version Information

- **Integration Version**: 2.11.0
- **Minimum Home Assistant**: 2026.3.0
- **Test Suite Status**: 192 passing tests (latest full Docker run)
- **API Version**: Oura v2 (OpenAPI spec 1.41)

## Support

- **Installation Guide**: [INSTALLATION.md](INSTALLATION.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Issues**: <https://github.com/louispires/Oura-Home-Assistant-Integration/issues>
