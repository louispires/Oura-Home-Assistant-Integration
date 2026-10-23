# Sensor Reference

The integration creates **117 sensors and 2 binary sensors** on one **Oura Ring** device per account.

- Entity IDs below are the defaults. A second Oura account gets a `_2` suffix, and renamed entities keep whatever ID you gave them.
- **Diagnostic** sensors appear in the device page's *Diagnostic* section and are left out of auto-generated dashboards.
- ⚠️ marks sensors that are often **unavailable** for new rings or accounts without the feature. Oura sends no value until it has enough baseline data, or the feature isn't available for your ring/membership. See [Troubleshooting](TROUBLESHOOTING.md#sensors-missing-or-unavailable).
- Every sensor exposes a `data_date` attribute (the Oura day the value belongs to) when available.

## Contents

- [Sleep](#sleep-27)
- [Readiness](#readiness-12)
- [Activity](#activity-23)
- [Heart Rate and HRV](#heart-rate-and-hrv-8)
- [Stress and Resilience](#stress-and-resilience-7)
- [SpO2 and Cardio Fitness](#spo2-and-cardio-fitness-5)
- [Sleep Optimization](#sleep-optimization-2)
- [Workouts](#workouts-7)
- [Sessions and Tags](#sessions-and-tags-4)
- [Rest Mode and Ring](#rest-mode-and-ring-3)
- [Lifetime Counters](#lifetime-counters-19)
- [Binary Sensors](#binary-sensors-2)

## Sleep (27)

| Sensor | Entity ID | Unit | Notes |
| --- | --- | --- | --- |
| Sleep Score | `sensor.oura_ring_sleep_score` | | |
| Total Sleep Duration | `sensor.oura_ring_total_sleep_duration` | h | |
| Deep Sleep Duration | `sensor.oura_ring_deep_sleep_duration` | h | |
| REM Sleep Duration | `sensor.oura_ring_rem_sleep_duration` | h | |
| Light Sleep Duration | `sensor.oura_ring_light_sleep_duration` | h | |
| Awake Time | `sensor.oura_ring_awake_time` | h | |
| Sleep Efficiency | `sensor.oura_ring_sleep_efficiency` | % | Actual efficiency percentage, not the contributor score |
| Restfulness | `sensor.oura_ring_restfulness` | % | |
| Sleep Latency | `sensor.oura_ring_sleep_latency` | min | |
| Sleep Timing | `sensor.oura_ring_sleep_timing` | | |
| Deep Sleep Contribution | `sensor.oura_ring_deep_sleep_contribution` | | Sleep score contributor (1-100) |
| REM Sleep Contribution | `sensor.oura_ring_rem_sleep_contribution` | | Sleep score contributor (1-100) |
| Total Sleep Contribution | `sensor.oura_ring_total_sleep_contribution` | | Sleep score contributor (1-100) |
| Sleep Latency Contribution | `sensor.oura_ring_sleep_latency_contribution` | | Sleep score contributor (1-100) |
| Deep Sleep Percentage | `sensor.oura_ring_deep_sleep_percentage` | % | Diagnostic |
| REM Sleep Percentage | `sensor.oura_ring_rem_sleep_percentage` | % | Diagnostic |
| Time in Bed | `sensor.oura_ring_time_in_bed` | h | |
| Bedtime Start | `sensor.oura_ring_bedtime_start` | | Timestamp; primary sleep (prefers `long_sleep`) |
| Bedtime End | `sensor.oura_ring_bedtime_end` | | Timestamp; primary sleep (prefers `long_sleep`) |
| Latest Bedtime Start | `sensor.oura_ring_latest_bedtime_start` | | Timestamp; most recent session, including naps |
| Latest Bedtime End | `sensor.oura_ring_latest_bedtime_end` | | Timestamp; unavailable while the latest session is still in progress |
| Average Breathing Rate | `sensor.oura_ring_average_breathing_rate` | breaths/min | |
| Restless Periods | `sensor.oura_ring_restless_periods` | | Diagnostic |
| Sleep Score Delta | `sensor.oura_ring_sleep_score_delta` | | Diagnostic; effect of this sleep period on the sleep score |
| Readiness Score Delta | `sensor.oura_ring_readiness_score_delta` | | Diagnostic; effect of this sleep period on the readiness score |
| Low Battery Alert | `sensor.oura_ring_low_battery_alert` | | Diagnostic; `true` if the ring hit low battery during sleep |
| Sleep Analysis Reason | `sensor.oura_ring_sleep_analysis_reason` | | Diagnostic; `foreground_sleep_analysis`, `bedtime_edit`, `background_sleep_analysis`, `background_created_foreground_updated` |

## Readiness (12)

| Sensor | Entity ID | Unit | Notes |
| --- | --- | --- | --- |
| Readiness Score | `sensor.oura_ring_readiness_score` | | |
| Temperature Deviation | `sensor.oura_ring_temperature_deviation` | °C | |
| Temperature Trend Deviation | `sensor.oura_ring_temperature_trend_deviation` | °C | |
| Resting Heart Rate Score | `sensor.oura_ring_resting_heart_rate_score` | | Contributor score, not BPM; may be unavailable without enough data |
| HRV Balance Score | `sensor.oura_ring_hrv_balance_score` | | Contributor score, not HRV; may be unavailable without enough data |
| Sleep Regularity Score | `sensor.oura_ring_sleep_regularity_score` | | Contributor score; may be unavailable without enough data |
| Activity Balance Contribution | `sensor.oura_ring_activity_balance_contribution` | | Readiness contributor (1-100) |
| Body Temperature Contribution | `sensor.oura_ring_body_temperature_contribution` | | Readiness contributor (1-100) |
| Previous Day Activity Contribution | `sensor.oura_ring_previous_day_activity_contribution` | | Readiness contributor (1-100) |
| Previous Night Contribution | `sensor.oura_ring_previous_night_contribution` | | Readiness contributor (1-100) |
| Recovery Index Contribution | `sensor.oura_ring_recovery_index_contribution` | | Readiness contributor (1-100) |
| Sleep Balance Contribution | `sensor.oura_ring_sleep_balance_contribution` | | Readiness contributor (1-100) |

## Activity (23)

| Sensor | Entity ID | Unit | Notes |
| --- | --- | --- | --- |
| Activity Score | `sensor.oura_ring_activity_score` | | |
| Steps | `sensor.oura_ring_steps` | steps | |
| Active Calories | `sensor.oura_ring_active_calories` | kcal | |
| Total Calories | `sensor.oura_ring_total_calories` | kcal | |
| Target Calories | `sensor.oura_ring_target_calories` | kcal | Diagnostic |
| Target Distance | `sensor.oura_ring_target_distance` | m | Diagnostic |
| Equivalent Walking Distance | `sensor.oura_ring_equivalent_walking_distance` | m | |
| High Activity MET Minutes | `sensor.oura_ring_high_activity_met_minutes` | | |
| Medium Activity MET Minutes | `sensor.oura_ring_medium_activity_met_minutes` | | |
| Low Activity MET Minutes | `sensor.oura_ring_low_activity_met_minutes` | | |
| High Activity Time | `sensor.oura_ring_high_activity_time` | min | |
| Medium Activity Time | `sensor.oura_ring_medium_activity_time` | min | |
| Low Activity Time | `sensor.oura_ring_low_activity_time` | min | |
| Resting Time | `sensor.oura_ring_resting_time` | min | |
| Sedentary Time | `sensor.oura_ring_sedentary_time` | min | |
| Ring Non-Wear Time | `sensor.oura_ring_ring_non_wear_time` | min | Diagnostic |
| Inactivity Alerts | `sensor.oura_ring_inactivity_alerts` | | Diagnostic |
| Meet Daily Targets Contribution | `sensor.oura_ring_meet_daily_targets_contribution` | | Activity contributor (1-100) |
| Move Every Hour Contribution | `sensor.oura_ring_move_every_hour_contribution` | | Activity contributor (1-100) |
| Recovery Time Contribution | `sensor.oura_ring_recovery_time_contribution` | | Activity contributor (1-100) |
| Stay Active Contribution | `sensor.oura_ring_stay_active_contribution` | | Activity contributor (1-100) |
| Training Frequency Contribution | `sensor.oura_ring_training_frequency_contribution` | | Activity contributor (1-100) |
| Training Volume Contribution | `sensor.oura_ring_training_volume_contribution` | | Activity contributor (1-100) |

## Heart Rate and HRV (8)

Heart rate comes from readings synced to the Oura cloud, not live Bluetooth readings. Check **Last Heart Rate Reading** to see how fresh the data is.

| Sensor | Entity ID | Unit | Notes |
| --- | --- | --- | --- |
| Current Heart Rate | `sensor.oura_ring_current_heart_rate` | bpm | Latest synced reading |
| Average Heart Rate | `sensor.oura_ring_average_heart_rate` | bpm | Last 24 h (falls back to the last 10 readings) |
| Minimum Heart Rate | `sensor.oura_ring_minimum_heart_rate` | bpm | Diagnostic; last 24 h |
| Maximum Heart Rate | `sensor.oura_ring_maximum_heart_rate` | bpm | Diagnostic; last 24 h |
| Last Heart Rate Reading | `sensor.oura_ring_last_heart_rate_reading` | | Diagnostic; timestamp of the latest reading |
| Lowest Sleep Heart Rate | `sensor.oura_ring_lowest_sleep_heart_rate` | bpm | |
| Average Sleep Heart Rate | `sensor.oura_ring_average_sleep_heart_rate` | bpm | |
| Average Sleep HRV | `sensor.oura_ring_average_sleep_hrv` | ms | |

## Stress and Resilience (7)

| Sensor | Entity ID | Unit | Notes |
| --- | --- | --- | --- |
| Stress High Duration | `sensor.oura_ring_stress_high_duration` | min | ⚠️ |
| Recovery High Duration | `sensor.oura_ring_recovery_high_duration` | min | ⚠️ |
| Stress Day Summary | `sensor.oura_ring_stress_day_summary` | | ⚠️ `restored`, `normal`, `stressful` |
| Resilience Level | `sensor.oura_ring_resilience_level` | | `limited`, `adequate`, `solid`, `strong`, `exceptional` |
| Sleep Recovery Score | `sensor.oura_ring_sleep_recovery_score` | | ⚠️ |
| Daytime Recovery Score | `sensor.oura_ring_daytime_recovery_score` | | ⚠️ |
| Stress Resilience Score | `sensor.oura_ring_stress_resilience_score` | | ⚠️ |

## SpO2 and Cardio Fitness (5)

SpO2 needs a Gen 3, Ring 4, or Ring 5. VO2 Max, Cardiovascular Age, and Pulse Wave Velocity need an Oura membership.

| Sensor | Entity ID | Unit | Notes |
| --- | --- | --- | --- |
| SpO2 Average | `sensor.oura_ring_spo2_average` | % | |
| Breathing Disturbance Index | `sensor.oura_ring_breathing_disturbance_index` | | Diagnostic |
| VO2 Max | `sensor.oura_ring_vo2_max` | ml/kg/min | ⚠️ |
| Cardiovascular Age | `sensor.oura_ring_cardiovascular_age` | years | ⚠️ |
| Pulse Wave Velocity | `sensor.oura_ring_pulse_wave_velocity` | m/s | ⚠️ Arterial stiffness |

## Sleep Optimization (2)

| Sensor | Entity ID | Unit | Notes |
| --- | --- | --- | --- |
| Optimal Bedtime Start | `sensor.oura_ring_optimal_bedtime_start` | | Diagnostic; ⚠️ timestamp |
| Optimal Bedtime End | `sensor.oura_ring_optimal_bedtime_end` | | Diagnostic; ⚠️ timestamp |

## Workouts (7)

`last_workout_*` sensors keep their last value when no new workout is in the polling window, and expose the raw latest workout in a `workout` attribute.

| Sensor | Entity ID | Unit | Notes |
| --- | --- | --- | --- |
| Workouts Today | `sensor.oura_ring_workouts_today` | | `workouts` attribute lists today's workouts |
| Last Workout Type | `sensor.oura_ring_last_workout_type` | | Oura activity name, e.g. `running` |
| Last Workout Distance | `sensor.oura_ring_last_workout_distance` | m | |
| Last Workout Calories | `sensor.oura_ring_last_workout_calories` | kcal | |
| Last Workout Intensity | `sensor.oura_ring_last_workout_intensity` | | `easy`, `moderate`, `hard` |
| Last Workout Duration | `sensor.oura_ring_last_workout_duration` | min | |
| Last Workout Source | `sensor.oura_ring_last_workout_source` | | Diagnostic; `manual`, `autodetected`, `confirmed`, `workout_heart_rate`, `live_third_party_heart_rate`, `live_oura_heart_rate` |

## Sessions and Tags (4)

| Sensor | Entity ID | Unit | Notes |
| --- | --- | --- | --- |
| Mindfulness Sessions Today | `sensor.oura_ring_mindfulness_sessions_today` | | Meditation, breathing, and rest sessions |
| Meditation Duration Today | `sensor.oura_ring_meditation_duration_today` | min | Total length of today's mindfulness sessions |
| Tags Today | `sensor.oura_ring_tags_today` | | Comma-separated tags; `tags` and `enhanced_tags` attributes |
| Tag Count Today | `sensor.oura_ring_tag_count_today` | | Number of distinct tags today |

## Rest Mode and Ring (3)

| Sensor | Entity ID | Unit | Notes |
| --- | --- | --- | --- |
| Rest Mode Start | `sensor.oura_ring_rest_mode_start` | | Timestamp of the active rest mode period |
| Rest Mode End | `sensor.oura_ring_rest_mode_end` | | Timestamp of the active rest mode period |
| Ring Battery Level | `sensor.oura_ring_ring_battery_level` | % | Diagnostic |

## Lifetime Counters (19)

Never-resetting totals of the daily sums: the sum of every day since the start of the imported history, plus today so far. The imported history lives in these counters' long-term statistics, so a `statistics-graph` card with `stat_types: change` shows each day's, week's, or month's total ([example](DASHBOARDS.md#daily-history-from-lifetime-counters)). Data Oura syncs late is moved onto the day it belongs to.

The daily sensors they are based on (Steps, Active Calories, …) start a new cycle every Oura day; their own statistics only cover the time Home Assistant recorded them.

| Sensor | Entity ID | Unit | Notes |
| --- | --- | --- | --- |
| Lifetime Total Sleep Duration | `sensor.oura_ring_lifetime_total_sleep_duration` | h | Naps included |
| Lifetime Deep Sleep Duration | `sensor.oura_ring_lifetime_deep_sleep_duration` | h | |
| Lifetime REM Sleep Duration | `sensor.oura_ring_lifetime_rem_sleep_duration` | h | |
| Lifetime Light Sleep Duration | `sensor.oura_ring_lifetime_light_sleep_duration` | h | |
| Lifetime Awake Time | `sensor.oura_ring_lifetime_awake_time` | h | |
| Lifetime Time in Bed | `sensor.oura_ring_lifetime_time_in_bed` | h | |
| Lifetime Steps | `sensor.oura_ring_lifetime_steps` | steps | |
| Lifetime Active Calories | `sensor.oura_ring_lifetime_active_calories` | kcal | |
| Lifetime Total Calories | `sensor.oura_ring_lifetime_total_calories` | kcal | |
| Lifetime High Activity MET Minutes | `sensor.oura_ring_lifetime_high_activity_met_minutes` | | |
| Lifetime Medium Activity MET Minutes | `sensor.oura_ring_lifetime_medium_activity_met_minutes` | | |
| Lifetime Low Activity MET Minutes | `sensor.oura_ring_lifetime_low_activity_met_minutes` | | |
| Lifetime Inactivity Alerts | `sensor.oura_ring_lifetime_inactivity_alerts` | | Diagnostic |
| Lifetime Ring Non-Wear Time | `sensor.oura_ring_lifetime_ring_non_wear_time` | min | Diagnostic |
| Lifetime Resting Time | `sensor.oura_ring_lifetime_resting_time` | min | |
| Lifetime Sedentary Time | `sensor.oura_ring_lifetime_sedentary_time` | min | |
| Lifetime Equivalent Walking Distance | `sensor.oura_ring_lifetime_equivalent_walking_distance` | m | |
| Lifetime Stress High Duration | `sensor.oura_ring_lifetime_stress_high_duration` | min | ⚠️ |
| Lifetime Recovery High Duration | `sensor.oura_ring_lifetime_recovery_high_duration` | min | ⚠️ |

## Binary Sensors (2)

| Sensor | Entity ID | Notes |
| --- | --- | --- |
| Rest Mode | `binary_sensor.oura_ring_rest_mode` | On during an active rest mode period; `id`, `start_day`, `end_day` attributes |
| Ring Charging | `binary_sensor.oura_ring_ring_charging` | On while the ring is charging |
