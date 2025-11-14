# Key Files, Locations & Implementation Details

## Essential File Locations

### Frontend Entry Point & Main Components
```
Frontend Root: /project-bolt-sb1-nqwbmccj/project/

src/
├── main.tsx                           # React entry point
├── App.tsx                            # Main app component (routing, API status)
├── pages/
│   ├── GeneratorPage.tsx             # Main video generation UI
│   └── GalleryPage.tsx               # Video gallery view
├── components/
│   ├── GenerateButton.tsx            # Start generation button
│   ├── GenerationProgress.tsx        # Progress display
│   ├── VoiceSelector.tsx             # Voice selection UI
│   ├── ImageStyleSelector.tsx        # Image style selection
│   ├── StoryTypeSelector.tsx         # Story type selection
│   ├── BasicSettings.tsx             # Topic, duration, scenes
│   ├── AdvancedSettings.tsx          # Hook intensity, pacing
│   ├── VideoFilters.tsx              # Color filters, effects
│   ├── CaptionEditor.tsx             # Caption configuration
│   └── VideoResult.tsx               # Video display
├── store/
│   └── useVideoStore.ts              # Zustand state management (entire app state)
├── utils/
│   └── api.ts                        # All API client functions
├── types/
│   └── index.ts                      # TypeScript interfaces
├── constants/
│   └── options.ts                    # All UI options (story types, voices, etc)
└── lib/
    └── supabase.ts                   # Optional gallery storage
```

### Backend Entry Points & API
```
Backend Root: /story-video-generator/

api_server.py                          # Main Flask API server (port 5000)
    - Line 487: GET /health
    - Line 499: GET /api/voices
    - Line 526: POST /api/generate-video (main endpoint)
    - Line 551: GET /api/progress
    - Line 558: GET /api/video/{filename}
    - Line 574: POST /api/analyze-script
    - Line 601: POST /api/search-facts
    - Line 628: POST /api/generate-with-template
    
main.py                                # CLI entry point
    - Line 32: VideoGenerator class
    - Line 200: quick_generate()
    - Line 216: interactive_mode()
```

### Configuration Files
```
config/
├── settings.py                        # ALL CONFIGURATION
│   - Line 24: GEMINI_SETTINGS
│   - Line 88: EDGE_TTS_SETTINGS
│   - Line 62: FLUX_SETTINGS
│   - Line 189: EFFECT_TYPES
│   - Line 201: TRANSITION_TYPES
│   - Line 150: NICHE_STYLES
│
├── story_types.py                    # 20 story type definitions
│   - Complete configuration for each story type
│   - Tone, pacing, voice style, visual style
│
└── niche_styles.py                   # Visual style configurations
```

### AI & Script Generation
```
src/ai/
├── enhanced_script_generator.py      # PRIMARY: Gemini integration
│   - Line 21: EnhancedScriptGenerator class
│   - Line 68: generate_with_template() - main function
│   - Line 120: _build_professional_prompt()
│   - Line 24: EXAMPLE_HOOKS (20+ examples for learning)
│
├── script_generator.py               # Basic script generation
├── image_generator.py                # FLUX.1 Schnell image generation
│   - Line 20: UltraImageGenerator class
│   - Line 34: generate_scene_image()
│
├── script_analyzer.py                # Template analysis
└── prompt_builder.py                 # Advanced prompt engineering
```

### Voice/TTS Systems
```
src/voice/
├── [PRIMARY] api_server.py (lines 45-179)
│   - generate_audio_edge() - main function
│   - generate_audio_edge_tts() - async edge-tts
│   - get_voice_id() - voice mapping
│
├── kokoro_tts.py                     # Alternative: 48 voices, GPU-accelerated
│   - Line 19: KokoroTTS class
│   - Line 89: generate_audio()
│   - VOICES dict with 48 configurations
│
├── tts_engine.py                     # TTS interface
├── ultra_voice_engine.py             # Advanced processing
├── audio_processor.py                # Audio manipulation
│   - Normalize, fade, merge, overlay, speed adjust
│
├── elevenlabs_tts.py                 # Alternative provider
├── puter_tts.py                      # Alternative provider
└── inworld_tts.py                    # AI character voices
```

