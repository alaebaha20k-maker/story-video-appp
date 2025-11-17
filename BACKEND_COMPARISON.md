# 🆚 OLD vs NEW BACKEND - COMPLETE COMPARISON

## 📊 PARAMETERS COMPARISON

### **OLD BACKEND (`api_server.py`)**

```python
# Endpoint: POST /api/generate-video
data = {
    'topic': str,                    # ✅ Same
    'story_type': str,               # ✅ Same
    'duration': int (minutes),       # ✅ Same
    'num_scenes': int,               # ✅ Same
    'image_style': str,              # ✅ Same
    'voice_id': str,                 # ✅ Same (Edge-TTS voices)
    'zoom_effect': bool,             # ⚠️ Changed to zoom_intensity
}
```

**What OLD backend does:**
1. Generate script with `enhanced_script_generator` (local Gemini)
2. Generate images with Pollinations/Together AI (local)
3. Generate voice with **Edge-TTS** (local, FREE)
4. Compile video with FFmpeg (local)
5. Apply zoom effect (boolean on/off)

**Missing in OLD:**
- ❌ No auto-captions
- ❌ No zoom intensity control (just on/off)
- ❌ No color filters
- ❌ No voice speed control
- ❌ No Google Colab integration
- ❌ No Coqui TTS (uses Edge-TTS instead)
- ❌ No SDXL (uses Pollinations/Together instead)

---

### **NEW BACKEND (`api_server_new.py`)**

```python
# Endpoint: POST /api/generate-video
data = {
    'topic': str,                    # ✅ Same
    'story_type': str,               # ✅ Same
    'duration': int (minutes),       # ✅ Same
    'num_scenes': int,               # ✅ Same
    'image_style': str,              # ✅ Same
    'template': dict,                # ✅ NEW - From Server 0 analysis
    'voice_id': str,                 # ✅ Same (Coqui TTS voices)
    'voice_speed': float,            # ✅ NEW - Voice speed control
    'zoom_effect': bool,             # ✅ Same
    'zoom_intensity': float,         # ✅ NEW - 1-10% zoom
    'auto_captions': bool,           # ✅ NEW - TikTok-style captions
    'color_filter': str,             # ✅ NEW - Color grading
}
```

**What NEW backend does:**
1. Generate script with **Server 1** (local Gemini with chunking)
2. Generate prompts with **Server 2** (local Gemini, SDXL-optimized)
3. Send to **Google Colab** (remote):
   - SDXL image generation (GPU)
   - Coqui TTS voice (GPU)
   - FFmpeg video compilation
   - Zoom effects (1-10%)
   - TikTok auto-captions
   - Color filters

**Added in NEW:**
- ✅ Template analysis (Server 0)
- ✅ Chunking for long scripts
- ✅ Auto-captions
- ✅ Zoom intensity (1-10%)
- ✅ Color filters
- ✅ Voice speed control
- ✅ Google Colab integration
- ✅ Coqui TTS (high quality)
- ✅ SDXL (professional images)

---

## 🔧 PARAMETERS DETAILS

### **Parameters Present in BOTH:**

| Parameter | OLD Backend | NEW Backend | Notes |
|-----------|-------------|-------------|-------|
| `topic` | ✅ Required | ✅ Required | Same |
| `story_type` | ✅ Optional (default: scary_horror) | ✅ Optional (default: scary_horror) | Same |
| `duration` | ✅ Optional (default: 5) | ✅ Optional (default: 10) | Different defaults |
| `num_scenes` | ✅ Optional (default: 10) | ✅ Optional (default: 10) | Same |
| `image_style` | ✅ Optional (default: cinematic_film) | ✅ Optional (default: cinematic_film) | Same |
| `voice_id` | ✅ Optional (Edge-TTS) | ✅ Optional (Coqui TTS) | Different voice engines |
| `zoom_effect` | ✅ Optional (bool, default: true) | ✅ Optional (bool, default: true) | Same |

---

### **Parameters ONLY in NEW Backend:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `template` | dict | None | Template from Server 0 analysis |
| `voice_speed` | float | 1.0 | Voice speed multiplier (0.5-2.0) |
| `zoom_intensity` | float | 5.0 | Zoom percentage (1-10%) |
| `auto_captions` | bool | false | TikTok-style auto-captions |
| `color_filter` | str | "none" | Color grading filter |

---

## 🎤 VOICE COMPARISON

### **OLD Backend - Edge-TTS (Microsoft)**

