# Troubleshooting Guide

- [OAuth Setup Fails with "401 Unauthorized"](#oauth-setup-fails-with-401-unauthorized)
- [Authentication Stops Working Later](#authentication-stops-working-later)
- [Sensors Missing or Unavailable](#sensors-missing-or-unavailable)
- [API Rate Limiting](#api-rate-limiting)
- [Long-Term Statistics Look Wrong (v2.10.1 and earlier)](#long-term-statistics-look-wrong-v2101-and-earlier)
- [Negative Changes on Sum Statistics](#negative-changes-on-sum-statistics)
- [Removing the Integration & Your Data](#removing-the-integration--your-data)
- [Integration Not Appearing](#integration-not-appearing)

## OAuth Setup Fails with "401 Unauthorized"

If adding the integration fails right after you approve access on Oura's site (log shows
`Error resolving OAuth token: 401 ... url='https://moi.ouraring.com/oauth/v2/ext/oauth-token'`
or a bare "OAuth token rejected" abort), check the following:

1. **Redirect URI**: your Oura app must register `https://my.home-assistant.io/redirect/oauth`
   exactly — see [FIXING_REDIRECT_URI.md](FIXING_REDIRECT_URI.md).
2. **Developer portal**: confirm which portal you registered the app on
   (`developer.ouraring.com` vs the legacy `cloud.ouraring.com/oauth/applications`). Both are
   supported; since v2.10.0 the integration tries `moi.ouraring.com` first (the endpoint Oura
   actually uses today — `cloud.ouraring.com`'s own docs are stale here) and falls back to the
   legacy endpoint automatically.
3. **Client secret**: if it was regenerated after the app was first configured in HA, remove
   and re-add the Application Credential with the current secret.
4. **Debug logs**: enable `homeassistant.helpers.config_entry_oauth2_flow: debug` and
   `custom_components.oura: debug` in `configuration.yaml` and retry — the log will show which
   endpoint was tried and the HTTP status returned.

If none of the above resolves it, open an issue with the debug log (redact your client_id).

## Authentication Stops Working Later

Home Assistant refreshes the OAuth token automatically. If Oura rejects the refresh (revoked access, regenerated client secret, deleted app), Home Assistant shows a **Re-authenticate** prompt for Oura Ring under **Settings → Devices & Services**. Follow it and sign in with the **same** Oura account; signing in with a different account aborts with "You must re-authenticate with the same Oura account".

## Sensors Missing or Unavailable

If sensors have no values:

1. Open the Oura app so the ring syncs. Sleep, readiness, and sleep-time data only reach Oura's cloud after an app sync; activity, stress, and heart rate also sync in the background.
2. Wait for the next update (default every 5 minutes).
3. Check **Settings → System → Logs** for `oura` errors.

If almost every sensor is unavailable at once, check **Ring Last Sync** (`sensor.oura_ring_ring_last_sync`). A time days in the past means nothing new has reached Oura's cloud since then: the ring has not synced through the Oura app, so there is nothing for the integration to show. Sensors only report data from the last day.

An unavailable sensor is usually expected. Oura simply sends no value for it yet:

- **Contributor scores** (Resting Heart Rate Score, HRV Balance Score, Sleep Regularity Score) need enough recent data, e.g. a full night of HRV.
- **New rings** (first few weeks): Cardiovascular Age, VO2 Max, Stress High Duration, Recovery High Duration, Stress Day Summary, the resilience scores, and Optimal Bedtime Start/End need a baseline first.
- **Ring or membership limits**: SpO2 needs a Gen 3, Ring 4, or Ring 5; VO2 Max, Cardiovascular Age, and Pulse Wave Velocity need an Oura membership. Oura answers these with 401/403, which the integration treats as "no data" rather than an error. An expired membership has the same effect on all of them.
- **Latest Bedtime End** stays unavailable while the latest sleep session is still in progress.
- Gaps after periods of not wearing the ring.

Sensors become available on their own once Oura provides values. The [Sensor Reference](SENSORS.md) marks sensors that are often unavailable with ⚠️.

## API Rate Limiting

The integration retries a `429 Too Many Requests` once, waiting for the `Retry-After` time Oura sends (capped at 30 seconds). If you still see rate-limit errors:

- Use the default 5-minute update interval or longer.
- Large historical imports (many months) make many requests; let them finish before reloading.
- Check whether other tools use the same Oura application credentials.

## Long-Term Statistics Look Wrong (v2.10.1 and earlier)

### Some sensors' history starts on the install day ([#81](https://github.com/louispires/Oura-Home-Assistant-Integration/issues/81))

On a fresh install with v2.10.1 or earlier, the historical import ran before the sensors were
registered. Sensors whose entity ID differs from their internal key (e.g. the `*_contribution`
sensors, `Average Breathing Rate`, `Minimum/Maximum Heart Rate`, the MET-minutes sensors) had
their history stored under unused `sensor.oura_ring_<key>` statistic IDs. Fixed in v2.10.2.

To repair an existing install:

1. **Settings → Devices & Services → Oura Ring → Configure**, turn **Historical data already
   imported** off and save. The entry reloads and re-imports the history into the correct entities.
2. **Developer tools → Statistics**: delete the leftover `sensor.oura_ring_<key>` entries that
   are reported as no longer provided by an entity.

### Huge negative/positive bar a few days back on sum statistics ([#80](https://github.com/louispires/Oura-Home-Assistant-Integration/issues/80))

Steps, calories, sleep durations and other sum statistics could show one huge bar at the start
of the daily reconcile window, because the cumulative sum before the window was read from the
wrong row. Fixed in v2.10.2.

To repair stored sums, after upgrading call the `oura.reconcile_statistics` action once with
`days` covering your imported history (e.g. `90` for the default 3 months, max `1440`):

```yaml
action: oura.reconcile_statistics
data:
  days: 90
```

The re-import rewrites every cumulative sum in that range; nothing needs to be deleted.
From v2.12.0 the re-import no longer writes the sums of sensors with an entity; see below.

## Negative Changes on Sum Statistics

([#86](https://github.com/louispires/Oura-Home-Assistant-Integration/issues/86))

Up to v2.11.0 two writers kept two different running sums in the statistic of each daily sum
sensor (steps, calories, sleep durations, …): Home Assistant's recorder, hourly from the
sensor's state, and the integration's daily import at 12:00 UTC. `statistics-graph` cards using
`change` showed jumps up and back down, negative days, and sums that restarted. On top of
that, the daily sensors had no `last_reset`, so the drop back to a small value on a new day
counted as a decrease.

Fixed in v2.12.0:

- The recorder is the only writer of every sum statistic. The integration no longer imports
  sums into the daily sensors' statistics.
- The history of the daily sums lives in the new **Lifetime** counters
  ([Sensor Reference](SENSORS.md#lifetime-counters-19)). Their statistic gets the imported
  history once; after that the recorder writes it, and data Oura syncs late is moved onto the
  day it belongs to. Use them for daily/weekly/monthly totals
  ([example](DASHBOARDS.md#daily-history-from-lifetime-counters)).
- The daily `total` sensors report the start of their Oura day as `last_reset`, so a new day
  starts a new cycle. `Equivalent Walking Distance` is now a `total` sensor too.

What stays: rows written before the upgrade are not rewritten, so the daily sensors' old
statistics keep their jumps. On the first update after upgrading, each daily `total` sensor
starts its first cycle, and today's value so far is counted once more. For clean history use
the Lifetime counters, or delete a daily sensor's statistics under **Developer tools →
Statistics** to let the recorder start fresh.

Installs from before v2.12.0 load the Lifetime counters' history in the background after the
first restart (the configured number of historical months); the counters are unavailable until
then.

## Removing the Integration & Your Data

If you want to fully remove the integration and all locally stored Oura data from Home Assistant:

### Step 1: Revoke OAuth access in Oura

1. Go to [Oura Cloud](https://cloud.ouraring.com) → Account → Connected Apps
2. Remove the Home Assistant application

This immediately stops all future API calls. Per [Oura's Privacy Policy](https://ouraring.com/privacy-policy), revoking access prevents future data transfers but does not automatically delete data already stored locally.

### Step 2: Delete the integration entry in Home Assistant

1. Go to **Settings → Devices & Services**
2. Find **Oura Ring** and click the three-dot menu → **Delete**
3. Restart Home Assistant

Deleting the entry removes the Oura Ring device and its entities. Recorded data is not deleted immediately:

- **State history** ages out with the recorder's normal purge (10 days by default).
- **Long-term statistics** stay until you delete them: go to **Developer tools → Statistics**, where they are listed as no longer provided by an entity, and remove them.

> **Note:** If you only revoke OAuth in Oura (step 1) without deleting in HA (step 2), historical data already imported into Home Assistant's statistics database will remain on your local instance. Complete all steps for a full removal.

---

## Integration Not Appearing

If you've copied the integration to custom_components but can't see it when trying to add integrations, follow these steps:

### Step 1: Verify File Structure

Your Home Assistant config directory should look like this:

```text
config/
  custom_components/
    oura/
      __init__.py
      api.py
      application_credentials.py
      binary_sensor.py
      config_flow.py
      const.py
      coordinator.py
      manifest.json
      sensor.py
      services.yaml
      statistics.py
      strings.json
      brand/
        icon.png
      translations/
        de.json
        en.json
        es.json
        fr.json
```

### Step 2: Check Home Assistant Logs

1. Go to Settings → System → Logs
2. Look for any errors containing "oura"
3. Common errors to look for:
   - Import errors
   - Manifest validation errors
   - Python syntax errors

### Step 3: Verify Manifest.json

The manifest.json must be valid JSON. Check that:

- No trailing commas
- All quotes are properly closed
- File is UTF-8 encoded

### Step 4: Restart Home Assistant

**Important**: A full restart is required, not just a reload:

1. Settings → System → Restart
2. Wait for Home Assistant to fully restart (check the UI comes back up)
3. Clear your browser cache (Ctrl+Shift+R or Cmd+Shift+R)

### Step 5: Check Integration Requirements

The integration needs:

- Valid manifest.json with all required fields
- Proper config_flow.py implementation
- OAuth2 flow properly configured

### Step 6: Enable Debug Logging

Add to your configuration.yaml:

```yaml
logger:
  default: warning
  logs:
    homeassistant.loader: debug
    custom_components.oura: debug
```

Then restart and check logs for detailed error messages.

### Common Issues and Fixes

#### Issue: "Integration has invalid manifest"

**Fix**: Check manifest.json syntax, ensure all required fields are present

#### Issue: "Failed to import component"

**Fix**: Check Python syntax in all .py files, verify imports

#### Issue: "Config flow not found"

**Fix**: Ensure config_flow.py has proper OuraFlowHandler class

#### Issue: Integration shows but configuration fails

**Fix**:

1. Check OAuth2 URLs in const.py
2. Verify application_credentials.py is present
3. Ensure you've set up application credentials first

### Manual Verification Steps

Run these commands from your Home Assistant config directory:

```bash
# Check if files exist
ls -la custom_components/oura/

# Validate JSON
cat custom_components/oura/manifest.json | python -m json.tool

# Check Python syntax
python3 -m py_compile custom_components/oura/__init__.py
python3 -m py_compile custom_components/oura/config_flow.py
```

### Still Not Working?

1. **Remove and re-copy files**:
   - Delete custom_components/oura/
   - Re-copy from the repository
   - Ensure no hidden files or cache

2. **Check file permissions**:
   - Files should be readable by the Home Assistant user
   - On Linux: chmod -R 755 custom_components/oura/

3. **Try a different browser**:
   - Clear cache completely
   - Try incognito/private mode

4. **Check Home Assistant version**:
   - This integration requires Home Assistant 2026.3.0 or newer
   - Update if necessary

### Getting Help

If still not working, gather this information:

1. Home Assistant version
2. Installation method (Docker, HAOS, Core, Supervised)
3. Full error from logs (Settings → System → Logs)
4. Output of: ls -la custom_components/oura/
5. Content of manifest.json

Then create an issue at: <https://github.com/louispires/Oura-Home-Assistant-Integration/issues>
