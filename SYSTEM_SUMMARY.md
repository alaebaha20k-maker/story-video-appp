# Story-Video-App: Quick Reference Summary

## Project Overview
AI-powered video generation system that transforms text topics into complete videos with AI-generated scripts, images, voice narration, and professional video editing.

---

## Architecture at a Glance

### Frontend
- **Location:** `/project-bolt-sb1-nqwbmccj/project/src`
- **Tech Stack:** React 18, TypeScript, Vite, Zustand, Tailwind CSS
- **Entry Point:** `main.tsx`
- **Key Components:** GeneratorPage, GalleryPage, VoiceSelector, ImageStyleSelector, etc.

### Backend
- **Location:** `/story-video-generator`
- **Tech Stack:** Python, Flask, Gemini AI, Edge-TTS, FFmpeg
- **Entry Points:** 
  - `api_server.py` (Flask API on port 5000)
  - `main.py` (CLI)

---

## Complete Data Processing Pipeline

```
User Input → Gemini Script Generation → FLUX.1 Image Generation
                    ↓
            Edge-TTS Voice Generation → FFmpeg Video Compilation
                    ↓
            Output: Final MP4 Video
```

### Timing for Typical Video (10 min, 10 scenes)
- Script generation: 10-15 seconds
- Image generation: 2-3 minutes
- Voice narration: 30-60 seconds
- Video compilation: 1-2 minutes
- **Total: ~5-8 minutes**

---

## Active AI Systems

### 1. Gemini 2.5 Pro (Script Generation)
- **Model:** `gemini-2.5-pro`
- **Features:**
  - Template-based generation
  - 20+ story types
  - Character consistency
  - Research integration
  - Advanced prompt engineering
- **Config:** `config/settings.py` (GEMINI_SETTINGS)

### 2. FLUX.1 Schnell (Image Generation)
- **Service:** Pollinations AI (free)
- **Resolution:** 1024x1024
- **Features:**
  - Parallel batch generation
  - Quality enhancement
  - Logo removal
  - Character consistency
- **Config:** `config/settings.py` (FLUX_SETTINGS)

### 3. Edge-TTS (Voice Narration) - PRIMARY VOICE SYSTEM
- **Provider:** Microsoft Azure
- **Cost:** FREE & UNLIMITED
- **Features:**
  - 13+ professional voices
  - Automatic chunking for long texts
  - Async generation
  - Rate control (+10% speed boost)
- **Voices:** Guy, Aria, Jenny, Sara, Christopher, Ryan, etc.
- **Config:** `config/settings.py` (EDGE_TTS_SETTINGS)

### 4. FFmpeg (Video Compilation)
- **Codec:** H.264 (libx264) - CPU-based
- **Resolution:** 1920x1080 (Full HD)
- **FPS:** 24
- **Features:**
  - Zoom effects (Ken Burns)
  - Transitions (crossfade, fade)
  - Audio sync
  - Multi-threaded encoding
- **Note:** GPU encoding NOT currently active

---

## Available Story Types (20)

```
1. scary_horror               11. comedy_funny
2. emotional_heartwarming     12. romantic_love
3. true_crime                13. scifi_future
4. anime_style               14. fantasy_epic
5. historical_documentary    15. biographical
6. surprising_twist          16. conspiracy
7. motivational_inspiring    17. psychological
8. mystery_thriller          18. adventure_survival
9. war_military              19. paranormal
10. nature_wildlife          20. documentary_real
```

---

## Available Image Styles (14)

```
cinematic, documentary, anime, horror, comic, historical,
scifi, noir, fantasy, 3d_render, sketch, watercolor,
oil_painting, retro
```

---

## Available Image Modes (7)

1. **ai_only** - Fully automated AI generation
2. **manual_only** - User uploads their own images
3. **stock_only** - Professional stock footage (Pexels)
4. **ai_manual** - 50/50 AI generated + user uploads
5. **ai_stock** - AI images + stock footage blend
6. **manual_stock** - User images + stock media
7. **all_mix** - All three sources combined

---

## Configuration Files

### Backend Config
- **`config/settings.py`** - All settings (Gemini, voices, FFmpeg, image generation)
- **`config/story_types.py`** - 20 story type definitions with tone, pacing, elements
- **`api_server.py`** - Flask API endpoints and generation logic

### Frontend Config
- **`src/constants/options.ts`** - Story types, voices, image styles, UI options
- **`src/store/useVideoStore.ts`** - Zustand state management
- **`src/types/index.ts`** - TypeScript interfaces

---

## API Endpoints

### Generation
- `POST /api/generate-video` - Start video generation
- `GET /api/progress` - Poll generation progress (returns 0-100%)
- `GET /api/video/{filename}` - Download finished video

### Information
- `GET /health` - Server health check
- `GET /api/voices` - List available voices

### Advanced
- `POST /api/analyze-script` - Analyze example scripts for templates
- `POST /api/search-facts` - Research/fact gathering
- `POST /api/generate-with-template` - Advanced generation with templates
- `GET /api/cache-stats` - Cache usage info
- `POST /api/clear-cache` - Clear generation cache

---

## Frontend Features (useVideoStore)

### Basic Settings
- Topic (required)
- Story Type (scary_horror, romance, etc)
- Duration (1-60 minutes)
- Number of Scenes (5-30)

