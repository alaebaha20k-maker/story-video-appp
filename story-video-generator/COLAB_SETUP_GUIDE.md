# 🚀 Google Colab GPU Setup Guide

## System Architecture

Your Story Video Generator uses a **hybrid architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                  STORY VIDEO GENERATOR                       │
└─────────────────────────────────────────────────────────────┘
                            │
           ┌────────────────┴────────────────┐
           │                                 │
    ┌──────▼──────┐                  ┌──────▼──────┐
    │   LOCAL     │                  │   COLAB     │
    │  BACKEND    │◄────────────────►│  GPU SERVER │
    │  (Flask)    │   HTTP/ngrok     │  (Flask)    │
    │  Port: 5000 │                  │  Port: 5001 │
    └─────────────┘                  └─────────────┘
           │                                 │
           │                          ┌──────┴──────┐
           │                          │             │
    ┌──────▼──────┐              ┌────▼───┐   ┌────▼────┐
    │   Gemini    │              │ Kokoro │   │  SDXL   │
    │     AI      │              │  TTS   │   │ Turbo   │
    │  (Scripts)  │              │ (GPU)  │   │  (GPU)  │
    └─────────────┘              └────────┘   └─────────┘
           │                          │             │
    ┌──────▼──────┐              └─────┬───────────┘
    │   FFmpeg    │                    │
    │   (Video)   │◄───────────────────┘
    └─────────────┘              Audio + Images
```

### Component Roles:

| Component | Location | Purpose |
|-----------|----------|---------|
| **Script Generation** | Local (Gemini API) | Generate story scripts |
| **Voice Generation** | Colab GPU (Kokoro TTS) | Generate narration audio |
| **Image Generation** | Colab GPU (SDXL-Turbo) | Generate 16:9 images |
| **Video Compilation** | Local (FFmpeg) | Combine audio + images → MP4 |

---

## 🎯 Quick Start (3 Steps)

### Step 1: Start Google Colab Notebook

1. Open your Colab notebook (the .ipynb file you shared)
2. **Enable GPU**: `Runtime` → `Change runtime type` → `GPU` → `T4 GPU`
3. **Run all cells** (Ctrl+F9 or Runtime → Run all)
4. Wait for ngrok URL to appear (e.g., `https://xxxx-xxxx.ngrok-free.app`)
5. **Copy the ngrok URL**

### Step 2: Configure Local Backend

1. Open `story-video-generator/config/__init__.py`
2. Update line 13:
   ```python
   COLAB_SERVER_URL = 'https://xxxx-xxxx.ngrok-free.app'  # ← Paste your ngrok URL here
   ```
3. Save the file

### Step 3: Start Local Backend

```powershell
cd story-video-generator
python api_server.py
```

Expected output:
```
🌐 Using Google Colab GPU Server (via ngrok)
✅ Kokoro TTS (48 voices, GPU-accelerated)
✅ SDXL-Turbo (16:9 images, GPU-accelerated)
✅ Colab server connected!

🔥 PROFESSIONAL YOUTUBE VIDEO GENERATOR!
📍 URL: http://localhost:5000
```

✅ **Done!** Your system is ready!

---

## 📋 Detailed Setup

### Prerequisites

#### On Local Machine:
- Python 3.8+
- FFmpeg installed
- Gemini API key
- Internet connection

#### On Google Colab:
- Google account
- GPU runtime enabled (T4, V100, or A100)

---

## 🔧 Configuration Files

### 1. `config/__init__.py`

This is where you configure the ngrok URL:

```python
# ⚠️ IMPORTANT: Update this URL when you start your Colab notebook!
COLAB_SERVER_URL = 'https://your-ngrok-url-here.ngrok-free.app'
```

**How to get the ngrok URL:**
1. Run all cells in your Colab notebook
2. Look for the output from the last cell
3. Copy the "Public URL" that looks like: `https://xxxx-xxxx.ngrok-free.app`
4. Paste it in `config/__init__.py`

---

## 🎤 Voice Options (Kokoro TTS)

Your Colab notebook has 48 professional voices. Here are the main ones:

### Male Voices:
- `guy` - Natural & Clear (default)
- `adam_narration` - Professional Narration
- `michael` - Warm & Friendly
- `brian` - Casual
- `george` - British Accent

### Female Voices:
- `aria` - Natural & Warm
- `sarah_pro` - Professional
- `nicole` - Cheerful & Clear
- `jenny` - Young & Energetic
- `emma` - British Accent

---

## 🎨 Image Generation (SDXL-Turbo)

**Resolution:** 1920x1080 (16:9 aspect ratio)
**Model:** SDXL-Turbo (4-step diffusion)
**Speed:** ~5-10 seconds per image on T4 GPU
**Quality:** Cinematic, professional

---

## 🔍 Testing Your Setup

### Test 1: Check Colab Connection

```powershell
python -c "from src.utils.colab_client import get_colab_client; client = get_colab_client(); client.check_health()"
```

Expected output:
```
✅ Colab server healthy!
   Device: cuda
   GPU: Tesla T4
```

### Test 2: Test Voice Generation

```powershell
python src/utils/colab_client.py
```

This will:
1. Test health check
2. Generate test audio
3. Generate test image
4. Generate batch images

---

## ⚠️ Troubleshooting

### Problem 1: "Cannot connect to Colab server"

**Cause:** ngrok URL is wrong or Colab is not running

