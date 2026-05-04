# 🚀 Quick Commands Reference

Copy and paste these commands to test your Google Fit sync:

---

## 1️⃣ GET YOUR JWT TOKEN

First, login to get your auth token:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

Copy the `access_token` from response. Use it in other commands as `YOUR_TOKEN`.

---

## 2️⃣ VIEW YOUR DATA

### Get Latest 20 Records
```bash
curl -X GET "http://localhost:8000/api/v1/monitor/history/1?limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Heart Rate Trend (Last 7 Days)
```bash
curl -X GET "http://localhost:8000/api/v1/monitor/trends/1?metric=heart_rate&period=week" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Step Count Trend
```bash
curl -X GET "http://localhost:8000/api/v1/monitor/trends/1?metric=steps&period=week" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Health Summary
```bash
curl -X GET http://localhost:8000/api/v1/monitor/summary/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Latest Vitals Only
```bash
curl -X GET http://localhost:8000/api/v1/monitor/latest/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 3️⃣ TRIGGER MANUAL SYNC

### Sync All Sources
```bash
curl -X POST http://localhost:8000/api/v1/data/sync/all \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Sync Google Fit Only
```bash
curl -X POST http://localhost:8000/api/v1/data/sync/google-fit \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Sync Fitbit Only
```bash
curl -X POST http://localhost:8000/api/v1/data/sync/fitbit \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 4️⃣ LOG MANUAL ENTRY

```bash
curl -X POST http://localhost:8000/api/v1/data/manual \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "heart_rate": 72,
    "blood_pressure_systolic": 120,
    "blood_pressure_diastolic": 80,
    "spo2": 98.5,
    "steps": 500,
    "calories_burned": 25.5
  }'
```

---

## 5️⃣ CHECK DATABASE

### Count Total Records
```bash
sqlite3 heart_health.db "SELECT COUNT(*) as total FROM watch_data;"
```

### Show Last 10 Records
```bash
sqlite3 heart_health.db "
SELECT timestamp, heart_rate, spo2, steps, source 
FROM watch_data 
ORDER BY timestamp DESC 
LIMIT 10;
"
```

### Count by Source
```bash
sqlite3 heart_health.db "SELECT source, COUNT(*) as count FROM watch_data GROUP BY source;"
```

### Show Average Vitals
```bash
sqlite3 heart_health.db "
SELECT 
  ROUND(AVG(heart_rate), 1) as avg_hr,
  ROUND(AVG(spo2), 1) as avg_spo2,
  SUM(steps) as total_steps
FROM watch_data
WHERE source = 'google_fit';
"
```

### Find Abnormal Records
```bash
sqlite3 heart_health.db "
SELECT timestamp, heart_rate, spo2 
FROM watch_data
WHERE heart_rate > 120 OR heart_rate < 40 OR spo2 < 90
ORDER BY timestamp DESC;
"
```

---

## 6️⃣ EXPORT DATA

### Export to CSV
```bash
sqlite3 -header -csv heart_health.db \
  "SELECT timestamp, heart_rate, spo2, steps, source FROM watch_data" \
  > health_data.csv
```

### Export Last 24 Hours
```bash
sqlite3 -header -csv heart_health.db "
SELECT * FROM watch_data 
WHERE datetime(timestamp) > datetime('now', '-1 day')
" > last_24_hours.csv
```

### Export to JSON (using Python)
```python
import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('heart_health.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM watch_data ORDER BY timestamp DESC LIMIT 100')

columns = [description[0] for description in cursor.description]
records = cursor.fetchall()

data = [dict(zip(columns, record)) for record in records]

with open('health_data.json', 'w') as f:
    json.dump(data, f, indent=2, default=str)

print(f"Exported {len(data)} records to health_data.json")
```

Run with: `python export_data.py`

---

## 7️⃣ MONITOR AUTO-SYNC

### Watch Logs in Real-Time
```bash
# Open a new terminal and run:
tail -f ~/.local/share/Heart/sync.log
```

### Check Last Sync Time
```bash
sqlite3 heart_health.db "SELECT MAX(timestamp) as last_sync FROM watch_data;"
```

### See Sync Activity
```bash
# Check terminal where app is running - you should see:
# 🔄 Auto-syncing data for user 1...
# 🟢 Data synced from google_fit
# ✅ Auto-sync completed for user 1
```

---

## 8️⃣ CONFIGURATION CHANGES

### Edit Sync Interval (in `.env`)
```bash
# Change to sync every 10 minutes instead of 5
echo "AUTO_SYNC_INTERVAL_MINUTES=10" >> .env

# Then restart: Ctrl+C and python main.py
```

### Disable Auto-Sync (in `.env`)
```bash
echo "AUTO_SYNC_ENABLED=false" >> .env

# Then restart
```

### Re-enable Auto-Sync
```bash
# Edit .env and change AUTO_SYNC_ENABLED=true
# Then restart
```

---

## 9️⃣ TROUBLESHOOTING COMMANDS

### Is App Running?
```bash
curl http://localhost:8000/
# Should return module info
```

### Check API Docs
```bash
# Open in browser: http://localhost:8000/docs
```

### List All Connected Sources
```bash
curl -X GET http://localhost:8000/api/v1/data/sources/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Force Database Rebuild
```bash
# Remove old database
rm heart_health.db