### Video Processing & Compilation
```
src/editor/
├── ffmpeg_compiler.py                # PRIMARY: FFmpeg compilation
│   - Line 9: FFmpegCompiler class
│   - Line 11: create_video()
│   - FFmpeg command building (H.264 libx264)
│
├── video_compiler.py                 # MoviePy-based compilation
│   - Line 23: VideoCompiler class
│   - Line 66: create_video_from_images()
│   - Effects and transitions support
│
├── effects.py                        # Visual effects
│   - apply_simple_zoom()
│   - apply_pan()
│   - apply_zoom_pan() (Ken Burns)
│   - apply_static()
│
├── transitions.py                    # Video transitions
│   - crossfade()
│   - fade_transition()
│   - concatenate_with_crossfade()
│
├── filters.py                        # Color filters & visual effects
├── captions.py                       # Caption generation
└── srt_generator.py                  # SRT subtitle generation
```

### Media & Timeline Management
```
src/media/
├── image_manager.py                  # Image timeline management
│   - batch_resize_images()
│   - assign_images_to_timeline()
│
├── video_manager.py                  # Video file management
└── stock_downloader.py               # Pexels stock media integration
```

### Utilities
```
src/utils/
├── api_manager.py                    # API key management
│   - Line 16: self.keys (API keys)
│   - get_key(), has_key(), check_required_keys()
│
├── file_handler.py                   # File operations
│   - get_output_path()
│   - get_temp_path()
│   - save_binary()
│
└── logger.py                         # Logging utility
    - Formatted console output
```

---

## Key Code Workflows

### Workflow 1: Video Generation Request (API)

**File:** `api_server.py` (Line 526)

```python
@app.route('/api/generate-video', methods=['POST', 'OPTIONS'])
def generate_video():
    # 1. Get request data
    data = request.json
    
    # 2. Validate
    if not data.get('topic'):
        return jsonify({'error': 'Topic is required'}), 400
    
    # 3. Start background thread
    threading.Thread(target=generate_video_background, args=(data,)).start()
    
    # 4. Return immediately
    return jsonify({'success': True, 'message': 'Generation started'}), 200
```

### Workflow 2: Script Generation (Gemini)

**File:** `src/ai/enhanced_script_generator.py` (Line 68)

```python
def generate_with_template(self, topic, story_type, template, 
                          research_data, duration_minutes, num_scenes):
    # 1. Get story type config
    style = STORY_TYPES[story_type]
    
    # 2. Build advanced prompt
    prompt = f"""You are an Emmy-award winning screenwriter...
    
    TOPIC: {topic}
    STORY TYPE: {style['description']}
    TONE: {style['tone']}
    PACING: {style['pacing']}
    TARGET LENGTH: {duration_minutes * 150} words
    STRUCTURE: Hook → Setup → Rising Action → Climax → Resolution
    ... [full prompt template]
    """
    
    # 3. Generate with Gemini
    response = self.model.generate_content(prompt)
    script_text = response.text
    
    # 4. Extract components
    characters = self._extract_characters(script_text)
    scenes = self._parse_scenes(script_text, num_scenes)
    
    # 5. Return structured data
    return {
        "script": script_text,
        "characters": characters,
        "scenes": scenes,
        "word_count": len(script_text.split()),
        "character_count": len(script_text)
    }
```

### Workflow 3: Image Generation (FLUX.1)

**File:** `src/ai/image_generator.py` (Line 34)

