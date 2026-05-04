# Google Fit Data Sync Guide

## ✅ What We've Implemented

We've enhanced your Heart Health Module with powerful data syncing capabilities:

1. **✅ New History Endpoint** - `/api/v1/monitor/history/{user_id}` - Returns all synced vitals
2. **✅ Auto-Sync Feature** - Automatically syncs data every 5 minutes
3. **✅ Manual Sync Endpoints** - Trigger sync on-demand
4. **✅ Database Integration** - All data stored in `watch_data` table

---

## 🚀 Quick Start: View Your Synced Data

### Step 1: Check Data in Dashboard

Open [http://localhost:8000/static/dashboard/index.html](http://localhost:8000/static/dashboard/index.html)

Your Google Fit data should now display showing:
- ❤️ Heart Rate (bpm)
- 📊 Blood Pressure (sys/dia)
- 💨 SpO2 (%)
- 👟 Steps
- 🏃 Activity minutes
- 🔥 Calories burned

### Step 2: View All Synced Records (JSON)

Copy your JWT token from browser localStorage, then run:

```bash
# Get all historical vitals
curl -X GET http://localhost:8000/api/v1/monitor/history/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response Example:**
```json
{
  "latest": {
    "id": 6374,
    "timestamp": "2026-04-05T13:30:05.564437",
    "heart_rate": 75.7,
    "spo2": 97.6,
    "steps": 1138,
    "sys_bp": null,
    "dia_bp": null,
    "calories": 53.1,
    "sleep_stage": null,
    "source": "google_fit"
  },
  "history": [
    { ...6373 more records... }
  ],
  "total_records": 6374
}
```

### Step 3: Check Database Directly

See all synced records in the database:

```bash
sqlite3 heart_health.db "SELECT timestamp, heart_rate, spo2, steps, source FROM watch_data ORDER BY timestamp DESC LIMIT 20;"
```

---

## 🔄 How Auto-Sync Works

### Automatic Sync Every 5 Minutes

The system now automatically syncs Google Fit data every 5 minutes:

```
Application Start
     ↓
🔄 Auto-sync initialized (every 5 minutes)
     ↓
Every 5 minutes:
  - Fetch from all connected sources (Google Fit, Fitbit, Firebolt, etc.)
  - Store in database
  - Check for anomalies
  - Generate alerts if needed
```

### Configuration

In your `.env` file:

```env
# Auto-sync settings (default: enabled)
AUTO_SYNC_ENABLED=true
AUTO_SYNC_INTERVAL_MINUTES=5
```

Change to sync every 10 minutes:
```env
AUTO_SYNC_INTERVAL_MINUTES=10
```

Disable auto-sync:
```env
AUTO_SYNC_ENABLED=false
```

---

## 📡 Manual Sync Endpoints

### Sync All Sources

```bash
curl -X POST http://localhost:8000/api/v1/data/sync/all \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Sync Only Google Fit

```bash
curl -X POST http://localhost:8000/api/v1/data/sync/google-fit \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Sync Only Fitbit

```bash
curl -X POST http://localhost:8000/api/v1/data/sync/fitbit \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 📊 Dashboard Data Display

The dashboard now displays:

### Real-Time Latest Vitals
```
Heart Rate:      75 bpm
Blood Pressure:  120/80 mmHg
SpO2:           97.6 %
Steps:          1,138
Calories:       53.1 kcal
```

### Data Source Badge
Each metric shows which source it came from:
- 🟢 Google Fit (green)
- 🔵 Fitbit (blue)
- 🔥 Firebolt (orange)
- ✏️ Manual (gray)

### Historical Chart
A 7-day trend graph showing:
- Heart rate over time
- Step count trends
- SpO2 patterns
- Activity levels

---

## 🔍 API Endpoints Reference

### Get Historical Data
```
GET /api/v1/monitor/history/{user_id}?limit=50
```
- Returns latest 50 records (configurable)
- Sorted by timestamp (newest first)
- Includes source information

### Get Trend Data
```
GET /api/v1/monitor/trends/{user_id}?metric=heart_rate&period=week
```
- Metrics: `heart_rate`, `spo2`, `steps`, `sleep_stage`
- Periods: `day`, `week`, `month`, `year`
- Returns dates and values for charting

### Get Latest Vitals
```
GET /api/v1/monitor/latest/{user_id}
```
- Single most recent record
- All vitals in one response
- Includes timestamp

### Get Health Summary
```
GET /api/v1/monitor/summary/{user_id}
```
- Comprehensive health analysis
- JARVIS-generated briefing
- Recommendations
- Alerts summary

---

## 🎯 Data Flow Diagram

```
┌─────────────────────────────┐
│   Google Fit App (Mobile)   │
│   (Your Android Phone)      │
└──────────┬──────────────────┘
           │
           │ [Synced data]
           ↓
┌─────────────────────────────────┐
│  Heart Health Module v2         │
│  (http://localhost:8000)        │
│                                 │
│  ┌─────────────────────────┐   │
│  │  Auto-Sync Task         │   │
│  │  (Every 5 minutes)      │   │
│  └────────┬────────────────┘   │
│           │                     │
│           ↓                     │
│  ┌─────────────────────────┐   │
│  │  Data Sources Layer     │   │
│  │  • Google Fit Connector │   │
│  │  • Data Fusion Engine   │   │
│  └────────┬────────────────┘   │
│           │                     │
│           ↓                     │
│  ┌─────────────────────────┐   │
│  │  watch_data Table       │   │
│  │  (Stored in DB)         │   │
│  │  6,000+ records         │   │
│  └────────┬────────────────┘   │
│           │                     │
│           ↓                     │
│  ┌─────────────────────────┐   │
│  │  API Endpoints          │   │
│  │  /monitor/history       │   │
│  │  /monitor/trends        │   │
│  │  /monitor/latest        │   │
│  └────────┬────────────────┘   │
└───────────┼────────────────────┘
            │
            ↓
┌─────────────────────────────┐
│  Dashboard (Web UI)         │
│  Charts & Visualizations    │
│  Real-time Updates          │
└─────────────────────────────┘
```

---

## 🐛 Troubleshooting

### ❌ "No data showing on dashboard"

**Solution:**
1. Check if Google Fit is connected:
   ```bash
   curl http://localhost:8000/api/v1/data/sources/1
   ```
   Should show `"google_fit": "connected"`

2. Manually trigger sync:
   ```bash
   curl -X POST http://localhost:8000/api/v1/data/sync/all
   ```

3. Check database:
   ```bash
   sqlite3 heart_health.db "SELECT COUNT(*) FROM watch_data;"
   ```
   Should return > 0

4. Clear browser cache:
   - Mac: `Cmd + Shift + Delete`
   - Refresh: `Cmd + R`

### ❌ "Auto-sync not working"

**Solution:**
1. Check logs - look for `🔄 Auto-sync enabled` message
2. Check config:
   ```bash
   grep AUTO_SYNC .env
   ```
3. Restart application:
   - Stop: `Ctrl + C`
   - Start: `python main.py`

### ❌ "Google Fit connection lost"

**Solution:**
1. Disconnect and reconnect:
   - Dashboard → Connected Devices → Google Fit → Disconnect
   - Click "Connect with OAuth"
   - Re-authorize

2. Check credentials in `.env`:
   ```bash
   grep GOOGLE_FIT .env
   ```

3. Ensure tokens haven't expired:
   - Google Fit tokens expire after 24 hours
   - System should auto-refresh, but manually reconnect if needed

### ✅ "Data is syncing but timestamps are wrong"

**Solution:**
This is expected - Google Fit returns data in UTC timezone. The system uses UTC internally and converts to local time in the dashboard.

---

## 📈 Monitoring Sync Status

### View Sync Logs

```bash
# Watch logs in real-time
tail -f ~/.local/share/Heart/sync.log

# Or check terminal output where app is running
```

### Check Last Sync Time

```bash
sqlite3 heart_health.db "SELECT timestamp FROM watch_data ORDER BY timestamp DESC LIMIT 1;"
```

### Count Records by Source

```bash
sqlite3 heart_health.db "SELECT source, COUNT(*) FROM watch_data GROUP BY source;"
```

Example output:
```
google_fit|1234
firebolt|5000
manual|100
fitbit|0
```

---

## 🎛️ Configuration Options

### Fine-Tune Sync Behavior

Edit `.env`:

```env
# Sync frequency (in minutes)
AUTO_SYNC_INTERVAL_MINUTES=5

# Number of historical records to keep
HISTORY_RETENTION_DAYS=90

# Enable/disable per-source
AUTO_SYNC_GOOGLE_FIT=true
AUTO_SYNC_FITBIT=true
AUTO_SYNC_FIREBOLT=true

# Alert thresholds
ALERT_HIGH_HR=120
ALERT_LOW_HR=40
ALERT_HIGH_BP=160/100
```

---

## 🔐 Security Notes

- **JWT Tokens**: All API calls require authentication
- **OAuth**: Google Fit uses OAuth 2.0 with secure code exchange
- **Data Privacy**: Data stored locally in SQLite (not sent to cloud)
- **Rate Limiting**: Each user can sync max 10 times per minute

---

## 📱 Next Steps

### 1. Monitor Your Health Trends
- Open dashboard daily
- Check historical trends
- Set custom alerts

### 2. Connect More Devices
- Fitbit
- Apple Health (iOS alternative)
- Firebolt data warehouse

### 3. Enable Notifications
- Email alerts for abnormalities
- SMS alerts for emergencies
- Push notifications in app

### 4. Export Your Data
```bash
# Export to CSV
sqlite3 -header -csv heart_health.db "SELECT * FROM watch_data;" > health_data.csv
```

---

## 🎓 Example: Custom Data Analysis

### Get last 24 hours of data:
```bash
sqlite3 heart_health.db "
SELECT 
  timestamp,
  heart_rate,
  spo2,
  steps,
  source
FROM watch_data
WHERE datetime(timestamp) > datetime('now', '-1 day')
ORDER BY timestamp DESC;
"
```

### Calculate daily average heart rate:
```bash
sqlite3 heart_health.db "
SELECT 
  DATE(timestamp) as day,
  ROUND(AVG(heart_rate), 1) as avg_hr,
  MIN(heart_rate) as min_hr,
  MAX(heart_rate) as max_hr
FROM watch_data
GROUP BY DATE(timestamp)
ORDER BY day DESC;
"
```

### Find anomalies:
```bash
sqlite3 heart_health.db "
SELECT 
  timestamp,
  heart_rate,
  spo2
FROM watch_data
WHERE heart_rate > 120 OR heart_rate < 40 OR spo2 < 90
ORDER BY timestamp DESC;
"
```

---

## 💡 Pro Tips

1. **Sync Before Sleep**: Data syncs automatically every 5 minutes
2. **Export Weekly**: Keep backups of your data
3. **Set Alerts**: Configure thresholds for your health
4. **Track Trends**: Look at weekly/monthly patterns, not just daily
5. **Integrate Other Sources**: Add Fitbit, Apple Health for complete picture

---

## 📞 Support

If you encounter issues:

1. Check logs: `tail -f ~/.local/share/Heart/sync.log`
2. Test connectivity: `curl http://localhost:8000/docs`
3. Verify database: `sqlite3 heart_health.db ".tables"`
4. Restart server: `Ctrl+C` then `python main.py`

---

**Last Updated**: April 5, 2026  
**Version**: 2.0.0  
**Status**: ✅ Auto-sync Active
