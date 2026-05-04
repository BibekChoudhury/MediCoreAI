# 🏗️ Modern Architecture: Android Health Connect Integration (2026)

## Current Problem ❌

Your browser-based web app is trying to OAuth directly with Google Fit REST API:
- ❌ Google Fit REST API is **deprecated** as of 2026
- ❌ Health Connect (the new standard) **requires Android-side access**
- ❌ Browser cannot directly read Android health data (security restriction)
- ❌ OAuth flow in browser won't work for real Health Connect data

Result: Falling back to simulated data, getting 403 errors

---

## ✅ Correct 2026 Architecture

### Modern Flow:
```
Android Phone (with Health Connect app)
    ↓ Reads real steps, heart rate, sleep
    ↓ from Health Connect API
    ↓
Android Companion App (Kotlin)
    ↓ POSTs JSON data
    ↓
Your Local Web App API (FastAPI on laptop)
    http://192.168.x.x:8000/api/v1/health/submit
    ↓ Receives & stores data
    ↓
Dashboard (http://localhost:8000)
    ↓ Displays REAL health data
    ✅ Works!
```

**Key Point**: Data flows FROM Android TO your laptop, NOT from browser TO Google

---

## 🚀 Implementation Steps

### Step 1: Enable Network Access on Your Laptop

Edit `config.py`:

```python
# Bind to all network interfaces (not just localhost)
HOST = "0.0.0.0"  # This allows Android phone to connect
PORT = 8000
```

✅ Your FastAPI server already does this!

### Step 2: Find Your Laptop's Local IP

```bash
# macOS/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# macOS (simpler)
ipconfig getifaddr en0  # Wi-Fi IP

# Windows
ipconfig
# Look for "IPv4 Address" under your Wi-Fi adapter
```

Example output:
```
192.168.1.5  ← This is your laptop IP on local Wi-Fi
```

### Step 3: Create Android Companion App (Kotlin)

Create a new Android project. Here's the key Health Connect reader:

**`HealthConnectManager.kt`:**
```kotlin
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.HeartRateRecord
import androidx.health.connect.client.records.StepsRecord
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.time.TimeRangeFilter
import java.time.Instant
import java.time.temporal.ChronoUnit
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.URL
import java.net.HttpURLConnection

class HealthConnectManager(val context: Context) {
    private val healthConnectClient = HealthConnectClient.getOrCreate(context)
    private val laptopIP = "192.168.1.5"  // Change to your laptop IP
    private val backendURL = "http://$laptopIP:8000/api/v1/health/submit"

    // Request permissions from user
    suspend fun requestPermissions() {
        val permissions = setOf(
            HealthPermission.getReadPermission(StepsRecord::class),
            HealthPermission.getReadPermission(HeartRateRecord::class),
        )
        healthConnectClient.requestPermissions(permissions)
    }

    // Read data from Health Connect and send to backend
    suspend fun syncHealthData() = withContext(Dispatchers.IO) {
        try {
            val now = Instant.now()
            val startTime = now.minus(24, ChronoUnit.HOURS)

            // Read steps
            val stepsRequest = ReadRecordsRequest(
                StepsRecord::class,
                timeRangeFilter = TimeRangeFilter.between(startTime, now)
            )
            val stepsResponse = healthConnectClient.readRecords(stepsRequest)
            val totalSteps = stepsResponse.records.sumOf { it.count }

            // Read heart rate
            val hrRequest = ReadRecordsRequest(
                HeartRateRecord::class,
                timeRangeFilter = TimeRangeFilter.between(startTime, now)
            )
            val hrResponse = healthConnectClient.readRecords(hrRequest)
            val avgHeartRate = if (hrResponse.records.isNotEmpty()) {
                hrResponse.records.map { it.samples.map { s -> s.beatsPerMinute } }
                    .flatten().average()
            } else {
                0.0
            }

            // Send to backend
            val data = JSONObject().apply {
                put("steps", totalSteps)
                put("heart_rate", avgHeartRate.toInt())
                put("timestamp", System.currentTimeMillis() / 1000)
                put("source", "health_connect")
            }

            sendToBackend(data)
            println("✅ Health data synced: $totalSteps steps, $avgHeartRate bpm")

        } catch (e: Exception) {
            println("❌ Health Connect error: ${e.message}")
        }
    }

    private fun sendToBackend(data: JSONObject) {
        try {
            val url = URL(backendURL)
            val connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "POST"
            connection.setRequestProperty("Content-Type", "application/json")
            connection.doOutput = true

            connection.outputStream.bufferedWriter().use {
                it.write(data.toString())
            }

            val responseCode = connection.responseCode
            if (responseCode == 200) {
                println("✅ Backend accepted data")
            } else {
                println("⚠️ Backend returned: $responseCode")
            }
        } catch (e: Exception) {
            println("❌ Send error: ${e.message}")
        }
    }
}
```

