# ⚡ Quick Start: Google Fit Real Data Sync

## 🎯 What You Need to Do Right Now

### 1️⃣ Open Dashboard
```
http://localhost:8000/static/dashboard/index.html
```

### 2️⃣ Connect Google Fit
- Click **Devices** tab (📱 icon)
- Click **Google Fit** card
- Click **"Connect with OAuth"** button
- Sign in with **your Gmail** (the one with Fit data)
- Grant permissions
- ✅ See success message

### 3️⃣ Wait for Sync
- Auto-sync happens **every 5 minutes**
- First sync is **immediate** after connecting
- Watch the **Dashboard** tab for real data

### 4️⃣ Verify Real Data
Your dashboard should now show:
- ❤️ Real heart rate from your phone
- 👟 Real step count
- 💨 Real SpO2 if available
- 📊 Historical data

---

## 🔍 Check It's Working

### In Browser
1. Open **Dashboard** tab
2. Look for your real heart rate & steps
3. Values should match your Android Fit app

### In Terminal
```bash
# Watch for real Google Fit data syncing
tail -f server.log | grep "Google Fit"

# Should see:
# ✅ Fetched X real readings from Google Fit for user 1
```

### In Database
```bash
# Check tokens were saved
sqlite3 heart_health.db "SELECT config FROM data_sources WHERE source_type='google_fit' LIMIT 1;"

# Should show JSON with access_token
```

---

## 🚀 What Happens After

1. **Tokens Saved** → Real Google Fit API calls start
2. **Data Flows** → Your actual health metrics appear
3. **Auto-Updates** → Dashboard refreshes every 5 minutes
4. **Alerts Ready** → System monitors for anomalies
5. **AI Analysis** → Cardia chat can discuss your health

---

## 📱 Your Data from Android Fit

From your screenshot:
- ✅ 299 Steps → Will appear on dashboard
- ✅ 70 BPM Heart Rate → Will display in live chart
- ✅ Historical 7-day data → Will load in history
- ✅ Calories, activity → All synced automatically

---

## ⚠️ If It Doesn't Work

### Check 1: Server Running?
```bash
curl http://localhost:8000/api/v1/data/google-fit/auth-url
# Should return JSON with auth_url
```

### Check 2: Tokens Saved?
```bash
sqlite3 heart_health.db "SELECT COUNT(*) FROM data_sources WHERE source_type='google_fit';"
# Should return 1
```

### Check 3: Browser Console
- F12 → Console tab
- Look for red errors
- Check Network tab for failed requests

### Check 4: Try Manual Sync
```bash
curl -X POST http://localhost:8000/api/v1/data/sync/google-fit
```

### Check 5: Clear Cache
- Ctrl+Shift+Delete (Windows/Linux)
- Cmd+Shift+Delete (Mac)
- Clear all for localhost:8000
- Reload dashboard

---

## 📞 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "Error connecting" popup | Restart server with `python main.py` |
| Google Fit shows "Not connected" | Click Connect again with same Gmail |
| Dashboard shows simulated data | Reconnect Google Fit (tokens not saved) |
| No data after 5 minutes | Check server logs for errors |
| WebSocket failed | Browser firewall, reload page |

---

## 🎉 Success Looks Like

**Before**:
- Dashboard shows random numbers
- Values change every second
- Doesn't match your phone

**After**: ✅
- Dashboard shows your real steps (299 or whatever you have)
- Dashboard shows your real heart rate (70 or whatever)
- Values match your Android Fit app exactly
- Updates every 5 minutes via auto-sync
- Historical data loads from last 24 hours

---

## 📊 Dashboard Features to Explore

Once real data is syncing:

1. **Dashboard Tab** - Real-time vitals
2. **Risk Scan Tab** - Heart attack risk prediction
3. **Reports Tab** - Upload ECG/heart sound files
4. **Devices Tab** - Manage connections
5. **Cardia Chat** - Ask health questions

---

## 🛠️ Server Commands

```bash
# Start server
cd /Users/sujalnivruttipagere/Desktop/Heart
source .venv/bin/activate
python main.py

# View logs (watch for Google Fit messages)
tail -f server.log | grep -v sqlalchemy

# Kill server if needed
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Test API is working
curl -s http://localhost:8000/docs | head -5
```

---

## ✨ That's It!

Your system is now set up to:
1. Accept your real Google Fit data
2. Display it on the dashboard
3. Analyze it with AI
4. Generate health alerts

**Go connect Google Fit now!** 🚀

---

**Server Location**: http://localhost:8000  
**Dashboard**: http://localhost:8000/static/dashboard/index.html  
**Updated**: 2026-04-05 21:10 UTC
