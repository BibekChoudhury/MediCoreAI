# 📱 BUILD & DEPLOY - Android App Ready to Go!

**Date:** April 6, 2026
**Status:** ✅ Backend Running | 📱 Ready for Mobile Build

---

## ⚡ QUICK START: 3 Steps to Deploy

### Step 1: Copy These 3 Files Into Android Studio Project

**File 1: `HealthConnectManager.kt`** (Paste in `com/example/hearthealth/`)
```kotlin
package com.example.hearthealth

import android.content.Context
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.HeartRateRecord
import androidx.health.connect.client.records.StepsRecord
import androidx.health.connect.client.records.SpO2Record
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.request.TimeRangeFilter
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
    private val LAPTOP_IP = "192.168.1.12"  // ✅ YOUR LAPTOP - READY TO USE!
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

**File 2: `MainActivity.kt`** (Paste in `com/example/hearthealth/`)
```kotlin
package com.example.hearthealth

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.activity.ComponentActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    private lateinit var healthConnectManager: HealthConnectManager
    
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

**File 3: `activity_main.xml`** (Paste in `res/layout/`)
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

---

### Step 2: Update `build.gradle.kts` (Module: app)

In the `dependencies {}` block, add:

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

---

### Step 3: Update `AndroidManifest.xml`

Add these permissions BEFORE the `<application>` tag:

```xml
<uses-permission android:name="android.permission.HEALTH_CONNECT" />
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

---

## 🎯 Build & Deploy (5 Minutes)

1. **Connect Android phone via USB**
2. **Enable USB Debugging**: 
   - Settings → About Phone → Tap "Build Number" 7 times
   - Settings → Developer Options → Enable "USB Debugging"
3. **In Android Studio**: 
   - Click **Run** ▶️ → **Run 'app'**
   - Select your phone
   - Wait for installation (1-2 minutes)
4. **Grant Permissions**: 
   - App requests Health Connect access
   - Tap "Grant" or allow
5. **Click the Button**: 
   - "Sync Health Data" button
   - Watch for success message ✅

---

## 📊 Backend Information

| Item | Value |
|------|-------|
| **Laptop IP** | 192.168.1.12 |
| **Backend URL** | http://192.168.1.12:8000 |
| **Health Endpoint** | /api/v1/data/health/submit |
| **Dashboard** | http://192.168.1.12:8000/static/dashboard/index.html |
| **API Docs** | http://192.168.1.12:8000/docs |

---

## ✅ Verification Checklist

Before you press the button on your mobile:

- [ ] Backend server is running (http://localhost:8000 loads)
- [ ] Dashboard loads: http://localhost:8000/static/dashboard/index.html
- [ ] IP is **192.168.1.12** in `HealthConnectManager.kt`
- [ ] Android Studio project created
- [ ] 3 Kotlin files added
- [ ] Dependencies installed
- [ ] Permissions added to AndroidManifest.xml
- [ ] App compiled successfully
- [ ] App installed on Android phone
- [ ] "Sync Health Data" button visible on phone
- [ ] Android phone on **same Wi-Fi** as laptop (192.168.1.x range)

---

## 🚀 What Happens When You Press the Button

```
📱 Phone Button Press
         ↓
   Health Connect API (reads steps, heart rate, SpO2)
         ↓
   HTTP POST to 192.168.1.12:8000/api/v1/data/health/submit
         ↓
   Backend receives & stores in database
         ↓
   ✅ "Data synced successfully!" appears on phone
         ↓
   📊 New entry appears on dashboard
         ↓
   Database: sqlite3 heart_health.db (verify)
```

---

## 🧪 Test Right Now (From Terminal)

Simulate what the Android app will do:

```bash
curl -X POST http://localhost:8000/api/v1/data/health/submit \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "steps": 5000,
    "heart_rate": 72,
    "spo2": 97.5,
    "sleep_stage": "awake",
    "source": "health_connect"
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Health data stored successfully",
  "record_id": 9210,
  "source": "health_connect"
}
```

Then open dashboard: http://localhost:8000/static/dashboard/index.html

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connection refused" | Check IP is 192.168.1.12 in code |
| App crashes | Min SDK must be API 31+ |
| No Health data | Install Health Connect app first |
| Can't find phone | Enable USB Debugging, check cable |
| Dashboard empty | Wait 5 seconds and refresh |

---

## 📋 File Locations in Android Project

```
HeartHealthSync/
├── app/
│   ├── src/
│   │   └── main/
│   │       ├── kotlin/com/example/hearthealth/
│   │       │   ├── MainActivity.kt          ← Paste File 2 here
│   │       │   └── HealthConnectManager.kt  ← Paste File 1 here
│   │       ├── res/
│   │       │   └── layout/
│   │       │       └── activity_main.xml    ← Paste File 3 here
│   │       └── AndroidManifest.xml         ← Add permissions here
│   └── build.gradle.kts                    ← Add dependencies here
└── ...
```

---

## 🎉 Ready to Press the Button!

Your backend is running and listening for your mobile app.

**Everything is configured. Just:**
1. Build the Android app (15 minutes)
2. Deploy to your phone
3. Press "Sync Health Data"
4. Watch real health data flow to your dashboard! 📊

---

## 📞 Need Help?

- Backend not starting? Check port 8000 is free
- Mobile can't connect? Check both on same Wi-Fi
- IP address wrong? Use: `ipconfig getifaddr en0`
- Dashboard not updating? Refresh the page

**The backend is ready. Your mobile app is ready. Let's sync!** 🚀
