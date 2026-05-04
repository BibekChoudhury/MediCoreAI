# 🔄 Google Fit Real Data Sync - Setup Guide

## Problem You're Experiencing

Your **Google Fit app on Android** has real data:
- ✅ 299 Steps today
- ✅ Heart Rate: 70 bpm  
- ✅ Historical data over 7 days

But the **Cardia dashboard** is showing **simulated data** that changes rapidly. This is because the OAuth access token wasn't being saved to the database after authentication.

## Solution: Updated Code ✨

I've just updated the system to **properly save and use your Google Fit tokens**:

### What Changed:

1. **OAuth Callback** (`api/v1/data_sources.py`)
   - Now saves `access_token` and `refresh_token` to the database after Google authentication
   - Stores tokens in the `data_sources` table with JSON config field

2. **Google Fit Connector** (`services/data_sources/google_fit.py`)
   - Loads tokens from database config when syncing
   - Uses real Google Fit API when tokens are available
   - Falls back to simulation only if no token exists

3. **Data Fusion Engine** (`services/data_sources/data_fusion.py`)
   - Queries database for saved sources and their tokens before syncing
   - Passes token config to connectors for real API calls

## How to Get Real Google Fit Data Syncing

### Step 1: Disconnect Google Fit (if already connected)
Go to the Devices tab → Google Fit → Click **"Connect with OAuth"** again

### Step 2: Authenticate with Google
- You'll be redirected to Google login
- **Important**: Use the SAME Gmail account that has the data in your Android Fit app
- Grant permissions to "Read" heart rate, steps, sleep data
- You should see: **✅ Google Fit Connected! Your health data is now syncing 🎉**

### Step 3: Check the Database
The tokens are now saved! Verify with:

```bash
sqlite3 heart_health.db
SELECT source_type, config FROM data_sources WHERE source_type='google_fit' LIMIT 1;
```

You should see a JSON config with `access_token` and `refresh_token`.

### Step 4: Watch Real Data Appear
- Wait for the auto-sync (every 5 minutes)
- Check the dashboard at: **http://localhost:8000/static/dashboard/index.html**
- Your real Google Fit data should now appear! 🎉

## What Data Will Sync

Once connected with real tokens, you'll get:
- ❤️ **Heart Rate** (from last 24 hours)
- 👟 **Steps** (daily totals)
- 💨 **SpO2** (if available from your device)
- 📊 **Historical data** (aggregated hourly)

## Debugging: Check Server Logs

While syncing, watch the logs for:

```bash
tail -f server.log | grep "Google Fit"
```

You should see:
- ✅ `✅ Fetched X real readings from Google Fit for user 1` → SUCCESS!
- ⚠️  `⚠️ Google Fit API error` → Token issue, needs reauth
- ℹ️  `ℹ️ No Google Fit access token` → Token not yet saved

## Token Refresh

If your Google Fit access token expires (after ~1 hour), the system will:
1. Automatically attempt to refresh using the `refresh_token`
2. Save the new token to database
3. Continue syncing seamlessly

## Still Not Working?

1. **Clear browser cache** - Old authentication might be cached
2. **Check .env file** - Make sure you have:
   ```
   GOOGLE_FIT_CLIENT_ID=your_client_id
   GOOGLE_FIT_CLIENT_SECRET=your_client_secret (or JSON key file)
   ```
3. **Restart server** - New changes require server restart
4. **Check database** - Verify tokens were saved:
   ```bash
   sqlite3 heart_health.db "SELECT config FROM data_sources WHERE source_type='google_fit';"
   ```

## Next Steps

After real Google Fit data is syncing:
- ✅ Set up **Fitbit** (same process, optional)
- ✅ Configure **Alert thresholds** (when to get notifications)
- ✅ Enable **Email/SMS alerts** if you want notifications

---

**Status**: ✅ Updated and ready!  
**Auto-Sync**: Every 5 minutes  
**Real-Time Monitoring**: WebSocket live data  
**Last Updated**: 2026-04-05
