# Android Health Connect App Setup Guide (2026)

## ✅ Status: Backend Ready for Real Data

Your backend infrastructure is now **fully prepared** to receive and store real health data from an Android device via Health Connect.

---

## 📱 Architecture Overview

```
┌─────────────────────┐
│  Android Phone      │
│  ┌───────────────┐  │
│  │ Health Connect│  │ (OS-level health DB)
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼────────┐ │
│  │ Companion App  │ │ (Your Kotlin app)
│  │   (Kotlin)     │ │
│  └───────┬────────┘ │
└──────────┼──────────┘
           │
           │ HTTP POST
           │ {"steps": 5000, "heart_rate": 72}
           │
      ┌────▼─────────┐
      │  Your Laptop │
      │  (FastAPI)   │
      │  Port 8000   │
      └────┬─────────┘
           │
      ┌────▼──────────────┐
      │  SQLite Database  │
      │  heart_health.db  │
      └───────────────────┘
```

---

## 🔧 Backend Setup Status

### ✅ What's Already Done

1. **New API Endpoint Created**
   - Route: `POST /api/v1/data/health/submit`
   - Location: `api/v1/data_sources.py`
   - Status: **WORKING** ✅

2. **Database Schema Ready**
   - Table: `watch_data`
   - Columns: `user_id`, `source`, `heart_rate`, `spo2`, `steps`, `sleep_stage`, `timestamp`, `raw_data`
   - Status: **READY** ✅

3. **Server Running**
   - FastAPI server: `http://localhost:8000`
   - API documentation: `http://localhost:8000/docs`
   - Status: **RUNNING** ✅

4. **Data Verification**
   - Test submission successful: `curl` command sent 5000 steps + 72 bpm
   - Database stored: Record ID 9157 with exact values
   - Status: **VERIFIED** ✅

---

## 🧪 Test the Backend Now (Before Building Android App)

### 1. **Quick Test with curl**

```bash
curl -X POST http://localhost:8000/api/v1/data/health/submit \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "steps": 8500,
    "heart_rate": 78,
    "spo2": 98.5,
    "sleep_stage": "awake",
    "source": "health_connect"
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Health data stored successfully",
  "record_id": 9158,
  "source": "health_connect"
}
```

### 2. **Verify Data in Dashboard**

1. Open: `http://localhost:8000/static/dashboard/index.html`
2. Look for recent entries with "health_connect" source
3. You should see the data you just submitted

### 3. **Check Database Directly**

```bash
sqlite3 heart_health.db "SELECT * FROM watch_data WHERE source='health_connect' ORDER BY timestamp DESC LIMIT 5;"
```

---

## 📋 What's Needed: Android Companion App

### Prerequisites

- **Android Studio** (latest version)
- **Android Phone** (with Android 10+)
- **Gradle** (included with Android Studio)
- **Kotlin 1.9+** (included with Android Studio)

### Step 1: Create Android Studio Project

1. Open Android Studio
2. **File** → **New** → **New Android Project**
3. Choose: **Phone and Tablet** → **Empty Views Activity**
4. Configure:
   - Name: `HeartHealthSync`
   - Package: `com.example.hearthealth`
   - Save Location: Anywhere
   - Language: **Kotlin**
   - Min SDK: API 31 (Android 12)

### Step 2: Add Dependencies

In `build.gradle.kts` (Module: app):

```kotlin
dependencies {
    // Health Connect
    implementation("androidx.health:health-connect-client:1.0.0-alpha02")
    
    // HTTP Client
    implementation("com.squareup.okhttp3:okhttp:4.11.0")
    
    // JSON
    implementation("com.google.code.gson:gson:2.10.1")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.1")
    
    // Lifecycle
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.6.1")
}
```

### Step 3: Add Permissions

In `AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.HEALTH_CONNECT" />
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

### Step 4: Create Kotlin Files

#### A. `HealthConnectManager.kt`

```kotlin
package com.example.hearthealth

import android.content.Context
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.HeartRateRecord
import androidx.health.connect.client.records.StepsRecord
import androidx.health.connect.client.records.SpO2Record
import androidx.health.connect.client.request.ReadRecordsRequest
import com.google.gson.JsonObject
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.time.LocalDateTime
import java.time.ZoneOffset

class HealthConnectManager(context: Context) {
    private val healthConnectClient = HealthConnectClient.getOrCreate(context)
    private val httpClient = OkHttpClient()
    private val LAPTOP_IP = "192.168.1.12"  // ✅ YOUR LAPTOP IP
    private val BACKEND_URL = "http://$LAPTOP_IP:8000/api/v1/data/health/submit"
    
