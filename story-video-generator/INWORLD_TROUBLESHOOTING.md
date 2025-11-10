# 🔧 INWORLD API TROUBLESHOOTING GUIDE

## ❌ Problem

**Error:** "❌ No audio data generated! All chunks failed!"

This means **ALL** Inworld API calls are failing, not just voice name issues.

---

## 🔍 STEP 1: Test Your Inworld API Credentials

Run the diagnostic tool I created:

```bash
cd story-video-generator
python test_inworld_api.py
```

**This will test:**
1. ✅ Your JWT credentials
2. ✅ All 8 voice names (Ashley, Emma, Sarah, Rachel, Brandon, Christopher, Daniel, Ethan)
3. ✅ API endpoint and authentication
4. ✅ Save test audio files for working voices

---

## 📊 DIAGNOSTIC RESULTS

### ✅ If Some Voices Work:

```
Testing voice: Ashley...
   Status Code: 200
   ✅ SUCCESS! Audio received: 12345 bytes
   ✅ Saved to: test_ashley.mp3
```

**Action:** Use ONLY the voices that work! Update the voice list.

---

### ❌ If ALL Voices Fail (Authentication Error):

```
Testing voice: Ashley...
   Status Code: 401
   ❌ ERROR: {"error": "Invalid credentials"}
```

**Possible Causes:**
1. ❌ Invalid JWT Key/Secret
2. ❌ Expired API key
3. ❌ Account not activated
4. ❌ Wrong API endpoint

**Solutions:**

#### A. Verify Your Credentials

Check your Inworld AI dashboard:
1. Go to https://platform.inworld.ai/
2. Navigate to API Keys section
3. Verify your JWT Key and Secret match:
   - JWT Key: `bMyt2B6JztQUliqlBm6HHdQCcAbsJXnJ`
   - JWT Secret: `siWpw2isZJkLIE6llDql2yi2D5xAyT7qQYop4he0X1seZ8ZksvCDzS1gWJcccIyD`

#### B. Regenerate API Key

If credentials are wrong:
1. Generate new API key in Inworld dashboard
2. Update `.env` file:
   ```
   INWORLD_JWT_KEY=your_new_key_here
   INWORLD_JWT_SECRET=your_new_secret_here
   ```

#### C. Check Account Status

- ✅ Account must be activated
- ✅ TTS API must be enabled
- ✅ Credits/quota must be available

---

### ❌ If Network/Connection Error:

```
Testing voice: Ashley...
   ❌ TIMEOUT after 30 seconds
```

**Possible Causes:**
1. ❌ Firewall blocking API
2. ❌ VPN interfering
3. ❌ Network restrictions
4. ❌ Inworld API down

**Solutions:**
1. Disable firewall temporarily
2. Disable VPN
3. Check https://status.inworld.ai/ for API status

---

## 🔄 STEP 2: TEMPORARY SOLUTION - Use Edge-TTS (FREE!)

**While troubleshooting Inworld, use Edge-TTS (Microsoft) - it's FREE and WORKS!**

### Enable Edge-TTS Fallback:

I'll add automatic fallback, but you can test Edge-TTS now:

```python
# In api_server.py, temporarily change:
voice_engine = 'edge'  # Instead of 'inworld'
```

**Edge-TTS Features:**
✅ **FREE** - Unlimited use
✅ **FAST** - Parallel processing
✅ **RELIABLE** - Always works
✅ **10+ voices** - Multiple options
✅ **NO API KEY** - No setup needed

**Edge-TTS Voices:**
- `en-US-AriaNeural` - Female, natural
- `en-US-GuyNeural` - Male, mature
- `en-US-JennyNeural` - Female, cheerful
- `en-US-ChristopherNeural` - Male, casual
- `en-GB-SoniaNeural` - Female, British
- And many more!

---

## 🚀 STEP 3: PERMANENT FIX OPTIONS

### Option A: Fix Inworld API

1. Run diagnostic: `python test_inworld_api.py`
2. Note which voices work (if any)
3. Update credentials if needed
4. Use only working voices

---

### Option B: Switch to Edge-TTS (Recommended!)

Edge-TTS is:
- ✅ More reliable
- ✅ Completely free
- ✅ No API limits
- ✅ No authentication issues
- ✅ More voice options

**To permanently switch:**

```bash
# Edit .env file
VOICE_ENGINE=edge  # Instead of inworld
```

Or in code, change default:
```python
voice_engine = data.get('voice_engine', 'edge')  # Was 'inworld'
```

---

### Option C: Hybrid Approach

Use both! Try Inworld first, fallback to Edge-TTS if it fails:

```python
try:
    # Try Inworld first
    audio_path = generate_audio_inworld(text, voice, output_path)
except Exception as e:
    print("⚠️ Inworld failed, falling back to Edge-TTS...")
    # Fallback to Edge-TTS
    audio_path = await generate_audio_edge_tts(text, edge_voice, output_path)
```

---

## 📝 QUICK TEST CHECKLIST

Run through these tests:

```bash
# 1. Test Inworld API directly
python test_inworld_api.py

# 2. Check if test audio files were created
ls -la test_*.mp3

# 3. If Inworld works, restart backend
python api_server.py

# 4. If Inworld fails, switch to Edge-TTS
# Edit .env: VOICE_ENGINE=edge
python api_server.py

# 5. Generate test video
# Should work with whichever engine you're using!
```

---

## 🎯 COMMON ISSUES & FIXES

### Issue 1: "Unknown voice: [name] not found"
**Fix:** Voice name doesn't exist. Use diagnostic to find working voices.

### Issue 2: "Status 401: Invalid credentials"
**Fix:** JWT Key/Secret wrong. Check Inworld dashboard and regenerate.

### Issue 3: "Status 429: Too many requests"
**Fix:** Rate limiting. Reduce parallel workers from 6 to 3.

### Issue 4: "Connection timeout"
**Fix:** Network issue. Check firewall, VPN, or use Edge-TTS.

### Issue 5: "All chunks failed"
**Fix:** API completely broken. Switch to Edge-TTS.

---

## 💡 RECOMMENDATION

**For most users, I recommend Edge-TTS:**

✅ **Why Edge-TTS?**
- Completely free (no API key needed)
- Unlimited use (no quotas)
- More reliable (Microsoft infrastructure)
- Faster setup (no authentication)
- 10+ professional voices
- Always works (no API issues)

❌ **Why NOT Inworld?**
- Requires API key/authentication
- Can have API failures
- Rate limiting possible
- Costs money (after free tier)
- More complex setup

**Your Choice:**
- Want reliability & simplicity? → **Use Edge-TTS**
- Want specific Inworld voices? → **Fix Inworld API** (use diagnostic)
- Want both? → **Hybrid approach** (try Inworld, fallback to Edge)

---

## 🚀 NEXT STEPS

1. **Run diagnostic:**
   ```bash
   python test_inworld_api.py
   ```

2. **Check results:**
   - If voices work → Great! Use those voices
   - If auth fails → Fix credentials or switch to Edge-TTS
   - If network fails → Check firewall or switch to Edge-TTS

3. **Choose solution:**
   - Fix Inworld (if you need those specific voices)
   - Switch to Edge-TTS (recommended for reliability)
   - Use hybrid (best of both)

4. **Test video generation:**
   - Should work with whichever engine you choose!

---

**Need help? Check the diagnostic results and follow the specific fix for your error!** 🔧