**`MainActivity.kt`:**
```kotlin
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
    private lateinit var healthManager: HealthConnectManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        healthManager = HealthConnectManager(this)

        // Step 1: Request permissions
        lifecycleScope.launch {
            healthManager.requestPermissions()
        }

        // Step 2: Sync data every 5 minutes
        lifecycleScope.launch {
            while (true) {
                healthManager.syncHealthData()
                kotlinx.coroutines.delay(5 * 60 * 1000) // 5 minutes
            }
        }
    }
}
```

**`AndroidManifest.xml`:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.fitnesssync">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <!-- Health Connect permissions -->
    <uses-permission android:name="android.permission.health.READ_STEPS" />
    <uses-permission android:name="android.permission.health.READ_HEART_RATE" />
    <uses-permission android:name="android.permission.health.READ_SLEEP" />

    <application>
        <!-- ... -->
    </application>
</manifest>
```

### Step 4: Update Your FastAPI Backend

The backend already has the structure! Just verify/update the endpoint:

**`api/v1/data_sources.py`** - Add this new endpoint:

```python
@router.post("/health/submit")
def api_submit_health_data(data: dict, db: Session = Depends(get_db)):
    """
    Receive health data from Android companion app via Health Connect.
    Data flows: Android Health Connect → Companion App → This endpoint → Database
    """
    try:
        from models.db_models import WatchData
        
        user_id = data.get("user_id", 1)  # Or extract from auth header
        source = data.get("source", "health_connect")
        
        watch_data = WatchData(
            user_id=user_id,
            source=source,
            heart_rate=data.get("heart_rate"),
            steps=data.get("steps"),
            spo2=data.get("spo2"),
            sleep_stage=data.get("sleep_stage"),
            raw_data=data,
        )
        
        db.add(watch_data)
        db.commit()
        
        print(f"✅ Received health data: {data.get('steps')} steps, {data.get('heart_rate')} bpm")
        return {
            "status": "success",
            "message": "Health data stored",
            "id": watch_data.id
        }
    except Exception as e:
        print(f"❌ Error storing health data: {e}")
        return {"status": "error", "message": str(e)}, 400
```

**Update `models/schemas.py`:**
```python
from pydantic import BaseModel

class HealthDataSubmit(BaseModel):
    steps: int
    heart_rate: int
    spo2: Optional[float] = None
    sleep_stage: Optional[str] = None
    source: str = "health_connect"
    user_id: int = 1
    timestamp: Optional[int] = None
```

### Step 5: Network Configuration

Your `config.py` already has:
```python
HOST = "0.0.0.0"  # ✅ Correct - allows network access
PORT = 8000       # ✅ Standard
```

**Verify it's accessible from Android:**
```bash
# On Android, test with curl from terminal emulator:
curl -X POST http://192.168.1.5:8000/api/v1/health/submit \
  -H "Content-Type: application/json" \
  -d '{"steps":5000,"heart_rate":72,"source":"health_connect"}'

