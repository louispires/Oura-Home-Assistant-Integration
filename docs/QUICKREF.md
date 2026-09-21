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

- **Sensors**: 71
- **Binary sensors**: 2
- **Total entities**: 73

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
sensor.oura_ring_met_min_high
sensor.oura_ring_met_min_medium
sensor.oura_ring_met_min_low
```

### Heart / Recovery

```text
sensor.oura_ring_current_heart_rate
sensor.oura_ring_average_heart_rate
sensor.oura_ring_min_heart_rate
sensor.oura_ring_max_heart_rate
sensor.oura_ring_heart_rate_timestamp
sensor.oura_ring_average_sleep_hrv
```

### Workout / Session / Tag / Rest Mode

```text
sensor.oura_ring_workouts_today
sensor.oura_ring_last_workout_type
sensor.oura_ring_last_workout_distance
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
```

For the complete list, see [README.md](../README.md#available-sensors).

## Statistics Reconciliation

To backfill late-arriving data into long-term statistics:

```yaml
service: oura.reconcile_statistics
data:
  days: 14  # optional
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

- **Integration Version**: 2.9.0
- **Test Suite Status**: 132 passing tests (latest full Docker run)
- **API Version**: Oura v2

## Support

- **Installation Guide**: [INSTALLATION.md](INSTALLATION.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Issues**: <https://github.com/louispires/oura-v2-custom-component/issues>
