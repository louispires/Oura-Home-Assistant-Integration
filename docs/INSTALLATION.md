# Installation and Setup Guide

This guide walks you through installing and configuring the Oura Ring v2 integration for Home Assistant.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Oura API Setup](#oura-api-setup)
4. [Home Assistant Configuration](#home-assistant-configuration)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

- Home Assistant 2024.1.0 or higher
- Active Oura Ring subscription
- Oura Ring synced with the Oura mobile app
- Internet connection for cloud API access

## Installation Methods

### Method 1: HACS Installation (Recommended)

1. **Install HACS** (if not already installed):
   - Follow the [HACS installation guide](https://hacs.xyz/docs/setup/download)

2. **Add Custom Repository**:
   - Open HACS in Home Assistant
   - Click on **Integrations**
   - Click the three dots () in the top right
   - Select **Custom repositories**
   - Add URL: `https://github.com/louispires/oura-v2-custom-component`
   - Category: **Integration**
   - Click **Add**

3. **Install Integration**:
   - Search for "Oura Ring" in HACS
   - Click **Download**
   - Restart Home Assistant

### Method 2: Manual Installation

1. **Download Files**:

   ```bash
   cd /config
   git clone https://github.com/louispires/oura-v2-custom-component.git
   ```

2. **Copy Integration**:

   ```bash
   cp -r oura-v2-custom-component/custom_components/oura custom_components/
   ```

3. **Restart Home Assistant**

## Oura API Setup

### Step 1: Create Oura Developer Account

1. Go to [Oura Cloud](https://developer.ouraring.com)
2. Log in with your Oura account credentials
3. Navigate to **Applications** or visit: <https://developer.ouraring.com/applications>

### Step 2: Create OAuth Application

1. Click **Create a New Application**

2. Fill in the application details:

   **Application Name**: `Home Assistant`

   **Application Website**: `https://your-home-assistant-url.com`
   - Use your actual Home Assistant URL
   - Can be local (<http://192.168.1.100:8123>) or external (<https://ha.example.com>)

   **Redirect URI**: `https://my.home-assistant.io/redirect/oauth`
   - This integration always uses Home Assistant's built-in "My Home Assistant" redirect relay for OAuth, regardless of whether your instance is local-only, on Nabu Casa, or on DuckDNS/a custom domain.
   - You do not need to register your own local IP, hostname, or Nabu Casa/DuckDNS URL as the Redirect URI — only the URL above. Note: Oura's developer portal will not accept non-localhost `http://` URIs, so a local IP such as `http://192.168.1.100:8123/...` cannot be registered there anyway.

   **Application Scope**: Select all available scopes:
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

3. Click **Create** or **Save**

4. **Important**: Save your credentials:
   - **Client ID**: `abc123xyz...` (copy this)
   - **Client Secret**: `secret456...` (copy this - you may only see it once!)

### Step 3: Keep Credentials Safe

 **Security Note**: Keep your Client Secret secure. Never share it or commit it to public repositories.

## Home Assistant Configuration

### Step 1: Add Application Credentials

1. In Home Assistant, navigate to:
   **Settings** → **Devices & Services** → **Application Credentials**

2. Click **+ Add Application Credential**

3. **Important**: You may see either:
   - A dropdown to select an integration (select **Oura Ring**)
   - OR a generic form asking for application details

   If you see the generic form, this is normal! Just proceed to the next step.

4. Enter your credentials:
   - **Client ID**: Paste the Client ID from Oura Cloud
   - **Client Secret**: Paste the Client Secret from Oura Cloud

5. Click **Create** or **Add**

**Note**: The Application Credentials page is just for storing OAuth credentials. You won't see the Oura Ring integration listed here - that comes in the next step!

### Step 2: Add the Oura Ring Integration

**Now** you'll see Oura Ring as an available integration!

1. Navigate to:
   **Settings** → **Devices & Services**

2. Click **+ Add Integration**

3. Search for "Oura Ring"

4. Click on **Oura Ring**

5. The integration will automatically use the credentials you added in Step 1

6. You'll be redirected to Oura's authorization page:
   - Log in if prompted
   - Review the permissions requested
   - Click **Authorize** or **Allow**

7. You'll be redirected back to Home Assistant

8. The integration will be added with the title "Oura Ring"

## Verification

### Check Integration Status

1. Go to **Settings**  **Devices & Services**
2. Look for **Oura Ring** integration
3. It should show as "Configured"

### Check Sensors

1. Click on the Oura Ring integration
2. You should see multiple entities listed:
   - Sleep and readiness sensors
   - Activity and heart-rate sensors
   - Stress/resilience and advanced metrics
   - Workout/session/tag/rest-mode sensors
   - Ring battery diagnostics and binary sensors
   - Current total: 71 sensors + 2 binary sensors

### Test Data Retrieval

1. Go to **Developer Tools**  **States**
2. Filter for "oura"
3. Check that sensors have values (not "unavailable" or "unknown")
4. Initial values may take a few minutes to appear

### Example Sensors to Check

- `sensor.oura_ring_sleep_score`
- `sensor.oura_ring_readiness_score`
- `sensor.oura_ring_activity_score`
- `sensor.oura_ring_steps`
- `sensor.oura_ring_total_sleep_duration`
- `sensor.oura_ring_latest_bedtime_start`

## Troubleshooting

### Integration Not Appearing

**Problem**: Can't find Oura Ring when adding integration

**Solutions**:

1. Restart Home Assistant after installation
2. Clear browser cache (Ctrl+F5 or Cmd+Shift+R)
3. Check that files are in `config/custom_components/oura/`
4. Check Home Assistant logs for errors

### OAuth Error: Invalid Redirect URI

**Problem**: "redirect_uri_mismatch" or similar error during OAuth authorization

**Solution**: Register `https://my.home-assistant.io/redirect/oauth` as the Redirect URI in your Oura application at [developer.ouraring.com/applications](https://developer.ouraring.com/applications). This integration always sends this exact URI during OAuth, regardless of how your Home Assistant instance is accessed (local IP, Nabu Casa, DuckDNS, or any other domain). Note: Oura's developer portal will not accept non-localhost `http://` URIs, so a local IP address cannot be registered there.

### Authentication Failed

**Problem**: Authentication fails during OAuth flow

**Solutions**:

1. Verify Client ID and Client Secret are correct
2. Check that application is active in Oura Cloud
3. Ensure all required scopes are selected
4. Try removing and re-adding application credentials

### Sensors Show "Unavailable"

**Problem**: Integration configured but sensors unavailable

**Solutions**:

1. Wait 5 minutes for first data update
2. Ensure Oura Ring is synced with mobile app
3. Check Home Assistant logs for API errors:

   ```
   Settings → System → Logs
   Search for "oura"
   ```

4. Verify you have recent data in the Oura mobile app
5. Check API rate limits haven't been exceeded

### No Recent Data

**Problem**: Sensors show old data or no data

**Solutions**:

1. Sync your Oura Ring with the mobile app
2. Wait for the next update cycle (default: 5 minutes)
3. Restart the integration:
   - Settings → Devices & Services
   - Click on Oura Ring
   - Click  (three dots)
   - Select "Reload"

### Token Expired Error

**Problem**: "Token expired" or authentication errors in logs

**Solutions**:

1. Token should auto-refresh - wait a few minutes
2. If persists, remove and re-add integration
3. Verify application is still active in Oura Cloud

## Advanced Configuration

### Changing Update Interval & History Settings

The default update interval is 5 minutes, which can be configured through the integration options:

1. Go to **Settings** → **Devices & Services**
2. Find "Oura Ring" and click **CONFIGURE**
3. Set your desired update interval (1-60 minutes)
4. Configure historical data months (1-48) and re-import behavior
5. Click **SUBMIT**

The integration will automatically reload with the new interval.

⚠️ **Warning**: Shorter intervals may hit API rate limits.

### Debugging

Enable debug logging for detailed troubleshooting:

1. Edit `configuration.yaml`:

   ```yaml
   logger:
     default: info
     logs:
       custom_components.oura: debug
   ```

2. Restart Home Assistant

3. Check logs at **Settings**  **System**  **Logs**

### Reconcile Late-Arriving Statistics Data

If you had downtime or delayed Oura cloud ingestion and need to backfill long-term statistics:

1. Go to **Developer Tools** → **Actions**
2. Choose service: `oura.reconcile_statistics`
3. Optional: set `days` to your desired reconciliation window
4. Run service

You can also configure daily reconciliation in integration options via **Statistics Reconcile Window**.

## Getting Help

If you're still experiencing issues:

1. **Check Logs**: Settings  System  Logs  Filter for "oura"
2. **Search Issues**: [GitHub Issues](https://github.com/louispires/oura-v2-custom-component/issues)
3. **Create New Issue**: Include:
   - Home Assistant version
   - Integration version
   - Error messages from logs
   - Steps to reproduce
   - Screenshot if applicable

## Next Steps

Once installed:

- [Create dashboard cards](../README.md#dashboard-examples)
- [Set up automations](../README.md#usage)
- [Explore all available sensors](../README.md#available-sensors)

---

**Need more help?** Visit the [main README](../README.md) or [open an issue](https://github.com/louispires/oura-v2-custom-component/issues).
