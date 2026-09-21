# Troubleshooting Guide

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

Deleting the entry removes all associated entities and clears the long-term statistics recorded by this integration from Home Assistant's database.

> **Note:** If you only revoke OAuth in Oura (step 1) without deleting in HA (step 2), historical data already imported into Home Assistant's statistics database will remain on your local instance. Complete both steps for a full removal.

---

## Integration Not Appearing

## Issue: Oura Integration Not Showing in Home Assistant

If you've copied the integration to custom_components but can't see it when trying to add integrations, follow these steps:

### Step 1: Verify File Structure

Your Home Assistant config directory should look like this:

```
config/
  custom_components/
    oura/
      __init__.py
      api.py
      application_credentials.py
      config_flow.py
      const.py
      coordinator.py
      manifest.json
      sensor.py
      strings.json
      translations/
        en.json
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
   - Use a currently supported Home Assistant version
   - Update if necessary

### Getting Help

If still not working, gather this information:

1. Home Assistant version
2. Installation method (Docker, HAOS, Core, Supervised)
3. Full error from logs (Settings → System → Logs)
4. Output of: ls -la custom_components/oura/
5. Content of manifest.json

Then create an issue at: <https://github.com/louispires/oura-v2-custom-component/issues>
