# 🔧 Troubleshooting: Voice Agent, Microphone & Google Fit Sync

## 📋 Issue Summary

You have **3 problems**:

1. ❌ **Voice agent not talking** (Text-to-Speech not working)
2. ❌ **Microphone not working** (Speech-to-Text not working)
3. ❌ **Google Fit data not syncing** (Getting 403 Forbidden error)

---

## 🔊 Problem 1: Voice Agent Not Talking (TTS)

### Root Cause
The ElevenLabs API key is configured in `.env`, but you might not have:
- ✅ **ElevenLabs API Key** (you have: `sk_3bd0528...`) ✓
- ❌ **Browser support** - Some browsers don't support this
- ❌ **Speaker/Audio output** - Device audio is muted or not configured

### Current Setup
```
ELEVENLABS_API_KEY=sk_3bd0528841b1a30002dc3599897c03d053b4e8acb762fe88 ✓
```

The system uses **TWO voice methods**:

#### Method 1: ElevenLabs Server-Side TTS
- Endpoint: `POST /api/v1/agent/voice`
- Returns MP3 audio
- High quality, professional voices
- **Status**: Configured and ready ✓

#### Method 2: Browser Native Speech Synthesis
- Fallback when ElevenLabs unavailable
- Uses your OS voices (Siri, Cortana, etc.)
- **Status**: Works but may sound robotic

### Fix: Test Voice Agent

1. **Open Dashboard**: http://localhost:8000/static/dashboard/index.html

2. **Open Chat Panel** (Bottom right "Cardia" button)

3. **Type a message**: "Hello, can you hear me?"

4. **Toggle voice ON** (see the voice toggle checkbox)

5. **Send message** → You should hear:
   - ✅ Text response in chat
   - 🔊 Audio playing automatically

### If Voice Still Doesn't Work:

**Check 1: Browser Compatibility**
```javascript
// Open browser DevTools (F12) → Console and paste:
console.log("ElevenLabs enabled:", window.speechSynthesis !== undefined);
```

**Check 2: Server Logs**
```bash
tail -f server.log | grep -i "elevenlabs\|TTS\|voice"
```

**Check 3: API Status**
```bash
curl http://localhost:8000/api/v1/agent/voice/status
```
Expected response:
```json
{
  "voice_enabled": true,
  "provider": "elevenlabs"
}
```

**Check 4: Test Direct TTS Call**
```bash
curl -X POST http://localhost:8000/api/v1/agent/tts \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello world"}' \
  --output test_audio.mp3 && \
  open test_audio.mp3
```

**Check 5: System Audio**
- 🔊 Make sure your computer speakers/headphones are turned **ON**
- Volume is **NOT muted**
- Try another app to confirm audio works

---

## 🎤 Problem 2: Microphone Not Working (STT)

### Root Cause
Browser **Web Speech Recognition API** requires:
1. ✅ **Browser support** (Chrome, Edge, Safari)
2. ❌ **Microphone permissions** (CRITICAL - usually denied)
3. ❌ **HTTPS or localhost** (security requirement)
4. ❌ **Microphone connected/working**

### Current Status
- ✓ Running on `localhost:8000` (OK)
- ✓ System uses **Google Chrome Web Speech API** (free, no key needed)
- ❓ **Microphone permissions**: Need to check

### Fix: Enable Microphone Permissions

#### For Chrome/Brave:
1. Go to: http://localhost:8000/static/dashboard/index.html
2. Click 🎤 **Voice Button** (mic icon in Cardia chat)
3. You should see a **permission popup** asking for microphone access
4. Click **"Allow"** ✓
5. **Reload page** and try again

#### For Safari (macOS):
1. Open **System Preferences** → **Security & Privacy** → **Microphone**
2. Find **Safari** and enable it
3. Try again in the dashboard

#### For Firefox:
1. When you click the mic button, Firefox shows a permission bar at top
2. Click **"Remember this decision"** and then **"Allow"**

### Test Microphone:

1. **Open DevTools** (F12)
2. Go to **Console** tab
3. Paste and run:
```javascript
// Test if browser supports Web Speech
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SpeechRecognition) {
    console.log("✅ Web Speech API available");
    const recognition = new SpeechRecognition();
    recognition.start();
    recognition.onresult = (e) => console.log("Heard:", e.results[0][0].transcript);
    recognition.onerror = (e) => console.log("❌ Error:", e.error);
} else {
    console.log("❌ Web Speech API NOT supported in this browser");
}
```

### If Microphone Still Doesn't Work:

**Check 1: Browser Permissions**
```bash
# Chrome: Check chrome://settings/content/microphone
# Should show: http://localhost:8000 → Allow
```

**Check 2: System Permissions**
```bash
# macOS:
# System Preferences → Security & Privacy → Microphone → Check your browser

# Windows:
# Settings → Privacy → Microphone → Allow apps to access microphone
```

**Check 3: Hardware**
- Microphone physically connected?
- Try in another app (Zoom, Slack) to confirm it works
- Check if muted with keyboard shortcut

**Check 4: Try Different Browser**
- Chrome ✓ (best support)
- Edge ✓ (good support)
- Safari ✓ (good support)
- Firefox ✗ (limited support)

---

## 📊 Problem 3: Google Fit Data Not Syncing (403 Forbidden)

### Root Cause
The server logs show:
```
⚠️ Google Fit API error (status 403), falling back to simulation
```

This means:
- ✓ OAuth credentials are configured in `.env`
- ✓ System can reach Google Fit API
- ❌ **Access token is INVALID or EXPIRED**
- ❌ **Token was never saved** after OAuth authentication

