# Oura Ring v2 Integration

A modern Home Assistant custom integration for Oura Ring using the v2 API with OAuth2 authentication.

## Features

✅ **OAuth2 Authentication** - Secure authentication using Home Assistant's application credentials  
✅ **Comprehensive Data** - 61 sensors and 1 binary sensor covering sleep, readiness, activity, workout, session, tag, rest mode, stress, resilience, and more  
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
   - In Home Assistant: Settings  Devices & Services  Application Credentials
   - Add your Oura credentials

3. **Add Integration**
   - Settings  Devices & Services  Add Integration
   - Search for "Oura Ring"
   - Follow the OAuth flow

## Available Sensors

### Sleep and Recovery
Sleep Score, Total/Deep/REM/Light Sleep Duration, Awake Time, Sleep Efficiency, Restfulness, Latency, Timing, Deep Sleep %, REM Sleep %, Time in Bed, Bedtime Start, Bedtime End, Low Battery Alert, Lowest Sleep Heart Rate, Average Sleep Heart Rate, Average Sleep HRV

### Readiness and Activity
Readiness Score, Temperature Deviation, Resting Heart Rate, HRV Balance, Sleep Regularity, Activity Score, Steps, Active/Total/Target Calories, High/Medium/Low Activity Time

### Heart, Stress, and Advanced Metrics
Current/Average/Minimum/Maximum Heart Rate, Stress High Duration, Recovery High Duration, Stress Day Summary, Resilience Level, Sleep Recovery Score, Daytime Recovery Score, Stress Resilience Score, SpO2 Average, Breathing Disturbance Index, VO2 Max, Cardiovascular Age, Optimal Bedtime Start, Optimal Bedtime End

### Workout, Session, Tags, and Rest Mode
Workouts Today, Last Workout Type, Last Workout Distance, Last Workout Calories, Last Workout Intensity, Last Workout Duration, Mindfulness Sessions Today, Meditation Duration Today, Tags Today, Tag Count Today, Rest Mode Start, Rest Mode End, Rest Mode binary sensor

**Total: 61 sensors + 1 binary sensor** providing comprehensive health tracking

Sleep Efficiency is now sourced from Oura detailed sleep data so it reflects the actual percentage rather than the contributor score.

## Support

For issues, questions, or feature requests, please visit the [GitHub repository](https://github.com/louispires/oura-v2-custom-component/issues).
