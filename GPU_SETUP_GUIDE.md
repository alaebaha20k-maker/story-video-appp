# 🚀 Complete GPU Setup Guide - Fix All Image & Voice Errors

## 📋 Overview

This guide will help you set up a **Google Colab GPU server** to handle:
- ✅ **SDXL-Turbo** - Ultra-fast image generation
- ✅ **Kokoro TTS** - Professional voice synthesis

## 🎯 What This Fixes

### Before (Errors):
```
❌ SDXL-Turbo API error: 500
❌ Kokoro API error: 500
   'Kokoro.init() missing 2 required positional arguments'
⚠️ WARNING: 10/10 images failed to generate!
```

### After (Working):
```
✅ Generated 10/10 images with SDXL-Turbo (Remote GPU)
✅ Audio generated successfully! Duration: 180.5 seconds
🎬 Video compiled successfully!
```

---

## 🔧 Step-by-Step Setup

### Step 1: Get ngrok Account (FREE)

1. Go to [ngrok.com](https://ngrok.com/)
2. Sign up for a free account
3. Get your auth token from: https://dashboard.ngrok.com/get-started/your-authtoken
4. Copy the token (looks like: `2abc123def456ghi789jkl0`)

---

### Step 2: Upload Notebook to Google Colab

1. Go to [Google Colab](https://colab.research.google.com/)
2. Click **File → Upload notebook**
3. Upload the file: `GPU_Server_Complete_Fix.ipynb`
4. Once uploaded, click **Runtime → Change runtime type**
5. Select **GPU** (T4 GPU - FREE tier)
6. Click **Save**

---

### Step 3: Configure the Notebook

1. Find **STEP 6** in the notebook (ngrok setup cell)
2. Replace `YOUR_NGROK_TOKEN_HERE` with your actual token:
   ```python
   NGROK_AUTH_TOKEN = "2abc123def456ghi789jkl0"  # Your actual token
   ```
3. Click the **Save** button (💾)

---

### Step 4: Run the Notebook

1. Click **Runtime → Run all** (or press Ctrl+F9)
2. Wait 2-5 minutes for setup to complete
3. Look for the output that says:

   ```
   ═══════════════════════════════════════════════════════════
   ✅ GPU SERVER IS RUNNING!
   ═══════════════════════════════════════════════════════════

   🌐 Your Public URL:
      https://abc123def.ngrok-free.dev

   📋 Copy this URL and use it in your local app!
   ```

4. **COPY THIS URL!** You'll need it in the next step.

---

### Step 5: Configure Your Local App

#### Option A: Using .env file (Recommended)

1. In your project root, create/edit `.env` file:
   ```env
   # GPU Server Configuration
   SDXL_API_URL=https://abc123def.ngrok-free.dev/generate_image
   KOKORO_API_URL=https://abc123def.ngrok-free.dev/generate_audio
   ```

2. Replace `https://abc123def.ngrok-free.dev` with YOUR actual ngrok URL

#### Option B: Using environment variables

**Windows (PowerShell):**
```powershell
$env:SDXL_API_URL="https://abc123def.ngrok-free.dev/generate_image"
$env:KOKORO_API_URL="https://abc123def.ngrok-free.dev/generate_audio"
```

**Linux/Mac:**
```bash
export SDXL_API_URL="https://abc123def.ngrok-free.dev/generate_image"
export KOKORO_API_URL="https://abc123def.ngrok-free.dev/generate_audio"
```

---

### Step 6: Update Your Code to Use GPU Server

Update `api_server.py` to use the remote GPU server for image and voice generation:

```python
import os
from src.ai.sdxl_turbo_client import generate_sdxl_image
from src.voice.kokoro_api_client import generate_kokoro_audio

# Get API URLs from environment
SDXL_API_URL = os.getenv('SDXL_API_URL')
KOKORO_API_URL = os.getenv('KOKORO_API_URL')

# For image generation:
if SDXL_API_URL:
    # Use remote GPU
    image_path = generate_sdxl_image(
        prompt=prompt,
        output_path=output_path,
        api_url=SDXL_API_URL
    )
else:
    # Fallback to local generation
    # ... existing code ...

# For voice generation:
if KOKORO_API_URL:
    # Use remote GPU
    audio_path = generate_kokoro_audio(
        text=text,
        voice=voice,
        speed=speed,
        output_path=output_path,
        api_url=KOKORO_API_URL
    )
else:
    # Fallback to Edge-TTS
    # ... existing code ...
```

---

### Step 7: Test Everything

1. **Test Health Check:**
   ```bash
   curl https://your-ngrok-url.ngrok-free.dev/health
   ```

   Should return:
   ```json
   {
     "status": "ok",
     "device": "cuda",
     "services": {
       "sdxl_turbo": "ready",
       "kokoro_tts": "ready"
     }
   }
   ```

2. **Test Image Generation:**
   ```bash
   curl -X POST https://your-ngrok-url.ngrok-free.dev/generate_image \
     -H "Content-Type: application/json" \
     -d '{"prompt": "a beautiful sunset"}'
   ```

3. **Test Voice Generation:**
   ```bash
   curl -X POST https://your-ngrok-url.ngrok-free.dev/generate_audio \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello world", "voice": "aria", "speed": 1.0}'
   ```

4. **Run Your App:**
   ```bash
   python api_server.py
   ```

   Generate a video and watch for:
   ```
   ✅ Generated 10/10 images with SDXL-Turbo (Remote GPU)
   ✅ Audio generated successfully!
   ```

---

## 🔍 Troubleshooting

### Problem: "Cannot connect to API"

**Solutions:**
1. Check if Colab notebook is still running
2. Verify ngrok URL is correct
3. Check internet connection
4. Restart the Colab notebook

---

### Problem: "ngrok connection closed"

**Solutions:**
1. Free ngrok tunnels disconnect after 2 hours of inactivity
2. Simply re-run the last cell in the notebook
3. Copy the NEW ngrok URL and update your .env file

---

### Problem: "CUDA out of memory"

**Solutions:**
1. In Google Colab, click **Runtime → Restart runtime**
2. Re-run all cells
3. This clears GPU memory

---

### Problem: "Still getting 500 errors"

**Solutions:**
1. Check the Colab notebook output for error messages
2. Make sure you're using the correct endpoints:
   - `/generate_image` for images
   - `/generate_audio` for voice
   - `/health` for status check
3. Verify the request format matches the examples above

---

## 💡 Tips & Best Practices

### 1. Keep Colab Notebook Running
- The free tier may disconnect after idle time
- Keep the browser tab open
- Consider upgrading to Colab Pro for longer sessions

### 2. Monitor GPU Usage
- In Colab, check **Runtime → Manage sessions**
- You can see GPU memory usage

### 3. Optimize Prompts
- SDXL-Turbo works best with clear, descriptive prompts
- Keep prompts concise (50-100 words)

### 4. Voice Generation
- For long texts, the API automatically splits into chunks
- Typical generation: ~5-10 seconds per 1000 characters

### 5. Speed Expectations
- **Image generation:** 2-5 seconds per image on GPU
- **Voice generation:** 10-30 seconds per minute of audio
- **Total video:** 3-10 minutes for 5-10 minute video

---

## 📊 Comparison: Before vs After

| Feature | Before (Errors) | After (GPU Server) |
|---------|----------------|-------------------|
| Image Generation | ❌ 500 errors | ✅ 2-5 sec/image |
| Voice Quality | ❌ Failed | ✅ Professional |
| Success Rate | ❌ 0/10 images | ✅ 10/10 images |
| Cost | N/A | 💰 FREE (Google Colab) |
| Setup Time | N/A | ⏱️ 5-10 minutes |

---

## 🎓 Understanding the Architecture

```
┌─────────────────────┐
│   Your Local App    │
│   (api_server.py)   │
└──────────┬──────────┘
           │
           │ HTTP POST
           │
           ▼
┌─────────────────────┐
│   ngrok Tunnel      │
│ (Public Internet)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Google Colab GPU   │
│                     │
│  ┌──────────────┐  │
│  │ SDXL-Turbo   │  │
│  │ (Images)     │  │
│  └──────────────┘  │
│                     │
│  ┌──────────────┐  │
│  │ Kokoro TTS   │  │
│  │ (Voice)      │  │
│  └──────────────┘  │
└─────────────────────┘
```

---

## 🆘 Need Help?

If you're still experiencing issues:

1. **Check Logs:**
   - Colab notebook output (scroll down)
   - Your local app terminal output

2. **Verify Setup:**
   - ngrok token is correct
   - GPU runtime is selected in Colab
   - Environment variables are set

3. **Test Endpoints:**
   - Use curl or Postman to test each endpoint
   - Verify responses match expected format

4. **Common Mistakes:**
   - Wrong ngrok URL (forgot to update .env)
   - Notebook stopped running
   - No GPU selected in Colab runtime

---

## ✅ Success Checklist

- [ ] ngrok account created and token obtained
- [ ] Notebook uploaded to Google Colab
- [ ] GPU runtime selected
- [ ] ngrok token added to notebook
- [ ] All cells executed successfully
- [ ] Public URL copied
- [ ] .env file updated with correct URLs
- [ ] Health check endpoint returns "ok"
- [ ] Test image generation works
- [ ] Test voice generation works
- [ ] Local app successfully generates videos

---

## 🎉 Congratulations!

Once everything is set up, you'll have:
- ✅ Professional image generation with SDXL-Turbo
- ✅ High-quality voice synthesis with Kokoro TTS
- ✅ FREE GPU acceleration via Google Colab
- ✅ No more 500 errors!

Happy video creating! 🎬