# Should return:
# {"status":"success","message":"Health data stored","id":123}
```

---

## 📱 Android Setup Prerequisites

1. **Install Health Connect app on Android phone**
   - Go to Google Play Store
   - Search "Health Connect"
   - Install the official Google app

2. **Create companion Android app** (using code above)

3. **Set up permissions in Android app:**
   - Request READ_STEPS, READ_HEART_RATE, READ_SLEEP
   - User must grant permissions
   - Health Connect app must be installed

4. **Build & install your companion app**
   ```bash
   # In Android Studio
   # Build → Build APK → Install on phone via USB or Android Studio
   ```

---

## 🔄 Data Flow Diagram

```
Health Connect App (Phone)
    ↓ (Stores real health data)
    ↓
Your Companion App (Kotlin)
    ↓ (Reads from Health Connect)
    ↓
    ├→ Heart Rate: 68 bpm
    ├→ Steps: 4,237 steps
    ├→ Sleep: 7.2 hours
    └→ SpO2: 96%
    ↓
POST http://192.168.1.5:8000/api/v1/health/submit
    ↓
FastAPI Backend
    ↓ (Validates & stores)
    ↓
SQLite Database
    ↓ (watch_data table)
    ↓
Dashboard (localhost:8000)
    ↓ (Displays REAL data)
    ✅ Shows exactly what phone shows!
```

---

## ✅ Testing the Flow

### Test 1: Backend Ready
```bash
curl http://192.168.1.5:8000/docs
# Should show API documentation
```

### Test 2: Android Connectivity
On Android phone (in terminal emulator or via ADB):
```bash
curl -X POST http://192.168.1.5:8000/api/v1/health/submit \
  -H "Content-Type: application/json" \
  -d '{
    "steps": 5421,
    "heart_rate": 72,
    "spo2": 97.2,
    "source": "health_connect"
  }'
```

Expected response:
```json
{
  "status": "success",
  "message": "Health data stored",
  "id": 9999
}
```

### Test 3: Dashboard Shows Real Data
1. Go to: http://localhost:8000/static/dashboard/index.html
2. Should show the data you just submitted!

---

## ⚙️ Why This Works

| Method | Browser OAuth | Android Companion App |
|--------|---------------|-----------------------|
| Google Fit REST | ❌ Deprecated | ❌ Not applicable |
| Health Connect | ❌ Browser can't access | ✅ **Recommended 2026** |
| Data Flow | Browser → Google | Android → Your Laptop |
| Security | Public OAuth | Local network only |
| Real Data | No | **Yes!** |
| Works on localhost | No | **Yes!** |

---

## 🎯 Next Steps

1. **Find your laptop IP**: `ipconfig getifaddr en0` (or equivalent)
2. **Create Android companion app** (copy Kotlin code above)
3. **Request permissions** in Android
4. **Install Health Connect app** on phone
5. **Pair phone to Health Connect**
6. **Run companion app** on phone
7. **Data starts flowing** to your laptop dashboard

---

## 📚 Documentation Links

- [Android Health Connect API Docs](https://developer.android.com/guide/health-and-fitness/health-connect)
- [Health Connect Permissions](https://developer.android.com/guide/health-and-fitness/health-connect-permissions)
- [Your FastAPI Backend Docs](http://localhost:8000/docs)

---

## 🚨 Important Notes

- **Use your laptop's LOCAL IP** (192.168.x.x or 10.0.x.x), NOT localhost
- **Phone and laptop must be on same Wi-Fi network**
- **Health Connect app MUST be installed** on Android phone
- **Permissions must be granted** for each data type (steps, HR, sleep, SpO2)
- **Deprecated tech to AVOID**: Old Google Fit REST API, older Fitbit integrations

---

**Updated**: April 2026  
**Architecture**: Android Health Connect → Companion App → FastAPI Backend  
**Status**: Ready to implement ✅
