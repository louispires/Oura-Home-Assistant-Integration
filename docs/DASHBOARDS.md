# Dashboard and Automation Examples

Ready-to-paste examples for the Oura Ring integration. Entity IDs are the defaults listed in the [Sensor Reference](SENSORS.md); adjust them if you renamed entities or have a second account (`_2` suffix).

Chart examples use [apexcharts-card](https://github.com/RomRider/apexcharts-card). Install it from HACS first.

## Contents

- ApexCharts cards: [Scores Overview](#scores-overview) · [Sleep Analysis](#sleep-analysis) · [Sleep Efficiency Trend](#sleep-efficiency-trend) · [Heart Health](#heart-health) · [Daily Activity](#daily-activity) · [Workout Summary](#workout-summary) · [Mindfulness and Tags](#mindfulness-and-tags) · [Temperature Deviation](#temperature-deviation)
- Built-in cards: [Daily History from Lifetime Counters](#daily-history-from-lifetime-counters) · [Rest Mode](#rest-mode) · [Summary Entities](#summary-entities) · [Score Gauges](#score-gauges)
- Automations: [Low Sleep Score Alert](#low-sleep-score-alert) · [Open Curtains After Latest Sleep](#open-curtains-after-latest-sleep)

## ApexCharts Cards

### Scores Overview

Sleep, readiness, and activity scores over the past week.

![Scores overview chart](https://github.com/user-attachments/assets/ddb7d8d6-6cab-417a-b596-5dd600f506ed)

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Oura Scores
  show_states: true
  colorize_states: true
graph_span: 7d
span:
  end: day
all_series_config:
  type: column
  opacity: 0.7
  stroke_width: 8
  group_by:
    func: last
    duration: 1d
series:
  - entity: sensor.oura_ring_sleep_score
    name: Sleep
    color: "#5E97F6"
  - entity: sensor.oura_ring_readiness_score
    name: Readiness
    color: "#FFA600"
  - entity: sensor.oura_ring_activity_score
    name: Activity
    color: "#00D9FF"
yaxis:
  - min: 0
    max: 100
    apex_config:
      tickAmount: 5
```

### Sleep Analysis

Sleep breakdown with durations.

![Sleep analysis chart](https://github.com/user-attachments/assets/a9731cbe-41f9-4d83-8648-98befd82f344)

```yaml
type: custom:apexcharts-card
graph_span: 7d
header:
  show: true
  show_states: true
  colorize_states: true
  title: Sleep
  standard_format: true
yaxis:
  - id: left
    opposite: false
    min: 0
    max: 10
    apex_config:
      title:
        text: Total Sleep
  - id: right
    opposite: true
    min: 0
    max: 8
    apex_config:
      title:
        text: Breakdown
series:
  - entity: sensor.oura_ring_sleep_score
    name: Score
    show:
      in_chart: false
    color: white
  - entity: sensor.oura_ring_average_heart_rate
    name: Avg HR
    show:
      in_chart: false
  - entity: sensor.oura_ring_minimum_heart_rate
    name: Lowest HR
    show:
      in_chart: false
  - entity: sensor.oura_ring_time_in_bed
    name: In Bed
    color: grey
    type: area
    show:
      in_chart: true
      in_header: false
    yaxis_id: left
    group_by:
      duration: 1d
      func: last
  - entity: sensor.oura_ring_total_sleep_duration
    name: Total Sleep
    color: purple
    type: area
    show:
      in_chart: true
      in_header: false
    yaxis_id: left
    group_by:
      duration: 1d
      func: last
  - entity: sensor.oura_ring_rem_sleep_duration
    name: REM
    color: "#20bf6b"
    type: column
    show:
      in_chart: true
      in_header: false
    yaxis_id: right
    group_by:
      duration: 1d
      func: last
  - entity: sensor.oura_ring_deep_sleep_duration
    name: Deep
    color: "#45aaf2"
    type: column
    show:
      in_chart: true
      in_header: false
    yaxis_id: right
    group_by:
      duration: 1d
      func: last
  - entity: sensor.oura_ring_light_sleep_duration
    name: Light
    color: "#fed330"
    type: column
    show:
      in_chart: true
      in_header: false
    yaxis_id: right
    group_by:
      duration: 1d
      func: last
  - entity: sensor.oura_ring_awake_time
    name: Awake
    color: "#fc5c65"
    type: column
    show:
      in_chart: true
      in_header: false
    yaxis_id: right
    group_by:
      duration: 1d
      func: last
```

### Sleep Efficiency Trend

![Sleep efficiency chart](https://github.com/user-attachments/assets/23d9d8cd-44ce-4944-8d21-292829208123)

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Sleep Efficiency
  show_states: true
graph_span: 14d
span:
  end: day
series:
  - entity: sensor.oura_ring_sleep_efficiency
    name: Efficiency
    color: '#4CAF50'
    stroke_width: 3
    type: line
    curve: smooth
    group_by:
      func: last
      duration: 1d
yaxis:
  - min: 0
    max: 100
    apex_config:
      tickAmount: 5
```

### Heart Health

Heart rate contributor scores and sleep HRV.

![Heart health chart](https://github.com/user-attachments/assets/57401ffc-988c-4912-a71a-a81f686739f5)

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Heart Health
  show_states: true
graph_span: 7d
span:
  end: day
series:
  - entity: sensor.oura_ring_resting_heart_rate_score
    name: Resting HR
    color: "#E91E63"
    stroke_width: 2
    type: line
    curve: smooth
    group_by:
      func: last
      duration: 1d
    yaxis_id: hr
  - entity: sensor.oura_ring_hrv_balance_score
    name: HRV Balance
    color: "#00BCD4"
    stroke_width: 2
    type: line
    curve: smooth
    group_by:
      func: last
      duration: 1d
    yaxis_id: hrv
  - entity: sensor.oura_ring_average_sleep_hrv
    name: Sleep HRV
    color: "#287233"
    stroke_width: 2
    type: line
    curve: smooth
    group_by:
      func: last
      duration: 1d
    yaxis_id: hrv
yaxis:
  - id: hr
    min: 40
    max: 80
    apex_config:
      tickAmount: 4
      title:
        text: BPM
  - id: hrv
    opposite: true
    min: 0
    max: 100
    apex_config:
      tickAmount: 4
      title:
        text: HRV
```

### Daily Activity

Steps and active calories.

![Daily activity chart](https://github.com/user-attachments/assets/675d862e-47dd-4772-a1c9-dab482d145ce)

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Daily Activity
  show_states: true
graph_span: 7d
span:
  end: day
series:
  - entity: sensor.oura_ring_steps
    name: Steps
    color: '#4CAF50'
    stroke_width: 2
    type: column
    opacity: 0.7
    group_by:
      func: last
      duration: 1d
    yaxis_id: steps
  - entity: sensor.oura_ring_active_calories
    name: Calories
    color: '#FF9800'
    stroke_width: 2
    type: line
    curve: smooth
    group_by:
      func: last
      duration: 1d
    yaxis_id: calories
yaxis:
  - id: steps
    apex_config:
      tickAmount: 4
      title:
        text: Steps
  - id: calories
    opposite: true
    apex_config:
      tickAmount: 4
      title:
        text: Calories
```

### Workout Summary

Workouts completed per day plus details from the latest workout.

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Workout Summary
  show_states: true
graph_span: 7d
span:
  end: day
series:
  - entity: sensor.oura_ring_workouts_today
    name: Workouts
    color: "#1E88E5"
    type: column
    opacity: 0.75
    group_by:
      func: last
      duration: 1d
    yaxis_id: count
  - entity: sensor.oura_ring_last_workout_duration
    name: Last Duration
    color: "#43A047"
    type: line
    curve: smooth
    stroke_width: 2
    group_by:
      func: last
      duration: 1d
    yaxis_id: minutes
  - entity: sensor.oura_ring_last_workout_calories
    name: Last Calories
    color: "#FB8C00"
    type: line
    curve: smooth
    stroke_width: 2
    group_by:
      func: last
      duration: 1d
    yaxis_id: calories
yaxis:
  - id: count
    min: 0
    apex_config:
      tickAmount: 4
      title:
        text: Workouts
  - id: minutes
    opposite: true
    min: 0
    apex_config:
      tickAmount: 4
      title:
        text: Minutes
  - id: calories
    opposite: true
    show: false
```

### Mindfulness and Tags

Mindfulness sessions, meditation time, and daily tags.

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Mindfulness and Tags
  show_states: true
graph_span: 14d
span:
  end: day
series:
  - entity: sensor.oura_ring_mindfulness_sessions_today
    name: Sessions
    color: "#8E24AA"
    type: column
    opacity: 0.75
    group_by:
      func: last
      duration: 1d
    yaxis_id: sessions
  - entity: sensor.oura_ring_meditation_duration_today
    name: Meditation (min)
    color: "#00897B"
    type: line
    curve: smooth
    stroke_width: 2
    group_by:
      func: last
      duration: 1d
    yaxis_id: minutes
  - entity: sensor.oura_ring_tag_count_today
    name: Tags
    color: "#F4511E"
    type: line
    curve: smooth
    stroke_width: 2
    group_by:
      func: last
      duration: 1d
    yaxis_id: tags
yaxis:
  - id: sessions
    min: 0
    apex_config:
      tickAmount: 4
      title:
        text: Sessions
  - id: minutes
    opposite: true
    min: 0
    apex_config:
      tickAmount: 4
      title:
        text: Minutes
  - id: tags
    opposite: true
    show: false
```

### Temperature Deviation

![Temperature deviation chart](https://github.com/user-attachments/assets/bb79c360-90c9-45b0-ac33-a96f7cc2ae9c)

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Temperature Deviation
  show_states: true
graph_span: 30d
span:
  end: day
series:
  - entity: sensor.oura_ring_temperature_deviation
    name: Deviation
    color: '#FF5722'
    stroke_width: 2
    type: line
    curve: smooth
    group_by:
      func: last
      duration: 1d
yaxis:
  - min: -2
    max: 2
    apex_config:
      tickAmount: 4
      decimalsInFloat: 1
```

## Built-in Cards

### Daily History from Lifetime Counters

The `Lifetime …` sensors carry the full imported history of the daily sums. The `change` of a lifetime counter per day, week, or month is that period's total, late-synced data included.

```yaml
type: statistics-graph
title: Steps per Day
entities:
  - sensor.oura_ring_lifetime_steps
stat_types:
  - change
period: day
days_to_show: 30
chart_type: bar
```

Use `period: week` or `period: month` for longer views, and swap in `sensor.oura_ring_lifetime_active_calories`, `sensor.oura_ring_lifetime_total_sleep_duration`, etc.

### Rest Mode

Current rest mode status with the active window from Oura.

```yaml
type: entities
title: Rest Mode
entities:
  - entity: binary_sensor.oura_ring_rest_mode
    name: Rest Mode Active
  - entity: sensor.oura_ring_rest_mode_start
    name: Rest Mode Start
  - entity: sensor.oura_ring_rest_mode_end
    name: Rest Mode End
```

### Summary Entities

A quick overview without ApexCharts.

![Summary entities card](https://github.com/user-attachments/assets/ac3462db-f6a0-417d-b1f4-cca43335e4cd)

```yaml
type: entities
title: Oura Ring Summary
entities:
  - entity: sensor.oura_ring_sleep_score
    secondary_info: last-changed
    name: Sleep Score
  - entity: sensor.oura_ring_readiness_score
    secondary_info: last-changed
    name: Readiness Score
  - entity: sensor.oura_ring_activity_score
    secondary_info: last-changed
    name: Activity Score
  - type: divider
  - entity: sensor.oura_ring_total_sleep_duration
    secondary_info: last-changed
    name: Total Sleep
  - entity: sensor.oura_ring_time_in_bed
    name: Time in Bed
    secondary_info: last-changed
  - entity: sensor.oura_ring_deep_sleep_duration
    secondary_info: last-changed
    name: Deep Sleep
  - entity: sensor.oura_ring_rem_sleep_duration
    secondary_info: last-changed
    name: REM Sleep
  - type: divider
  - entity: sensor.oura_ring_steps
    secondary_info: last-changed
    name: Steps Today
  - entity: sensor.oura_ring_active_calories
    secondary_info: last-changed
    name: Active Calories
  - entity: sensor.oura_ring_workouts_today
    secondary_info: last-changed
    name: Workouts Today
  - entity: sensor.oura_ring_mindfulness_sessions_today
    secondary_info: last-changed
    name: Mindfulness Sessions
  - entity: sensor.oura_ring_tag_count_today
    secondary_info: last-changed
    name: Tags Today
  - entity: binary_sensor.oura_ring_rest_mode
    secondary_info: last-changed
    name: Rest Mode
  - entity: sensor.oura_ring_current_heart_rate
    secondary_info: last-changed
  - entity: sensor.oura_ring_average_heart_rate
    secondary_info: last-changed
  - entity: sensor.oura_ring_minimum_heart_rate
    secondary_info: last-changed
  - entity: sensor.oura_ring_maximum_heart_rate
    secondary_info: last-changed
```

### Score Gauges

![Score gauges](https://github.com/user-attachments/assets/bc8666fd-856c-4fd5-b05e-68e587b6b2ce)

```yaml
type: horizontal-stack
cards:
  - type: gauge
    entity: sensor.oura_ring_sleep_score
    name: Sleep
    needle: true
    min: 0
    max: 100
    severity:
      green: 85
      yellow: 70
      red: 0
  - type: gauge
    entity: sensor.oura_ring_readiness_score
    name: Readiness
    needle: true
    min: 0
    max: 100
    severity:
      green: 85
      yellow: 70
      red: 0
  - type: gauge
    entity: sensor.oura_ring_activity_score
    name: Activity
    needle: true
    min: 0
    max: 100
    severity:
      green: 85
      yellow: 70
      red: 0
```

## Automations

### Low Sleep Score Alert

```yaml
automation:
  - alias: "Low Sleep Alert"
    triggers:
      - trigger: numeric_state
        entity_id: sensor.oura_ring_sleep_score
        below: 70
    actions:
      - action: notify.mobile_app
        data:
          message: "Your sleep score is low. Consider resting today."
```

### Open Curtains After Latest Sleep

Opens the curtains 8 hours after the most recent sleep session (including naps) started. **Latest Bedtime Start** updates as soon as Oura exposes a new session, independent of the primary-bedtime logic.

```yaml
automation:
  - alias: "Open Curtains After Latest Sleep"
    triggers:
      - trigger: template
        value_template: |
          {% set latest_start = states('sensor.oura_ring_latest_bedtime_start') %}
          {% if latest_start not in ['unknown', 'unavailable', 'none', 'None', ''] %}
            {{ (as_timestamp(now()) - as_timestamp(latest_start)) >= 28800 }}
          {% else %}
            false
          {% endif %}
    actions:
      - action: cover.open_cover
        target:
          entity_id: cover.bedroom_curtains
```
