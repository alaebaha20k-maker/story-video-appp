"""
🔌 API SERVER - With Google Colab GPU (FULL GPU Processing)

System Architecture:
- Script: Gemini AI (local API call)
- Voice: Kokoro TTS (Colab GPU via ngrok)
- Images: SDXL-Turbo (Colab GPU via ngrok)
- Video: FFmpeg (Colab GPU via ngrok) ← ALL EFFECTS on GPU!
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pathlib import Path
import os
import threading
import re
from pydub import AudioSegment

# ✅ IMPORTS
from src.ai.enhanced_script_generator import enhanced_script_generator
from src.utils.colab_client import get_colab_client

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
    'voice_engine': 'kokoro',
    'voice_id': None,
}

# ═══════════════════════════════════════════════════════════════
# 🌐 COLAB CLIENT - Kokoro TTS + SDXL-Turbo
# ═══════════════════════════════════════════════════════════════

print(f"\n🌐 Using Google Colab GPU Server (via ngrok)")
print("✅ Kokoro TTS (48 voices, GPU-accelerated)")
print("✅ SDXL-Turbo (16:9 images, GPU-accelerated)")
print("✅ FFmpeg (video compilation with ALL effects, GPU-accelerated)")

# Initialize Colab client
try:
    colab_client = get_colab_client()
    # Test connection
    if colab_client.check_health():
        print("✅ Colab server connected!")
    else:
        print("⚠️ Warning: Colab server not responding!")
        print("   Make sure your Colab notebook is running")
except Exception as e:
    print(f"⚠️ Warning: Cannot connect to Colab: {e}")
    print("   Update COLAB_SERVER_URL in config/__init__.py")
    colab_client = None

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def sanitize_filename(filename):
    """Clean filename"""
    filename = re.sub(r'[^a-zA-Z0-9_\-]', '', filename)
    filename = re.sub(r'_+', '_', filename)
    return filename[:50]


def get_audio_duration(audio_path):
    """Get duration of audio file (MP3 or WAV)"""
    try:
        audio_path = str(audio_path)

        if audio_path.endswith('.mp3'):
            audio = AudioSegment.from_mp3(audio_path)
        elif audio_path.endswith('.wav'):
            audio = AudioSegment.from_wav(audio_path)
        else:
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
    """Video generation using Colab GPU"""
    global progress_state

    try:
        print(f"\n🎬 Starting generation: {data.get('topic', 'Untitled')}")

        voice_id = data.get('voice_id', 'guy')
        zoom_effect = data.get('zoom_effect', True)

        print(f"🎤 Voice Engine: Kokoro TTS (Colab GPU)")
        print(f"🎤 Voice ID: {voice_id}")
        print(f"🎨 Image Engine: SDXL-Turbo (Colab GPU)")
        print(f"🎬 Zoom Effect: {'ENABLED' if zoom_effect else 'DISABLED'}")

        # Update progress state
        progress_state['voice_engine'] = 'kokoro'
        progress_state['voice_id'] = voice_id

        # STEP 1: Script Generation (Gemini AI - Local)
        progress_state['status'] = 'Generating script...'
        progress_state['progress'] = 10
        print("📝 Step 1/4: Generating script with Gemini AI...")

        result = enhanced_script_generator.generate_with_template(
            topic=data.get('topic', 'Test Story'),
            story_type=data.get('story_type', 'scary_horror'),
            template=None,
            research_data=None,
            duration_minutes=int(data.get('duration', 5)),
            num_scenes=int(data.get('num_scenes', 10))
        )

        print(f"   ✅ Script: {len(result['script'])} characters")
        print(f"   ✅ Scenes: {len(result['scenes'])} generated")

        # STEP 2: Image Generation (SDXL-Turbo - Colab GPU)
        progress_state['status'] = 'Generating images with SDXL-Turbo (GPU)...'
        progress_state['progress'] = 30
        print("🎨 Step 2/4: Generating images with SDXL-Turbo (Colab GPU)...")

        # Call Colab for batch image generation
        image_style = data.get('image_style', 'cinematic')

        images = colab_client.generate_images_batch(
            scenes=result['scenes'],
            style=image_style
        )

        # Filter successful images
        image_paths = [Path(img['filepath']) for img in images if img.get('success')]

        print(f"   ✅ Images: {len(image_paths)} generated (1920x1080)")
        for i, img_path in enumerate(image_paths):
            exists = "EXISTS" if img_path.exists() else "MISSING!"
            print(f"      Image {i+1}: {img_path.name} - {exists}")

        # STEP 3: Voice Generation (Kokoro TTS - Colab GPU)
        progress_state['status'] = 'Generating voice with Kokoro TTS (GPU)...'
        progress_state['progress'] = 60
        print(f"🎤 Step 3/4: Generating voice with Kokoro TTS (Colab GPU)...")

        audio_path = Path("output/temp/narration.wav")
        audio_path.parent.mkdir(parents=True, exist_ok=True)

        # Call Colab for audio generation
        audio_file = colab_client.generate_audio(
            text=result['script'],
            voice=voice_id,
            speed=float(data.get('voice_speed', 1.0)),
            output_path=audio_path
        )

        audio_duration = get_audio_duration(audio_path)
        print(f"   ✅ Audio: {audio_duration:.1f} seconds ({audio_duration/60:.1f} minutes)")

        # Calculate durations - MATCH VIDEO TO AUDIO
        time_per_image = audio_duration / len(image_paths) if image_paths else 5
        durations = [time_per_image] * len(image_paths)

        print(f"   🔧 Image timing:")
        print(f"      Images: {len(image_paths)}")
        print(f"      Duration per image: {time_per_image:.1f}s")
        print(f"      Total video duration: {sum(durations):.1f}s ({sum(durations)/60:.1f} minutes)")

        # STEP 4: Video Compilation (FFmpeg - Colab GPU)
        progress_state['status'] = 'Compiling video with FFmpeg (GPU)...'
        progress_state['progress'] = 80
        print("🎬 Step 4/4: Compiling video with FFmpeg (Colab GPU)...")

        safe_topic = sanitize_filename(data.get('topic', 'video'))
        output_filename = f"{safe_topic}_video.mp4"

        # Get effects from request
        color_filter = data.get('color_filter', 'none')
        grain_effect = data.get('grain_effect', False)
        captions = data.get('captions', {})

        # Compile video on Colab GPU
        video_path = colab_client.compile_video(
            image_paths,
            audio_path,
            durations,
            output_path=Path(f"output/videos/{output_filename}"),
            zoom_effect=zoom_effect,
            color_filter=color_filter,
            grain_effect=grain_effect,
            captions=captions
        )

        progress_state['progress'] = 100
        progress_state['status'] = 'complete'
        progress_state['video_path'] = output_filename

        print(f"\n✅ SUCCESS! Video: {output_filename}")
        print(f"   Script: Gemini AI")
        print(f"   Voice: Kokoro TTS (Colab GPU)")
        print(f"   Images: SDXL-Turbo (Colab GPU)")
        print(f"   Video: FFmpeg (Colab GPU)")
        print(f"   Zoom: {'ON' if zoom_effect else 'OFF'}")
        print(f"   Color Filter: {color_filter}")
        print(f"   Grain: {'ON' if grain_effect else 'OFF'}\n")

    except Exception as e:
        progress_state['status'] = 'error'
        progress_state['error'] = str(e)
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()


def generate_with_template_background(
    topic, story_type, template, research_data, duration, num_scenes,
    voice_engine, voice_id, voice_speed=1.0, zoom_effect=True
):
    """Background generation with template + research + Colab GPU"""
    global progress_state

    try:
        progress_state['status'] = 'generating'
        progress_state['progress'] = 10

        progress_state['voice_engine'] = 'kokoro'
        progress_state['voice_id'] = voice_id

        print(f"📝 Generating script with template...")
        print(f"🎤 Voice Engine: Kokoro TTS (Colab GPU)")
        print(f"🎤 Voice: {voice_id}")
        print(f"🎬 Zoom Effect: {'ENABLED' if zoom_effect else 'DISABLED'}")

        # Script generation (Gemini AI - Local)
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

        print("🎨 Generating images with SDXL-Turbo (Colab GPU)...")

        # Use scenes from result if available
        if 'scenes' in result and result['scenes']:
            scenes = result['scenes'][:num_scenes]
            print(f"   Using {len(scenes)} varied scenes from script generator")
        else:
            # Fallback: Extract image prompts from script
            image_prompts = re.findall(r'IMAGE:\s*(.+?)(?:\n|$)', script_text, re.IGNORECASE)

            if not image_prompts or len(image_prompts) < num_scenes:
                print(f"   ⚠️ Creating varied prompts (no scenes in result)")
                story_parts = script_text.split('.')[:num_scenes]
                image_prompts = []
                for i, part in enumerate(story_parts):
                    if part.strip():
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

        # Generate images with Colab
        images = colab_client.generate_images_batch(scenes, style='cinematic')
        image_paths = [Path(img['filepath']) for img in images if img.get('success')]

        print(f"✅ Generated {len(image_paths)} images")

        progress_state['progress'] = 70
        progress_state['status'] = 'generating_voice_kokoro'

        print(f"🎤 Generating voice with Kokoro TTS (Colab GPU)...")

        # Generate audio with Colab
        audio_path = Path("output/temp/narration.wav")
        audio_path.parent.mkdir(parents=True, exist_ok=True)

        audio_file = colab_client.generate_audio(
            text=script_text,
            voice=voice_id,
            speed=voice_speed,
            output_path=audio_path
        )

        audio_duration = get_audio_duration(audio_path)
        print(f"✅ Audio: {audio_duration:.1f} seconds ({audio_duration/60:.1f} minutes)")

        progress_state['progress'] = 80
        progress_state['status'] = 'compiling_video'

        print("🎬 Compiling video with FFmpeg (Colab GPU)...")

        # Compile video on Colab GPU
        safe_topic = re.sub(r'[^a-zA-Z0-9_\-]', '', topic)[:50]
        output_filename = f"{safe_topic}_video.mp4"

        time_per_image = audio_duration / len(image_paths) if image_paths else 5
        durations = [time_per_image] * len(image_paths)

        video_path = colab_client.compile_video(
            image_paths,
            audio_path,
            durations,
            output_path=Path(f"output/videos/{output_filename}"),
            zoom_effect=zoom_effect,
            color_filter='none',  # Can be added as parameter
            grain_effect=False,   # Can be added as parameter
            captions={}          # Can be added as parameter
        )

        progress_state['progress'] = 100
        progress_state['status'] = 'complete'
        progress_state['video_path'] = output_filename

        print(f"\n✅ SUCCESS!")
        print(f"   Video: {output_filename}")
        print(f"   Script: {len(script_text)} chars")
        print(f"   Voice: Kokoro TTS (Colab GPU)")
        print(f"   Images: SDXL-Turbo (Colab GPU)")
        print(f"   Video: FFmpeg (Colab GPU)")
        print(f"   Zoom: {'ON' if zoom_effect else 'OFF'}")
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

    # Check Colab connection
    colab_healthy = False
    try:
        if colab_client:
            colab_healthy = colab_client.check_health()
    except:
        pass

    return jsonify({
        'status': 'ok',
        'message': 'API Server running',
        'voice_engine': 'kokoro_colab',
        'image_engine': 'sdxl_colab',
        'script_engine': 'gemini_ai',
        'colab_connected': colab_healthy
    }), 200


@app.route('/api/voices', methods=['GET', 'OPTIONS'])
def list_voices():
    """List all available Kokoro TTS voices"""
    if request.method == 'OPTIONS':
        return '', 204

    # Kokoro voices (from Colab notebook mapping)
    voices = {
        # Male voices
        'guy': {'engine': 'kokoro', 'name': 'Guy (Adam)', 'gender': 'male', 'style': 'Natural & Clear'},
        'adam_narration': {'engine': 'kokoro', 'name': 'Adam', 'gender': 'male', 'style': 'Professional Narration'},
        'michael': {'engine': 'kokoro', 'name': 'Michael', 'gender': 'male', 'style': 'Warm & Friendly'},
        'brian': {'engine': 'kokoro', 'name': 'Brian', 'gender': 'male', 'style': 'Casual'},
        'george': {'engine': 'kokoro', 'name': 'George', 'gender': 'male', 'style': 'British Accent'},

        # Female voices
        'aria': {'engine': 'kokoro', 'name': 'Aria (Bella)', 'gender': 'female', 'style': 'Natural & Warm'},
        'sarah_pro': {'engine': 'kokoro', 'name': 'Sarah', 'gender': 'female', 'style': 'Professional'},
        'nicole': {'engine': 'kokoro', 'name': 'Nicole', 'gender': 'female', 'style': 'Cheerful & Clear'},
        'jenny': {'engine': 'kokoro', 'name': 'Jenny', 'gender': 'female', 'style': 'Young & Energetic'},
        'emma': {'engine': 'kokoro', 'name': 'Emma', 'gender': 'female', 'style': 'British Accent'},
    }

    return jsonify({
        'voices': voices,
        'engine': 'kokoro_colab',
        'total': len(voices),
        'gpu_accelerated': True
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
        'voice_engine': 'kokoro',
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


@app.route('/api/generate-with-template', methods=['POST', 'OPTIONS'])
def generate_with_template_endpoint():
    """Generate script using template + optional research"""
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
        voice_engine = 'kokoro'
        voice_id = data.get('voice_id', 'guy')
        voice_speed = float(data.get('voice_speed', 1.0))
        zoom_effect = data.get('zoom_effect', True)

        print(f"\n🎬 Generating with template: {topic}")
        print(f"   Type: {story_type}")
        print(f"   Scenes: {num_scenes}")
        print(f"   Voice: {voice_id}")
        print(f"   Zoom: {'ON' if zoom_effect else 'OFF'}")

        progress_state = {
            'status': 'starting',
            'progress': 0,
            'video_path': None,
            'error': None,
            'voice_engine': 'kokoro',
            'voice_id': None,
        }

        thread = threading.Thread(
            target=generate_with_template_background,
            args=(topic, story_type, template, research_data, duration, num_scenes,
                  voice_engine, voice_id, voice_speed, zoom_effect)
        )
        thread.start()

        return jsonify({
            'success': True,
            'message': 'Generation started',
            'voice_engine': 'kokoro',
            'zoom_effect': zoom_effect
        }), 200

    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔥 PROFESSIONAL YOUTUBE VIDEO GENERATOR!")
    print("="*60)
    print("📍 URL: http://localhost:5000")
    print("✨ Features: GPU-Accelerated + High Quality!")
    print("")
    print("📝 SCRIPT: Gemini AI (Local API)")
    print("   - Enhanced prompts for better stories")
    print("   - Perfect timing calculation")
    print("")
    print("🎤 VOICE: Kokoro TTS (Google Colab GPU)")
    print("   - 48 professional voices")
    print("   - GPU-accelerated generation")
    print("   - High quality natural speech")
    print("")
    print("🎨 IMAGES: SDXL-Turbo (Google Colab GPU)")
    print("   - 1920x1080 (16:9 ratio)")
    print("   - 4-step generation (ultra-fast)")
    print("   - Cinematic quality")
    print("")
    print("🎬 VIDEO: FFmpeg (Google Colab GPU)")
    print("   - 1080p HD quality")
    print("   - Zoom effects ✅")
    print("   - Color filters (warm, cool, vintage, cinematic) ✅")
    print("   - Grain effects ✅")
    print("   - Captions support ✅")
    print("   - GPU-accelerated compilation")
    print("="*60)
    print("\n✅ ENDPOINTS:")
    print("   GET  /health - Server status")
    print("   GET  /api/voices - List all voices")
    print("   POST /api/generate-video - Generate video")
    print("   POST /api/generate-with-template - Generate with template")
    print("="*60)
    print("\n🏆 PROFESSIONAL YOUTUBE VIDEO GENERATOR READY!")
    print("⚡ GPU-Accelerated with Google Colab!")
    print("🎬 Quality: 10/10 - Professional YouTube content!")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
