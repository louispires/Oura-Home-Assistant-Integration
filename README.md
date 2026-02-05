# Oura Ring v2 Custom Component for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/louispires/oura-v2-custom-component/validate.yml?logo=github&label=HACS%20validate)](https://github.com/louispires/oura-v2-custom-component/actions/workflows/validate.yml)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/louispires/oura-v2-custom-component/validate.yml?logo=github&label=HASSFEST%20validate)](https://github.com/louispires/oura-v2-custom-component/actions/workflows/validate.yml)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow.svg)](https://buymeacoffee.com/louispires)

A modern Home Assistant custom integration for Oura Ring using the v2 API with OAuth2 authentication.

## Features

- **OAuth2 Authentication**: Secure authentication using Home Assistant's application credentials
- **Comprehensive Data**: 49 sensors covering all Oura Ring metrics including sleep, readiness, activity, stress, resilience, and more
- **HA 2025.11 Compliant**: Modern entity naming, translation keys, entity categories, and proper state classes
- **Historical Data Loading**: Automatically loads 3 months of historical data on first setup (configurable 1-48 months, up to 4 years)
- **Entity Categories**: Diagnostic sensors properly categorized for better UI organization
- **Multi-Account Support**: Entry-scoped unique IDs allow multiple Oura accounts
- **HACS Compatible**: Easy installation and updates via HACS
- **Modern Architecture**: Configuration-driven design following latest Home Assistant standards
- **Comprehensive Testing**: 50 automated tests ensuring reliability
- **Efficient Updates**: Uses DataUpdateCoordinator with specialized processing methods

## Available Sensors

### Sleep Sensors (16)
- Sleep Score
- Total Sleep Duration
- Deep Sleep Duration
- REM Sleep Duration
- Light Sleep Duration
- Awake Time
- Sleep Efficiency
- Restfulness
- Sleep Latency
- Sleep Timing
- Deep Sleep Percentage
- REM Sleep Percentage
- Time in Bed
- Bedtime Start (when you went to sleep)
- Bedtime End (when you woke up)
- Low Battery Alert

### Readiness Sensors (5)
- Readiness Score
- Temperature Deviation
- Resting Heart Rate Score (contribution score, not actual BPM)*
- HRV Balance Score (contribution score, not actual HRV)*
- Sleep Regularity Score (contribution score for sleep schedule consistency)*

**Note**: Sensors marked with * may be unavailable if Oura doesn't have sufficient data to calculate the contributor score.

### Activity Sensors (8)
- Activity Score
- Steps
- Active Calories
- Total Calories
- Target Calories
- High Activity Time
- Medium Activity Time
- Low Activity Time

### Heart Rate Sensors (6)
- Current Heart Rate (latest reading)
- Average Heart Rate (from recent readings)
- Minimum Heart Rate (from recent readings)
- Maximum Heart Rate (from recent readings)
- Lowest Sleep Heart Rate (lowest heart rate during sleep)
- Average Sleep Heart Rate (average heart rate during sleep)

### HRV Sensors (1)
- Average Sleep HRV (heart rate variability during sleep)

### Stress Sensors (3) - *May be unavailable for new rings*
- Stress High Duration ⚠️
- Recovery High Duration ⚠️
- Stress Day Summary ⚠️

### Resilience Sensors (4) - *May be unavailable for new rings*
- Resilience Level
- Sleep Recovery Score ⚠️
- Daytime Recovery Score ⚠️
- Stress Resilience Score ⚠️

### SpO2 Sensors (2) - *Gen3/Ring4 only*
- SpO2 Average
- Breathing Disturbance Index

### Fitness Sensors (2) - *May be unavailable for new rings*
- VO2 Max ⚠️
- Cardiovascular Age ⚠️

### Sleep Optimization Sensors (2) - *May be unavailable for new rings*
- Optimal Bedtime Start ⚠️
- Optimal Bedtime End ⚠️

**Total: 49 sensors**

