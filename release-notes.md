# 🎉 Oura Ring v2 Integration v2.5.1 - Data Verification & Sleep Regularity

This release adds data verification attributes and a new Sleep Regularity sensor from the latest Oura API update.

## ✨ FEATURES IN v2.5.1

### New Sleep Regularity Sensor

- **New Sensor**: `sleep_regularity` - Contribution score for sleep schedule consistency (1-100)
- **Data Source**: Extracted from Readiness contributors in the Oura API
- **Use Case**: Track how consistent your sleep schedule is and its impact on your readiness score
- **Category**: Readiness sensors (now 5 total)

### Data Date Attribute

- **New Attribute**: All sensors now include a `data_date` attribute showing which day's data is being displayed
- **Use Case**: Verify that sensor values match the expected date from the Oura app
- **Debugging**: Helps identify any data synchronization issues

## 📊 SENSOR COUNT UPDATE

- **Previous version**: 48 sensors
- **This version**: 49 sensors (+1 new sensor)
- **Total Readiness Sensors**: 5 (added Sleep Regularity Score)

## 🔧 INTERNAL IMPROVEMENTS

- Code cleanup and removal of debug logging
- Improved data processing reliability

## 🧪 TESTING & VALIDATION

- ✅ All automated tests passing
- ✅ Hassfest validation passed
- ✅ HACS compliance verified

---

# 🎉 Oura Ring v2 Integration v2.5.0 - Multiple Account Support

This release enables support for multiple Oura Ring accounts in a single Home Assistant instance!

## ✨ NEW FEATURES IN v2.5.0

### Multiple Account Support

- **Add Multiple Accounts**: You can now configure multiple Oura Ring accounts (e.g., for family members)
- **Unique Account Identification**: Each account is uniquely identified by your Oura user ID
- **Account-Specific Titles**: Config entries show your email address for easy identification
- **No Duplicate Accounts**: The integration prevents adding the same Oura account twice

### Re-authentication Support

- **Token Expiry Handling**: When your OAuth token expires, you'll be prompted to re-authenticate
- **Same Account Enforcement**: Re-authentication ensures you log in with the same Oura account
- **Graceful Recovery**: Automatic recovery from authentication failures

## 🔧 TECHNICAL IMPROVEMENTS

- **User Info API Call**: Integration now fetches user profile during setup to get unique user ID
- **Per-User Unique IDs**: Config entries use Oura user ID instead of domain-wide ID
- **Reauth Flow**: Added proper re-authentication flow following Home Assistant standards
- **Error Handling**: Better error messages for connection issues and invalid responses

## 🧪 TESTING & VALIDATION

- ✅ All 50 automated tests passing (+5 new config flow tests)
- ✅ Hassfest validation passed
- ✅ HACS compliance verified

## 📋 HOW TO ADD MULTIPLE ACCOUNTS

1. **Add Application Credentials for each account** (if not already done):
   - Go to **Settings** → **Devices & Services** → **Application Credentials**
   - Add the OAuth Client ID and Secret for each Oura account's application
2. Go to **Settings** → **Devices & Services**
3. Click **+ Add Integration**
4. Search for **Oura Ring**
5. Select the OAuth credentials for the account you want to add
6. Complete the OAuth flow with that account's Oura login
7. Each account will appear as a separate integration with its email as the title

---

## 🎉 Oura Ring v2 Integration v2.4.0 - Enhanced Sleep & Heart Rate Metrics

This release brings deeper insights into your sleep quality with new bedtime and heart rate sensors!

## ✨ NEW FEATURES IN v2.4.0

### New Sleep Sensors

- **Bedtime Start**: Tracks exactly when you went to sleep
- **Bedtime End**: Tracks exactly when you woke up
- **Use Cases**:
  - Automate lights or blinds based on your actual wake-up time
  - Track sleep schedule consistency over time

### New Heart Rate Sensors

- **Lowest Sleep Heart Rate**: The lowest heart rate recorded during your sleep
- **Average Sleep Heart Rate**: The average heart rate during your sleep
- **Use Cases**:
  - Monitor cardiovascular recovery during sleep
  - Correlate resting heart rate with sleep quality

### Configuration Updates

