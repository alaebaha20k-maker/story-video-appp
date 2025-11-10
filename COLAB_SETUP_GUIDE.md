# 🚀 GOOGLE COLAB GPU SERVER - COMPLETE SETUP GUIDE

**Last Updated**: 2025-11-10
**GPU**: NVIDIA T4 (15 GB)
**System**: Story Video Generator with Kokoro TTS + SDXL-Turbo

---

## 📋 WHAT YOU NEED

1. **Google Account** (for Google Colab)
2. **Ngrok Account** (for public URL) - Get free at: https://ngrok.com/
3. **GPU Runtime** (T4 GPU in Google Colab)

---

## 🎯 STEP-BY-STEP SETUP

### STEP 1: Upload Notebook to Google Colab

1. **Open Google Colab**: https://colab.research.google.com/
2. **Upload notebook**:
   - Click: `File` → `Upload notebook`
   - Select: `Google_Colab_GPU_Server.ipynb` from this repo
   - Wait for upload to complete

### STEP 2: Enable GPU Runtime

⚠️ **CRITICAL: You MUST enable GPU or it won't work!**

1. Click: `Runtime` → `Change runtime type`
2. Select: `Hardware accelerator` → **GPU**
3. Select: `GPU type` → **T4 GPU** (free tier)
4. Click: `Save`

**Verify GPU is enabled:**
- You'll see "🔥 Connected to GPU" message when you run the notebook

### STEP 3: Get Ngrok Auth Token

1. Go to: https://dashboard.ngrok.com/signup
2. Sign up (free account)
3. Go to: https://dashboard.ngrok.com/get-started/your-authtoken
4. Copy your auth token (looks like: `2abcd...xyz123`)

### STEP 4: Run the Notebook

1. **Update Ngrok token** (Cell 6):
   ```python
   NGROK_AUTH_TOKEN = "2abcd...xyz123"  # ← Paste your token here
   ```

2. **Run all cells**:
   - Click: `Runtime` → `Run all`
   - OR: Press `Ctrl+F9` (Windows) / `Cmd+F9` (Mac)

3. **Wait for setup** (2-3 minutes):
   - Installing dependencies...
   - Loading GPU...
   - Starting server...

### STEP 5: Copy Your Ngrok URL

When the server starts, you'll see:

```
═══════════════════════════════════════════════════════════════
🎉 SERVER RUNNING!
═══════════════════════════════════════════════════════════════

📡 Public URL: https://abc-123-xyz.ngrok-free.dev
🖥️  Local URL:  http://localhost:5000

🎮 Device: CUDA
🔥 GPU: Tesla T4
💾 GPU Memory: 14.7 GB

📌 API Endpoints:
   https://abc-123-xyz.ngrok-free.dev/health
   https://abc-123-xyz.ngrok-free.dev/generate_audio
   https://abc-123-xyz.ngrok-free.dev/generate_image
   https://abc-123-xyz.ngrok-free.dev/generate_images_batch
```

**COPY the Public URL**: `https://abc-123-xyz.ngrok-free.dev`

### STEP 6: Update Backend Configuration

1. **Open** `story-video-generator/config.py`
2. **Replace** the URL:
   ```python
   COLAB_SERVER_URL = os.getenv(
       'COLAB_SERVER_URL',
       'https://abc-123-xyz.ngrok-free.dev'  # ← Paste your URL here
   )
   ```
3. **Save** the file

### STEP 7: Start Your Backend Server

```bash
cd story-video-generator
python api_server.py
```

You should see:
```
🌐 Colab Server URL: https://abc-123-xyz.ngrok-free.dev
🎤 Kokoro API: https://abc-123-xyz.ngrok-free.dev/generate_audio
🎨 SDXL API: https://abc-123-xyz.ngrok-free.dev/generate_image
```

### STEP 8: Start Your Frontend

```bash
cd project-bolt-sb1-nqwbmccj/project
npm run dev
```

---

## ✅ VERIFICATION CHECKLIST

### Check GPU is Working:
- [ ] Colab shows "🔥 GPU: Tesla T4"
- [ ] Device shows "CUDA" (not "CPU")
- [ ] GPU Memory shows "14.7 GB"

### Check Server is Running:
- [ ] Ngrok URL is displayed
- [ ] All 4 endpoints are listed
- [ ] No errors in Colab output

### Check Backend Connection:
- [ ] Backend shows Colab URL in startup
- [ ] No connection errors when generating
- [ ] Voice generation works
- [ ] Image generation works

---

## 🔧 TROUBLESHOOTING

### Problem 1: "Device: CPU" (GPU Not Detected)

**Symptoms:**
```
⚠️  WARNING: GPU NOT DETECTED - Running on CPU (SLOW!)
RuntimeError: Found no NVIDIA driver
```

