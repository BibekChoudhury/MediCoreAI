# ⚡ QUICK START - Fix Your Issues in 5 Minutes

## 🎯 Your 3 Problems - Quick Fixes

### Problem 1: Microphone Not Working
**Status**: ✅ Ready - Just grant permission!
```
1. Open: http://localhost:8000/static/dashboard/index.html
2. Click Cardia (bottom right)
3. Click 🎤 microphone icon
4. Click "Allow" when browser asks
5. Speak → text appears!
```

### Problem 2: Voice Agent Not Talking  
**Status**: ✅ Ready - Turn up speakers!
```
1. Open dashboard (same link above)
2. Cardia chat → Check "Voice" toggle
3. Type message
4. Send → You hear response! 🔊
5. If no sound: Check speaker volume
```

### Problem 3: Google Fit Data Simulated (Getting 403)
**Status**: ✅ FIXED - Reconnect Google!
```
1. Open dashboard
2. Devices tab (📱 icon)
3. Google Fit → "Connect with OAuth"
4. Log in with your Gmail
5. Grant permissions
6. Wait 1 minute → Real data appears!
```

---

## 🚀 One-Minute Action Plan

### Right Now:
```
1. Go: http://localhost:8000/static/dashboard/index.html
2. Devices tab → Google Fit → OAuth connect
3. (Do this while reading next section)
```

### While Waiting for Google:
```
1. Test Microphone: Click 🎤 → Say something
2. Test Voice: Chat → "Hello" → Hear response?
3. Check both work before proceeding
```

### After Google Fit Reconnects (2-3 min):
```
1. Go to Dashboard tab
2. Look at heart rate card
3. Does it match your phone? ✅
4. Done! Real data syncing now
```

---

## ✅ What Should Happen

### Google Fit Reconnection
- Google login page appears
- You use YOUR GMAIL (same as Android Fit)
- Permission requests for heart rate, steps, sleep, SpO2
- You click "Allow"
- Redirected back to dashboard
- Message: "✅ Google Fit Connected!"

### Real Data Appears
```
Before (Wrong):
Heart Rate: 85 → 72 → 91 → 78 → 84 (rapid changes)
Steps: 6000 → 6100 → 6200 (always increasing)

After (Correct):
Heart Rate: 68 bpm (stable, your actual HR)
Steps: 4,237 (your actual count today)
```

### Verification
```bash
# In terminal, check logs:
tail server.log | grep "Google Fit"

# Should show:
✅ Google Fit connected with access token
✅ Fetched 24 real readings from Google Fit

# NOT:
⚠️ Google Fit API error (status 403)
```

---

## 🎤 Microphone Setup (2 Steps)

**Step 1**: Click 🎤 button in Cardia chat

**Step 2**: Browser permission popup appears
- Chrome: "Allow" button
- Safari: "Allow"  
- Edge: "Allow"
- Firefox: "Allow" 

**That's it!** Permission granted = microphone works

---

## 🔊 Voice Setup (1 Step)

Open chat → Check "Voice" toggle → Send message → Hear response

If no sound:
- Check 🔊 speaker icon (not muted)
- Check volume > 20%
- Try other app (YouTube) to confirm speakers work

---

## 📊 How to Know It's Working

### Google Fit Real Data ✅
- Matches Android Fit app exactly
- Updates every 5 minutes
- Shows "google_fit" as source
- Data is 5-60 minutes old (realistic)

### Voice ✅
- Hear clear AI response
- Takes ~1-3 seconds
- Natural sounding

### Microphone ✅
- "Listening..." appears
- Voice input becomes text
- Text appears in message box
- Send → processes your voice

---

## 🛑 If Still Having Issues

### Google Fit Not Syncing?
```bash
# Check token was saved:
sqlite3 heart_health.db "SELECT config FROM data_sources WHERE source_type='google_fit';"

# Should show: access_token and refresh_token

# If empty/null → Token wasn't saved
# Solution: Reconnect OAuth again
```

### Voice Not Working?
```bash
# Check system audio:
# macOS: Top-right corner volume icon
# Windows: Bottom-right speaker icon
# Both: Try volume +50%

# If still nothing:
curl http://localhost:8000/api/v1/agent/voice/status
# Should show: "voice_enabled": true
```

### Microphone Not Recording?
```bash
# Test in different app first:
# - Open Zoom
# - Start recording
# - Does microphone work there?
# If yes: Browser permission issue
# If no: Hardware problem

# Grant permission:
# Chrome: Settings → Privacy → Site Settings → Microphone → Allow localhost:8000
```

---

## 📚 Full Guides Available

If you need detailed troubleshooting:

1. **SOLUTION_SUMMARY.md** - Complete overview
2. **TROUBLESHOOTING_VOICE_AND_GOOGLE_FIT.md** - Step-by-step fixes
3. **FIXES_AND_STATUS.md** - Technical details of what was fixed

---

## ⏱️ Timeline

```
Now:        Reconnect Google Fit (1-2 min)
1-2 min:    Real data syncs to dashboard  
2-5 min:    Confirm data matches phone
Done!       Everything working ✅
```

---

**Quick Links:**
- Dashboard: http://localhost:8000/static/dashboard/index.html
- API Docs: http://localhost:8000/docs
- Server: Running on localhost:8000

**Next Action:** Go to Devices tab → Connect Google Fit!
