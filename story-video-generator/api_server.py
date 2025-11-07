"""
🔌 API SERVER - With Kokoro TTS (PRIMARY) + Edge-TTS (BACKUP)
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pathlib import Path
import threading
import re
import asyncio
import edge_tts
from pydub import AudioSegment

# ✅ KOKORO TTS IMPORT
try:
    from src.voice.kokoro_tts import create_kokoro_tts
    KOKORO_AVAILABLE = True
except ImportError:
    KOKORO_AVAILABLE = False
    print("⚠️ Kokoro TTS not available - using Edge-TTS only")

# ✅ IMPORTS FOR TEMPLATES + RESEARCH
from src.ai.script_analyzer import script_analyzer
from src.research.fact_searcher import fact_searcher
from src.ai.enhanced_script_generator import enhanced_script_generator

# ✅ EXISTING IMPORTS
from src.ai.image_generator import create_image_generator
from src.editor.ffmpeg_compiler import FFmpegCompiler
from config.settings import KOKORO_SETTINGS, EDGE_TTS_SETTINGS

app = Flask(__name__)

# CORS for all origins
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

progress_state = {'status': 'ready', 'progress': 0, 'video_path': None, 'error': None}

# ═══════════════════════════════════════════════════════════════
# 🎤 VOICE ENGINE INITIALIZATION
# ═══════════════════════════════════════════════════════════════

kokoro_tts = None
if KOKORO_AVAILABLE and KOKORO_SETTINGS.get("enabled"):
    try:
        kokoro_tts = create_kokoro_tts(device=KOKORO_SETTINGS.get("device", "cpu"))
        print("✅ Kokoro TTS initialized")
    except Exception as e:
        print(f"⚠️ Failed to initialize Kokoro TTS: {e}")
        kokoro_tts = None

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def sanitize_filename(filename):
    """Clean filename"""
    filename = re.sub(r'[^a-zA-Z0-9_\-]', '', filename)
    filename = re.sub(r'_+', '_', filename)
    return filename[:50]


def get_voice_engine_and_id(voice_engine=None, voice_id=None):
    """
    Determine which voice engine to use and map voice ID
    Returns: (engine, voice_id)
    """
    # Default to kokoro if available
    if voice_engine is None:
        voice_engine = "kokoro" if kokoro_tts else "edge"
    
    # If kokoro requested but not available, fallback to edge
    if voice_engine == "kokoro" and not kokoro_tts:
        print("⚠️ Kokoro not available, falling back to Edge-TTS")
        voice_engine = "edge"
    
    # Map voice IDs
    if voice_engine == "kokoro":
        # Map common voice names to kokoro voices
        voice_map = {
            'male_narrator_deep': 'am_adam',
            'female_narrator': 'af_bella',
            'female_young': 'af_nova',
            'narrator_male_deep': 'am_adam',
            'narrator_female_warm': 'af_bella',
            'narrator_british_female': 'bf_emma',
        }
        
        # Use mapping or default
        if voice_id:
            voice_id = voice_map.get(voice_id, voice_id)
        else:
            voice_id = KOKORO_SETTINGS.get("default_voice", "af_bella")
    
    elif voice_engine == "edge":
        # Map to Edge-TTS voices
        voice_map = {
            'male_narrator_deep': 'en-US-GuyNeural',
            'female_narrator': 'en-US-AriaNeural',
            'female_young': 'en-US-JennyNeural',
            'narrator_male_deep': 'en-US-GuyNeural',
            'narrator_female_warm': 'en-US-AriaNeural',
        }
        
        if voice_id:
            voice_id = voice_map.get(voice_id, voice_id)
        else:
            voice_id = EDGE_TTS_SETTINGS.get("default_voice", "en-US-AriaNeural")
    
    return voice_engine, voice_id


async def generate_audio_edge_tts(text, voice="en-US-AriaNeural", output_path="narration.mp3", speed_boost=True):
    """✅ Generate audio using Edge-TTS (FREE, no API key) - SUPER FAST with speed boost + parallel"""
    try:
        # ⚡ SPEED BOOST: Make voice speak 1.3x faster (reduces audio duration by 23%)
        rate = "+30%" if speed_boost else "+0%"
        
        print(f"🎤 Generating audio with Edge-TTS...")
        print(f"   Voice: {voice}")
        print(f"   Speech Rate: {rate} {'⚡ FAST MODE!' if speed_boost else ''}")
        print(f"   Text: {len(text)} characters")
        
        # ⚡ AGGRESSIVE PARALLEL: Use parallel chunking for ANY text >800 chars (was 5000)
        # Smaller threshold = more parallelism = MUCH FASTER!
        if len(text) > 800:
            print(f"   🚀 Using AGGRESSIVE parallel chunking for 5-10x speedup...")
            return await _generate_audio_edge_parallel(text, voice, output_path, rate)
        
        # For very short text (<800 chars), generate directly
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(str(output_path))
        
        print(f"✅ Audio generated: {output_path}")
        return str(output_path)
        
    except Exception as e:
        print(f"❌ Edge-TTS Error: {e}")
        raise


async def _generate_audio_edge_parallel(text, voice, output_path, rate="+0%"):
    """Generate audio in parallel chunks using asyncio.gather - SUPER FAST!"""
    from pydub import AudioSegment
    
    # ⚡ EVEN SMALLER CHUNKS = MORE PARALLEL TASKS = FASTER!
    # Changed from 2000 to 1000 chars per chunk for MAXIMUM parallelism
    chunks = _split_text_smart(text, max_chars=1000)
    print(f"   Split into {len(chunks)} chunks")
    print(f"   🚀 Processing {len(chunks)} chunks in AGGRESSIVE PARALLEL for 10x+ speedup...")
    
    # Create temporary directory
    temp_dir = Path("output/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate all chunks in parallel
    chunk_files = []
    tasks = []
    
    for i, chunk in enumerate(chunks):
        chunk_file = temp_dir / f"chunk_{i:03d}.mp3"
        chunk_files.append(chunk_file)
        
        # Create async task for each chunk with speed boost
        communicate = edge_tts.Communicate(chunk, voice, rate=rate)
        tasks.append(communicate.save(str(chunk_file)))
    
    # Execute all tasks in parallel
    await asyncio.gather(*tasks)
    
    # Merge all chunks
    print(f"   Merging {len(chunk_files)} audio chunks...")
    combined = AudioSegment.empty()
    
    for chunk_file in chunk_files:
        audio = AudioSegment.from_mp3(str(chunk_file))
        combined += audio
        chunk_file.unlink()  # Clean up
    
    # Save final audio
    combined.export(str(output_path), format="mp3")
    
    print(f"✅ Audio generated: {output_path}")
    return str(output_path)


def _split_text_smart(text, max_chars=1000):
    """Split text at sentence boundaries"""
    # Split by sentences
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
    
    return chunks


def generate_audio_kokoro(text, voice="af_bella", speed=1.0, output_path="narration.wav"):
    """✅ Generate audio using Kokoro TTS"""
    try:
        if not kokoro_tts:
            raise RuntimeError("Kokoro TTS not initialized")
        
        print(f"🎤 Generating audio with Kokoro TTS...")
        
        audio_path = kokoro_tts.generate_audio(
            text=text,
            voice=voice,
            speed=speed,
            output_path=str(output_path)
        )
        
        return audio_path
        
    except Exception as e:
        print(f"❌ Kokoro TTS Error: {e}")
        raise


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
        
        # Determine voice engine
        voice_engine = data.get('voice_engine', 'kokoro')
        voice_id = data.get('voice_id')
        voice_engine, voice_id = get_voice_engine_and_id(voice_engine, voice_id)
        
        print(f"🎤 Voice Engine: {voice_engine.upper()}")
        print(f"🎤 Voice ID: {voice_id}")
        
        # Script
        progress_state['status'] = 'Generating script...'
        progress_state['progress'] = 10
        print("📝 Step 1/4: Generating script...")
        
        result = enhanced_script_generator.generate_with_template(
            topic=data.get('topic', 'Test Story'),
            story_type=data.get('story_type', 'scary_horror'),
            template=None,  # No template
            research_data=None,  # No research
            duration_minutes=int(data.get('duration', 5)),
            num_scenes=10
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
        
        # Voice Generation
        progress_state['status'] = f'Generating voice with {voice_engine.upper()}...'
        progress_state['progress'] = 60
        print(f"🎤 Step 3/4: Generating voice with {voice_engine.upper()}...")
        
        audio_path = Path("output/temp/narration.wav" if voice_engine == "kokoro" else "output/temp/narration.mp3")
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        
        if voice_engine == "kokoro":
            # ✅ KOKORO TTS
            generate_audio_kokoro(
                text=result['script'],
                voice=voice_id,
                speed=data.get('voice_speed', 1.0),
                output_path=str(audio_path)
            )
        else:
            # ✅ EDGE-TTS FALLBACK
            asyncio.run(generate_audio_edge_tts(
                result['script'],
                voice=voice_id,
                output_path=str(audio_path)
            ))
        
        audio_duration = get_audio_duration(audio_path)
        print(f"   ✅ Audio: {audio_duration:.1f} seconds")
        
        # Calculate durations
        time_per_image = audio_duration / len(image_paths) if image_paths else 5
        durations = [time_per_image] * len(image_paths)
        
        # Video
        progress_state['status'] = 'Compiling video...'
        progress_state['progress'] = 80
        print("🎬 Step 4/4: Compiling video...")
        
        compiler = FFmpegCompiler()
        safe_topic = sanitize_filename(data.get('topic', 'video'))
        output_filename = f"{safe_topic}_video.mp4"
        
        # Get optional filters and captions from request
        color_filter = data.get('color_filter', 'none')
        zoom_effect = data.get('zoom_effect', False)
        caption = data.get('caption')  # Dict with text, style, position, etc.
        auto_captions_enabled = data.get('auto_captions', False)
        
        # Generate auto captions from script if enabled
        auto_captions = None
        if auto_captions_enabled:
            from src.editor.captions import generate_auto_captions
            print("📝 Generating auto captions from script...")
            auto_captions = generate_auto_captions(result['script'], audio_duration)
            print(f"   ✅ Auto Captions: {len(auto_captions)} sentences")
        
        video_path = compiler.create_video(
            image_paths,
            str(audio_path),
            Path(f"output/videos/{output_filename}"),
            durations,
            color_filter=color_filter,
            zoom_effect=zoom_effect,
            caption=caption,
            auto_captions=auto_captions
        )
        
        progress_state['progress'] = 100
        progress_state['status'] = 'complete'
        progress_state['video_path'] = output_filename
        
        print(f"\n✅ SUCCESS! Video: {output_filename}")
        print(f"   Voice Engine: {voice_engine.upper()}")
        print(f"   Voice: {voice_id}\n")
        
    except Exception as e:
        progress_state['status'] = 'error'
        progress_state['error'] = str(e)
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()


def generate_with_template_background(topic, story_type, template, research_data, duration, num_scenes, voice_engine, voice_id):
    """✅ Background generation with template + research + voice selection"""
    global progress_state
    
    try:
        progress_state['status'] = 'generating'
        progress_state['progress'] = 10
        
        # Determine voice engine
        voice_engine, voice_id = get_voice_engine_and_id(voice_engine, voice_id)
        
        print(f"📝 Generating script with template...")
        print(f"🎤 Voice Engine: {voice_engine.upper()}")
        print(f"🎤 Voice: {voice_id}")
        
        # Generate script
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
        
        # Extract image prompts from script
        image_prompts = re.findall(r'IMAGE:\s*(.+?)(?:\n|$)', script_text, re.IGNORECASE)
        
        if not image_prompts:
            image_prompts = [f"{topic} scene {i+1}" for i in range(num_scenes)]
        
        # Generate images
        image_gen = create_image_generator('cinematic_film', story_type)
        characters = {char: f"{char}, character" for char in result.get('characters', [])[:3]}
        images = image_gen.generate_batch(image_prompts[:num_scenes], characters)
        image_paths = [Path(img['filepath']) for img in images if img]
        
        print(f"✅ Generated {len(image_paths)} images")
        
        progress_state['progress'] = 70
        progress_state['status'] = f'generating_voice_{voice_engine}'
        
        print(f"🎤 Generating voice with {voice_engine.upper()}...")
        
        # Generate audio based on engine
        audio_path = Path("output/temp/narration.wav" if voice_engine == "kokoro" else "output/temp/narration.mp3")
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        
        if voice_engine == "kokoro":
            # ✅ KOKORO TTS
            generate_audio_kokoro(
                text=script_text,
                voice=voice_id,
                speed=1.0,
                output_path=str(audio_path)
            )
        else:
            # ✅ EDGE-TTS
            asyncio.run(generate_audio_edge_tts(
                script_text,
                voice=voice_id,
                output_path=str(audio_path)
            ))
        
        audio_duration = get_audio_duration(audio_path)
        print(f"✅ Audio: {audio_duration:.1f} seconds")
        
        progress_state['progress'] = 80
        progress_state['status'] = 'compiling_video'
        
        print("🎬 Compiling video...")
        
        # Compile video
        compiler = FFmpegCompiler()
        safe_topic = re.sub(r'[^a-zA-Z0-9_\-]', '', topic)[:50]
        output_filename = f"{safe_topic}_video.mp4"
        
        time_per_image = audio_duration / len(image_paths) if image_paths else 5
        durations = [time_per_image] * len(image_paths)
        
        # Note: Template generation doesn't get filters/captions from request yet
        # Can be added later if needed
        video_path = compiler.create_video(
            image_paths,
            str(audio_path),
            Path(f"output/videos/{output_filename}"),
            durations
        )
        
        progress_state['progress'] = 100
        progress_state['status'] = 'complete'
        progress_state['video_path'] = output_filename
        
        print(f"\n✅ SUCCESS!")
        print(f"   Video: {output_filename}")
        print(f"   Script: {len(script_text)} chars")
        print(f"   Voice Engine: {voice_engine.upper()}")
        print(f"   Voice: {voice_id}")
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
        'kokoro_available': KOKORO_AVAILABLE and kokoro_tts is not None,
        'edge_available': True
    }), 200


@app.route('/api/voices', methods=['GET', 'OPTIONS'])
def list_voices():
    """✅ List all available voices from both engines"""
    if request.method == 'OPTIONS':
        return '', 204
    
    voices = {}
    
    # Kokoro voices
    if kokoro_tts:
        from src.voice.kokoro_tts import KokoroTTS
        voices['kokoro'] = {
            'engine': 'kokoro',
            'voices': list(KokoroTTS.VOICES.keys()),
            'categories': KOKORO_SETTINGS.get('voice_categories', {})
        }
    
    # Edge-TTS voices
    voices['edge'] = {
        'engine': 'edge',
        'voices': ['male_narrator_deep', 'female_narrator', 'female_young'],
        'categories': EDGE_TTS_SETTINGS.get('voice_categories', {})
    }
    
    return jsonify(voices), 200


@app.route('/api/generate-video', methods=['POST', 'OPTIONS'])
def generate_video():
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.json
    
    # Validate required fields
    if not data.get('topic'):
        return jsonify({'error': 'Topic is required'}), 400
    
    global progress_state
    progress_state = {'status': 'starting', 'progress': 0, 'video_path': None, 'error': None}
    
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
        voice_engine = data.get('voice_engine', 'kokoro')
        voice_id = data.get('voice_id')
        
        print(f"\n🎬 Generating with template: {topic}")
        print(f"   Type: {story_type}")
        print(f"   Template: {'Yes' if template else 'No'}")
        print(f"   Research: {'Yes' if research_data else 'No'}")
        print(f"   Voice Engine: {voice_engine}")
        
        progress_state = {
            'status': 'starting',
            'progress': 0,
            'video_path': None,
            'error': None
        }
        
        thread = threading.Thread(
            target=generate_with_template_background,
            args=(topic, story_type, template, research_data, duration, num_scenes, voice_engine, voice_id)
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Generation started',
            'used_template': template is not None,
            'used_research': research_data is not None,
            'voice_engine': voice_engine
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
    print("🚀 API SERVER READY - WITH KOKORO TTS!")
    print("="*60)
    print("📍 URL: http://localhost:5000")
    print("✨ Features: Templates + Research + Video Generation")
    
    if kokoro_tts:
        print("🎤 Voice: Kokoro TTS (48 voices, FREE!)")
        print("🎤 Backup: Edge-TTS (FREE)")
    else:
        print("🎤 Voice: Edge-TTS (FREE)")
        print("⚠️  Kokoro TTS not available")
    
    print("🎨 Images: Pollinations AI + FLUX.1 Schnell (HIGH QUALITY, FREE)")
    print("📝 Script: Gemini AI with Templates")
    print("="*60)
    print("\n✅ ENDPOINTS:")
    print("   GET  /api/voices - List all voices")
    print("   POST /api/generate-video - Generate video")
    print("   POST /api/analyze-script - Extract template")
    print("   POST /api/search-facts - Get research facts")
    print("   POST /api/generate-with-template - Generate with template")
    print("   GET  /api/cache-stats - Cache statistics")
    print("   POST /api/clear-cache - Clear cache")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)