"""
🔌 API SERVER - Hybrid TTS (PlayHT + gTTS Fallback)
Supports both PlayHT (Premium) and gTTS (Free) - Automatic Fallback
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pathlib import Path
import threading
import re
import os
import subprocess

from src.ai.pro_script_generator import pro_script_generator
from src.ai.image_generator import create_image_generator
from src.editor.ffmpeg_compiler import FFmpegCompiler

# ===== TTS ENGINE DETECTION =====
TTS_ENGINE = None
PLAYHT_AVAILABLE = False
GTTS_AVAILABLE = False

# Try PlayHT
try:
    import playht
    PLAYHT_AVAILABLE = True
    print("✅ PlayHT library found")
except ImportError:
    print("⚠️ PlayHT not installed (optional)")

# Try gTTS
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
    print("✅ gTTS library found")
except ImportError:
    print("⚠️ gTTS not installed (will install on first use)")

app = Flask(__name__)

# CORS Configuration
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

progress_state = {'status': 'ready', 'progress': 0, 'video_path': None, 'error': None}

# ===== PlayHT Configuration =====
PLAYHT_USER_ID = os.getenv('PLAYHT_USER_ID', '')
PLAYHT_API_KEY = os.getenv('PLAYHT_API_KEY', '')

# PlayHT Voice Mapping
PLAYHT_VOICE_MAPPING = {
    'male_narrator_deep': 'James',
    'male_professional': 'George',
    'male_warm': 'Michael',
    'female_narrator': 'Rachel',
    'female_professional': 'Catherine',
    'male_energetic': 'Scott',
    'british_male': 'Edward',
    'female_warm': 'Lily',
}

# gTTS Voice Mapping
GTTS_VOICE_MAPPING = {
    'male_narrator_deep': 'en',
    'male_professional': 'en',
    'male_warm': 'en',
    'female_narrator': 'en',
    'female_professional': 'en',
    'male_energetic': 'en',
    'british_male': 'en-gb',
    'female_warm': 'en',
}

# Initialize PlayHT if credentials available
if PLAYHT_AVAILABLE and PLAYHT_USER_ID and PLAYHT_API_KEY:
    try:
        print("🎤 Initializing PlayHT...")
        playht.api_key = PLAYHT_API_KEY
        playht.user_id = PLAYHT_USER_ID
        print("✅ PlayHT ready!")
        TTS_ENGINE = "PlayHT"
    except Exception as e:
        print(f"❌ PlayHT initialization failed: {e}")
        PLAYHT_AVAILABLE = False

# Fallback to gTTS
if not PLAYHT_AVAILABLE and GTTS_AVAILABLE:
    print("🎤 Using gTTS as TTS engine (FREE, no credentials needed)")
    TTS_ENGINE = "gTTS"
elif not PLAYHT_AVAILABLE and not GTTS_AVAILABLE:
    print("⚠️ No TTS engine available. Will attempt to install gTTS on startup.")

def sanitize_filename(filename):
    """Remove special characters from filename"""
    filename = re.sub(r'[^a-zA-Z0-9_\-]', '', filename)
    filename = re.sub(r'_+', '_', filename)
    return filename[:50]

def generate_audio_playht(script, output_path, voice_id='James'):
    """Generate audio using PlayHT TTS"""
    
    if not PLAYHT_AVAILABLE:
        raise Exception("PlayHT not available")
    
    try:
        print(f"🎤 Generating audio with PlayHT...")
        print(f"   Voice: {voice_id}")
        print(f"   Text length: {len(script)} characters")
        
        # Create output directory
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate audio stream from PlayHT
        output = playht.generate(
            text=script,
            voice=voice_id,
            output_format="mp3"
        )
        
        # Save audio file
        with open(str(output_path), 'wb') as f:
            for chunk in output:
                f.write(chunk)
        
        print(f"✅ Audio saved: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ PlayHT TTS error: {e}")
        raise

def generate_audio_gtts(script, output_path, voice_id='en'):
    """Generate audio using gTTS (Google Text-to-Speech)"""
    
    if not GTTS_AVAILABLE:
        raise Exception("gTTS not available")
    
    try:
        print(f"🎤 Generating audio with gTTS...")
        print(f"   Language: {voice_id}")
        print(f"   Text length: {len(script)} characters")
        
        # Create output directory
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate speech from text
        from gtts import gTTS
        tts = gTTS(text=script, lang=voice_id, slow=False)
        tts.save(str(output_path))
        
        print(f"✅ Audio saved: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ gTTS error: {e}")
        raise

def generate_audio(script, output_path, voice_id='en'):
    """Generate audio with automatic fallback"""
    
    # Try PlayHT first
    if PLAYHT_AVAILABLE:
        try:
            playht_voice = PLAYHT_VOICE_MAPPING.get(voice_id, 'James')
            return generate_audio_playht(script, output_path, playht_voice)
        except Exception as e:
            print(f"⚠️ PlayHT failed: {e}")
            print("🔄 Falling back to gTTS...")
    
    # Fallback to gTTS
    if GTTS_AVAILABLE:
        try:
            gtts_lang = GTTS_VOICE_MAPPING.get(voice_id, 'en')
            return generate_audio_gtts(script, output_path, gtts_lang)
        except Exception as e:
            print(f"❌ gTTS failed: {e}")
            raise Exception("All TTS engines failed")
    
    raise Exception("No TTS engine available")

def get_audio_duration(audio_path):
    """Get audio duration using ffprobe"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
             '-of', 'default=noprint_wrappers=1:nokey=1:noprint_wrappers=1', 
             str(audio_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        return float(result.stdout.strip())
    except:
        print("⚠️ Could not determine audio duration, using fallback")
        return 60

def generate_video_background(data):
    global progress_state
    
    try:
        # Script
        progress_state['status'] = 'Generating script...'
        progress_state['progress'] = 10
        
        result = pro_script_generator.generate_story(
            topic=data['topic'],
            story_type=data['story_type'],
            duration_minutes=data['duration'],
            num_scenes=10
        )
        
        # Images
        progress_state['status'] = 'Generating images...'
        progress_state['progress'] = 30
        
        image_gen = create_image_generator(data['image_style'], data['story_type'])
        characters = {char: f"{char}, character" for char in result.get('characters', [])[:3]}
        images = image_gen.generate_batch(result['scenes'], characters)
        image_paths = [Path(img['filepath']) for img in images if img]
        
        # Voice - Use TTS with automatic fallback
        progress_state['status'] = f'Generating voice with {TTS_ENGINE}...'
        progress_state['progress'] = 60
        
        try:
            voice_id = data.get('voice_id', 'male_narrator_deep')
            audio_path = generate_audio(
                result['script'],
                Path("output/temp/narration.mp3"),
                voice_id
            )
            
            # Get audio duration
            audio_duration = get_audio_duration(audio_path)
                
        except Exception as e:
            print(f"❌ Audio generation failed: {e}")
            raise
        
        # Calculate durations
        time_per_image = audio_duration / len(image_paths) if image_paths else 5
        durations = [time_per_image] * len(image_paths)
        
        # Video
        progress_state['status'] = 'Compiling video...'
        progress_state['progress'] = 80
        
        compiler = FFmpegCompiler()
        
        # Sanitize filename
        safe_topic = sanitize_filename(data['topic'])
        output_filename = f"{safe_topic}_video.mp4"
        video_path = compiler.create_video(
            image_paths,
            audio_path,
            Path(f"output/videos/{output_filename}"),
            durations
        )
        
        progress_state['progress'] = 100
        progress_state['status'] = 'complete'
        progress_state['video_path'] = output_filename
        print(f"✅ Video completed: {output_filename}")
        
    except Exception as e:
        progress_state['status'] = 'error'
        progress_state['error'] = str(e)
        print(f"❌ ERROR: {e}")

# Health Check Endpoint
@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify({
        'status': 'ok',
        'message': 'API Server is running',
        'tts_engine': TTS_ENGINE or 'not configured',
        'playht_available': 'yes' if PLAYHT_AVAILABLE else 'no',
        'gtts_available': 'yes' if GTTS_AVAILABLE else 'no'
    }), 200

# Generate Video Endpoint
@app.route('/api/generate-video', methods=['POST', 'OPTIONS'])
def generate_video():
    if request.method == 'OPTIONS':
        return '', 204
    
    if not TTS_ENGINE:
        return jsonify({'error': 'No TTS engine available. Install gTTS: pip install gtts'}), 500
    
    data = request.json
    global progress_state
    progress_state = {'status': 'starting', 'progress': 0, 'video_path': None, 'error': None}
    
    threading.Thread(target=generate_video_background, args=(data,)).start()
    return jsonify({'success': True, 'message': f'Video generation started with {TTS_ENGINE}'}), 200

# Progress Endpoint
@app.route('/api/progress', methods=['GET', 'OPTIONS'])
def get_progress():
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify(progress_state), 200

# Video Stream Endpoint
@app.route('/api/video/<path:filename>', methods=['GET', 'OPTIONS'])
def stream_video(filename):
    if request.method == 'OPTIONS':
        return '', 204
    
    video_path = f"output/videos/{filename}"
    return send_file(video_path, mimetype='video/mp4'), 200

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 API Server Running: http://localhost:5000")
    print("="*70)
    
    if TTS_ENGINE:
        print(f"\n✅ TTS Engine: {TTS_ENGINE}")
        if PLAYHT_AVAILABLE:
            print("   └─ PlayHT (Premium voices)")
        if GTTS_AVAILABLE:
            print("   └─ gTTS (Free, fallback)")
    else:
        print("\n⚠️  No TTS engine configured!")
        print("\nQuick fix:")
        print("   pip install gtts")
        print("\nOptional: Add PlayHT for premium voices:")
        print("   pip install playht")
        print("   export PLAYHT_USER_ID='your_id'")
        print("   export PLAYHT_API_KEY='your_key'")
    
    print("\n" + "="*70 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)