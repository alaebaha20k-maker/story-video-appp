"""
🔌 API SERVER - With Remote Kokoro TTS (Google Colab GPU)
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pathlib import Path
import os
import threading
import re
from pydub import AudioSegment

# ✅ IMPORTS FOR TEMPLATES + RESEARCH
from src.ai.script_analyzer import script_analyzer
from src.research.fact_searcher import fact_searcher
from src.ai.enhanced_script_generator import enhanced_script_generator

# ✅ NEW: ADVANCED SCRIPT ANALYSIS
from src.ai.narration_extractor import narration_extractor
from src.ai.image_prompt_extractor import image_prompt_extractor

# ✅ EXISTING IMPORTS
from src.ai.image_generator import create_image_generator
from src.editor.ffmpeg_compiler import FFmpegCompiler

# ✅ VOICE: KOKORO TTS (Remote API)
from src.voice.kokoro_api_client import generate_kokoro_audio, get_kokoro_voice

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
# 🎤 KOKORO TTS - REMOTE GPU-POWERED (Google Colab)
# ═══════════════════════════════════════════════════════════════

print(f"\n🔧 Using Kokoro TTS (Remote Google Colab GPU)")
print("✅ Kokoro API ready - High-quality voice generation!")
print("   ⚡ GPU-powered for better quality & speed!")
print("   🎬 6 professional voices (American + British)!")

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def sanitize_filename(filename):
    """Clean filename"""
    filename = re.sub(r'[^a-zA-Z0-9_\-]', '', filename)
    filename = re.sub(r'_+', '_', filename)
    return filename[:50]


def get_voice_id(voice_id=None):
    """Get voice ID for Kokoro TTS (uses mapping from kokoro_api_client)"""

    # Default to 'guy' if not provided
    if not voice_id:
        voice_id = 'guy'

    # Use the Kokoro voice mapper
    kokoro_voice = get_kokoro_voice(voice_id)

    print(f"   🔧 Voice for Kokoro: {voice_id} → {kokoro_voice}")
    return voice_id  # Return frontend voice ID, will be mapped in generation


def generate_audio_kokoro(text, voice="guy", speed=1.0, output_path="narration.wav"):
    """✅ Generate audio using Remote Kokoro TTS (Google Colab GPU)"""
    print(f"\n🎤 Generating audio with Kokoro TTS (GPU-Powered!)...")
    print(f"   Voice: {voice}")
    print(f"   Speed: {speed}x")
    print(f"   Text length: {len(text)} characters")
    print(f"   Output path: {output_path}")

    try:
        # Generate with Kokoro API
        audio_path = generate_kokoro_audio(
            text=text,
            voice=voice,
            speed=speed,
            output_path=output_path,
            timeout=600  # 10 minutes timeout for long texts
        )

        print(f"✅ Kokoro TTS generation SUCCESS!")
        print(f"   🎬 High-quality GPU-generated voice!")
        return audio_path

    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ KOKORO TTS GENERATION FAILED!")
        print(f"{'='*60}")
        print(f"Error: {e}")
        print(f"Voice: {voice}")
        print(f"Speed: {speed}x")
        print(f"Text length: {len(text)}")
        print(f"\n💡 Troubleshooting:")
        print(f"   1. Check if Google Colab server is running")
        print(f"   2. Verify ngrok URL is correct")
        print(f"   3. Check internet connection")
        print(f"   4. Try a different voice")
        print(f"{'='*60}\n")
        raise


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


def get_audio_duration(audio_path):
    """✅ UNIVERSAL: Get exact duration of ANY audio file (MP3, WAV, etc.)"""
    try:
        import subprocess
        import json

        audio_path = str(audio_path)

        # Use ffprobe for EXACT duration (works with any format)
        result = subprocess.run([
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json',
            audio_path
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            data = json.loads(result.stdout)
            duration = float(data['format']['duration'])
            print(f"   📊 Exact audio duration: {duration:.2f}s ({duration/60:.2f} minutes)")
            return duration
        else:
            # Fallback to pydub if ffprobe fails
            if audio_path.endswith('.mp3'):
                audio = AudioSegment.from_mp3(audio_path)
            elif audio_path.endswith('.wav'):
                audio = AudioSegment.from_wav(audio_path)
            else:
                audio = AudioSegment.from_file(audio_path)

            duration = len(audio) / 1000.0  # Convert to seconds
            print(f"   📊 Audio duration (pydub): {duration:.2f}s")
            return duration

    except Exception as e:
        print(f"❌ Error reading audio duration: {e}")
        print(f"   ⚠️  Using fallback duration: 5.0 seconds")
        return 5.0  # Fallback


# ═══════════════════════════════════════════════════════════════
# BACKGROUND FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def generate_video_background(data):
    """Original video generation (without template)"""
    global progress_state

    try:
        print(f"\n🎬 Starting generation: {data.get('topic', 'Untitled')}")
        
        # Get voice from user (Kokoro TTS)
        voice_id = get_voice_id(data.get('voice_id'))
        zoom_effect = data.get('zoom_effect', True)

        print(f"🎤 Voice Engine: KOKORO TTS (Remote GPU)")
        print(f"🎤 Voice ID: {voice_id}")
        print(f"🎬 Zoom Effect: {'ENABLED' if zoom_effect else 'DISABLED'}")

        # Update progress state
        progress_state['voice_engine'] = 'kokoro'
        progress_state['voice_id'] = voice_id
        
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

        # ✨ Check if Advanced Analysis is enabled
        use_advanced_analysis = data.get('use_advanced_analysis', False)

        if use_advanced_analysis:
            print("✨ Advanced Analysis ENABLED")

            # Extract clean narration
            progress_state['status'] = 'Analyzing script for narration...'
            progress_state['progress'] = 15
            print("📊 Step 2a/5: Extracting clean narration...")

            narration_scenes = narration_extractor.extract_narration(
                result['script'],
                num_scenes=data.get('num_scenes', 10)
            )
            print(f"   ✅ Narration: {len(narration_scenes)} clean scenes extracted")

            # Generate detailed image prompts
            progress_state['status'] = 'Creating detailed image prompts...'
            progress_state['progress'] = 20
            print("🎨 Step 2b/5: Generating detailed image prompts...")

            image_prompt_scenes = image_prompt_extractor.generate_prompts(
                result['script'],
                num_scenes=data.get('num_scenes', 10),
                image_style=data.get('image_style', 'cinematic_film'),
                story_type=data.get('story_type', 'scary_horror')
            )
            print(f"   ✅ Image Prompts: {len(image_prompt_scenes)} detailed prompts generated")

            # Replace the scenes in result with analyzed ones
            result['narration_scenes'] = narration_scenes
            result['image_prompt_scenes'] = image_prompt_scenes
        else:
            print("✨ Advanced Analysis DISABLED (using standard mode)")

        # Images
        progress_state['status'] = 'Generating images...'
        progress_state['progress'] = 30
        print("🎨 Step 2/4: Generating images...")
        
        image_gen = create_image_generator(
            data.get('image_style', 'cinematic_film'),
            data.get('story_type', 'scary_horror')
        )
        characters = {char: f"{char}, character" for char in result.get('characters', [])[:3]}

        # Use detailed prompts if advanced analysis was enabled
        if use_advanced_analysis and 'image_prompt_scenes' in result:
            # Create scenes with image_description field from extracted prompts
            scenes_with_prompts = []
            for prompt_scene in result['image_prompt_scenes']:
                scenes_with_prompts.append({
                    'scene_num': prompt_scene['scene_number'],
                    'image_description': prompt_scene['image_prompt'],  # Detailed prompt
                    'content': ''  # Not used when image_description exists
                })
            images = image_gen.generate_batch(scenes_with_prompts, characters)
        else:
            # Standard mode - use original scenes
            images = image_gen.generate_batch(result['scenes'], characters)

        image_paths = [Path(img['filepath']) for img in images if img]
        
        print(f"   ✅ Images: {len(image_paths)} generated")
        print(f"   🔍 DEBUG: Image paths:")
        for i, img_path in enumerate(image_paths):
            exists = "EXISTS" if img_path.exists() else "MISSING!"
            print(f"      Image {i+1}: {img_path.name} - {exists}")
        
        # Voice Generation - Kokoro TTS
        progress_state['status'] = 'Generating voice with Kokoro TTS...'
        progress_state['progress'] = 60
        print(f"🎤 Step 4/5: Generating voice with Kokoro TTS (GPU!)..." if use_advanced_analysis else "🎤 Step 3/4: Generating voice with Kokoro TTS (GPU!)...")

        audio_path = Path("output/temp/narration.wav")
        audio_path.parent.mkdir(parents=True, exist_ok=True)

        # ✨ Use clean narration if advanced analysis was enabled
        if use_advanced_analysis and 'narration_scenes' in result:
            # Combine all narration scenes into one text
            narration_text = '\n\n'.join([scene['narration'] for scene in result['narration_scenes']])
            print(f"   Using CLEAN narration ({len(narration_text)} chars)")
        else:
            # Standard mode - use full script
            narration_text = result['script']
            print(f"   Using FULL script ({len(narration_text)} chars)")

        # ✅ KOKORO TTS - GPU-POWERED!
        voice_speed = data.get('voice_speed', 1.0)
        generate_audio_kokoro(
            text=narration_text,
            voice=voice_id,
            speed=voice_speed,
            output_path=str(audio_path)
        )
        
        # ✅ UNIVERSAL DYNAMIC AUDIO/VIDEO SYNC
        audio_duration = get_audio_duration(audio_path)
        print(f"   ✅ Audio generated: {audio_duration:.2f}s ({audio_duration/60:.2f} minutes)")

        # Check if we have images
        if not image_paths or len(image_paths) == 0:
            raise Exception("❌ No images were generated! Cannot create video without images.")

        # ✅ DYNAMIC CALCULATION - Works with ANY number of images
        num_images = len(image_paths)
        time_per_image = audio_duration / num_images

        print(f"\n   📊 UNIVERSAL VIDEO SYNC:")
        print(f"      Audio Duration: {audio_duration:.2f}s")
        print(f"      Number of Images: {num_images}")
        print(f"      Duration per Image: {time_per_image:.2f}s")
        print(f"      Total Video Length: {audio_duration:.2f}s (matches audio exactly)")
        print(f"      ✅ Video will end EXACTLY when audio ends (no extra silence)\n")

        # Create duration list for FFmpeg
        durations = [time_per_image] * num_images
        
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
        print(f"   Voice Engine: Kokoro TTS (Remote GPU)")
        print(f"   Voice: {voice_id}")
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
        
        # Get voice (Kokoro TTS)
        voice_id = get_voice_id(voice_id)
        progress_state['voice_engine'] = 'kokoro'
        progress_state['voice_id'] = voice_id

        print(f"📝 Generating script with template...")
        print(f"🎤 Voice Engine: KOKORO TTS (Remote GPU)")
        print(f"🎤 Voice: {voice_id}")
        print(f"🎤 Speed: {voice_speed}x")
        print(f"🎬 Zoom Effect: {'ENABLED' if zoom_effect else 'DISABLED'}")
        
        # 📝 Generate script with Gemini (improved prompts!)
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
        
        # Generate images
        image_gen = create_image_generator('cinematic_film', story_type)
        characters = {char: f"{char}, character" for char in result.get('characters', [])[:3]}
        images = image_gen.generate_batch(scenes, characters)
        image_paths = [Path(img['filepath']) for img in images if img]

        print(f"✅ Generated {len(image_paths)} images")
        print(f"   🔍 DEBUG: Image paths:")
        for i, img_path in enumerate(image_paths):
            exists = "EXISTS" if img_path.exists() else "MISSING!"
            print(f"      Image {i+1}: {img_path.name} - {exists}")
        
        progress_state['progress'] = 70
        progress_state['status'] = 'generating_voice_kokoro'

        print(f"🎤 Generating voice with Kokoro TTS (GPU!)...")

        # Generate audio with Kokoro TTS
        audio_path = Path("output/temp/narration.wav")
        audio_path.parent.mkdir(parents=True, exist_ok=True)

        # ✅ KOKORO TTS - GPU-POWERED!
        generate_audio_kokoro(
            text=script_text,
            voice=voice_id,
            speed=voice_speed,
            output_path=str(audio_path)
        )
        
        audio_duration = get_audio_duration(audio_path)
        print(f"✅ Audio: {audio_duration:.1f} seconds ({audio_duration/60:.1f} minutes)")
        
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
        print(f"   Voice Engine: Kokoro TTS (Remote GPU)")
        print(f"   Voice: {voice_id}")
        print(f"   Speed: {voice_speed}x")
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
        'voice_engine': 'kokoro_tts',
        'script_engine': 'gemini_ai'
    }), 200


@app.route('/api/voices', methods=['GET', 'OPTIONS'])
def list_voices():
    """✅ List all available Kokoro TTS voices"""
    if request.method == 'OPTIONS':
        return '', 204

    # Kokoro TTS voices (Remote GPU API)
    voices = {
        'guy': {'engine': 'kokoro', 'name': 'Adam', 'gender': 'male', 'style': 'Deep & Natural', 'best_for': 'General narration', 'kokoro_voice': 'am_adam'},
        'andrew': {'engine': 'kokoro', 'name': 'Adam', 'gender': 'male', 'style': 'Deep & Natural', 'best_for': 'Business content', 'kokoro_voice': 'am_adam'},
        'christopher': {'engine': 'kokoro', 'name': 'Michael', 'gender': 'male', 'style': 'Friendly & Warm', 'best_for': 'Vlogs, tutorials', 'kokoro_voice': 'am_michael'},
        'brian': {'engine': 'kokoro', 'name': 'Michael', 'gender': 'male', 'style': 'Friendly', 'best_for': 'Tutorials', 'kokoro_voice': 'am_michael'},
        'george': {'engine': 'kokoro', 'name': 'George (British)', 'gender': 'male', 'style': 'British Authoritative', 'best_for': 'Documentaries', 'kokoro_voice': 'bm_george'},
        'aria': {'engine': 'kokoro', 'name': 'Sarah', 'gender': 'female', 'style': 'Clear & Professional', 'best_for': 'Stories, lifestyle', 'kokoro_voice': 'af_sarah'},
        'jenny': {'engine': 'kokoro', 'name': 'Nicole', 'gender': 'female', 'style': 'Warm & Friendly', 'best_for': 'Education, tutorials', 'kokoro_voice': 'af_nicole'},
        'sara': {'engine': 'kokoro', 'name': 'Sarah', 'gender': 'female', 'style': 'Clear & Natural', 'best_for': 'Adventure, action', 'kokoro_voice': 'af_sarah'},
        'jane': {'engine': 'kokoro', 'name': 'Nicole', 'gender': 'female', 'style': 'Warm', 'best_for': 'Stories', 'kokoro_voice': 'af_nicole'},
        'libby': {'engine': 'kokoro', 'name': 'Emma (British)', 'gender': 'female', 'style': 'British Professional', 'best_for': 'Business, formal', 'kokoro_voice': 'bf_emma'},
        'emma': {'engine': 'kokoro', 'name': 'Emma (British)', 'gender': 'female', 'style': 'British Expressive', 'best_for': 'Narration', 'kokoro_voice': 'bf_emma'},
    }

    return jsonify({
        'voices': voices,
        'engine': 'kokoro_tts',
        'total': len(voices),
        'gpu_powered': True,
        'remote_api': True
    }), 200


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
    print("🎤 VOICE: KOKORO TTS (Remote GPU - Google Colab)")
    print("   - 11 frontend voices → 6 Kokoro voices")
    print("   - GPU-powered for high quality")
    print("   - American + British accents")
    print("   - Variable speed control (0.5x - 2.0x)")
    
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
    print("⚡ GPU-POWERED: Kokoro TTS (voice) + Gemini (scripts) + FLUX (images)!")
    print("🚀 Fast: 3-10 minutes for 10-60 minute videos")
    print("🎬 Quality: 10/10 - Professional YouTube content with GPU voices!")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)