# Restart app - will auto-create new one
# Ctrl+C then python main.py
```

### Check Python Environment
```bash
source .venv/bin/activate
python --version
pip list | grep -E "fastapi|sqlalchemy|librosa"
```

### View App Logs
```bash
# Terminal where app is running shows:
# - Startup messages
# - Sync status
# - Any errors
# - API requests (GET, POST, etc.)
```

---

## 🔟 COMMON USE CASES

### "I want to see all my heart rate data from today"
```bash
sqlite3 heart_health.db "
SELECT timestamp, heart_rate, source 
FROM watch_data 
WHERE DATE(timestamp) = DATE('now')
ORDER BY timestamp DESC;
"
```

### "Show me my average HR by hour today"
```bash
sqlite3 heart_health.db "
SELECT 
  strftime('%H:00', timestamp) as hour,
  ROUND(AVG(heart_rate), 1) as avg_hr,
  MIN(heart_rate) as min_hr,
  MAX(heart_rate) as max_hr
FROM watch_data
WHERE DATE(timestamp) = DATE('now')
GROUP BY hour
ORDER BY hour DESC;
"
```

### "I want data only from Google Fit"
```bash
curl -X GET "http://localhost:8000/api/v1/monitor/history/1?limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq '.history[] | select(.source == "google_fit")'
```

### "Show me weekly statistics"
```bash
sqlite3 heart_health.db "
SELECT 
  strftime('%Y-W%W', timestamp) as week,
  ROUND(AVG(heart_rate), 1) as avg_hr,
  ROUND(AVG(spo2), 1) as avg_spo2,
  SUM(steps) as total_steps,
  COUNT(*) as data_points
FROM watch_data
GROUP BY week
ORDER BY week DESC
LIMIT 4;
"
```

### "Delete old data (keep only last 30 days)"
```bash
sqlite3 heart_health.db "
DELETE FROM watch_data 
WHERE datetime(timestamp) < datetime('now', '-30 days');
"
```

---

## ⚡ Pro Tips

### 1. Save Common Queries
```bash
# Create a file called queries.sh
cat > queries.sh << 'EOF'
#!/bin/bash
echo "=== Last 10 Records ==="
sqlite3 heart_health.db "SELECT timestamp, heart_rate FROM watch_data LIMIT 10;"

echo "=== Today's Average HR ==="
sqlite3 heart_health.db "SELECT AVG(heart_rate) FROM watch_data WHERE DATE(timestamp) = DATE('now');"
EOF

chmod +x queries.sh
./queries.sh
```

### 2. Pretty Print JSON
```bash
curl -s http://localhost:8000/api/v1/monitor/history/1 \
  -H "Authorization: Bearer TOKEN" | python -m json.tool
```

### 3. Watch Auto-Sync in Real-Time
```bash
# Terminal 1: Watch database
watch -n 5 'sqlite3 heart_health.db "SELECT COUNT(*) FROM watch_data;"'

# Terminal 2: Check last update
watch -n 5 'sqlite3 heart_health.db "SELECT MAX(timestamp) FROM watch_data;"'
```

### 4. Test Endpoint Performance
```bash
time curl -X GET http://localhost:8000/api/v1/monitor/history/1?limit=100 \
  -H "Authorization: Bearer YOUR_TOKEN" > /dev/null
```

---

## 📋 Complete Workflow Example

```bash
#!/bin/bash
# Complete workflow script

TOKEN="your-jwt-token-here"
USER_ID=1

echo "📊 === Heart Health Data Dashboard === 📊"
echo ""

echo "1️⃣  Latest Vitals:"
curl -s "http://localhost:8000/api/v1/monitor/latest/$USER_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.data'

echo ""
echo "2️⃣  Last 5 Records:"
curl -s "http://localhost:8000/api/v1/monitor/history/$USER_ID?limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq '.history[] | {timestamp, heart_rate, spo2}'

echo ""
echo "3️⃣  Health Summary:"
curl -s "http://localhost:8000/api/v1/monitor/summary/$USER_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.jarvis_briefing'

echo ""
echo "4️⃣  Database Stats:"
sqlite3 heart_health.db "SELECT COUNT(*) as total_records, COUNT(DISTINCT source) as sources FROM watch_data;"

echo ""
echo "✅ Dashboard Updated!"
```

Save as `dashboard.sh` and run: `bash dashboard.sh`

---

## 🎯 Quick Status Check

Run this to verify everything is working:

```bash
echo "✅ Checking Heart Health Module Status..."
echo ""

echo "1. API Running?"
curl -s http://localhost:8000/ > /dev/null && echo "✅ API is UP" || echo "❌ API is DOWN"

echo "2. Database?"
[ -f heart_health.db ] && echo "✅ Database exists" || echo "❌ Database missing"

echo "3. Records Count:"
sqlite3 heart_health.db "SELECT COUNT(*) FROM watch_data;" 2>/dev/null || echo "❌ Database error"

echo "4. Last Sync:"
sqlite3 heart_health.db "SELECT MAX(timestamp) FROM watch_data;" 2>/dev/null || echo "❌ No data"

echo ""
echo "✅ Status check complete!"
```

---

**Save this file for quick reference!**  
**Copy commands as needed for your workflow.**