```python
# Available voices (Edge-TTS)
EDGE_VOICES = {
    'aria': 'en-US-AriaNeural',
    'guy': 'en-US-GuyNeural',
    'jenny': 'en-US-JennyNeural',
    'christopher': 'en-US-ChristopherNeural',
    'eric': 'en-US-EricNeural',
    'steffan': 'en-US-SteffanNeural',
    'sara': 'en-US-SaraNeural',
    'andrew': 'en-US-AndrewNeural',
    'roger': 'en-US-RogerNeural',
    'nancy': 'en-US-NancyNeural',
    'michelle': 'en-US-MichelleNeural',
    'brian': 'en-US-BrianNeural'
}

# Voice generation (local)
generate_audio_edge(text, voice, output_path)
```

**Pros:**
- ✅ FREE & Unlimited
- ✅ Fast (local generation)
- ✅ Many voices available

**Cons:**
- ❌ Lower quality than Coqui
- ❌ Less natural sounding
- ❌ No speed control

---

### **NEW Backend - Coqui TTS (Google Colab)**

```python
# Available voices (Coqui TTS)
COQUI_VOICES = {
    'aria': 'p225',      # Female - Natural & Warm
    'guy': 'p226',       # Male - Natural & Clear
    'jenny': 'p227',     # Female - Cheerful
    'matthew': 'p243',   # Male - Deep & Professional
    'sara': 'p228',      # Female - Young & Energetic
    'andrew': 'p245',    # Male - Professional
    'christopher': 'p246', # Male - Casual & Friendly
    'roger': 'p247'      # Male - Authoritative
}

# Voice generation (Colab GPU)
# Processed in Google Colab with Coqui TTS
# Voice speed control: 0.5-2.0
```

**Pros:**
- ✅ Higher quality (GPU-powered)
- ✅ More natural sounding
- ✅ Voice speed control
- ✅ Professional quality

**Cons:**
- ⚠️ Requires Google Colab (remote)
- ⚠️ Slower (network latency)

---

## 🖼️ IMAGE GENERATION COMPARISON

### **OLD Backend - Pollinations/Together AI**

```python
# Image generation (local)
image_gen = create_image_generator(image_style, story_type)
images = image_gen.generate_batch(scenes, characters)

# Engines:
# - Pollinations AI (free, unlimited)
# - Together AI (API key needed)
```

**Pros:**
- ✅ Fast (local generation)
- ✅ Free (Pollinations)
- ✅ Many styles available

**Cons:**
- ❌ Lower quality than SDXL
- ❌ Less consistent character appearance
- ❌ Limited style control

---

### **NEW Backend - SDXL (Google Colab)**

```python
# Image generation (Colab GPU)
# Server 2 generates SDXL-optimized prompts
# Colab uses DreamShaper XL model
# 25-40 word prompts for professional quality
```

**Pros:**
- ✅ Professional quality (SDXL)
- ✅ Better character consistency
- ✅ Optimized prompts (Server 2)
- ✅ GPU-accelerated

**Cons:**
- ⚠️ Requires Google Colab (remote)
- ⚠️ Slower (network + GPU time)

---

## 🎬 VIDEO COMPILATION COMPARISON

### **OLD Backend - FFmpeg (Local)**

```python
# Compiles video locally
compiler = FFmpegCompiler()
video_path = compiler.create_video(
    image_paths,
    audio_path,
    output_path,
    durations,
    zoom_effect=zoom_effect  # Boolean on/off
)
```

**Features:**
- ✅ Ken Burns zoom effect (on/off)
- ❌ No zoom intensity control
- ❌ No auto-captions
- ❌ No color filters

---

### **NEW Backend - FFmpeg (Google Colab)**

```python
# Compiles video in Colab
# Sent from backend:
colab_options = {
    'voice_id': str,
    'voice_speed': float,
    'zoom_effect': bool,
    'zoom_intensity': float,      # NEW: 1-10%
    'auto_captions': bool,         # NEW: TikTok-style
    'color_filter': str,           # NEW: Color grading
}
```

**Features:**
- ✅ Ken Burns zoom effect (1-10%)
- ✅ TikTok-style auto-captions
- ✅ Color filters (cinematic, warm, cool, etc.)
- ✅ Hardware acceleration (GPU)

---

## 🔀 MIGRATION GUIDE

### **If you're using OLD backend, here's what changes:**