- **Prevent Historical Re-import**: New option to disable historical data import on reconfiguration
- **Use Case**: Prevents overwriting existing historical data when changing other settings or restarting Home Assistant

## 🐛 BUG FIXES

### Historical Data Sensor Types

- **Fixed**: Incorrect sensor types for some historical data metrics
- **Solution**: Ensure correct sensor types (e.g. duration, score) are applied during historical import
- **Impact**: Historical data now displays with correct units and formatting in graphs

## 📊 SENSOR COUNT UPDATE

- **Previous version**: 44 sensors
- **This version**: 48 sensors (+4 new sensors)
- **Total Sleep Sensors**: 16
- **Total Heart Rate Sensors**: 6

## 🧪 TESTING & VALIDATION

- ✅ All 45 automated tests passing
- ✅ Merged functionality from multiple development branches
- ✅ Validated with Oura API v2

---

## 🎉 Oura Ring v2 Integration v2.3.1 - Historical Data Fix

This release fixes a critical issue where historical data was not linking correctly to sensor entities.

## 🐛 BUG FIXES

### Historical Data Linking

- **Fixed**: Historical data imported during setup was not visible in sensor history graphs.
- **Solution**: Updated statistics import to correctly link data to sensor entities (`sensor.oura_ring_*`) instead of internal IDs.
- **Impact**: Historical data charts should now populate correctly for new installations.

---

## 🎉 Oura Ring v2 Integration v2.3.0 - Heart Health Scope

This release adds support for the new `heart_health` scope and requires user action to enable.

## ⚠️ ACTION REQUIRED

**To enable the new features in this release, you must:**

