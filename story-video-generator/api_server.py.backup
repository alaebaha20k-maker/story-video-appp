"""
🔌 API SERVER - With Kokoro TTS (PRIMARY) + Edge-TTS (BACKUP)
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pathlib import Path
import os
import threading
import re
from pydub import AudioSegment
import asyncio
import edge_tts

# ✅ IMPORTS FOR TEMPLATES + RESEARCH
from src.ai.script_analyzer import script_analyzer
from src.research.fact_searcher import fact_searcher
from src.ai.enhanced_script_generator import enhanced_script_generator

# ✅ EXISTING IMPORTS
from src.ai.image_generator import create_image_generator
from src.editor.ffmpeg_compiler import FFmpegCompiler
<<<<<<< HEAD
=======
from config.settings import KOKORO_SETTINGS, EDGE_TTS_SETTINGS, VOICE_PRIORITY

# ✅ OPTIONAL TTS ENGINES
PLAYHT_AVAILABLE = False
PLAYHT_READY = False
PLAYHT_USER_ID = os.getenv('PLAYHT_USER_ID', '')
PLAYHT_API_KEY = os.getenv('PLAYHT_API_KEY', '')

try:
    import playht
    PLAYHT_AVAILABLE = True
except ImportError:
    playht = None
    print("⚠️ PlayHT not installed (optional)")

if PLAYHT_AVAILABLE:
    if PLAYHT_USER_ID and PLAYHT_API_KEY:
        try:
            playht.api_key = PLAYHT_API_KEY
            playht.user_id = PLAYHT_USER_ID
            PLAYHT_READY = True
            print("✅ PlayHT configured")
        except Exception as e:
            print(f"⚠️ Failed to configure PlayHT: {e}")
    else:
        print("⚠️ PlayHT credentials not provided (PLAYHT_USER_ID / PLAYHT_API_KEY)")

GTTS_AVAILABLE = False
try:
    from gtts import gTTS  # type: ignore
    GTTS_AVAILABLE = True
except ImportError:
    gTTS = None
    print("⚠️ gTTS not installed (optional)")

# ✅ VOICE MAPPINGS (Canonical voice IDs → Engine-specific voices)
KOKORO_VOICE_MAP = {
    'male_narrator_deep': 'am_adam',
    'female_narrator': 'af_bella',
    'female_young': 'af_nova',
    'narrator_male_deep': 'am_adam',
    'narrator_female_warm': 'af_bella',
    'narrator_british_female': 'bf_emma',
}

EDGE_VOICE_MAP = {
    'male_narrator_deep': 'en-US-GuyNeural',
    'female_narrator': 'en-US-AriaNeural',
    'female_young': 'en-US-JennyNeural',
    'narrator_male_deep': 'en-US-GuyNeural',
    'narrator_female_warm': 'en-US-AriaNeural',
}

PLAYHT_VOICE_MAP = {
    'male_narrator_deep': 'James',
    'male_professional': 'George',
    'male_warm': 'Michael',
    'female_narrator': 'Rachel',
    'female_professional': 'Catherine',
    'male_energetic': 'Scott',
    'british_male': 'Edward',
    'female_warm': 'Lily',
}

GTTS_VOICE_MAP = {
    'male_narrator_deep': 'en',
    'male_professional': 'en',
    'male_warm': 'en',
    'female_narrator': 'en',
    'female_professional': 'en',
    'male_energetic': 'en',
    'british_male': 'en-gb',
    'female_warm': 'en',
}

ENGINE_LABELS = {
    'kokoro': 'Kokoro TTS',
    'edge': 'Edge-TTS',
    'playht': 'PlayHT',
    'gtts': 'gTTS',
}

DEFAULT_VOICES = {
    'kokoro': KOKORO_SETTINGS.get('default_voice', 'af_bella'),
    'edge': EDGE_TTS_SETTINGS.get('default_voice', 'en-US-AriaNeural'),
    'playht': 'James',
    'gtts': 'en',
}
>>>>>>> 8a672db9f56fce6ed963282e2210b52ac39849e2

app = Flask(__name__)

# CORS for all origins
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

progress_state = {
    'status': 'ready',
    'progress': 0,
    'video_path': None,
    'error': None,
    'voice_engine': None,
    'voice_id': None,
}

# ═══════════════════════════════════════════════════════════════
# 🎤 EDGE-TTS - FREE, RELIABLE, ALWAYS WORKS!
# ═══════════════════════════════════════════════════════════════

print(f"\n🔧 Using Edge-TTS (Microsoft) - FREE & UNLIMITED!")
print("✅ Edge-TTS ready - No API key needed!")
print("   💰 FREE & UNLIMITED forever!")
print("   🎬 10+ professional voices!")

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def sanitize_filename(filename):
    """Clean filename"""
    filename = re.sub(r'[^a-zA-Z0-9_\-]', '', filename)
    filename = re.sub(r'_+', '_', filename)
    return filename[:50]


<<<<<<< HEAD
def get_voice_id(voice_id=None):
    """Get Edge-TTS voice ID"""
    
    # ✅ Map to Edge-TTS voices (Microsoft)
    voice_map = {
        # Male voices
        'guy': 'en-US-GuyNeural',
        'andrew': 'en-US-AndrewNeural',
        'brian': 'en-US-BrianNeural',
        'christopher': 'en-US-ChristopherNeural',
        'roger': 'en-US-RogerNeural',
        
        # Female voices
        'aria': 'en-US-AriaNeural',
        'jenny': 'en-US-JennyNeural',
        'sara': 'en-US-SaraNeural',
        'nancy': 'en-US-NancyNeural',
        'michelle': 'en-US-MichelleNeural',
        
        # Old mappings
        'matthew': 'en-US-GuyNeural',
        'joey': 'en-US-ChristopherNeural',
        'justin': 'en-US-RogerNeural',
        'joanna': 'en-US-AriaNeural',
        'salli': 'en-US-JennyNeural',
        'kimberly': 'en-US-SaraNeural',
        'ivy': 'en-US-NancyNeural',
    }
    
    # Use mapping or default
    if voice_id:
        voice_id = voice_map.get(voice_id.lower() if isinstance(voice_id, str) else 'en-US-GuyNeural', 'en-US-GuyNeural')
    else:
        voice_id = 'en-US-GuyNeural'  # Default male voice
    
    print(f"   🔧 Voice for Edge-TTS: {voice_id}")
    return voice_id
=======
def is_engine_available(engine):
    engine = (engine or '').lower()
    if engine == 'kokoro':
        return kokoro_tts is not None
    if engine == 'edge':
        return True
    if engine == 'playht':
        return PLAYHT_READY
    if engine == 'gtts':
        return GTTS_AVAILABLE
    return False


def get_engine_order(preferred_engine=None):
    """Return a prioritized list of voice engines to try"""
    candidates = []
    if preferred_engine:
        candidates.append(preferred_engine.lower())

    candidates.extend([engine.lower() for engine in VOICE_PRIORITY])

    # Ensure Edge and gTTS are present as safety nets
    candidates.extend(['edge', 'gtts'])

    order = []
    for engine in candidates:
        if engine not in ENGINE_LABELS:
            continue
        if engine in order:
            continue
        if is_engine_available(engine):
            order.append(engine)

    if not order:
        raise RuntimeError("No voice engines available")

    return order


def map_voice_id(engine, voice_id=None):
    """Map canonical voice IDs to engine-specific voices"""
    engine = engine.lower()
    voice_id = voice_id or ''

    if engine == 'kokoro':
        if voice_id:
            # If voice_id already starts with standard Kokoro prefixes, use it directly
            if voice_id.startswith(('af_', 'am_', 'bf_', 'bm_')):
                return voice_id
            # Otherwise try legacy mapping
            return KOKORO_VOICE_MAP.get(voice_id, voice_id)
        return DEFAULT_VOICES['kokoro']

    if engine == 'edge':
        if voice_id:
            # If voice_id matches Edge-TTS format, use it directly
            if 'Neural' in voice_id or voice_id.startswith('en-'):
                return voice_id
            # Otherwise try legacy mapping
            return EDGE_VOICE_MAP.get(voice_id, voice_id)
        return DEFAULT_VOICES['edge']

    if engine == 'playht':
        if voice_id:
            return PLAYHT_VOICE_MAP.get(voice_id, DEFAULT_VOICES['playht'])
        return DEFAULT_VOICES['playht']

    if engine == 'gtts':
        if voice_id:
            return GTTS_VOICE_MAP.get(voice_id, DEFAULT_VOICES['gtts'])
        return DEFAULT_VOICES['gtts']

    return voice_id or DEFAULT_VOICES.get('edge', 'en-US-AriaNeural')


def get_audio_output_path(engine):
    """Return the correct audio file path/extension for an engine"""
    ext = 'wav' if engine == 'kokoro' else 'mp3'
    path = Path(f"output/temp/narration.{ext}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
>>>>>>> 8a672db9f56fce6ed963282e2210b52ac39849e2


def generate_audio_edge(text, voice="en-US-GuyNeural", output_path="narration.mp3"):
    """✅ Generate audio using Edge-TTS - FREE, RELIABLE, ALWAYS WORKS!"""
    print(f"\n🎤 Generating audio with Edge-TTS (Microsoft - FREE!)...")
    print(f"   Voice: {voice}")
    print(f"   Text length: {len(text)} characters")
    print(f"   Output path: {output_path}")
    print(f"   💰 Cost: $0 (FREE!)")
    
    try:
        # Generate with Edge-TTS
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_path = loop.run_until_complete(
            generate_audio_edge_tts(text, voice, output_path)
        )
        loop.close()
        
        print(f"✅ Edge-TTS generation SUCCESS!")
        print(f"   🎬 Good quality for YouTube - FREE forever!")
        return audio_path
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ EDGE-TTS GENERATION FAILED!")
        print(f"{'='*60}")
        print(f"Error: {e}")
        print(f"Voice: {voice}")
        print(f"Text length: {len(text)}")
        print(f"\n💡 Troubleshooting:")
        print(f"   1. Check internet connection")
        print(f"   2. Try a different voice")
        print(f"   3. Check text length")
        print(f"{'='*60}\n")
        raise


<<<<<<< HEAD
async def generate_audio_edge_tts(text, voice="en-US-GuyNeural", output_path="narration.mp3"):
    """✅ Edge-TTS fallback - Always works!"""
    from pydub import AudioSegment
    
    print(f"   🎤 Edge-TTS generating...")
    
    # For long text, use chunking
    if len(text) > 3000:
        chunks = _split_text_smart(text, max_chars=2000)
        print(f"   Split into {len(chunks)} chunks for Edge-TTS")
        
        temp_dir = Path("output/temp/edge_chunks")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate chunks in parallel
        tasks = []
        chunk_files = []
        
        for i, chunk in enumerate(chunks):
            chunk_file = temp_dir / f"chunk_{i:03d}.mp3"
            chunk_files.append(chunk_file)
            communicate = edge_tts.Communicate(chunk, voice, rate="+10%")
            tasks.append(communicate.save(str(chunk_file)))
        
        await asyncio.gather(*tasks)
        
        # Combine chunks
        combined = AudioSegment.empty()
        for chunk_file in chunk_files:
            if chunk_file.exists():
                audio_chunk = AudioSegment.from_mp3(str(chunk_file))
                combined += audio_chunk
                chunk_file.unlink()
        
        combined.export(str(output_path), format="mp3", bitrate="192k")
    else:
        # Short text - generate directly
        communicate = edge_tts.Communicate(text, voice, rate="+10%")
        await communicate.save(str(output_path))
    
    return str(output_path)


def _split_text_smart(text, max_chars=2000):
    """Split text at sentence boundaries"""
    sentences = text.replace('!', '.').replace('?', '.').split('.')
    sentences = [s.strip() + '.' for s in sentences if s.strip()]
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chars:
            current_chunk += " " + sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks if chunks else [text]
=======
def generate_audio_playht(text, voice="James", output_path="narration.mp3"):
    """✅ Generate audio using PlayHT (premium)"""
    if not PLAYHT_READY:
        raise RuntimeError("PlayHT not configured")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        print("🎤 Generating audio with PlayHT...")
        print(f"   Voice: {voice}")
        print(f"   Text: {len(text)} characters")

        stream = playht.generate(
            text=text,
            voice=voice,
            output_format="mp3",
        )

        with open(str(output_path), 'wb') as handle:
            for chunk in stream:
                handle.write(chunk)

        print(f"✅ Audio generated: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ PlayHT Error: {e}")
        raise


def generate_audio_gtts(text, language="en", output_path="narration.mp3"):
    """✅ Generate audio using gTTS (free)"""
    if not GTTS_AVAILABLE:
        raise RuntimeError("gTTS not installed")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        print("🎤 Generating audio with gTTS...")
        print(f"   Language: {language}")
        print(f"   Text: {len(text)} characters")

        from gtts import gTTS  # Local import to avoid module requirement when unavailable

        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(str(output_path))

        print(f"✅ Audio generated: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ gTTS Error: {e}")
        raise


def generate_audio_for_engine(engine, text, voice_id, speed, output_path):
    """Generate audio for the specified engine"""
    engine = engine.lower()

    if engine == 'kokoro':
        return Path(
            generate_audio_kokoro(
                text=text,
                voice=voice_id,
                speed=speed,
                output_path=str(output_path),
            )
        )

    if engine == 'edge':
        return Path(
            asyncio.run(
                generate_audio_edge_tts(
                    text,
                    voice=voice_id,
                    output_path=str(output_path),
                )
            )
        )

    if engine == 'playht':
        return generate_audio_playht(text, voice=voice_id, output_path=str(output_path))

    if engine == 'gtts':
        return generate_audio_gtts(text, language=voice_id, output_path=str(output_path))

    raise ValueError(f"Unknown voice engine: {engine}")


def generate_voice_with_fallback(text, preferred_engine=None, voice_id=None, speed=1.0, status_callback=None):
    """Generate narration using available engines with graceful fallback"""
    engine_order = get_engine_order(preferred_engine)
    last_error = None

    for engine in engine_order:
        resolved_voice = map_voice_id(engine, voice_id)
        output_path = get_audio_output_path(engine)

        if status_callback:
            status_callback(engine, 'start')

        print(f"🎤 Trying {ENGINE_LABELS[engine]} (voice: {resolved_voice})")

        try:
            audio_path = generate_audio_for_engine(
                engine,
                text,
                resolved_voice,
                speed,
                output_path,
            )

            print(f"✅ Voice ready using {ENGINE_LABELS[engine]}")

            if status_callback:
                status_callback(engine, 'success')

            return engine, audio_path, resolved_voice

        except Exception as e:
            last_error = e
            print(f"⚠️ {ENGINE_LABELS[engine]} failed: {e}")

            if status_callback:
                status_callback(engine, 'error', e)

    raise last_error or RuntimeError("All voice engines failed")
>>>>>>> 8a672db9f56fce6ed963282e2210b52ac39849e2


def get_audio_duration(audio_path):
    """Get duration of audio file (MP3 or WAV)"""
    try:
        audio_path = str(audio_path)

        if audio_path.endswith('.mp3'):
            audio = AudioSegment.from_mp3(audio_path)
        elif audio_path.endswith('.wav'):
            audio = AudioSegment.from_wav(audio_path)
        else:
            # Try to detect format
            audio = AudioSegment.from_file(audio_path)
        
        duration = len(audio) / 1000.0  # Convert to seconds
        return duration
    except Exception as e:
        print(f"❌ Error reading audio: {e}")
        return 5.0  # Fallback


# ═══════════════════════════════════════════════════════════════
# BACKGROUND FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def generate_video_background(data):
    """Original video generation (without template)"""
    global progress_state

    try:
        print(f"\n🎬 Starting generation: {data.get('topic', 'Untitled')}")
<<<<<<< HEAD
        
        # Determine voice engine
        voice_engine = data.get('voice_engine', 'kokoro')
        voice_id = data.get('voice_id')
        voice_engine, voice_id = get_voice_engine_and_id(voice_engine, voice_id)
        
        print(f"🎤 Voice Engine: {voice_engine.upper()}")
        print(f"🎤 Voice ID: {voice_id}")
=======

        # Determine voice preferences
        preferred_engine = data.get('voice_engine')
        requested_voice_id = data.get('voice_id')
        voice_speed = data.get('voice_speed', 1.0)

        # Get zoom effect setting (default: True for better UX)
        zoom_effect = data.get('zoom_effect', True)

        progress_state['voice_engine'] = None
        progress_state['voice_id'] = None

        print(f"🎤 Requested Engine: {preferred_engine or 'auto'}")
        print(f"🎤 Requested Voice ID: {requested_voice_id or 'auto'}")
        print(f"🎤 Voice Speed: {voice_speed}x")
>>>>>>> 8a672db9f56fce6ed963282e2210b52ac39849e2
        print(f"🎬 Zoom Effect: {'ENABLED' if zoom_effect else 'DISABLED'}")
        
        # Script
        progress_state['status'] = 'Generating script...'
        progress_state['progress'] = 10
        print("📝 Step 1/4: Generating script...")
        
        # 📝 Generate script with Gemini (10/10 quality with improved prompts!)
        result = enhanced_script_generator.generate_with_template(
            topic=data.get('topic', 'Test Story'),
            story_type=data.get('story_type', 'scary_horror'),
            template=None,  # No template
            research_data=None,  # No research
            duration_minutes=int(data.get('duration', 5)),
            num_scenes=int(data.get('num_scenes', 10))  # ✅ User selection!
        )
        
        print(f"   ✅ Script: {len(result['script'])} characters")
        
        # Images
        progress_state['status'] = 'Generating images...'
        progress_state['progress'] = 30
        print("🎨 Step 2/4: Generating images...")
        
        image_gen = create_image_generator(
            data.get('image_style', 'cinematic_film'), 
            data.get('story_type', 'scary_horror')
        )
        characters = {char: f"{char}, character" for char in result.get('characters', [])[:3]}
        images = image_gen.generate_batch(result['scenes'], characters)
        image_paths = [Path(img['filepath']) for img in images if img]
        
        print(f"   ✅ Images: {len(image_paths)} generated")
        print(f"   🔍 DEBUG: Image paths:")
        for i, img_path in enumerate(image_paths):
            exists = "EXISTS" if img_path.exists() else "MISSING!"
            print(f"      Image {i+1}: {img_path.name} - {exists}")
        
<<<<<<< HEAD
        # Voice Generation - Edge-TTS
        progress_state['status'] = 'Generating voice with Edge-TTS...'
        progress_state['progress'] = 60
        print(f"🎤 Step 3/4: Generating voice with Edge-TTS (FREE!)...")
        
        audio_path = Path("output/temp/narration.mp3")
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        
        # ✅ EDGE-TTS - FREE & UNLIMITED!
        generate_audio_edge(
            text=result['script'],
            voice=voice_id,
            output_path=str(audio_path)
        )
        
        audio_duration = get_audio_duration(audio_path)
        print(f"   ✅ Audio: {audio_duration:.1f} seconds ({audio_duration/60:.1f} minutes)")
=======
        # Voice Generation
        progress_state['progress'] = 60

        def _voice_status(engine, stage, error=None):
            label = ENGINE_LABELS[engine]
            if stage == 'start':
                progress_state['status'] = f'Generating voice with {label}...'
            elif stage == 'success':
                progress_state['status'] = f'Voice ready ({label})'
                progress_state['voice_engine'] = engine
            elif stage == 'error':
                progress_state['status'] = f'{label} failed, trying fallback'

        print("🎤 Step 3/4: Generating voice narration...")

        voice_engine, audio_path, resolved_voice = generate_voice_with_fallback(
            result['script'],
            preferred_engine=preferred_engine,
            voice_id=requested_voice_id,
            speed=voice_speed,
            status_callback=_voice_status,
        )

        progress_state['voice_engine'] = voice_engine
        progress_state['voice_id'] = resolved_voice

        audio_duration = get_audio_duration(audio_path)
        print(f"   ✅ Audio: {audio_duration:.1f} seconds")
        print(f"   Engine Used: {ENGINE_LABELS[voice_engine]}")
        print(f"   Voice Used: {resolved_voice}")
>>>>>>> 8a672db9f56fce6ed963282e2210b52ac39849e2
        
        # Calculate durations - MATCH VIDEO TO AUDIO!
        time_per_image = audio_duration / len(image_paths) if image_paths else 5
        durations = [time_per_image] * len(image_paths)
        
        # Debug: Show calculation
        print(f"   🔧 Image timing:")
        print(f"      Images: {len(image_paths)}")
        print(f"      Duration per image: {time_per_image:.1f}s")
        print(f"      Total video duration: {sum(durations):.1f}s ({sum(durations)/60:.1f} minutes)")
        
        # Video
        progress_state['status'] = 'Compiling video...'
        progress_state['progress'] = 80
        print("🎬 Step 4/4: Compiling video...")

        compiler = FFmpegCompiler()
        safe_topic = sanitize_filename(data.get('topic', 'video'))
        output_filename = f"{safe_topic}_video.mp4"

        video_path = compiler.create_video(
            image_paths,
            str(audio_path),
            Path(f"output/videos/{output_filename}"),
            durations,
            zoom_effect=zoom_effect
        )
        
        progress_state['progress'] = 100
        progress_state['status'] = 'complete'
        progress_state['video_path'] = output_filename

        print(f"\n✅ SUCCESS! Video: {output_filename}")
        print(f"   Voice Engine: {ENGINE_LABELS[voice_engine]}")
        print(f"   Voice: {resolved_voice}")
        print(f"   Zoom Effect: {'ENABLED' if zoom_effect else 'DISABLED'}\n")
        
    except Exception as e:
        progress_state['status'] = 'error'
        progress_state['error'] = str(e)
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()


def generate_with_template_background(topic, story_type, template, research_data, duration, num_scenes, voice_engine, voice_id, voice_speed=1.0,
zoom_effect=True):
    """✅ Background generation with template + research + voice selection + zoom effect"""
    global progress_state

    try:
        progress_state['status'] = 'generating'
        progress_state['progress'] = 10
        progress_state['voice_engine'] = None
        progress_state['voice_id'] = None

        preferred_engine = voice_engine
        requested_voice_id = voice_id

        print(f"📝 Generating script with template...")
<<<<<<< HEAD
        print(f"🎤 Voice Engine: {voice_engine.upper()}")
        print(f"🎤 Voice: {voice_id}")
        print(f"🎬 Zoom Effect: {'ENABLED' if zoom_effect else 'DISABLED'}")
        
        # 📝 Generate script with Gemini (improved prompts!)
=======
        print(f"🎤 Requested Engine: {preferred_engine or 'auto'}")
        print(f"🎤 Requested Voice: {requested_voice_id or 'auto'}")
        print(f"🎬 Zoom Effect: {'ENABLED' if zoom_effect else 'DISABLED'}")

        # Generate script
>>>>>>> 8a672db9f56fce6ed963282e2210b52ac39849e2
        result = enhanced_script_generator.generate_with_template(
            topic=topic,
            story_type=story_type,
            template=template,
            research_data=research_data,
            duration_minutes=duration,
            num_scenes=num_scenes
        )

        script_text = result['script']

        progress_state['progress'] = 50
        progress_state['status'] = 'generating_images'

        print("🎨 Generating images...")
<<<<<<< HEAD
        
        # ✅ FIX: Use scenes from result if available (MUCH BETTER VARIETY!)
        if 'scenes' in result and result['scenes']:
            # Use the structured scenes from script generator - BEST QUALITY!
            scenes = result['scenes'][:num_scenes]
            print(f"   Using {len(scenes)} varied scenes from script generator")
        else:
            # Fallback: Extract image prompts from script
            image_prompts = re.findall(r'IMAGE:\s*(.+?)(?:\n|$)', script_text, re.IGNORECASE)
            
            if not image_prompts or len(image_prompts) < num_scenes:
                # Create VARIED prompts based on story progression
                print(f"   ⚠️  Creating varied prompts (no scenes in result)")
                story_parts = script_text.split('.')[:num_scenes]
                image_prompts = []
                for i, part in enumerate(story_parts):
                    if part.strip():
                        # Use actual story content for variety!
                        image_prompts.append(f"{part.strip()[:100]}")
                    else:
                        image_prompts.append(f"{topic}, scene {i+1}, {story_type} atmosphere")
            
            # Convert string prompts to scene dictionaries
            scenes = []
            for i, prompt in enumerate(image_prompts[:num_scenes]):
                scenes.append({
                    'image_description': prompt,
                    'content': prompt,
                    'scene_number': i + 1
                })
        
=======

        # Extract image prompts from script
        image_prompts = re.findall(r'IMAGE:\s*(.+?)(?:\n|$)', script_text, re.IGNORECASE)

        if not image_prompts:
            image_prompts = [f"{topic} scene {i+1}" for i in range(num_scenes)]

>>>>>>> 8a672db9f56fce6ed963282e2210b52ac39849e2
        # Generate images
        image_gen = create_image_generator('cinematic_film', story_type)
        characters = {char: f"{char}, character" for char in result.get('characters', [])[:3]}
        images = image_gen.generate_batch(scenes, characters)
        image_paths = [Path(img['filepath']) for img in images if img]

        print(f"✅ Generated {len(image_paths)} images")
<<<<<<< HEAD
        print(f"   🔍 DEBUG: Image paths:")
        for i, img_path in enumerate(image_paths):
            exists = "EXISTS" if img_path.exists() else "MISSING!"
            print(f"      Image {i+1}: {img_path.name} - {exists}")
        
        progress_state['progress'] = 70
        progress_state['status'] = 'generating_voice_edge'
        
        print(f"🎤 Generating voice with Edge-TTS (FREE!)...")
        
        # Generate audio with Edge-TTS
        audio_path = Path("output/temp/narration.mp3")
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        
        # ✅ EDGE-TTS - FREE & UNLIMITED!
        generate_audio_edge(
            text=script_text,
            voice=voice_id,
            output_path=str(audio_path)
        )
        
        audio_duration = get_audio_duration(audio_path)
        print(f"✅ Audio: {audio_duration:.1f} seconds ({audio_duration/60:.1f} minutes)")
        
        # ✅ SRT Subtitle Generation (if enabled)
        srt_path = None
        if srt_enabled:
            from src.editor.srt_generator import generate_srt_subtitles
            print("📝 Generating SRT subtitles (unlimited captions!)...")
            safe_topic_srt = re.sub(r'[^a-zA-Z0-9_\-]', '', topic)[:50]
            srt_path = generate_srt_subtitles(
                script_text,
                audio_duration,
                Path(f"output/subtitles/{safe_topic_srt}_subtitles.srt"),
                detect_emotions=emotion_captions
            )
            print(f"   ✅ SRT file: {srt_path}")
        
        # ✅ Auto Captions (burned-in, only if NOT using SRT)
        auto_captions = None
        if auto_captions_enabled and not srt_enabled:
            from src.editor.captions import generate_auto_captions
            print("📝 Generating auto captions from script...")
            auto_captions = generate_auto_captions(script_text, audio_duration)
            print(f"   ✅ Auto Captions: {len(auto_captions)} sentences")
        
=======

        progress_state['progress'] = 70

        def _voice_status(engine, stage, error=None):
            label = ENGINE_LABELS[engine]
            if stage == 'start':
                progress_state['status'] = f'Generating voice with {label}...'
            elif stage == 'success':
                progress_state['status'] = f'Voice ready ({label})'
                progress_state['voice_engine'] = engine
            elif stage == 'error':
                progress_state['status'] = f'{label} failed, trying fallback'

        print("🎤 Generating voice narration...")

        voice_engine, audio_path, resolved_voice = generate_voice_with_fallback(
            script_text,
            preferred_engine=preferred_engine,
            voice_id=requested_voice_id,
            speed=voice_speed,
            status_callback=_voice_status,
        )

        progress_state['voice_engine'] = voice_engine
        progress_state['voice_id'] = resolved_voice

        audio_duration = get_audio_duration(audio_path)
        print(f"✅ Audio: {audio_duration:.1f} seconds")
        print(f"   Engine Used: {ENGINE_LABELS[voice_engine]}")
        print(f"   Voice Used: {resolved_voice}")

>>>>>>> 8a672db9f56fce6ed963282e2210b52ac39849e2
        progress_state['progress'] = 80
        progress_state['status'] = 'compiling_video'

        print("🎬 Compiling video...")

        # Compile video
        compiler = FFmpegCompiler()
        safe_topic = re.sub(r'[^a-zA-Z0-9_\-]', '', topic)[:50]
        output_filename = f"{safe_topic}_video.mp4"

        time_per_image = audio_duration / len(image_paths) if image_paths else 5
        durations = [time_per_image] * len(image_paths)

        video_path = compiler.create_video(
            image_paths,
            str(audio_path),
            Path(f"output/videos/{output_filename}"),
            durations,
            zoom_effect=zoom_effect
        )

        progress_state['progress'] = 100
        progress_state['status'] = 'complete'
        progress_state['video_path'] = output_filename

        print(f"\n✅ SUCCESS!")
        print(f"   Video: {output_filename}")
        print(f"   Script: {len(script_text)} chars")
        print(f"   Voice Engine: {ENGINE_LABELS[voice_engine]}")
        print(f"   Voice: {resolved_voice}")
        print(f"   Zoom Effect: {'ENABLED' if zoom_effect else 'DISABLED'}")
        print(f"   Template: {'Used' if template else 'Not used'}")
        print(f"   Research: {'Used' if research_data else 'Not used'}\n")

    except Exception as e:
        progress_state['status'] = 'error'
        progress_state['error'] = str(e)
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()

# ═══════════════════════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify({
        'status': 'ok',
        'message': 'API Server running',
<<<<<<< HEAD
        'voice_engine': 'edge_tts',
        'script_engine': 'gemini_ai'
=======
        'kokoro_available': KOKORO_AVAILABLE and kokoro_tts is not None,
        'edge_available': True,
        'playht_available': PLAYHT_READY,
        'gtts_available': GTTS_AVAILABLE
>>>>>>> 8a672db9f56fce6ed963282e2210b52ac39849e2
    }), 200


@app.route('/api/voices', methods=['GET', 'OPTIONS'])
def list_voices():
    """✅ List all available Edge-TTS voices"""
    if request.method == 'OPTIONS':
        return '', 204
<<<<<<< HEAD
    
    # Edge-TTS voices (Microsoft)
    voices = {
        'guy': {'engine': 'edge', 'name': 'Guy', 'gender': 'male', 'style': 'Natural & Clear', 'best_for': 'General narration'},
        'andrew': {'engine': 'edge', 'name': 'Andrew', 'gender': 'male', 'style': 'Professional', 'best_for': 'Business content'},
        'christopher': {'engine': 'edge', 'name': 'Christopher', 'gender': 'male', 'style': 'Casual & Friendly', 'best_for': 'Vlogs, tutorials'},
        'roger': {'engine': 'edge', 'name': 'Roger', 'gender': 'male', 'style': 'Authoritative', 'best_for': 'News, documentaries'},
        'aria': {'engine': 'edge', 'name': 'Aria', 'gender': 'female', 'style': 'Natural & Warm', 'best_for': 'Stories, lifestyle'},
        'jenny': {'engine': 'edge', 'name': 'Jenny', 'gender': 'female', 'style': 'Cheerful & Clear', 'best_for': 'Education, tutorials'},
        'sara': {'engine': 'edge', 'name': 'Sara', 'gender': 'female', 'style': 'Young & Energetic', 'best_for': 'Adventure, action'},
        'nancy': {'engine': 'edge', 'name': 'Nancy', 'gender': 'female', 'style': 'Professional', 'best_for': 'Business, formal'},
    }
    
    return jsonify({
        'voices': voices,
        'engine': 'edge_tts',
        'total': len(voices),
        'cost': 'FREE',
        'unlimited': True
    }), 200
=======

    voices = {}

    # Kokoro voices (list even if engine unavailable for UI purposes)
    kokoro_available = kokoro_tts is not None
    kokoro_voice_list = []
    try:
        from src.voice.kokoro_tts import KokoroTTS
        kokoro_voice_list = list(KokoroTTS.VOICES.keys())
    except Exception:
        kokoro_voice_list = sorted(set(KOKORO_VOICE_MAP.values()))

    voices['kokoro'] = {
        'engine': 'kokoro',
        'available': kokoro_available,
        'voices': kokoro_voice_list,
        'aliases': KOKORO_VOICE_MAP,
        'default': DEFAULT_VOICES['kokoro'],
        'categories': KOKORO_SETTINGS.get('voice_categories', {})
    }

    # Edge-TTS voices
    voices['edge'] = {
        'engine': 'edge',
        'available': True,
        'voices': sorted(set(EDGE_VOICE_MAP.values())),
        'aliases': EDGE_VOICE_MAP,
        'default': DEFAULT_VOICES['edge'],
        'categories': EDGE_TTS_SETTINGS.get('voice_categories', {})
    }

    # PlayHT voices (premium)
    voices['playht'] = {
        'engine': 'playht',
        'available': PLAYHT_READY,
        'voices': sorted(set(PLAYHT_VOICE_MAP.values())),
        'aliases': PLAYHT_VOICE_MAP,
        'default': DEFAULT_VOICES['playht'],
        'requires_credentials': True
    }

    # gTTS voices (free)
    voices['gtts'] = {
        'engine': 'gtts',
        'available': GTTS_AVAILABLE,
        'voices': sorted(set(GTTS_VOICE_MAP.values())),
        'aliases': GTTS_VOICE_MAP,
        'default': DEFAULT_VOICES['gtts']
    }

    return jsonify(voices), 200
>>>>>>> 8a672db9f56fce6ed963282e2210b52ac39849e2


@app.route('/api/generate-video', methods=['POST', 'OPTIONS'])
def generate_video():
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.json
    
    # Validate required fields
    if not data.get('topic'):
        return jsonify({'error': 'Topic is required'}), 400
    
    global progress_state
    progress_state = {
        'status': 'starting',
        'progress': 0,
        'video_path': None,
        'error': None,
        'voice_engine': None,
        'voice_id': None,
    }
    
    threading.Thread(target=generate_video_background, args=(data,)).start()
    return jsonify({'success': True, 'message': 'Generation started'}), 200


@app.route('/api/progress', methods=['GET', 'OPTIONS'])
def get_progress():
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify(progress_state), 200


@app.route('/api/video/<path:filename>', methods=['GET', 'OPTIONS'])
def stream_video(filename):
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        video_path = f"output/videos/{filename}"
        return send_file(video_path, mimetype='video/mp4')
    except FileNotFoundError:
        return jsonify({'error': 'Video not found'}), 404


# ═══════════════════════════════════════════════════════════════
# TEMPLATE + RESEARCH ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route('/api/analyze-script', methods=['POST', 'OPTIONS'])
def analyze_script_endpoint():
    """✅ Analyze example script and extract template"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.json
        script_content = data.get('scriptContent', '')
        script_type = data.get('scriptType', 'story')
        
        if not script_content or len(script_content) < 100:
            return jsonify({'error': 'Script too short (min 100 chars)'}), 400
        
        print(f"\n📊 Analyzing script ({len(script_content)} chars)...")
        
        template = script_analyzer.analyze_script(script_content, script_type)
        
        print(f"✅ Template extracted: {len(template)} fields")
        
        return jsonify(template), 200
    
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/search-facts', methods=['POST', 'OPTIONS'])
def search_facts_endpoint():
    """✅ Search facts for topic (for documentaries)"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.json
        topic = data.get('topic', '')
        story_type = data.get('story_type', 'historical_documentary')
        
        if not topic or len(topic) < 3:
            return jsonify({'error': 'Topic required (min 3 chars)'}), 400
        
        print(f"\n🔍 Searching facts for: {topic}")
        
        result = fact_searcher.search_facts(topic, story_type)
        
        print(f"✅ Found facts for: {topic}")
        
        return jsonify(result), 200
    
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-with-template', methods=['POST', 'OPTIONS'])
def generate_with_template_endpoint():
    """✅ Generate script using template + optional research"""
    if request.method == 'OPTIONS':
        return '', 204
    
    global progress_state
    
    try:
        data = request.json
        
        if not data.get('topic'):
            return jsonify({'error': 'Topic required'}), 400
        
        topic = data.get('topic', '')
        story_type = data.get('story_type', 'scary_horror')
        template = data.get('template')
        research_data = data.get('research_data')
        duration = int(data.get('duration', 10))
        num_scenes = int(data.get('num_scenes', 10))
        voice_engine = data.get('voice_engine', 'inworld')
        voice_id = data.get('voice_id')
        voice_speed = float(data.get('voice_speed', 1.0))
        zoom_effect = data.get('zoom_effect', True)  # Default: True for better UX

        print(f"\n🎬 Generating with template: {topic}")
        print(f"   Type: {story_type}")
        print(f"   Scenes: {num_scenes}")
        print(f"   Template: {'Yes' if template else 'No'}")
        print(f"   Research: {'Yes' if research_data else 'No'}")
        print(f"   Voice Engine: {voice_engine}")
        print(f"   Voice ID: {voice_id}")
        print(f"   Voice Speed: {voice_speed}x")
        print(f"   Zoom Effect: {'ENABLED' if zoom_effect else 'DISABLED'}")

        progress_state = {
            'status': 'starting',
            'progress': 0,
            'video_path': None,
            'error': None,
            'voice_engine': None,
            'voice_id': None,
        }
        
        thread = threading.Thread(
            target=generate_with_template_background,
            args=(topic, story_type, template, research_data, duration, num_scenes, voice_engine, voice_id, voice_speed, zoom_effect)
        )
        thread.start()

        return jsonify({
            'success': True,
            'message': 'Generation started',
            'used_template': template is not None,
            'used_research': research_data is not None,
            'voice_engine': voice_engine,
            'zoom_effect': zoom_effect
        }), 200
    
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cache-stats', methods=['GET', 'OPTIONS'])
def cache_stats_endpoint():
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        stats = fact_searcher.get_cache_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/clear-cache', methods=['POST', 'OPTIONS'])
def clear_cache_endpoint():
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        fact_searcher.clear_cache()
        return jsonify({'success': True, 'message': 'Cache cleared'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔥 PROFESSIONAL YOUTUBE VIDEO GENERATOR!")
    print("="*60)
    print("📍 URL: http://localhost:5000")
    print("✨ Features: High Quality + Speed + FREE!")
    print("")
    print("📝 SCRIPT: Gemini AI (10/10 QUALITY!)")
    print("   - Enhanced prompts for better stories")
    print("   - Perfect timing calculation")
    print("   - ALL 5 senses, emotional depth")
    print("   - First-person narrative")
    print("   - Unique IMAGE descriptions")
    
    print("")
    print("🎤 VOICE: EDGE-TTS (Microsoft - FREE & UNLIMITED!)")
    print("   - 8 professional voices")
    print("   - FREE forever, no API key")
    print("   - Reliable, always works")
    print("   - $0 Forever!")
    
    print("")
    print("🎨 IMAGES: FLUX.1 Schnell (10/10 QUALITY, FREE)")
    print("   - Pollinations AI")
    print("   - Unique per scene")
    print("   - Cinematic variety")
    
    print("")
    print("🎬 VIDEO: FFmpeg + All Effects")
    print("   - 1080p HD quality")
    print("   - Zoom, captions, filters")
    print("   - 1-60 minute support")
    print("="*60)
    print("\n✅ ENDPOINTS:")
    print("   GET  /health - Server status")
    print("   GET  /api/voices - List all voices")
    print("   POST /api/generate-video - Generate video (quick)")
    print("   POST /api/generate-with-template - Generate with template")
    print("   POST /api/analyze-script - Extract template")
    print("   POST /api/search-facts - Get research facts")
    print("   GET  /api/cache-stats - Cache statistics")
    print("   POST /api/clear-cache - Clear cache")
    print("="*60)
    print("\n🏆 PROFESSIONAL YOUTUBE VIDEO GENERATOR READY!")
    print("💰 FREE - Puter TTS (voice) + Gemini (scripts) + FLUX (images)!")
    print("⚡ Fast: 3-10 minutes for 10-60 minute videos")
    print("🎬 Quality: 10/10 - Professional YouTube content!")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)