### Current Configuration
```
GOOGLE_FIT_CLIENT_ID=625558417644-d3f1uveheeqp6k4o8l2bvk22355u9gsg.apps.googleusercontent.com ✓
GOOGLE_FIT_CLIENT_SECRET={"web":{...}}  ✓
```

### Fix: Re-authenticate with Google Fit

#### Step 1: Check Current Status
```bash
# Check if token is saved in database
sqlite3 heart_health.db "SELECT source_type, config FROM data_sources WHERE source_type='google_fit';"
```

If you see `null` or empty config → **Token not saved**, need to reconnect.

#### Step 2: Disconnect Google Fit
```bash
# Remove old connection
sqlite3 heart_health.db "DELETE FROM data_sources WHERE source_type='google_fit';"
```

#### Step 3: Reconnect via Dashboard
1. Go to: http://localhost:8000/static/dashboard/index.html
2. Click **"Devices"** tab (📱 icon)
3. Find **"Google Fit"** card
4. Click **"Connect with OAuth"** button
5. **IMPORTANT**: Log in with your **GMAIL account** that has Fit data
6. Grant permissions:
   - ✅ "See your heart rate data"
   - ✅ "See your steps"
   - ✅ "See your sleep data"
   - ✅ "See your oxygen saturation"
7. Click **"Allow"** at the end

#### Step 4: Watch Server Logs
```bash
tail -f server.log | grep -i "Google Fit"
```

You should see:
```
✅ Google Fit connected with access token for user 1
✅ Fetched X real readings from Google Fit for user 1
```

NOT:
```
⚠️ Google Fit API error (status 403)
```

#### Step 5: Verify in Dashboard
- Wait 30-60 seconds for first sync
- Go to **Dashboard** tab
- Look for **real data** from your Android Fit app:
  - 🔴 Heart rate (should match your phone)
  - 👟 Step count (should match your phone)
  - 💨 SpO2 if available

### Expected vs Actual Data

#### Simulated Data (Current - WRONG) ❌
```
Heart Rate: Rapidly changing (72 → 85 → 79 → 91 → etc.)
Steps: Rapidly increasing (6000 → 6100 → 6200 → etc.)
Updates: Every 2 seconds
Source: "firebolt" (simulated)
```

#### Real Google Fit Data (After Fix - CORRECT) ✅
```
Heart Rate: Stable (68 bpm - matches your phone)
Steps: Real value (4,237 steps today)
Updates: Every 5-10 minutes (auto-sync)
Source: "google_fit"
```

### If Google Fit Still Not Working:

**Check 1: Verify OAuth Credentials**
```bash
# Are credentials in .env?
grep GOOGLE_FIT ~/.env

# Should show:
# GOOGLE_FIT_CLIENT_ID=625558417644-...
# GOOGLE_FIT_CLIENT_SECRET={...}
```

**Check 2: Token Was Saved?**
```bash
sqlite3 heart_health.db
SELECT id, source_type, config FROM data_sources WHERE user_id=1;
```

If `config` column is empty/null → **Token not saved**, need to re-auth.

**Check 3: Check Token Expiration**
```bash
# Extract token from database
sqlite3 heart_health.db "SELECT config FROM data_sources WHERE source_type='google_fit';" | \
  python3 -c "import json, sys; print(json.load(sys.stdin).get('access_token', 'NOT FOUND'))"
```

**Check 4: Try Token Refresh**
```bash
# If you have refresh_token, server will auto-refresh
# Check logs for success:
tail -f server.log | grep -i "refresh\|token"
```

**Check 5: Clear All Data and Start Fresh**
```bash
# Backup database
cp heart_health.db heart_health.db.backup

# Remove Google Fit connection
sqlite3 heart_health.db "DELETE FROM data_sources WHERE source_type='google_fit';"

# Restart server
# Then re-authenticate
```

---

## 🎯 Quick Checklist

### For Voice:
- [ ] ElevenLabs API key configured: ✓
- [ ] Browser supports audio playback: Test in YouTube
- [ ] Speakers/headphones connected: Test volume
- [ ] Try both methods: Server TTS + Browser Native

### For Microphone:
- [ ] Browser supports Web Speech API: Chrome/Edge/Safari
- [ ] Microphone permissions granted: Check browser settings
- [ ] Microphone works in other apps: Zoom, Slack
- [ ] Running on localhost or HTTPS: ✓

### For Google Fit:
- [ ] .env has valid credentials: ✓
- [ ] Re-authenticated recently: Last 1 hour
- [ ] Token saved in database: Check `data_sources.config`
- [ ] Dashboard shows real data: Not simulated

---

## 🚀 Performance Tips

### Speed Up Google Fit Sync:
```bash
# Change auto-sync interval in .env
AUTO_SYNC_INTERVAL_MINUTES=1  # Sync every minute
```

### Reduce Voice Latency:
```bash
# System will prefer ElevenLabs TTS (faster than browser native)
# ElevenLabs: ~1 second
# Browser: ~2-3 seconds
```

### Reduce Microphone Lag:
```bash
# Browser Web Speech API is local-only (fastest)
# No network latency
# ~500ms recognition time
```

---

## 📞 Still Having Issues?

### Check Server Status:
```bash
# Is server running?
curl http://localhost:8000/docs

# Should show Swagger API docs
```

### Check All Services:
```bash
curl http://localhost:8000/api/v1/agent/voice/status
curl http://localhost:8000/api/v1/data/source/list

# If both respond with data, backend is OK
```

### View All Logs:
```bash
tail -100 server.log

# Look for errors starting with ❌ or ⚠️
```

### Restart Everything:
```bash
# Stop server (Ctrl+C)
# Kill any lingering processes
pkill -f "python main.py"

# Restart
python main.py
```

---

**Last Updated**: 2026-04-05  
**Status**: Ready for diagnosis 🔧
