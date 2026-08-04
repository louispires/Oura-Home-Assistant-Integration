# CRITICAL FIX: Redirect URI Mismatch

## The Problem

Home Assistant is sending:
- redirect_uri: https://my.home-assistant.io/redirect/oauth

But your Oura application only has a different URI registered (e.g. your own domain or IP).

This integration always uses `https://my.home-assistant.io/redirect/oauth` as the redirect URI during OAuth — unconditionally, regardless of whether you're accessing Home Assistant via your local IP, a custom domain, Nabu Casa, or DuckDNS. It does not use your Home Assistant's own URL.

## The Solution

Register `https://my.home-assistant.io/redirect/oauth` as the Redirect URI in your Oura application. That is the only URI this integration will ever send — you do not need to register your own HA URL.

### Step 1: Update Your Oura Application

1. Go to: https://developer.ouraring.com/applications
2. Find your Home Assistant application
3. Click Edit
4. Set the Redirect URI to:

```
https://my.home-assistant.io/redirect/oauth
```

> **Note:** Oura's developer portal does not accept non-localhost `http://` URIs (e.g. `http://192.168.1.100:8123/...`). Use the `https://my.home-assistant.io/redirect/oauth` URI above — it works for all Home Assistant setups regardless of whether you access HA locally, via Nabu Casa, or via a custom domain.

### Step 2: How to Access Your Home Assistant

You can access Home Assistant however you normally do — the integration sends `https://my.home-assistant.io/redirect/oauth` unconditionally, so there is no need to access HA through my.home-assistant.io specifically. Your direct URL, local IP, Nabu Casa link, or DuckDNS URL all work.

### Step 3: After Updating Oura

1. Save your changes in Oura Cloud
2. Go back to Home Assistant
3. Settings → Devices & Services
4. Try adding the Oura Ring integration again (or reauthenticate if it was previously set up)
