"""
🔌 API SERVER - Edge-TTS narration + Flux image prompts
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pathlib import Path
import threading
import re
import asyncio
import edge_tts
from pydub import AudioSegment

# ✅ IMPORTS FOR TEMPLATES + RESEARCH
from src.ai.script_analyzer import script_analyzer
from src.research.fact_searcher import fact_searcher
from src.ai.enhanced_script_generator import enhanced_script_generator

# ✅ EXISTING IMPORTS
from src.ai.image_generator import create_image_generator
from src.editor.ffmpeg_compiler import FFmpegCompiler
import config.settings as settings

from config.settings import (
    EDGE_TTS_SETTINGS,
    EDGE_VOICE_MAP,
    resolve_edge_voice,
)

# Some user environments may still run an older settings module that does not
# export the resolver helper. Guard the import so the API never crashes with a
# NameError when background threads call the helper.
if hasattr(settings, "get_voice_engine_and_id"):
    get_voice_engine_and_id = settings.get_voice_engine_and_id
else:
    def get_voice_engine_and_id(requested_engine=None, requested_voice=None):
        engine = "edge"
        if requested_engine and requested_engine.lower() != "edge":
            print(
                f"⚠️ Voice engine '{requested_engine}' requested but Edge-TTS is enforced."
            )
        voice_id = resolve_edge_voice(requested_voice)
        return engine, voice_id

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
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def sanitize_filename(filename):
    """Clean filename"""
    filename = re.sub(r'[^a-zA-Z0-9_\-]', '', filename)
    filename = re.sub(r'_+', '_', filename)
    return filename[:50]


def clean_script_for_voice(script_text):
    """Remove image prompt annotations before feeding text to TTS."""
    cleaned_lines = []
    for line in script_text.splitlines():
        if re.match(r"^\s*(IMAGE(?: PROMPT)?|PROMPT|SCENE IMAGE)\b", line, re.IGNORECASE):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()


async def generate_audio_edge_tts(text, voice="en-US-AriaNeural", output_path="narration.mp3"):
    """✅ Generate audio using Edge-TTS (FREE, no API key)"""
    try:
        print(f"🎤 Generating audio with Edge-TTS...")
        print(f"   Voice: {voice}")
        print(f"   Text: {len(text)} characters")

        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(output_path))

        print(f"✅ Audio generated: {output_path}")
        return str(output_path)

    except Exception as e:
        print(f"❌ Edge-TTS Error: {e}")
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

        voice_engine, voice_id = get_voice_engine_and_id(
            data.get('voice_engine'),
            data.get('voice_id')
        )

        # Get zoom effect setting (default: True for better UX)
        zoom_effect = data.get('zoom_effect', True)

        print(f"🎤 Voice Engine: {voice_engine.upper()}")
        print(f"🎤 Voice ID: {voice_id}")
        print(f"🎬 Zoom Effect: {'ENABLED' if zoom_effect else 'DISABLED'}")
        
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

        audio_path = Path("output/temp/narration.mp3")
        audio_path.parent.mkdir(parents=True, exist_ok=True)

        narration_text = clean_script_for_voice(result['script'])

        asyncio.run(generate_audio_edge_tts(
            narration_text,
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
        print(f"   Voice Engine: {voice_engine.upper()}")
        print(f"   Voice: {voice_id}")
        print(f"   Zoom Effect: {'ENABLED' if zoom_effect else 'DISABLED'}\n")
        
    except Exception as e:
        progress_state['status'] = 'error'
        progress_state['error'] = str(e)
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()


def generate_with_template_background(topic, story_type, template, research_data, duration, num_scenes, voice_engine, voice_id, zoom_effect=True):
    """✅ Background generation with template + research + voice selection + zoom effect"""
    global progress_state

    try:
        progress_state['status'] = 'generating'
        progress_state['progress'] = 10

        print(f"📝 Generating script with template...")
        print(f"🎤 Voice Engine: {voice_engine.upper()}")
        print(f"🎤 Voice: {voice_id}")
        print(f"🎬 Zoom Effect: {'ENABLED' if zoom_effect else 'DISABLED'}")

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
        
        # Prepare scene data for image generation
        scenes = result.get('scenes', [])
        if not scenes:
            scenes = [{'scene_num': i + 1, 'content': f"{topic} scene {i + 1}"} for i in range(num_scenes)]

        scene_inputs = []
        for idx, scene in enumerate(scenes[:num_scenes]):
            scene_inputs.append({
                'scene_number': scene.get('scene_num', idx + 1),
                'content': scene.get('content', ''),
                'image_description': scene.get('image_description', scene.get('content', ''))
            })

        # Generate images
        image_gen = create_image_generator('cinematic_film', story_type)
        characters = {char: f"{char}, character" for char in result.get('characters', [])[:3]}
        images = image_gen.generate_batch(scene_inputs, characters)
        image_paths = [Path(img['filepath']) for img in images if img]

        print(f"✅ Generated {len(image_paths)} images")

        progress_state['progress'] = 70
        progress_state['status'] = f'generating_voice_{voice_engine.lower()}'

        print(f"🎤 Generating voice with {voice_engine.upper()}...")

        # Generate audio with Edge-TTS
        audio_path = Path("output/temp/narration.mp3")
        audio_path.parent.mkdir(parents=True, exist_ok=True)

        narration_text = clean_script_for_voice(script_text)

        asyncio.run(generate_audio_edge_tts(
            narration_text,
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
        print(f"   Voice Engine: {voice_engine.upper()}")
        print(f"   Voice: {voice_id}")
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
        'edge_available': True
    }), 200


@app.route('/api/voices', methods=['GET', 'OPTIONS'])
def list_voices():
    """✅ List all available Edge-TTS voices"""
    if request.method == 'OPTIONS':
        return '', 204
    
    voices = {
        'edge': {
            'engine': 'edge',
            'voices': sorted(set(list(EDGE_VOICE_MAP.keys()) + list(EDGE_TTS_SETTINGS.get('voice_categories', {}).keys()))),
            'categories': EDGE_TTS_SETTINGS.get('voice_categories', {})
        }
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
        requested_engine = data.get('voice_engine')
        requested_voice = data.get('voice_id')
        voice_engine, voice_id = get_voice_engine_and_id(requested_engine, requested_voice)
        zoom_effect = data.get('zoom_effect', True)  # Default: True for better UX

        print(f"\n🎬 Generating with template: {topic}")
        print(f"   Type: {story_type}")
        print(f"   Template: {'Yes' if template else 'No'}")
        print(f"   Research: {'Yes' if research_data else 'No'}")
        if requested_engine and requested_engine.lower() != voice_engine:
            print(f"   Voice Engine request: {requested_engine} (overridden to {voice_engine.upper()})")
        else:
            print(f"   Voice Engine: {voice_engine}")
        print(f"   Zoom Effect: {'ENABLED' if zoom_effect else 'DISABLED'}")
        
        progress_state = {
            'status': 'starting',
            'progress': 0,
            'video_path': None,
            'error': None
        }

        thread = threading.Thread(
            target=generate_with_template_background,
            args=(topic, story_type, template, research_data, duration, num_scenes, voice_engine, voice_id, zoom_effect)
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
    print("🚀 API SERVER READY - EDGE TTS ONLY!")
    print("="*60)
    print("📍 URL: http://localhost:5000")
    print("✨ Features: Templates + Research + Video Generation")

    print("🎤 Voice: Edge-TTS (FREE)")
    print("🎨 Images: Pollinations AI (Flux model)")
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