**Solution:**
1. Make sure Colab notebook is running
2. Check if ngrok URL in `config/__init__.py` is correct
3. Try copying the URL again from Colab output

### Problem 2: "CUDA out of memory"

**Cause:** GPU RAM is full (T4 has 15GB)

**Solution:**
- Colab automatically unloads models to save memory
- If error persists, restart Colab runtime:
  - `Runtime` → `Restart runtime`
  - Run all cells again

### Problem 3: ngrok URL changes every time

**Cause:** Free ngrok URLs are temporary

**Solution:**
- Update `config/__init__.py` every time you restart Colab
- OR upgrade to ngrok Pro for permanent URLs

### Problem 4: "Ngrok auth token invalid"

**Cause:** Ngrok token in Colab notebook is wrong

**Solution:**
1. Get your ngrok token from https://dashboard.ngrok.com/get-started/your-authtoken
2. Update Cell 6 in Colab notebook:
   ```python
   NGROK_AUTH_TOKEN = "your-token-here"
   ```

---

## 🚀 Starting Your System (Daily Workflow)

### Every time you want to generate videos:

1. **Start Colab** (1 minute)
   - Open Colab notebook
   - Run all cells
   - Copy ngrok URL

2. **Update Config** (10 seconds)
   - Paste ngrok URL in `config/__init__.py`
   - Save file

3. **Start Backend** (5 seconds)
   ```powershell
   cd story-video-generator
   python api_server.py
   ```

4. **Start Frontend** (5 seconds)
   ```powershell
   cd project-bolt-sb1-nqwbmccj/project
   npm run dev
   ```

5. **Generate Videos!** 🎬

---

## 📊 System Performance

| Task | Time | Location |
|------|------|----------|
| Script Generation | 30s | Local (Gemini API) |
| Image Generation (x10) | 1-2 min | Colab GPU (SDXL-Turbo) |
| Voice Generation | 30-60s | Colab GPU (Kokoro TTS) |
| Video Compilation | 1-2 min | Local (FFmpeg) |
| **Total** | **3-5 min** | **for 5-min video** |

---

## 💰 Cost Breakdown

| Component | Cost | Notes |
|-----------|------|-------|
| Google Colab | **FREE** | T4 GPU included in free tier |
| Kokoro TTS | **FREE** | Open-source model |
| SDXL-Turbo | **FREE** | Open-source model |
| Ngrok | **FREE** | Free tier (temporary URLs) |
| Gemini API | **FREE** | 15 requests/min free tier |
| FFmpeg | **FREE** | Open-source software |
| **TOTAL** | **$0/month** | 100% free! |

---

## 🔐 Security Notes

### ngrok URL:
- Your ngrok URL is **public** (anyone with the URL can access it)
- Don't share your ngrok URL publicly
- URL changes every time you restart Colab (free tier)

### API Keys:
- Keep your Gemini API key secret
- Keep your ngrok auth token secret
- Never commit API keys to git

---

## 📚 File Structure

```
story-video-appp/
├── story-video-generator/          ← LOCAL BACKEND
│   ├── api_server.py               ← Main server (uses Colab)
│   ├── config/
│   │   └── __init__.py             ← COLAB_SERVER_URL here!
│   ├── src/
│   │   ├── ai/
│   │   │   └── enhanced_script_generator.py  ← Gemini (local)
│   │   ├── editor/
│   │   │   └── ffmpeg_compiler.py  ← FFmpeg (local)
│   │   └── utils/
│   │       └── colab_client.py     ← Calls Colab endpoints
│   └── output/
│       ├── videos/                 ← Final MP4 files
│       └── temp/                   ← Images & audio from Colab
│
└── project-bolt-sb1-nqwbmccj/project/  ← FRONTEND
    ├── src/
    │   ├── pages/
    │   │   └── GeneratorPage.tsx   ← Main UI
    │   └── utils/
    │       └── api.ts              ← Calls local backend
    └── package.json
```

---

## 🎬 How Video Generation Works

1. **User enters topic** in frontend
2. **Frontend sends request** to local backend (port 5000)
3. **Local backend:**
   - Calls Gemini API to generate script ✅
   - Calls Colab `/generate_images_batch` to get 10 images ✅
   - Calls Colab `/generate_audio` to get narration ✅
   - Saves images and audio to `output/temp/`
   - Uses FFmpeg to compile video ✅
4. **Frontend displays video**

---

## ✅ Checklist: Is Everything Working?

- [ ] Colab notebook is running
- [ ] Colab shows ngrok URL
- [ ] `config/__init__.py` has correct ngrok URL
- [ ] Local backend starts without errors
- [ ] Backend says "✅ Colab server connected!"
- [ ] Frontend is running
- [ ] Can generate videos successfully

---

## 🆘 Need Help?

1. Check Colab output for errors
2. Check backend terminal for errors
3. Test Colab connection:
   ```powershell
   python src/utils/colab_client.py
   ```
4. Make sure GPU is enabled in Colab
5. Verify ngrok URL is correct

---

## 🎉 You're All Set!

Your system now uses:
- ✅ **Kokoro TTS (48 voices)** - GPU-accelerated on Colab
- ✅ **SDXL-Turbo** - GPU-accelerated on Colab
- ✅ **FFmpeg** - Local video compilation
- ✅ **Gemini AI** - Local script generation

**Total cost: $0/month** 🎊

Start generating professional YouTube videos! 🚀
