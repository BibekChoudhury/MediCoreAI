// ✅ CORRECTED HealthConnectManager.kt - TODAY'S DATA ONLY
// This version reads ONLY TODAY'S steps (not cumulative)
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
            println("🔄 Starting health data sync (TODAY'S DATA ONLY)...")
            
            // 🔧 FIX: Get TODAY'S data only - from midnight to now
            val now = Instant.now()
            val today = now.atZone(ZoneId.systemDefault()).toLocalDate()
            
            // Midnight today (start of day)
            val startTime = today.atStartOfDay(ZoneId.systemDefault()).toInstant()
            val endTime = now
            
            println("⏰ Time range: $startTime to $endTime")
            println("⏰ Reading TODAY's data only!")
            
            // Get Steps - TODAY ONLY
            var totalSteps = 0L
            try {
                val stepsRequest = ReadRecordsRequest(
                    recordType = StepsRecord::class,
                    timeRangeFilter = TimeRangeFilter.between(startTime, endTime)
                )
                val stepsResponse = healthConnectClient.readRecords(stepsRequest)
                totalSteps = stepsResponse.records.sumOf { it.count }
                println("✅ TODAY's steps read: ${totalSteps} (${stepsResponse.records.size} records)")
            } catch (e: Exception) {
                println("❌ Error reading steps: ${e.message}")
            }
            
            // Get Heart Rate - TODAY ONLY
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
                println("✅ TODAY's heart rate read: ${avgHeartRate} bpm (${hrResponse.records.size} records)")
            } catch (e: Exception) {
                println("❌ Error reading heart rate: ${e.message}")
            }
            
            // Get SpO2 - TODAY ONLY
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
                println("✅ TODAY's SpO2 read: ${avgSpO2}% (${spO2Response.records.size} records)")
            } catch (e: Exception) {
                println("❌ Error reading SpO2: ${e.message}")
            }
            
            println("\n📊 TODAY's data collected:")
            println("   Steps: $totalSteps")
            println("   HR: $avgHeartRate bpm")
            println("   SpO2: $avgSpO2%")
            
            sendToBackend(totalSteps, avgHeartRate, avgSpO2)
            
            return@withContext true
        } catch (e: Exception) {
            println("❌ Sync failed: ${e.message}")
            e.printStackTrace()
            return@withContext false
        }
    }
    
    private suspend fun sendToBackend(
        steps: Long,
        heartRate: Int,
        spO2: Double
    ) = withContext(Dispatchers.IO) {
        try {
            val json = JsonObject().apply {
                addProperty("user_id", "cardia_user_1")  // ✅ Use correct user_id
                addProperty("steps", steps)
                addProperty("heart_rate", heartRate)
                addProperty("spo2", if (spO2 > 0) spO2 else null)
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
                println("✅ TODAY's data sent successfully!")
            } else {
                println("❌ Backend returned error: ${response.code}")
            }
        } catch (e: Exception) {
            println("❌ Send failed: ${e.message}")
            e.printStackTrace()
        }
    }
}
