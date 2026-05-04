// ✅ CORRECTED HealthConnectManager.kt - WORKING VERSION
// Replace your current HealthConnectManager.kt with this code

package com.example.hearthealth

import android.content.Context
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.HeartRateRecord
import androidx.health.connect.client.records.StepsRecord
import androidx.health.connect.client.records.SpO2Record
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.time.TimeRangeFilter
import com.google.gson.JsonObject
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.time.Instant
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.ZonedDateTime

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
        
        try {
            healthConnectClient.requestPermissions(permissions)
        } catch (e: Exception) {
            println("Permission request failed: ${e.message}")
        }
    }
    
    suspend fun syncHealthData() = withContext(Dispatchers.IO) {
        try {
            println("🔄 Starting health data sync...")
            
            // Get time range: last 24 hours
            val now = Instant.now()
            val startTime = now.minusSeconds(86400) // 24 hours ago
            val endTime = now
            
            println("⏰ Time range: ${startTime} to ${endTime}")
            
            // Get Steps
            var totalSteps = 0L
            try {
                val stepsRequest = ReadRecordsRequest(
                    recordType = StepsRecord::class,
                    timeRangeFilter = TimeRangeFilter.between(startTime, endTime)
                )
                val stepsResponse = healthConnectClient.readRecords(stepsRequest)
                totalSteps = stepsResponse.records.sumOf { it.count }
                println("✅ Steps read: ${totalSteps} (${stepsResponse.records.size} records)")
            } catch (e: Exception) {
                println("❌ Error reading steps: ${e.message}")
            }
            
            // Get Heart Rate
            var avgHeartRate = 0
            try {
                val hrRequest = ReadRecordsRequest(
                    recordType = HeartRateRecord::class,
                    timeRangeFilter = TimeRangeFilter.between(startTime, endTime)
                )
                val hrResponse = healthConnectClient.readRecords(hrRequest)
                avgHeartRate = if (hrResponse.records.isNotEmpty()) {
                    hrResponse.records.map { it.beatsPerMinute }.average().toInt()
                } else 0
                println("✅ Heart rate read: ${avgHeartRate} bpm (${hrResponse.records.size} records)")
            } catch (e: Exception) {
                println("❌ Error reading heart rate: ${e.message}")
            }
            
            // Get SpO2
            var avgSpO2 = 0.0
            try {
                val spO2Request = ReadRecordsRequest(
                    recordType = SpO2Record::class,
                    timeRangeFilter = TimeRangeFilter.between(startTime, endTime)
                )
                val spO2Response = healthConnectClient.readRecords(spO2Request)
                avgSpO2 = if (spO2Response.records.isNotEmpty()) {
                    spO2Response.records.map { it.percentage.value }.average()
                } else 0.0
                println("✅ SpO2 read: ${avgSpO2}% (${spO2Response.records.size} records)")
            } catch (e: Exception) {
                println("❌ Error reading SpO2: ${e.message}")
            }
            
            println("\n📊 Data collected:")
            println("   Steps: $totalSteps")
            println("   Heart Rate: $avgHeartRate bpm")
            println("   SpO2: $avgSpO2%")
            
            // Send to Backend - FLAT STRUCTURE (not summary)
            sendToBackend(
                steps = totalSteps.toInt(),
                heartRate = avgHeartRate,
                spO2 = avgSpO2
            )
            
            return@withContext true
        } catch (e: Exception) {
            println("❌ Sync failed: ${e.message}")
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
            println("\n🌐 Sending to backend: $BACKEND_URL")
            
            // Build JSON - FLAT STRUCTURE (backend handles both flat and summary)
            val json = JsonObject().apply {
                addProperty("user_id", 1)
                addProperty("steps", steps)
                addProperty("heart_rate", heartRate)
                addProperty("spo2", spO2)
                addProperty("sleep_stage", "awake")
                addProperty("source", "health_connect")
            }
            
            println("📤 Payload: $json")
            
            val requestBody = json.toString().toRequestBody("application/json".toMediaType())
            val request = Request.Builder()
                .url(BACKEND_URL)
                .post(requestBody)
                .addHeader("Content-Type", "application/json")
                .build()
            
            val response = httpClient.newCall(request).execute()
            val responseBody = response.body?.string()
            
            println("📬 Response status: ${response.code}")
            println("📬 Response body: $responseBody")
            
            response.close()
            
            if (response.code == 200) {
                println("✅ Data sent successfully!")
            } else {
                println("❌ Backend returned error: ${response.code}")
            }
        } catch (e: Exception) {
            println("❌ Send failed: ${e.message}")
            e.printStackTrace()
        }
    }
}