1. **Update Developer Portal**: Go to [Oura Developer Portal](https://developer.ouraring.com/applications), `View Details` of your application, `Edit` the application, and select `Heart Health` under Scopes.
2. Check `I agree to the Oura API Agreement`
3. Select `Save Changes`
4. **Re-authenticate**: In Home Assistant, go to Settings > Devices & Services > Oura Ring, and delete and re-add the integration to grant the new permission.
5. Ensure that you see `Heart Health Data (VO2 Max, CVA)` and it is selected

## ✨ NEW FEATURES IN v2.3.0

- **Heart Health Scope**: Added support for the `heart_health` OAuth2 scope to access cardiovascular health data.

## 🔧 TECHNICAL IMPROVEMENTS

- Updated OAuth2 scopes list to include `heart_health`.

## 🧪 TESTING & VALIDATION

- ✅ All automated tests passing
- ✅ Hassfest validation passed
- ✅ HACS compliance verified

---

## 🎉 Oura Ring v2 Integration v2.2.0 - Extended Historical Data

This feature release significantly extends historical data capabilities and improves API efficiency!

## ✨ NEW FEATURES IN v2.2.0

### Extended Historical Data Support

- **Increased Maximum**: Historical data now supports up to **48 months (4 years)** of data
- **Month-Based Configuration**: Switched from days to months for easier configuration
- **Default Changed**: Default historical data load changed from 14 days to **3 months (90 days)**
- **Better User Experience**: Configure in intuitive monthly increments (1-48 months)
- **Use Cases**:
  - Import years of historical health data when first setting up
  - Analyze long-term trends and patterns
  - Maintain comprehensive health history in Home Assistant

### API Efficiency Improvements

- **Optimized Batching**: Heartrate data batching increased from 7 days to 30 days per request
- **Fewer API Calls**: Reduced API calls when fetching large historical datasets
- **Example Impact**: Fetching 90 days of data now requires only 3 heartrate requests instead of 13

## 🔧 TECHNICAL IMPROVEMENTS

- Heartrate endpoint now respects Oura's 30-day maximum range per request
- Historical data loading converts months to days automatically (30 days per month)
- **Statistics Compatibility**: Added `unit_class` parameter to statistics metadata for Home Assistant 2026.11+ forward compatibility
- **Mean Type Support**: Added proper `mean_type` configuration for statistics (arithmetic, circular, none)
- **Device Class Mapping**: Automatic mapping of sensor units to appropriate device classes (duration, temperature, energy)
- Updated configuration flow to use month-based validation
- All strings and translations updated to reflect month-based configuration
- **Added `mean_type` parameter**: Now properly specifies `StatisticMeanType` for all statistics (required for Home Assistant 2026.11+)
  - `ARITHMETIC`: For all numeric sensors (scores, durations, heart rates, etc.)
  - `CIRCULAR`: For time-of-day sensors (optimal bedtime start/end)
  - `NONE`: For text/categorical sensors (stress summary, resilience level)

## 🧪 TESTING & VALIDATION

- ✅ All 43 automated tests passing
- ✅ Hassfest validation: 0 invalid integrations  
- ✅ HACS compliance verified
- ✅ Docker-based testing with Home Assistant 2025.11
- ✅ Historical data loading validated with extended timeframes

## 📊 CONFIGURATION UPDATES

- **Previous**: 1-90 days (default 14 days)
- **Current**: 1-48 months (default 3 months, ~90 days)
- **Maximum**: Up to 4 years of historical data

---

## 🎉 Oura Ring v2 Integration v2.1.0 - Feature Release

This feature release adds a new diagnostic sensor and improves documentation for easier installation!

## ✨ NEW FEATURES

### Low Battery Alert Sensor

- **New Sensor**: `low_battery_alert` diagnostic sensor
- **Data Source**: Extracted from Oura sleep data endpoint
- **Type**: Boolean sensor indicating if battery was low during sleep
- **Category**: Diagnostic (hidden from main UI by default)
- **Icon**: `mdi:battery-alert`
- **Default Value**: False when not present in API response
- **Use Cases**:
  - Track ring battery alerts during sleep sessions
  - Create automations for low battery notifications
  - Better understand data quality issues related to battery level

### Documentation Improvements

- **HACS Default Repository**: Updated installation instructions to reflect that Oura Ring is now in HACS default repository
- **Simplified Installation**: Removed custom repository instructions - now just search for "Oura Ring" in HACS
- **Add Integration Button**: Added my.home-assistant.io badge for one-click integration setup
- **Better User Experience**: Streamlined installation process for new users

## 🧪 TESTING & VALIDATION

- ✅ All 43 automated tests passing (4 new tests added)
- ✅ Hassfest validation: 0 invalid integrations  
- ✅ HACS compliance verified
- ✅ Docker-based testing with Home Assistant 2025.11
- ✅ New sensor extraction logic tested with True/False/missing values
- ✅ Boolean sensor entity tests added

## 📊 SENSOR COUNT UPDATE

- **Previous version**: 43 sensors
- **This version**: 44 sensors (+1 new diagnostic sensor)
- **Total Sleep Sensors**: 14 (added Low Battery Alert)

---

## 🐛 Oura Ring v2 Integration v2.0.1 - Network Resilience

This bugfix release improves integration resilience to transient network issues.

## 🐛 BUG FIXES

### Network Resilience Improvements

- **Fixed**: All sensors becoming unavailable during transient network issues (DNS failures, timeouts)
- **Solution**: Coordinator now retains last known sensor values when API is temporarily unreachable
- **Impact**: Sensors maintain their values during network outages instead of showing "Unavailable"

### Reduced Log Spam

- **Fixed**: 44+ ERROR messages flooding logs during network issues
- **Solution**: Network errors now logged as WARNING with single aggregated message when 50%+ endpoints fail
- **Impact**: Cleaner logs with clear indication of network issues and retry timing

### Smart Error Handling

- Individual endpoint failures logged at DEBUG level when not systemic
- Clear warning messages showing when next retry will occur
- Automatic recovery when network connectivity is restored
- Only shows error on first setup if API cannot be reached

### Updated Developer Portal URLs

- **Fixed**: Outdated Oura application management URLs
- **Updated**: Application management now points to `https://developer.ouraring.com/applications`
- **Note**: API documentation remains at `https://cloud.ouraring.com/v2/docs`

## 🧪 TESTING & VALIDATION

- ✅ All 39 automated tests passing
- ✅ Hassfest validation: 0 invalid integrations
- ✅ HACS compliance verified
- ✅ Docker-based testing with Home Assistant 2025.11

---

## 🎉 Oura Ring v2 Integration v2.0.0 - Production Ready

This is a **major milestone release** marking the integration as **production-ready** with critical bug fixes, enhanced reliability, and comprehensive testing!

## 🐛 CRITICAL BUG FIXES IN v2.0.0

### OAuth Token Access Fix

- **Fixed**: OAuth token was being accessed incorrectly, causing `None` token errors
- **Root Cause**: `async_ensure_token_valid()` validates/refreshes but doesn't return the token
- **Solution**: Now properly accesses token via `session.token` property after validation
- **Impact**: Eliminates authentication failures and API call errors

### Entity Category Validation Fix

- **Fixed**: Entity category validation errors preventing sensor creation
- **Root Cause**: Using string `"diagnostic"` instead of `EntityCategory.DIAGNOSTIC` enum
- **Solution**: Imported `EntityCategory` from `homeassistant.helpers.entity` and converted all strings to enums
- **Impact**: All diagnostic sensors now properly categorized and functional

### Coordinator Entry Attribute Fix

- **Fixed**: `AttributeError: 'OuraDataUpdateCoordinator' object has no attribute 'entry'`
- **Root Cause**: Coordinator wasn't storing the ConfigEntry reference needed for unique IDs
- **Solution**: Added `entry: ConfigEntry` parameter to coordinator and stored as instance attribute
- **Impact**: Fixes sensor initialization and multi-account support

## ✨ ENHANCEMENTS IN v2.0.0

### Enum Device Class Support

- **Resilience Level** sensor now has proper enum device class
- **Valid Options**: limited, adequate, solid, strong, exceptional
- **User Experience**: Users can see all possible resilience levels in the UI

### Enhanced Debugging

- Added debug logging for OAuth session state to aid troubleshooting
- Authentication success messages in config flow
- Better error context for API failures

### Documentation Improvements

- **README Updates**: Added ⚠️ warnings for 10 sensors commonly unavailable for new users
- **Sensor Availability**: Clear documentation explaining why certain sensors may be unavailable initially
- **New User Guidance**: Detailed explanation of baseline data collection requirements
- **Corrected Defaults**: Fixed historical data default from 30 to 14 days to match actual code

## 🧪 TESTING & VALIDATION

### Comprehensive Test Suite

- **39 automated tests** all passing
- Docker-based testing with Home Assistant 2025.11
- Tests cover coordinator, sensors, statistics, entity categories, and integration setup
- Validates all bug fixes and enhancements

### Real-World Deployment

- Tested with actual Home Assistant 2025.11 installation
- Verified OAuth flow works correctly
- Confirmed all 43 sensors populate properly
- Validated historical data loading and statistics integration

## 📊 COMPLETE FEATURE SET

All features from v1.2.0 remain available:

- **43 sensors** covering sleep, readiness, activity, heart rate, HRV, stress, resilience, SpO2, fitness, and sleep optimization
- **Historical data loading** with 14-day default (configurable 1-90 days)
- **Long-term statistics** integration for all sensors
- **Home Assistant 2025.11 compliance** with modern entity naming and device grouping
- **OAuth2 authentication** with proper scope handling
- **HACS compatible** for easy installation

## ⚠️ BREAKING CHANGES & UPGRADE NOTES

### 🔴 BREAKING CHANGE: Entity ID Naming Convention

Due to Home Assistant 2025.11 modernization, **all entity IDs have changed**:

**Old format (v1.x.x):**

```
sensor.oura_sleep_score
sensor.oura_readiness_score
sensor.oura_resilience_level
```

**New format (v2.0.0):**

```
sensor.oura_ring_sleep_score
sensor.oura_ring_readiness_score
sensor.oura_ring_resilience_level
```

### 📋 Migration Path to Preserve Historical Data

**Option 1: Rename Device to Keep Old Entity IDs (Recommended)**

This method preserves ALL historical data by keeping your old entity IDs:

1. **Upgrade** to v2.0.0 via HACS
2. **Restart** Home Assistant
3. Go to **Settings** → **Devices & Services** → **Oura Ring**
4. Click on the **Oura Ring** device
5. Click the **⚙️ (gear icon)** at the top right
6. **Rename** the device from "Oura Ring" to **"Oura"**
7. Click the **☰ (burger menu)** at the top right
8. Select **"Rename entities"**
9. This will rename all entities back to the old format (`sensor.oura_*`)
10. ✅ **All your historical data is preserved!**

**Optional:** If you want custom entity names:

- Rename the device again to anything you like (e.g., "Louis' Oura")
- Use "Rename entities" again to update to your preferred naming scheme

**Option 2: Manual Entity Rename (For Custom Names)**

If you want to keep the new `sensor.oura_ring_*` format but preserve history:

1. **Before upgrading**, note down your entity IDs
2. **Upgrade** to v2.0.0 via HACS and restart
3. For each entity, go to **Settings** → **Entities** → search for the entity
4. Click the entity, then click the **⚙️ (gear icon)**
5. Change the **Entity ID** to match your old one
6. Historical data will be preserved for renamed entities

**Option 3: Update All References (No Data Preservation)**

If historical data preservation isn't critical:

1. **Upgrade** to v2.0.0 via HACS
2. **Find & Replace**: Use `sensor.oura_` → `sensor.oura_ring_` in:
   - Automations
   - Scripts
   - Dashboards/Lovelace cards
   - Templates
3. New data will start recording under new entity IDs

### ✅ What Still Works

- **No re-authorization required** - existing OAuth tokens will continue working
- **Historical data preserved** - long-term statistics remain intact
- **Automatic bug fixes** - all bug fixes apply immediately upon upgrade

### 🆕 For New Installations

- Follow standard installation process via HACS
- Entity IDs will use the new `sensor.oura_ring_*` format from the start
- Some sensors may be unavailable initially (see documentation)
- Historical data will load automatically on first setup

## 📈 STABILITY IMPROVEMENTS

- **Production Ready**: All critical bugs resolved
- **Enhanced Reliability**: Proper error handling and validation
- **Better User Experience**: Clear documentation and helpful error messages
- **Tested at Scale**: Validated with comprehensive automated test suite

## 🙏 ACKNOWLEDGMENTS

Special thanks to users who reported issues and provided logs that helped identify and fix these critical bugs!

---

## 🎉 Welcome to Oura Ring v2 Integration v1.2.0

This release adds **comprehensive stress, resilience, SpO2, fitness, and sleep optimization sensors** for deeper health insights, plus **Home Assistant 2025.11 modernization** for improved device grouping and entity naming!

## ✨ NEW FEATURES IN v1.2.0

### 🧬 Code Quality & Maintainability Improvements

#### Phase 5: Entity Categories & Metadata

- **Entity Categories:** Added diagnostic category for 8 technical/secondary sensors
  - Deep/REM sleep percentages, min/max heart rate, breathing disturbance index
  - Target calories, optimal bedtime timestamps
  - Primary health metrics remain in main view, diagnostics hidden by default
- **Improved State Classes:** Changed duration/cumulative sensors from `measurement` to `total`
  - Sleep durations, activity times, stress durations now properly accumulate
  - Steps changed to `total_increasing` for better energy dashboard integration
- **Better HA Integration:** Sensors now properly categorized for energy/statistics dashboards
- **Testing:** Added 6 comprehensive tests validating entity categories and state classes

#### Phase 4: Logging & Token Handling

- **Cleaner Logs:** Removed excessive debug logging for production-ready output
- **Simplified Token Handling:** Streamlined OAuth2 token management in API client
- **Essential Logging Only:** Kept only critical info/error messages for operations
- **Graceful 401 Handling:** Silent handling of unavailable features (SpO2, VO2 Max, etc.)
- **Reduced Noise:** Removed redundant success/progress messages during normal operation

#### Phase 3: Coordinator Refactoring

- **Code Simplification:** Refactored `coordinator.py` from 252 to 241 lines (4.4% reduction)
- **Method Extraction:** Split 162-line `_process_data` method into 12 focused methods for better maintainability
- **Separation of Concerns:** Each data type now has its own processing method:
  - Sleep scores, sleep details, readiness, activity, heart rate
  - Stress, resilience, SpO2, VO2 Max, cardiovascular age, sleep time
- **Testing:** Added 13 comprehensive unit tests for all data processing methods
- **Orchestration:** Main `_process_data` method now delegates to specialized processors

#### Phase 2: Statistics Module Refactoring

- **Code Reduction:** Reduced `statistics.py` from 896 to 435 lines (51.5% reduction)
- **Configuration-Driven Design:** Replaced 11 duplicated functions with single generic processor
- **Helper Functions:** Added 4 reusable utility functions for data transformations
- **Testing:** Added 6 unit tests covering all transformation logic

#### Phase 1: Device Registry & Modern Entity Naming

- **Single Device Entry**: All 43 sensors now properly grouped under one "Oura Ring" device
- **Modern Entity Naming**: Follows HA 2025.11 standards with `has_entity_name=True`
- **Full Translation Support**: Entity names properly translated (currently English)
- **Entry-Scoped Unique IDs**: Prevents conflicts with multiple Oura accounts
- **Testing:** Added 7 unit tests and Docker-based test infrastructure

### 🏠 Home Assistant 2025.11 Modernization

- **Single Device Entry**: All 43 sensors now properly grouped under one "Oura Ring" device
- **Modern Entity Naming**: Follows HA 2025.11 naming standards with `has_entity_name=True`
- **Full Translation Support**: Entity names properly translated (currently English)
- **Entry-Scoped Unique IDs**: Prevents conflicts when using multiple Oura accounts
- **Docker Test Infrastructure**: Automated testing with Home Assistant Docker image

### 🧠 Stress & Recovery Tracking

- **Stress High Duration**: Minutes of elevated stress during the day
- **Recovery High Duration**: Minutes of elevated recovery (low stress)
- **Stress Day Summary**: Daily stress assessment (good/bad/unknown)

### 💪 Resilience & Adaptation

- **Resilience Level**: Your ability to adapt (limited/adequate/solid/strong/exceptional)
- **Sleep Recovery Score**: How well you recovered overnight
- **Daytime Recovery Score**: Your recovery throughout the day
- **Stress Resilience Score**: Your capacity to handle stress

### 🫁 Blood Oxygen Sensing (SpO2) - Gen3 & Oura Ring 4 Only

- **SpO2 Average**: Your average blood oxygen saturation percentage
- **Breathing Disturbance Index**: Indicators of sleep breathing quality

### 💓 Advanced Fitness Metrics

- **VO2 Max**: Your aerobic capacity in ml/kg/min
- **Cardiovascular Age**: Your biological cardiovascular age in years

### 😴 Sleep Optimization

- **Optimal Bedtime Start**: Recommended bedtime window start
- **Optimal Bedtime End**: Recommended bedtime window end

## 📊 SENSOR EXPANSION

- **Previous version**: 30 sensors
- **This version**: 43 sensors (+13 new sensors)
- All new sensors support long-term statistics for historical tracking
- SpO2 and Cardiovascular Age features exclusive to Gen3 and Oura Ring 4

## ⚡ IMPROVEMENTS

- Extended API coverage for all Oura Ring v2 endpoints
- Better health insights with stress and resilience data
- Sleep optimization recommendations built-in
- Fitness tracking capabilities expanded
- All new sensors integrate seamlessly with existing home automation
- **Modern Device Architecture**: All sensors properly group under a single device entry in Home Assistant
- **Improved Entity Names**: Cleaner entity names following HA 2025.11 conventions (e.g., "Sleep Score" instead of "Oura Sleep Score")
- **Translation Framework**: Entity names now support localization through strings.json
- **Better Multi-Account Support**: Entry-scoped unique IDs prevent conflicts with multiple Oura accounts
- **Corrected OAuth Scopes**: Fixed scope names to match Oura's actual API requirements
  - Changed `spo2Daily` → `spo2` (correct scope name)
  - Added `stress` scope (required for stress data endpoints)
  - Added `ring_configuration` scope (for ring configuration data)
  - Added `tag` scope (for user tags)
- **Graceful Error Handling**: 401 errors for unsupported features are handled silently
  - No ERROR log spam for features your ring doesn't support
  - Sensors for unsupported features show as "unavailable"
  - Core functionality (sleep, readiness, activity) unaffected
- **Better Debugging**: Added helpful debug messages explaining when features aren't available
- **Comprehensive Documentation**: Updated all scope references and added troubleshooting guides

## ⚠️ IMPORTANT: Re-authorization Required

To access all new features, users must re-authorize the integration:

1. Remove the Oura Ring integration from Home Assistant
2. Re-add it and complete the OAuth flow with the updated scopes
3. All new sensors and features will then be available

## 📚 COMPLETE SENSOR COUNT BY CATEGORY

- Sleep: 13 sensors
- Readiness: 4 sensors
- Activity: 8 sensors
- Heart Rate: 3 sensors
- **NEW - Stress:** 3 sensors
- **NEW - Resilience:** 4 sensors
- **NEW - SpO2:** 2 sensors (Gen3/Gen4 only)
- **NEW - Fitness:** 2 sensors
- **NEW - Sleep Optimization:** 2 sensors
- **Total:** 43 sensors

---

## ✨ NEW FEATURES IN v1.1.0

This release adds **historical data loading with Long-Term Statistics** to populate your dashboards from day one!

## ✨ NEW FEATURES IN v1.1.0

### 📜 Historical Data Loading with Long-Term Statistics

- **Automatic historical data fetch** on first setup (default: 30 days)
- **Long-Term Statistics import**: All historical data properly stored with timestamps
- **Instant dashboard population**: Works immediately with ApexCharts, History Graph, and Statistics Graph
- **Configurable timeframe**: Choose 7-90 days of historical data
- **One-time fetch**: Historical data only loaded during initial setup
- **Efficient updates**: After initial load, only fetches new data

### 🎛️ Enhanced Configuration

- New option to configure historical data days (7-90 days)
- Historical data setting available in integration options
- Smart detection of first-time setup vs. ongoing updates

### � Long-Term Statistics Support

All 30 sensors now support long-term statistics:

- **Sleep metrics**: All 13 sleep sensors with historical data
- **Readiness metrics**: All 4 readiness sensors with historical data
- **Activity metrics**: All 8 activity sensors with historical data
- **Heart rate**: Daily average heart rate statistics
- **HRV**: Sleep HRV with historical trends

### 🎯 Benefits

- ✅ **Immediate insights**: See 30 days of trends from installation
- ✅ **Proper timestamps**: Each data point has the correct historical date
- ✅ **Database efficiency**: Uses HA's optimized statistics storage
- ✅ **Dashboard ready**: Works with all history visualization cards
- ✅ **API efficient**: Bulk load once, then incremental daily updates

## �🔧 IMPROVEMENTS

- Better logging for historical data loading and statistics import
- More efficient API usage pattern (initial bulk load + incremental updates)
- Follows Oura API best practices for data access
- Statistics database integration for long-term data storage

## 📚 TECHNICAL DETAILS

- New `statistics.py` module for handling long-term statistics
- Automatic import of historical data points with proper timestamps
- Support for both mean and sum statistics where appropriate
- Comprehensive metadata for all sensor types

---

## Previous Release: v1.0.0

This was the **first official release** of the modern Oura Ring custom integration for Home Assistant, built from the ground up using the Oura API v2 with OAuth2 authentication.

## ✨ KEY FEATURES IN v1.0.0

### Comprehensive Health Tracking - 30 Sensors

- **Sleep Monitoring** (13 sensors): Sleep score, durations for all sleep stages, awake time, time in bed, efficiency, restfulness, latency, timing, and stage percentages
- **Readiness Tracking** (4 sensors): Readiness score, temperature deviation, resting heart rate score, HRV balance score
- **Activity Metrics** (8 sensors): Activity score, steps, calories, and activity time by intensity
- **Heart Rate Data** (4 sensors): Current, average, minimum, and maximum heart rate
- **HRV Monitoring** (1 sensor): Average sleep HRV for recovery tracking

### Modern Architecture

- **OAuth2 Authentication**: Secure authentication using Home Assistant's application credentials system
- **Efficient Data Fetching**: Parallel fetching of 5 Oura API v2 endpoints
- **DataUpdateCoordinator**: Optimal data management following Home Assistant best practices
- **Configurable Updates**: Refresh interval configurable from 1-60 minutes (default: 5 minutes)
- **Type-Safe**: Full type hint coverage for reliability
- **Async Throughout**: All operations are asynchronous for performance

### HACS Compatible

- Easy installation through HACS custom repositories
- Automatic updates when new versions are released
- Custom branding with Oura Ring icon

### Accurate Data Interpretation

- Sleep durations from actual measurements (not contribution scores)
- Activity times from actual MET minutes
- Clear distinction between scores and measured values
- Proper handling of null values for optional metrics

## 📊 COMPLETE SENSOR LIST

### Sleep Sensors (13)

1. Sleep Score
2. Total Sleep Duration (hours)
3. Deep Sleep Duration (hours)
4. REM Sleep Duration (hours)
5. Light Sleep Duration (hours)
6. Awake Time (hours)
7. Sleep Efficiency (%)
8. Restfulness (%)
9. Sleep Latency (minutes)
10. Sleep Timing (score)
11. Deep Sleep Percentage (%)
12. REM Sleep Percentage (%)
13. Time in Bed (hours)

### Readiness Sensors (4)

1. Readiness Score
2. Temperature Deviation (°C)
3. Resting Heart Rate Score (contribution score 1-100)
4. HRV Balance Score (contribution score 1-100)

### Activity Sensors (8)

1. Activity Score
2. Steps
3. Active Calories (kcal)
4. Total Calories (kcal)
5. Target Calories (kcal)
6. High Activity Time (minutes)
7. Medium Activity Time (minutes)
8. Low Activity Time (minutes)

### Heart Rate Sensors (4)

1. Current Heart Rate (bpm)
2. Average Heart Rate (bpm)
3. Minimum Heart Rate (bpm)
4. Maximum Heart Rate (bpm)

### HRV Sensors (1)

1. Average Sleep HRV (ms)

## 🚀 GETTING STARTED

### Installation via HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to Integrations
3. Click the three dots → Custom repositories
4. Add: `https://github.com/louispires/oura-v2-custom-component`
5. Category: Integration
6. Install "Oura Ring"
7. Restart Home Assistant

### Configuration

1. **Create Oura Application**
   - Go to [Oura Cloud](https://developer.ouraring.com/applications)
   - Create a new application
   - Save your Client ID and Client Secret

2. **Add Application Credentials**
   - Settings → Devices & Services → Application Credentials
   - Add your Oura Client ID and Secret

3. **Add Integration**
   - Settings → Devices & Services → Add Integration
   - Search for "Oura Ring"
   - Follow the OAuth2 authentication flow

## 📚 DOCUMENTATION

Complete documentation is available in the repository:

- [Installation Guide](https://github.com/louispires/oura-v2-custom-component/blob/main/docs/INSTALLATION.md)
- [Quick Reference](https://github.com/louispires/oura-v2-custom-component/blob/main/docs/QUICKREF.md)
- [Troubleshooting](https://github.com/louispires/oura-v2-custom-component/blob/main/docs/TROUBLESHOOTING.md)
- [Dashboard Examples](https://github.com/louispires/oura-v2-custom-component/blob/main/README.md#dashboard-examples)

## 🎯 WHAT MAKES THIS INTEGRATION SPECIAL

- **Built for Oura API v2**: Uses the latest API with all modern features
- **OAuth2 Security**: Leverages Home Assistant's secure credential system
- **Accurate Data**: Correctly interprets all API fields and data types
- **Well Documented**: Comprehensive guides and dashboard examples
- **Actively Maintained**: Built with modern HA standards (2025)

## 🎯 WHAT MAKES THIS INTEGRATION SPECIAL

- **Built for Oura API v2**: Uses the latest API with all modern features
- **OAuth2 Security**: Leverages Home Assistant's secure credential system
- **Accurate Data**: Correctly interprets all API fields and data types
- **Well Documented**: Comprehensive guides and dashboard examples
- **Actively Maintained**: Built with modern HA standards (2025)

## 💬 SUPPORT

- **Issues**: [GitHub Issues](https://github.com/louispires/oura-v2-custom-component/issues)
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Full guides available in the repository

## 🙏 CREDITS

- Original Oura Component: [nitobuendia/oura-custom-component](https://github.com/nitobuendia/oura-custom-component)
- Oura Ring API: [Oura Cloud API Documentation](https://cloud.ouraring.com/v2/docs)
- Development assisted by: Claude Sonnet 4 (Anthropic AI)

---