```python
def generate_scene_image(self, scene_description, scene_number, 
                        scene_type, characters):
    # 1. Build professional prompt
    prompt_data = self.prompt_builder.build_scene_prompt(
        scene_description, scene_type, characters
    )
    
    # 2. Call Pollinations API with FLUX.1
    params = {
        'model': 'flux',
        'width': 1024,
        'height': 1024,
        'nologo': 'true',
        'enhance': 'true'
    }
    
    url = f"https://image.pollinations.ai/prompt/{quoted_prompt}?{params}"
    response = requests.get(url, timeout=180)  # 3-minute timeout
    
    # 3. Save image
    filename = f"scene_{scene_number:03d}.png"
    filepath = file_handler.save_binary(response.content, filename)
    
    # 4. Return image info
    return {
        "filepath": str(filepath),
        "scene_number": scene_number,
        "prompt": prompt_data['prompt'],
        "model": "FLUX.1 Schnell"
    }
```

### Workflow 4: Voice Generation (Edge-TTS)

**File:** `api_server.py` (Line 139)

```python
async def generate_audio_edge_tts(text, voice, output_path):
    # 1. Check text length
    if len(text) > 3000:
        # Split at sentence boundaries
        chunks = _split_text_smart(text, max_chars=2000)
        
        # Generate chunks in parallel
        tasks = []
        chunk_files = []
        for i, chunk in enumerate(chunks):
            chunk_file = Path(f"chunk_{i:03d}.mp3")
            communicate = edge_tts.Communicate(chunk, voice, rate="+10%")
            tasks.append(communicate.save(str(chunk_file)))
            chunk_files.append(chunk_file)
        
        # Wait for all to complete
        await asyncio.gather(*tasks)
        
        # Merge chunks
        combined = AudioSegment.empty()
        for chunk_file in chunk_files:
            audio = AudioSegment.from_mp3(str(chunk_file))
            combined += audio
        
        combined.export(str(output_path), format="mp3", bitrate="192k")
    else:
        # Short text - direct generation
        communicate = edge_tts.Communicate(text, voice, rate="+10%")
        await communicate.save(str(output_path))
    
    return str(output_path)
```

### Workflow 5: Video Compilation (FFmpeg)

**File:** `src/editor/ffmpeg_compiler.py` (Line 11)

```python
def create_video(self, image_paths, audio_path, output_path, 
                durations, zoom_effect=True):
    # 1. Create concat file
    with open("concat.txt", 'w') as f:
        for img, dur in zip(image_paths, durations):
            f.write(f"file '{img}'\n")
            f.write(f"duration {dur}\n")
    
    # 2. Build video filter
    if zoom_effect:
        video_filter = (
            "scale=1920:1080,"
            "zoompan=z='min(zoom+0.0015,1.1)':d=1:"
            "x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):s=1920x1080,"
            "fps=24"
        )
    else:
        video_filter = 'scale=1920:1080,fps=24'
    
    # 3. Build FFmpeg command
    cmd = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', str(concat_file),
        '-i', str(audio_path),
        '-vf', video_filter,
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-crf', '23',
        '-threads', '0',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',
        '-y',
        str(output_path)
    ]
    
    # 4. Execute
    subprocess.run(cmd, check=True)
    
    # 5. Cleanup
    concat_file.unlink()
    return output_path
```

---

## Progress State Flow

**File:** `api_server.py` (Line 35)

```python
progress_state = {
    'status': 'ready',        # Current status
    'progress': 0,            # 0-100%
    'video_path': None,       # Output filename when complete
    'error': None,            # Error message if failed
    'voice_engine': None,     # Voice system used
    'voice_id': None,         # Specific voice ID
}

# Progress updates:
# 1. 'starting' → 10% (script generation starting)
# 2. 'generating' → 30% (images generating)
# 3. 'generating' → 60% (voice generation)
# 4. 'generating' → 80% (video compilation)
# 5. 'complete' → 100% (finished, video_path set)
# Or: 'error' + error message if failed
```

---

## State Management (Frontend)

**File:** `src/store/useVideoStore.ts`