**Important Notes**:
- Sensors marked with ⚠️ may be **unavailable** for new Oura Ring users (typically the first few weeks of usage). The Oura API does not provide data for these sensors until sufficient baseline data has been collected. This is normal behavior and they may become available over time as you continue using your ring.
- Some sensors marked with feature requirements may return 401 Unauthorized errors if your Oura account/ring doesn't have access to those features.
- The integration will continue to work with all available sensors - unavailable sensors simply won't display values until Oura provides data for them.

## Installation

### HACS Installation (Recommended)

**Oura Ring is now available in the HACS default repository!**

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Search for "Oura Ring"
4. Click "Download"
5. Restart Home Assistant

### Add Integration to Home Assistant

[![Open your Home Assistant instance and start the Oura Ring integration setup.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=oura)

**Click the button above** to add the Oura Ring integration to your Home Assistant instance.

### Manual Installation

1. Copy the `custom_components/oura` directory to your `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

### Step 1: Create Oura Application

1. Go to [Oura Cloud](https://developer.ouraring.com/applications)
2. Sign in with your Oura account
3. Click "Create a New Application"
4. Fill in the application details:
   - **Application Name**: Home Assistant
   - **Application Website**: Your Home Assistant URL
   - **Redirect URI**: `https://my.home-assistant.io/redirect/oauth`
5. Save the **Client ID** and **Client Secret**

### Step 2: Configure Application Credentials in Home Assistant

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click on **Application Credentials** (in the top menu)
3. Click **Add Application Credential**
4. **Note**: You may see either a dropdown to select "Oura Ring" OR a generic form - both work!
5. Enter your **Client ID** and **Client Secret** from Step 1
6. Click **Create**

**Important**: Application Credentials is just for storing OAuth credentials. You won't see Oura Ring listed as an active integration here.

### Step 3: Add Oura Ring Integration

**Now** you can add the actual integration:

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Oura Ring" - **you should see it here!**
4. Click on it and follow the OAuth2 authentication flow
5. You'll be redirected to Oura's website to authorize the integration
6. After authorization, you'll be redirected back to Home Assistant
7. The integration will be configured and sensors will start appearing

## Usage

Once configured, sensors will appear under the Oura Ring integration. You can use these sensors in:

- **Dashboards**: Display your sleep, readiness, and activity data with beautiful charts
- **Automations**: Trigger actions based on your Oura Ring data
- **Scripts**: Use sensor values in your scripts
- **Templates**: Create custom sensors based on Oura data

For dashboard examples using ApexCharts, see the [Dashboard Examples](#dashboard-examples) section below.

### Example Automation

```yaml
automation:
  - alias: "Low Sleep Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.oura_ring_sleep_score
        below: 70
    action:
      - service: notify.mobile_app
        data:
          message: "Your sleep score is low. Consider resting today."
```

## Data Update Frequency

The integration polls the Oura API with a configurable update interval (default: 5 minutes). You can configure this interval:

1. Go to **Settings** → **Devices & Services**
2. Find "Oura Ring" and click **CONFIGURE**
3. Set your desired update interval (1-60 minutes)
4. Set historical data months (1-48 months, default: 3 months) - **only loaded on first setup**
5. **Historical Data Imported**: Keep checked to prevent re-importing history. Uncheck to force re-import on next restart.
6. Click **SUBMIT**

The integration will automatically reload with the new interval. The default 5-minute interval is optimized to:
- Provide timely updates
- Minimize API calls
- Respect Oura's rate limits

### Historical Data Loading

On **first setup**, the integration automatically fetches historical data (default: 3 months) to populate your dashboards immediately. This means:

✅ **Instant dashboard population** - Your charts show data from day one  
✅ **No waiting period** - See trends and patterns immediately  
✅ **One-time fetch** - Historical data is only loaded once during initial setup  
✅ **Configurable** - Choose 1-48 months of history based on your needs (up to 4 years)  

After the initial historical load, the integration fetches only new data during regular updates (every 5 minutes by default), keeping API usage minimal.

#### How It Works

The integration uses Home Assistant's **Long-Term Statistics** system to store historical data:

1. **Initial Setup**: When you first add the integration, it fetches 3 months (or your configured amount) of historical data
2. **Statistics Import**: All historical data points are imported as long-term statistics with proper timestamps
3. **Database Storage**: Data is stored in Home Assistant's statistics database (separate from state history)
4. **Immediate Availability**: All history graphs, ApexCharts, and Energy dashboard cards can access this data immediately
5. **Daily Updates**: Ongoing updates only fetch new data (typically 1 day), which is much more efficient

**Benefits of Long-Term Statistics**:
- 📊 Works with all history visualization cards (ApexCharts, History Graph, Statistics Graph)
- 💾 Efficient database storage (optimized for long-term data)
- 🔄 Properly timestamped (each data point has the correct historical date)
- ⚡ Fast queries (statistics database is optimized for time-series data)
- 🎯 No fake "state changes" - clean, accurate historical data

## Dashboard Examples

### Using ApexCharts Card

The [apexcharts-card](https://github.com/RomRider/apexcharts-card) is a highly customizable graphing card that works great with Oura data. Install it via HACS first.

#### Scores Overview Card

Track your sleep, readiness, and activity scores over the past week:
<img width="947" height="804" alt="image" src="https://github.com/user-attachments/assets/ddb7d8d6-6cab-417a-b596-5dd600f506ed" />

<details>
<summary>yaml</summary>
   
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
</details>

#### Sleep Analysis Card

Detailed sleep breakdown with durations:
<img width="2904" height="1243" alt="image" src="https://github.com/user-attachments/assets/a9731cbe-41f9-4d83-8648-98befd82f344" />
<details>
<summary>yaml</summary>

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
</details>

#### Sleep Efficiency Trend

Monitor your sleep efficiency over time:
<img width="945" height="797" alt="image" src="https://github.com/user-attachments/assets/23d9d8cd-44ce-4944-8d21-292829208123" />
<details>
<summary>yaml</summary>
   
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
</details>

#### Heart Rate Monitoring

Track heart rate scores and HRV:
<img width="947" height="800" alt="image" src="https://github.com/user-attachments/assets/57401ffc-988c-4912-a71a-a81f686739f5" />
<details>
<summary>yaml</summary>
   
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
</details>

#### Activity Summary

Daily steps and calories:
<img width="938" height="803" alt="image" src="https://github.com/user-attachments/assets/675d862e-47dd-4772-a1c9-dab482d145ce" />
<details>
<summary>yaml</summary>
   
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
</details>

#### Temperature Deviation

Track body temperature trends:
<img width="942" height="800" alt="image" src="https://github.com/user-attachments/assets/bb79c360-90c9-45b0-ac33-a96f7cc2ae9c" />
<details>
<summary>yaml</summary>
   
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
</details>

### Simple Entity Cards

For a quick overview without ApexCharts:
<img width="946" height="1471" alt="image" src="https://github.com/user-attachments/assets/ac3462db-f6a0-417d-b1f4-cca43335e4cd" />
<details>
<summary>yaml</summary>
   
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
  - entity: sensor.oura_ring_current_heart_rate
    secondary_info: last-changed
  - entity: sensor.oura_ring_average_heart_rate
    secondary_info: last-changed
  - entity: sensor.oura_ring_minimum_heart_rate
    secondary_info: last-changed
  - entity: sensor.oura_ring_maximum_heart_rate
    secondary_info: last-changed
```
</details>

### Gauge Cards

Visual representation of your scores:
<img width="905" height="228" alt="image" src="https://github.com/user-attachments/assets/bc8666fd-856c-4fd5-b05e-68e587b6b2ce" />
<details>
<summary>yaml</summary>
   
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
</details>

## Troubleshooting

### Authentication Issues

If you encounter authentication issues:

1. Verify your Client ID and Client Secret are correct
2. Ensure the Redirect URI matches exactly in both Oura Cloud and Home Assistant
3. Check Home Assistant logs for specific error messages
4. Try removing and re-adding the integration

### Missing Sensors

If some sensors are not appearing:

1. Ensure your Oura Ring is synced with the Oura app
2. Check that you have recent data in the Oura app
3. Wait for the next update cycle (default: 5 minutes)
4. Check Home Assistant logs for errors

### Unavailable Sensors

Some sensors may show as "unavailable" when Oura doesn't have sufficient data or hasn't established baseline measurements:

**Common for all users (temporary unavailability):**
- **Resting Heart Rate Score**: Requires sufficient heart rate measurements during rest periods
- **HRV Balance Score**: Requires sufficient HRV data collection (usually from sleep)

**Common for new ring users (may take weeks to become available):**
- **Cardiovascular Age**: Requires extended baseline data collection
- **VO2 Max**: Requires sufficient activity and cardiovascular data
- **Stress/Recovery Metrics**: Stress High Duration, Recovery High Duration, Stress Day Summary
- **Resilience Scores**: Sleep Recovery Score, Daytime Recovery Score, Stress Resilience Score
- **Sleep Optimization**: Optimal Bedtime Start, Optimal Bedtime End

This is normal behavior, especially:
- **In the first few weeks of wearing your ring** - Most advanced metrics require baseline establishment
- After periods of not wearing the ring
- If you haven't had sufficient sleep for HRV measurements
- During data processing delays

These sensors will automatically become available once Oura collects and processes the necessary baseline data. The Oura API simply does not provide values for these sensors until sufficient data history exists.

### API Rate Limiting

If you see rate limiting errors:

- The integration is designed to respect Oura's API limits
- Avoid manually triggering updates too frequently
- Check if you have other integrations also accessing the Oura API

## Development

This integration is built using modern Home Assistant patterns:

- **OAuth2 Flow**: Uses Home Assistant's built-in OAuth2 implementation
- **DataUpdateCoordinator**: Efficient data fetching with 12 specialized processing methods
- **Configuration-Driven Design**: Maintainable, declarative structures throughout
- **Modern Entity Standards**: `has_entity_name=True`, translation keys, entity categories
- **Entry-Scoped IDs**: Multi-account support with proper unique ID scoping
- **Type Hints**: Full type hint coverage for better code quality
- **Async**: All operations are asynchronous
- **Error Handling**: Comprehensive error handling and clean logging
- **Test Coverage**: 45 automated tests with comprehensive fixtures
- **Code Efficiency**: 51.5% code reduction in statistics module through refactoring

## Contributing

Contributions are welcome! Please read our [Contributing Guide](docs/CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup instructions
- **[Quick Reference](docs/QUICKREF.md)** - Quick reference for common tasks
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Redirect URI Fix](docs/FIXING_REDIRECT_URI.md)** - OAuth redirect URI troubleshooting
- **[Project Summary](docs/PROJECT_SUMMARY.md)** - Technical overview and architecture

## License

This project is licensed under the MIT License.

## Credits

- Original Oura Component: [nitobuendia/oura-custom-component](https://github.com/nitobuendia/oura-custom-component)
- Oura Ring API: [Oura Cloud API Documentation](https://cloud.ouraring.com/v2/docs)
- v2.0.0 Modernization: Comprehensive refactoring to HA 2025.11 standards
- Test Infrastructure: Docker-based testing with 45 automated tests
- Development assisted by: Claude Sonnet 4.5 (Anthropic AI)

## Sponsoring

If this integration is helpful, feel free to [Buy Me a Coffee](https://buymeacoffee.com/louispires); or check other options on the Github ❤️ Sponsor link on the top of this page.

[![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/louispires)

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/louispires/oura-v2-custom-component/issues) page
2. Create a new issue with detailed information
3. Include relevant logs from Home Assistant

## Disclaimer

This is an unofficial integration and is not affiliated with or endorsed by Oura Health Oy.
