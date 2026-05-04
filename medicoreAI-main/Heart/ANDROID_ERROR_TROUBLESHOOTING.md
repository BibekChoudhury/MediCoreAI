# 🔧 ANDROID APP TROUBLESHOOTING - "Failed. Check IP / backend / permissions"

**Error:** ❌ Failed. Check IP / backend / permissions  
**Status:** 🔴 App can't connect to backend

---

## 🎯 Quick Fixes (Try These First!)

### 1️⃣ **Verify Wi-Fi Connection**

**On your Android phone:**
- Settings → Wi-Fi → Check you're connected to: **`Kanha-Mac` or similar (your home network)**
- NOT on mobile data or different Wi-Fi!
- Phone and laptop must be on **same Wi-Fi network**

**Check network range:**
- Your laptop IP: `192.168.1.12`
- Your phone should show: `192.168.1.x` (same first 3 numbers)

---

### 2️⃣ **Verify Backend is Running**

**On your laptop terminal:**
```bash
curl http://localhost:8000/api/v1/data/health/submit
```

Should see error about POST method (that's OK - it means server is running):
```
{"detail":"Method Not Allowed"}
```

If you see "Connection refused" - backend is NOT running! Start it:
```bash
cd /Users/sujalnivruttipagere/Desktop/Heart
source .venv/bin/activate
python main.py
```

---

### 3️⃣ **Verify IP Address is Correct**

**Your laptop IP: `192.168.1.12`** ✅ (already set in code)

Check it didn't change:
```bash
ipconfig getifaddr en0
```

Result should be: `192.168.1.12`

If different, update in Android code:
```kotlin
private val LAPTOP_IP = "192.168.1.x"  // ← Your actual IP
```

---

### 4️⃣ **Test Connection FROM Phone**

**On your Android phone, open browser and try:**
```
http://192.168.1.12:8000/docs
```

**Expected:** You see Swagger API documentation page ✅

**If fails:**
- Check IP again (try `192.168.1.12:8000` in browser first)
- Check Wi-Fi is same network
- Check firewall (macOS: System Preferences → Security → allow connections)

---

## 🔍 Common Issues & Solutions

### Issue: "Connection refused"

**Cause:** Backend server is not running

**Solution:**
```bash
# Check if running
ps aux | grep "python main.py" | grep -v grep

# If nothing shows, start it:
cd /Users/sujalnivruttipagere/Desktop/Heart
source .venv/bin/activate
python main.py

# Keep it running! (do NOT close terminal)
```

---

### Issue: "Network unreachable"

**Cause:** Phone not on same Wi-Fi as laptop

**Solution:**
- Open Settings → Wi-Fi on phone
- Connect to: `Kanha-Mac` or your home Wi-Fi
- Verify you see Wi-Fi icon in status bar
- Laptop must also be on same Wi-Fi

**Verify connection:**
```bash
# On phone browser, try:
http://192.168.1.12:8000/docs
```

Should load the API documentation.

---

### Issue: "Health Connect permission denied"

**Cause:** App doesn't have Health Connect permissions

**Solution:**
1. On phone, open **Health Connect** app (Google Play Store app)
2. Tap **Permissions**
3. Find your **Heart Health Sync** app
4. Grant access to:
   - Steps
   - Heart Rate
   - SpO2
5. Try syncing again

---

### Issue: "Timeout" or takes forever

**Cause:** Slow network or backend is slow

**Solution:**
1. Check backend is running (see above)
2. Restart app on phone
3. Wait 5 seconds before pressing button
4. Check phone Wi-Fi signal strength (should be strong)

---

## 🧪 STEP-BY-STEP VERIFICATION

### Step 1: Check Backend Status

```bash
# Terminal on laptop
ps aux | grep "python.*main.py"
```

**Expected output:** Should show a line with `python main.py` running

**If NOT running:**
```bash
cd /Users/sujalnivruttipagere/Desktop/Heart
source .venv/bin/activate
python main.py
# Keep terminal open!
```

---

### Step 2: Test Backend Endpoint

```bash
# From laptop terminal
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

**Expected response:**
```json
{
  "status": "success",
  "message": "Health data stored successfully",
  "record_id": 9211,
  "source": "health_connect"
}
```

---

### Step 3: Test from Phone Browser

1. **On your Android phone**, open Chrome browser
2. Type: `http://192.168.1.12:8000/docs`
3. **Expected:** Swagger API page loads ✅

**If page loads:**
- Wi-Fi connection works ✅
- IP address is correct ✅
- Backend is running ✅

**If page does NOT load:**
- Check Wi-Fi connection
- Check IP address (`192.168.1.12`)
- Check backend is running on laptop

---

### Step 4: Rebuild Android App

If backend and Wi-Fi are working, rebuild the app:

1. In Android Studio: **Build** → **Clean Project**
2. **Build** → **Rebuild Project**
3. **Run** → **Run 'app'**
4. Deploy to phone
5. Try syncing again

---

## 🚨 ADVANCED TROUBLESHOOTING

### Check Android Logcat for Error Details

In Android Studio:
1. **View** → **Tool Windows** → **Logcat**
2. Search for: `hearthealth` or `HealthConnect`
3. Look for error messages (will show actual exception)

Common errors:
- `java.net.ConnectException` → Network problem
- `java.io.IOException` → Connection problem
- `SocketTimeoutException` → Slow network

---

### Check Firewall (macOS)

```bash
# Check firewall status
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Temporarily disable (for testing only!)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off

# Re-enable after testing
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
```

---

### Monitor Backend in Real-Time

Keep terminal open and watch for requests:

```bash
cd /Users/sujalnivruttipagere/Desktop/Heart
source .venv/bin/activate
python main.py 2>&1 | tee server.log
```

When you press button on phone, you should see:
```
POST /api/v1/data/health/submit HTTP/1.1" 200 OK
✅ Health data stored successfully
```

---

## ✅ CHECKLIST - Do These Now

- [ ] Backend server is running on laptop
  - Command: `ps aux | grep "python main.py"`
  - Should see process running

- [ ] Phone is on same Wi-Fi as laptop
  - Settings → Wi-Fi → Connected to home network

- [ ] IP address is correct: `192.168.1.12`
  - Check: `ipconfig getifaddr en0` on laptop
  - Check in code: `private val LAPTOP_IP = "192.168.1.12"`

- [ ] Test from phone browser works
  - Open: `http://192.168.1.12:8000/docs` on phone
  - Should see API documentation

- [ ] Health Connect permissions granted
  - Health Connect app → Permissions → Grant all

- [ ] Backend test works from laptop
  - Run curl command above
  - Should get success response

---

## 🎯 IF ALL ELSE FAILS

### Complete Reset

1. **Stop backend:**
   ```bash
   pkill -9 -f "python.*main.py"
   ```

2. **Start fresh:**
   ```bash
   cd /Users/sujalnivruttipagere/Desktop/Heart
   source .venv/bin/activate
   python main.py
   ```

3. **In Android Studio:**
   - Build → Clean Project
   - Build → Rebuild Project
   - Run → Run 'app'

4. **On phone:**
   - Uninstall app
   - Reinstall from Android Studio
   - Grant all permissions fresh

5. **Test:**
   - Open phone browser: http://192.168.1.12:8000/docs
   - Press sync button

---

## 📞 NEED HELP?

Provide this information:

1. **Backend running?** (yes/no)
   ```bash
   ps aux | grep "python main.py"
   ```

2. **Your laptop IP?**
   ```bash
   ipconfig getifaddr en0
   ```

3. **Phone can access backend?** (yes/no)
   - Try in phone browser: http://192.168.1.12:8000/docs

4. **Android Logcat error** (copy exact error)
   - From Android Studio Logcat tab

5. **curl test works?** (yes/no)
   ```bash
   curl http://localhost:8000/api/v1/data/health/submit
   ```

---

## 🔄 WHEN IT WORKS

You'll see on your phone:
- ✅ "Data synced successfully!"

You'll see on dashboard:
- http://localhost:8000/static/dashboard/index.html
- New entry with your health data

You'll see in server logs:
```
POST /api/v1/data/health/submit HTTP/1.1" 200 OK
✅ Health data stored successfully
```

---

**Backend is running now. Check your Wi-Fi and try again!** 📱✅