    suspend fun requestHealthPermissions() = withContext(Dispatchers.Default) {
        val permissions = setOf(
            HealthPermission.getReadPermission(HeartRateRecord::class),
            HealthPermission.getReadPermission(StepsRecord::class),
            HealthPermission.getReadPermission(SpO2Record::class),
        )
        
        healthConnectClient.requestPermissions(permissions)
    }
    
    suspend fun syncHealthData() = withContext(Dispatchers.IO) {
        try {
            // Get Steps
            val stepsRequest = ReadRecordsRequest(
                recordType = StepsRecord::class,
                timeRangeFilter = TimeRangeFilter.between(
                    startTime = LocalDateTime.now().minusDays(1).toInstant(ZoneOffset.UTC),
                    endTime = LocalDateTime.now().toInstant(ZoneOffset.UTC)
                )
            )
            val stepsResponse = healthConnectClient.readRecords(stepsRequest)
            val totalSteps = stepsResponse.records.sumOf { it.count }
            
            // Get Heart Rate
            val hrRequest = ReadRecordsRequest(
                recordType = HeartRateRecord::class,
                timeRangeFilter = TimeRangeFilter.between(
                    startTime = LocalDateTime.now().minusDays(1).toInstant(ZoneOffset.UTC),
                    endTime = LocalDateTime.now().toInstant(ZoneOffset.UTC)
                )
            )
            val hrResponse = healthConnectClient.readRecords(hrRequest)
            val avgHeartRate = if (hrResponse.records.isNotEmpty()) {
                hrResponse.records.map { it.beatsPerMinute }.average().toInt()
            } else 0
            
            // Get SpO2
            val spO2Request = ReadRecordsRequest(
                recordType = SpO2Record::class,
                timeRangeFilter = TimeRangeFilter.between(
                    startTime = LocalDateTime.now().minusDays(1).toInstant(ZoneOffset.UTC),
                    endTime = LocalDateTime.now().toInstant(ZoneOffset.UTC)
                )
            )
            val spO2Response = healthConnectClient.readRecords(spO2Request)
            val avgSpO2 = if (spO2Response.records.isNotEmpty()) {
                spO2Response.records.map { it.percentage.value }.average()
            } else 0.0
            
            // Send to Backend
            sendToBackend(
                steps = totalSteps.toInt(),
                heartRate = avgHeartRate,
                spO2 = avgSpO2
            )
            
            return@withContext true
        } catch (e: Exception) {
            e.printStackTrace()
            return@withContext false
        }
    }
    
    private suspend fun sendToBackend(
        steps: Int,
        heartRate: Int,
        spO2: Double
    ) = withContext(Dispatchers.IO) {
        try {
            val json = JsonObject().apply {
                addProperty("user_id", 1)
                addProperty("steps", steps)
                addProperty("heart_rate", heartRate)
                addProperty("spo2", spO2)
                addProperty("sleep_stage", "awake")
                addProperty("source", "health_connect")
            }
            
            val requestBody = json.toString().toRequestBody("application/json".toMediaType())
            val request = Request.Builder()
                .url(BACKEND_URL)
                .post(requestBody)
                .build()
            
            val response = httpClient.newCall(request).execute()
            response.body?.string()
            response.close()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}
```

#### B. `MainActivity.kt`

```kotlin
package com.example.hearthealth

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    private lateinit var healthConnectManager: HealthConnectManager
    
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        if (permissions.values.all { it }) {
            // All permissions granted
            findViewById<TextView>(R.id.statusText).text = "✅ Permissions granted! Ready to sync."
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        healthConnectManager = HealthConnectManager(this)
        
        // Request permissions
        lifecycleScope.launch {
            healthConnectManager.requestHealthPermissions()
        }
        
        // Sync button
        findViewById<Button>(R.id.syncButton).setOnClickListener {
            lifecycleScope.launch {
                val success = healthConnectManager.syncHealthData()
                val status = if (success) "✅ Data synced successfully!" else "❌ Sync failed"
                findViewById<TextView>(R.id.statusText).text = status
            }
        }
    }
}
```

#### C. `activity_main.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp"
    android:gravity="center">
    
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Heart Health Sync"
        android:textSize="24sp"
        android:textStyle="bold"
        android:layout_marginBottom="32dp" />
    