**Solution:**
1. Stop notebook execution
2. Click: `Runtime` → `Change runtime type`
3. Select: `Hardware accelerator` → **GPU**
4. Click: `Save`
5. Click: `Runtime` → `Run all`

### Problem 2: "Out of Memory" Error

**Symptoms:**
```
OutOfMemoryError: CUDA out of memory
```

**Solution:**
- This is normal! The notebook uses **on-demand model loading**
- TTS and Image models load separately
- One model unloads before loading the other
- If still happening, restart runtime: `Runtime` → `Restart runtime`

### Problem 3: Ngrok Token Error

**Symptoms:**
```
⚠️  WARNING: Please set your Ngrok auth token above!
```

**Solution:**
1. Get token: https://dashboard.ngrok.com/get-started/your-authtoken
2. Edit Cell 6: Replace `"YOUR_NGROK_TOKEN_HERE"` with your token
3. Re-run Cell 6 only

### Problem 4: Backend Can't Connect to Colab

**Symptoms:**
```
Error: Failed to connect to Colab server
Connection refused
```

**Solution:**
1. Verify Colab server is running
2. Copy the EXACT Ngrok URL (with https://)
3. Update `story-video-generator/config.py`
4. Restart backend server

### Problem 5: Colab Session Disconnected

**Symptoms:**
```
Server stopped running
Ngrok tunnel closed
```

**Solution:**
- Colab free tier disconnects after **90 minutes** of inactivity
- Or after **12 hours** maximum
- **To fix**: Re-run all cells in Colab
- Copy new Ngrok URL
- Update `config.py`
- Restart backend

---

## ⚡ PERFORMANCE EXPECTATIONS

### With GPU T4 (This Setup):
```
Audio Generation:    1-2 seconds per sentence
Image Generation:    2-3 seconds per image (1920x1080)
Batch Images (10):   20-30 seconds
1-hour video:        5-8 minutes total ⚡
```

### Without GPU (CPU - Not Recommended):
```
Audio Generation:    5-10 seconds per sentence
Image Generation:    30-60 seconds per image
1-hour video:        30-45 minutes total 🐌
```

---

## 🎮 USAGE TIPS

### Keep Colab Session Alive:
- Keep Colab tab open in browser
- Colab disconnects if inactive for 90 minutes
- Consider Colab Pro ($10/month) for:
  - Longer runtimes (24 hours)
  - Better GPUs (V100, A100)
  - Priority access

### Monitor GPU Usage:
```python
# Run this in a new Colab cell
!nvidia-smi
```

You'll see:
- GPU temperature
- Memory usage
- Current processes

### Restart Models if Stuck:
```python
# Run this in a new Colab cell
clear_gpu_memory()
```

---

## 📊 SYSTEM ARCHITECTURE

```
Frontend (React)
    ↓
Backend (Flask Python)
    ↓
Google Colab GPU Server (Ngrok)
    ├─ Kokoro TTS (Voice Generation)
    └─ SDXL-Turbo (Image Generation)
    ↓
Video Output (1920x1080 MP4)
```

---

## 🔐 SECURITY NOTES

- **Ngrok URL is public** - Anyone with URL can access your server
- **Free Ngrok** changes URL every time you restart
- **Colab free** tier has usage limits
- **Don't share** your Ngrok auth token

---

## 💡 ALTERNATIVE: Run Without Colab

If you have a local GPU:

1. Install dependencies:
   ```bash
   pip install kokoro-onnx diffusers transformers torch
   ```

2. Update config to use `localhost`:
   ```python
   COLAB_SERVER_URL = "http://localhost:5000"
   ```

3. Run server locally (instead of Colab)

---

## 📞 SUPPORT

### Getting Help:

1. **Check Colab logs** - Errors appear in notebook output
2. **Check backend logs** - Errors appear in terminal
3. **Verify GPU** - Run Cell 2 to check GPU status
4. **Test endpoints** - Visit ngrok-url/health in browser

### Common Issues:

| Issue | Quick Fix |
|-------|-----------|
| CPU instead of GPU | Change runtime type to GPU |
| Out of memory | Normal! Uses on-demand loading |
| Connection refused | Update config.py with new ngrok URL |
| Colab disconnected | Re-run all cells, copy new URL |
| Voice/Image errors | Check backend logs for details |

---

## 🎉 SUCCESS INDICATORS

You'll know everything is working when:

✅ Colab shows: "🔥 GPU: Tesla T4"
✅ Backend shows: "🌐 Colab Server URL: https://..."
✅ Frontend generates videos successfully
✅ Audio plays correctly (Kokoro TTS)
✅ Images look high quality (SDXL-Turbo)
✅ Videos compile in 5-8 minutes

---

**Ready? Start with STEP 1 above! 🚀**