```javascript
// OLD REQUEST (api_server.py)
POST /api/generate-video
{
  "topic": "Haunted Lighthouse",
  "story_type": "scary_horror",
  "duration": 5,
  "num_scenes": 10,
  "image_style": "cinematic_film",
  "voice_id": "aria",
  "zoom_effect": true
}

// NEW REQUEST (api_server_new.py)
POST /api/generate-video
{
  "topic": "Haunted Lighthouse",
  "story_type": "scary_horror",
  "duration": 5,
  "num_scenes": 10,
  "image_style": "cinematic_film",
  "voice_id": "aria",                  // Same ID, different engine
  "voice_speed": 1.0,                  // NEW: Optional
  "zoom_effect": true,
  "zoom_intensity": 5.0,               // NEW: 1-10%
  "auto_captions": false,              // NEW: Optional
  "color_filter": "none",              // NEW: Optional
  "template": null                     // NEW: Optional (from Server 0)
}
```

### **NEW FEATURES YOU CAN USE:**

1. **Template Analysis (Server 0):**
```javascript
// Step 1: Analyze template
POST /api/analyze-script
{
  "scriptContent": "your example script here...",
  "scriptType": "scary_horror"
}

// Returns: template object

// Step 2: Use template in generation
POST /api/generate-video
{
  "topic": "New Story",
  "template": template_from_step_1,  // Script will match this style!
  ...
}
```

2. **Auto-Captions:**
```javascript
{
  "auto_captions": true  // Adds TikTok-style captions
}
```

3. **Zoom Intensity:**
```javascript
{
  "zoom_effect": true,
  "zoom_intensity": 7.5  // 1-10% (7.5% zoom)
}
```

4. **Color Filters:**
```javascript
{
  "color_filter": "cinematic"  // Options: none, cinematic, warm, cool, vibrant, vintage, noir, dramatic, horror, anime
}
```

5. **Voice Speed:**
```javascript
{
  "voice_speed": 1.2  // 1.2x speed (0.5-2.0)
}
```

---

## ✅ RECOMMENDATION

### **Use OLD Backend (`api_server.py`) if:**
- ✅ You want local-only processing
- ✅ You want Edge-TTS (FREE, unlimited)
- ✅ You don't need auto-captions
- ✅ You don't need color filters
- ✅ You want fast generation (no Colab latency)

### **Use NEW Backend (`api_server_new.py`) if:**
- ✅ You want professional quality (SDXL + Coqui)
- ✅ You want template matching (Server 0 analysis)
- ✅ You want auto-captions (TikTok-style)
- ✅ You want color filters
- ✅ You want chunking (handle long scripts)
- ✅ You have Google Colab running

---

## 📊 SUMMARY TABLE

| Feature | OLD Backend | NEW Backend |
|---------|-------------|-------------|
| **Script Generation** | Local Gemini | Local Gemini (Server 1) |
| **Script Chunking** | ❌ No | ✅ Yes (>10 min) |
| **Template Analysis** | ❌ No | ✅ Yes (Server 0) |
| **Image Generation** | Pollinations/Together | SDXL (Colab) |
| **Image Prompts** | Basic prompts | SDXL-optimized (Server 2) |
| **Voice Engine** | Edge-TTS (local) | Coqui TTS (Colab) |
| **Voice Speed** | ❌ No | ✅ Yes (0.5-2.0x) |
| **Zoom Effect** | ✅ Yes (on/off) | ✅ Yes (1-10%) |
| **Auto-Captions** | ❌ No | ✅ Yes (TikTok-style) |
| **Color Filters** | ❌ No | ✅ Yes (9 options) |
| **Processing** | 100% Local | Hybrid (Gemini local, video remote) |
| **Speed** | ⚡ Fast | ⏱️ Moderate (Colab latency) |
| **Quality** | 🔸 Good | ⭐ Professional |
| **Cost** | 💰 FREE (Gemini + Pollinations) | 💰 FREE (Gemini + Colab) |

---

## 🚀 BOTH BACKENDS ARE AVAILABLE!

**You can run BOTH simultaneously:**

```bash
# Terminal 1: OLD Backend (port 5000)
cd story-video-generator
python api_server.py

# Terminal 2: NEW Backend (port 5001)
cd story-video-generator
python api_server_new.py
```

**Choose based on your needs:**
- **Quick + Local** → Use OLD backend
- **Professional + Features** → Use NEW backend

**Both have the same CORE parameters!** Migration is easy! 🎉