```typescript
// Zustand store for entire app state
export const useVideoStore = create<VideoStore>((set) => ({
  // Input fields
  topic: '',
  storyType: 'scary_horror',
  imageStyle: 'cinematic',
  imageMode: 'ai_only',
  voiceId: 'guy',
  duration: 5,
  numScenes: 10,
  hookIntensity: 'medium',
  pacing: 'medium',
  
  // Effects
  colorFilter: 'none',
  zoomEffect: false,
  
  // Captions
  autoCaptions: false,
  captionEnabled: false,
  
  // State
  isGenerating: false,
  progress: null,
  result: null,
  error: null,
  
  // Actions
  setTopic: (topic) => set({ topic }),
  setStoryType: (storyType) => set({ storyType }),
  startGeneration: () => set({ isGenerating: true, progress: null, error: null }),
  updateProgress: (progress) => set({ progress }),
  setResult: (result) => set({ result, isGenerating: false }),
  setError: (error) => set({ error, isGenerating: false }),
  reset: () => set({ isGenerating: false, progress: null, result: null, error: null }),
}));
```

---

## API Request/Response Examples

### POST /api/generate-video

**Request:**
```json
{
  "topic": "The Mystery of the Bermuda Triangle",
  "story_type": "mystery_thriller",
  "image_style": "cinematic",
  "image_mode": "ai_only",
  "voice_id": "male_narrator_deep",
  "voice_speed": 1.0,
  "duration": 10,
  "num_scenes": 10,
  "hook_intensity": "extreme",
  "pacing": "dynamic",
  "zoom_effect": true,
  "auto_captions": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Generation started"
}
```

### GET /api/progress

**Response (During Generation):**
```json
{
  "status": "generating",
  "progress": 45,
  "substatus": "generating_images",
  "details": "Generated 5 of 10 images",
  "voice_engine": "edge",
  "voice_id": "en-US-GuyNeural"
}
```

**Response (Complete):**
```json
{
  "status": "complete",
  "progress": 100,
  "video_path": "the_mystery_of_the_bermuda_triangle_video.mp4",
  "voice_engine": "edge",
  "voice_id": "en-US-GuyNeural"
}
```

---

## Configuration Examples

### Enable Zoom Effect

**Frontend:** User toggles zoom effect
```typescript
store.setZoomEffect(true)
```

**Backend Receives:**
```python
zoom_effect = data.get('zoom_effect', True)  # True/False
```

**FFmpeg Applies:**
```bash
-vf "scale=1920:1080,zoompan=z='min(zoom+0.0015,1.1)':d=1:...,fps=24"
```

### Change Voice

**Frontend:** User selects voice
```typescript
store.setVoiceId('female_narrator_warm')  // Sara
```

**Mapping:** `config/settings.py`
```python
EDGE_VOICE_MAP = {
    "female_narrator_warm": "en-US-SaraNeural"
}
```

**Edge-TTS:** Uses mapped voice ID
```python
voice_id = resolve_edge_voice("female_narrator_warm")  # → en-US-SaraNeural
generate_audio_edge(text, voice=voice_id)
```

---

## Debugging & Logging

### Enable Logging
**File:** `src/utils/logger.py`

```python
logger.header("🎥 AI VIDEO GENERATOR")     # Large header
logger.step("STEP 1: Generating Script")   # Step indicator
logger.info(f"Scenes: {num_scenes}")       # Info message
logger.success("Script generated!")        # Success message
logger.warning("No images found")          # Warning
logger.error("Generation failed!")         # Error
logger.divider()                           # Visual separator
```

### Check Progress During Generation
```bash
# Terminal 1: Start generation
curl -X POST http://localhost:5000/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{"topic":"Test","story_type":"scary_horror",...}'

# Terminal 2: Check progress repeatedly
curl http://localhost:5000/api/progress | jq
```

---

## Performance Notes

### Bottlenecks
1. **Image Generation** - Slowest (2-3 min for 10 images)
   - Limit: Parallel requests to Pollinations
   
2. **Video Compilation** - 1-2 minutes for FFmpeg
   - Limit: CPU cores available
   - Optimization: Reduce FPS, lower CRF

3. **Script Generation** - Fast (10-15 sec)
   - Limit: Gemini API rate limits

### Optimization Tips
- Use fewer scenes (reduces image generation time)
- Use `preset: "ultrafast"` for faster FFmpeg encoding
- Parallel image generation (already implemented)
- Async voice chunk generation (already implemented)

