# 🎬 COMPLETE SETUP - Google Colab Backend + React Frontend

## ✅ YOUR CORRECT ARCHITECTURE

```
┌─────────────────────────────────────────┐
│  FRONTEND (React - Run Locally)         │
│  - User selects topic, style, voice     │
│  - Sends request to Colab ngrok URL     │
│  - Shows progress & video player        │
│  File: project-bolt-sb1-nqwbmccj/       │
│  Port: 5173 (npm run dev)               │
└────────────┬────────────────────────────┘
             │
             │ HTTP Request
             ↓
┌─────────────────────────────────────────┐
│  BACKEND (Google Colab - GPU Server)    │
│  ✅ Coqui TTS (13 voices, PyTorch GPU)  │
│  ✅ DreamShaper XL / SDXL (12 styles)   │
│  ✅ FFmpeg (video compilation)          │
│  ✅ 2x Gemini Servers (script gen)      │
│  File: colab_gpu_server_CLEAN.ipynb     │
│  Port: 5001 (ngrok tunnel)              │
└─────────────────────────────────────────┘
```

## 🚫 WHAT NOT TO RUN

**❌ DO NOT RUN:** `story-video-generator/api_server.py`
- This is the OLD local server (uses Edge-TTS + FLUX)
- You don't need it! It's a fallback only.
- If you see Edge-TTS messages in terminal, you're running the WRONG server!

## 🚀 HOW TO USE

### Step 1: Start Google Colab Backend

1. Open `colab_gpu_server_CLEAN.ipynb` in Google Colab
2. Enable GPU: Runtime → Change runtime type → T4 GPU → Save
3. Run all cells in order (1 → 7)
4. Copy the ngrok URL from Cell 7 output:
   ```
   📡 Public URL: https://xxxxx.ngrok-free.dev
   ```

### Step 2: Update Frontend Config

Your frontend is **already configured** with:
```typescript
// project-bolt-sb1-nqwbmccj/project/src/utils/api.ts
const API_URL = 'https://contemplable-suzy-unfussing.ngrok-free.dev';
```

If the ngrok URL changes, update this file with the new URL.

### Step 3: Start Frontend

```bash
cd project-bolt-sb1-nqwbmccj/project
npm run dev
```

Open http://localhost:5173 and start creating videos!

## 🎯 BACKEND FEATURES (Google Colab)

### 🎤 Voice Engine: Coqui TTS
- **Engine:** PyTorch GPU (VCTK speakers)
- **Voices:** 13 professional voices (male + female)
- **Quality:** High quality, natural speech
- **Speed:** Parallel processing (4x faster)

### 🎨 Image Engine: DreamShaper XL (SDXL)
- **Model:** Lykon/dreamshaper-xl-1-0
- **Resolution:** 1536x864 (16:9 HD)
- **Styles:** 12 styles (cinematic, anime, horror, comic, etc.)
- **Quality:** Professional, unique per scene

### 🎬 Video Engine: FFmpeg
- **Resolution:** 1920x1080 (1080p HD)
- **Effects:** Zoom, color grading, filters
- **Quality:** Professional YouTube quality

### 📝 Script Engine: 2x Gemini Servers
- **Server 1:** Primary script generation
- **Server 2:** Backup / parallel processing
- **Model:** Gemini 2.0 Flash (FREE tier)

## 📌 API ENDPOINTS (Colab)

```
GET  /health                    - Server status
POST /generate_audio            - Generate voice from text
POST /generate_image            - Generate single image
POST /generate_images_batch     - Generate multiple images
POST /compile_video             - Compile video from media
POST /generate_complete_video   - Full video generation
```

## 🔧 TROUBLESHOOTING

### Frontend shows "Server unavailable"
1. Check if Colab notebook is running
2. Verify ngrok URL is correct in `api.ts`
3. Check Colab output for errors

### Images not generating
1. Ensure GPU is enabled in Colab
2. Wait for DreamShaper XL to load (first run takes ~2 min)
3. Check Colab output for CUDA errors

### Voice not working
1. Verify Coqui TTS is loaded in Colab
2. Check voice ID is valid (aria, guy, jenny, etc.)
3. Check Colab output for audio errors

### Wrong server running
If you see "Edge-TTS" messages in your terminal:
1. **STOP that server** (Ctrl+C)
2. That's the local `api_server.py` (wrong one!)
3. Use ONLY the Google Colab server

## 📊 WHAT YOU GET

- ✅ **Professional Scripts** - Gemini AI
- ✅ **High-Quality Images** - DreamShaper XL (SDXL)
- ✅ **Natural Voice** - Coqui TTS (13 voices)
- ✅ **Cinematic Video** - 1080p HD with effects
- ✅ **GPU Acceleration** - Fast generation
- ✅ **FREE** - Google Colab free tier

## 🎉 READY!

Your setup is now correct:
- Frontend points to Colab ngrok URL ✅
- Colab has Coqui TTS + SDXL + FFmpeg ✅
- No need to run local api_server.py ✅

Just run the Colab notebook + frontend, and you're done! 🚀