    <TextView
        android:id="@+id/statusText"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Requesting permissions..."
        android:textSize="16sp"
        android:layout_marginBottom="16dp" />
    
    <Button
        android:id="@+id/syncButton"
        android:layout_width="200dp"
        android:layout_height="50dp"
        android:text="Sync Health Data"
        android:textSize="16sp" />
    
</LinearLayout>
```

### Step 5: Update Your IP Address

**CRITICAL:** Find your laptop IP and update the code:

```bash
# On macOS:
ipconfig getifaddr en0

# On Linux:
hostname -I

# On Windows:
ipconfig | findstr "IPv4"
```

Result will be like: `192.168.1.5` or `192.168.0.10`

Update this line in `HealthConnectManager.kt`:
```kotlin
private val LAPTOP_IP = "192.168.x.x"  // ← REPLACE WITH YOUR IP
```

### Step 6: Build and Run

1. **Connect Android phone** via USB
2. **Enable USB Debugging**: Settings → About → Tap Build Number 7x → Back → Developer Options → USB Debugging
3. In Android Studio: **Run** → **Run 'app'**
4. Select your connected phone
5. App will install and launch

### Step 7: Grant Health Connect Permissions

1. App shows "Requesting permissions..."
2. Click through to grant access to:
   - Steps
   - Heart Rate
   - SpO2
3. Once granted, status shows: "✅ Permissions granted!"

### Step 8: Test Sync

1. Click **"Sync Health Data"** button
2. App reads from Health Connect
3. Sends data to your laptop
4. Check dashboard: `http://localhost:8000/static/dashboard/index.html`

---

## 📊 Monitoring Real Data Flow

### Dashboard Updates (Real-time)

1. Open: `http://localhost:8000/static/dashboard/index.html`
2. Look for entries with `source: "health_connect"`
3. Values will match your phone data ✅

### Database Query

```bash
sqlite3 heart_health.db "SELECT user_id, source, heart_rate, steps, spo2, timestamp FROM watch_data WHERE source='health_connect' ORDER BY timestamp DESC LIMIT 10;"
```

### API Logs

The server logs show each submission:
```
POST /api/v1/data/health/submit HTTP/1.1" 200 OK
✅ Health data stored successfully
```

---

## 🔧 Troubleshooting

### 1. "Connection refused" Error

**Problem:** App can't reach your laptop

**Solutions:**
- Verify IP address is correct in code
- Check both devices are on **same Wi-Fi network**
- Disable firewall temporarily (macOS: System Preferences → Security & Privacy)
- Test: `ping 192.168.x.x` from phone browser (should work)

### 2. "Permission Denied" on Phone

**Problem:** App doesn't have Health Connect access

**Solutions:**
- Install "Health Connect" app from Google Play Store first
- Go to Health Connect app → Grant app permissions → Select your app
- Try again

### 3. "No Health Data" Syncing

**Problem:** Your phone has no data in Health Connect

**Solutions:**
- Wear a smartwatch (Fitbit, Wear OS) for automatic sync
- Use Google Fit app to manually add sample data
- Wait a few hours for watch to sync data
- Use Android Health app to add test data

### 4. App Crashes on Startup

**Problem:** Build failed or runtime error

**Solutions:**
- Check min SDK is API 31 or higher
- Verify all dependencies are installed
- Run `Sync Now` in Android Studio
- Check Logcat for error messages

---

## ✨ Next Steps

1. ✅ **Backend is ready** (verified working)
2. 🏗️ **Build Android app** (follow steps above)
3. 📱 **Deploy to phone** (USB or Play Store)
4. 🔄 **Run sync** (click button or set up scheduler)
5. 📊 **View real data on dashboard** (http://localhost:8000)

---

## 🎯 Your Real Data Flow Path

```
Health Connect (Android OS)
    ↓ (Kotlin reads data)
Your App (Companion)
    ↓ (HTTP POST)
Backend API (/api/v1/data/health/submit)
    ↓ (Stores in DB)
SQLite watch_data table
    ↓ (Frontend fetches)
Your Dashboard (shows live health metrics)
```

---

## 📞 Support

For issues, check:
- `ANDROID_HEALTH_CONNECT_2026.md` (detailed implementation)
- `SOLUTION_COMPLETE_2026.md` (architecture explanation)
- Backend logs: `server.log`
- Database: `sqlite3 heart_health.db`

**Server is running and waiting for Android submissions!** 🚀
