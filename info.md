# Oura Ring v2 Integration

A modern Home Assistant custom integration for Oura Ring using the v2 API with OAuth2 authentication. Requires Home Assistant 2026.3.0 or newer.

## Features

✅ **OAuth2 Authentication** - Secure authentication using Home Assistant's application credentials  
✅ **Comprehensive Data** - 118 sensors and 2 binary sensors covering sleep, readiness, activity, workout, session, tag, rest mode, stress, resilience, ring battery, lifetime totals, and more  
✅ **Extended Historical Data** - Load up to 48 months (4 years) of historical data on first setup (default: 3 months)  
✅ **Configurable Updates** - Data refresh interval configurable from 1-60 minutes (default: 5 minutes)  
✅ **Modern Architecture** - Built following the latest Home Assistant standards  
✅ **Custom Branding** - Includes Oura Ring icon for visual identification
✅ **Expanded Daily Tracking** - Adds workout, mindfulness session, tag, and rest mode entities with historical statistics support

## Quick Start

After installation:

1. **Create Oura Application**
   - Go to [Oura Cloud](https://developer.ouraring.com/applications)
   - Create a new application
   - Save your Client ID and Client Secret

2. **Configure Application Credentials**
   - In Home Assistant: Settings → Devices & Services → Application Credentials
   - Add your Oura credentials

3. **Add Integration**
   - Settings → Devices & Services → Add Integration
   - Search for "Oura Ring"
   - Follow the OAuth flow

## Available Sensors

### Sleep and Recovery

Sleep Score, Total/Deep/REM/Light Sleep Duration, Awake Time, Sleep Efficiency, Restfulness, Sleep Latency, Sleep Timing, Deep Sleep/REM Sleep/Total Sleep/Sleep Latency Contributions, Deep Sleep %, REM Sleep %, Time in Bed, Bedtime Start, Bedtime End, Latest Bedtime Start, Latest Bedtime End, Average Breathing Rate, Restless Periods, Sleep Score Delta, Readiness Score Delta, Low Battery Alert, Sleep Analysis Reason, Lowest Sleep Heart Rate, Average Sleep Heart Rate, Average Sleep HRV

### Readiness and Activity

Readiness Score, Temperature Deviation, Temperature Trend Deviation, Resting Heart Rate Score, HRV Balance Score, Sleep Regularity Score, Activity Balance/Body Temperature/Previous Day Activity/Previous Night/Recovery Index/Sleep Balance Contributions, Activity Score, Steps, Active/Total/Target Calories, Target Distance, Equivalent Walking Distance, High/Medium/Low Activity MET Minutes, High/Medium/Low Activity Time, Resting Time, Sedentary Time, Ring Non-Wear Time, Inactivity Alerts, Meet Daily Targets/Move Every Hour/Recovery Time/Stay Active/Training Frequency/Training Volume Contributions

### Heart, Stress, and Advanced Metrics

Current/Average/Minimum/Maximum Heart Rate, Last Heart Rate Reading, Stress High Duration, Recovery High Duration, Stress Day Summary, Resilience Level, Sleep Recovery Score, Daytime Recovery Score, Stress Resilience Score, SpO2 Average, Breathing Disturbance Index, VO2 Max, Cardiovascular Age, Pulse Wave Velocity, Optimal Bedtime Start, Optimal Bedtime End, Ring Battery Level, Ring Last Sync

### Workout, Session, Tags, and Rest Mode

Workouts Today, Last Workout Type, Last Workout Distance, Last Workout Calories, Last Workout Intensity, Last Workout Duration, Last Workout Source, Mindfulness Sessions Today, Meditation Duration Today, Tags Today, Tag Count Today, Rest Mode Start, Rest Mode End

### Lifetime Counters

Lifetime Total/Deep/REM/Light Sleep Duration, Lifetime Awake Time, Lifetime Time in Bed, Lifetime Steps, Lifetime Active/Total Calories, Lifetime High/Medium/Low Activity MET Minutes, Lifetime Inactivity Alerts, Lifetime Ring Non-Wear Time, Lifetime Resting Time, Lifetime Sedentary Time, Lifetime Equivalent Walking Distance, Lifetime Stress/Recovery High Duration

### Binary Sensors

Rest Mode, Ring Charging

**Total: 118 sensors + 2 binary sensors** providing comprehensive health tracking

Sleep Efficiency is now sourced from Oura detailed sleep data so it reflects the actual percentage rather than the contributor score.

## Support

For issues, questions, or feature requests, please visit the [GitHub repository](https://github.com/louispires/Oura-Home-Assistant-Integration/issues).