### Voice Control
- Voice ID (Edge-TTS voices)
- Voice Speed (0.5x to 2.0x)
- Voice Engine (currently 'edge' only)

### Narrative Control
- Hook Intensity (mild, medium, extreme)
- Pacing (slow, medium, dynamic, fast)

### Visual Effects
- Image Style (14 options)
- Image Mode (7 options)
- Zoom Effect (optional Ken Burns)
- Color Filters

### Captions
- Auto-generation from script
- Style customization
- Position control (top, bottom, center)
- Animation effects

### Character Management
- Character definitions and descriptions
- Auto-extracted from script
- Consistency across images

---

## System Components

### AI & Generation
- `src/ai/enhanced_script_generator.py` - Gemini integration
- `src/ai/image_generator.py` - FLUX.1 image generation
- `src/ai/script_analyzer.py` - Template analysis

### Voice Systems
- `src/voice/` - 6 TTS implementations
  - Primary: `api_server.py` (Edge-TTS)
  - Alternative: Kokoro, ElevenLabs, Puter, InWorld

### Video Processing
- `src/editor/ffmpeg_compiler.py` - FFmpeg compilation
- `src/editor/video_compiler.py` - MoviePy effects
- `src/editor/effects.py` - Visual effects (zoom, pan)
- `src/editor/transitions.py` - Transition effects

### Media Management
- `src/media/image_manager.py` - Timeline creation
- `src/media/stock_downloader.py` - Pexels integration

### Utilities
- `src/utils/api_manager.py` - API key management
- `src/utils/file_handler.py` - File operations
- `src/utils/logger.py` - Logging

---

## Working & Active Components

✅ **Fully Functional:**
- Gemini 2.5 Pro script generation
- FLUX.1 Schnell image generation
- Edge-TTS voice narration (free, unlimited)
- FFmpeg video compilation
- MoviePy effects and transitions
- React frontend with real-time progress
- Zustand state management
- Supabase gallery integration (optional)

⚠️ **Available But Not Primary:**
- Kokoro TTS (48 voices, GPU acceleration)
- ElevenLabs TTS
- Alternative image APIs

❌ **Not Currently Implemented:**
- GPU video encoding (NVENC/VCE/QSV)
- Advanced caption rendering
- Music generation
- Real-time streaming

---

## Key Workflow Steps

### 1. Frontend User Input
User provides topic, story type, duration, voice, effects

### 2. API Request
POST to `/api/generate-video` with all settings

### 3. Script Generation (Gemini)
- Builds advanced prompt
- Targets: `duration * 150` words
- Extracts characters and scenes
- Time: ~10-15 seconds

### 4. Image Generation (FLUX.1)
- Creates prompts from scenes
- Parallel batch processing
- Saves to `output/temp/`
- Time: ~2-3 minutes

### 5. Voice Generation (Edge-TTS)
- Splits long text at sentences
- Parallel async generation
- Merges chunks
- Time: ~30-60 seconds

### 6. Timeline Creation
- Maps images to audio timeline
- Calculates per-image duration
- Creates timeline JSON

### 7. Video Compilation (FFmpeg)
- Creates concat.txt file
- Applies zoom/transitions
- Combines audio
- Outputs MP4
- Time: ~1-2 minutes

### 8. Frontend Display
- Polls `/api/progress` every 1000ms
- Shows progress bar
- Displays video when complete
- Option to save to gallery

---

## Environment & Dependencies

### Required APIs
- Google Gemini API (AI script generation)
- Free APIs for images & voices (Pollinations, Edge-TTS)

### System Requirements
- Python 3.8+
- Node.js 16+
- FFmpeg 4.0+
- 4-8GB RAM
- Optional: NVIDIA GPU for faster video encoding

### Key Dependencies
**Backend:** Flask, edge-tts, moviepy, pydub, requests, google-generativeai
**Frontend:** React, Zustand, Tailwind CSS, Vite, TypeScript

---

## Important Notes

### Performance
- **CPU Mode:** Video compilation uses all available CPU cores
- **GPU:** No GPU encoding currently active (could add NVENC/HEVC)
- **Parallel Processing:** Images generated in parallel, scripts sequentially

### Cost
- **Gemini:** Free tier (limited) or paid
- **FLUX.1:** Free (via Pollinations)
- **Edge-TTS:** FREE & UNLIMITED
- **FFmpeg:** Free (open-source)
- **Total Cost:** Minimal (Gemini API only)

### Quality
- **Video Resolution:** 1920x1080 (Full HD)
- **Audio Quality:** 192kbps MP3
- **Image Quality:** 1024x1024 PNG
- **Codec:** H.264 (industry standard)

---

## Files Available

Full documentation saved to:
- `/COMPLETE_SYSTEM_ARCHITECTURE.md` (1,244 lines - comprehensive guide)
- `/SYSTEM_SUMMARY.md` (this file - quick reference)

---

## Next Steps for Enhancement

1. **GPU Acceleration:** Add NVENC encoding for 10x faster videos
2. **Kokoro TTS:** Enable as alternative with 48 voices
3. **Advanced Effects:** Add more transitions and filters
4. **Music Generation:** Integrate background music API
5. **Captions:** Full SRT subtitle generation
6. **Batch Processing:** Generate multiple videos in queue
7. **Streaming:** Real-time video streaming instead of download

