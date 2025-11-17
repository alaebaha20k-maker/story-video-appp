"""
🔌 NEW API SERVER - Orchestrates Gemini Server 1 → Server 2 → Colab Flow
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pathlib import Path
import threading
import uuid

# Import our servers
from src.ai.gemini_server_1 import gemini_server_1
from src.ai.gemini_server_2 import gemini_server_2
from src.colab.colab_client import colab_client

app = Flask(__name__)

# CORS for all origins
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Global state for progress tracking
progress_state = {
    'status': 'ready',
    'progress': 0,
    'message': '',
    'video_path': None,
    'error': None,
    'job_id': None
}

# Colab URL (auto-loaded from file or set via API)
COLAB_URL = None

# Output directory
OUTPUT_DIR = Path("output/videos")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# AUTO-LOAD COLAB URL FROM FILE
# ═══════════════════════════════════════════════════════════════

def extract_clean_url(url_string: str) -> str:
    """
    Extract clean ngrok URL from various formats:
    - "https://contemplable-suzy-unfussing.ngrok-free.dev" → as-is
    - "NgrokTunnel: "https://..." -> "http://..." → extract https URL
    - Lines from file with markdown → extract URL
    """
    import re

    # Remove markdown formatting
    url_string = url_string.replace('**', '').strip()

    # If it looks like the NgrokTunnel format, extract the https URL
    if 'NgrokTunnel:' in url_string or '->' in url_string:
        # Extract https URL from: NgrokTunnel: "https://..." -> "http://..."
        match = re.search(r'https://[a-zA-Z0-9\-\.]+\.ngrok-free\.dev', url_string)
        if match:
            return match.group()

    # If it's already a clean URL
    if url_string.startswith('http'):
        return url_string

    # Try to find any ngrok URL in the string
    match = re.search(r'https://[a-zA-Z0-9\-\.]+\.ngrok-free\.dev', url_string)
    if match:
        return match.group()

    return url_string


def load_colab_url_from_file():
    """
    Try to auto-load Colab URL from COLAB_NGROK_URL.txt
    This runs at startup to avoid manual configuration
    """
    global COLAB_URL

    # Try multiple possible locations
    possible_paths = [
        Path(__file__).parent.parent / "COLAB_NGROK_URL.txt",
        Path("../COLAB_NGROK_URL.txt"),
        Path("COLAB_NGROK_URL.txt"),
    ]

    for file_path in possible_paths:
        try:
            if file_path.exists():
                content = file_path.read_text()

                # Extract URL from file (handles markdown, comments, etc.)
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue

                    # Extract clean URL
                    clean_url = extract_clean_url(line)

                    # Validate it's a proper URL
                    if clean_url.startswith('http'):
                        COLAB_URL = clean_url
                        colab_client.set_url(clean_url)

                        # Test connection
                        is_connected = colab_client.check_health()

                        print(f"✅ Auto-loaded Colab URL from: {file_path.name}")
                        print(f"   URL: {clean_url}")
                        print(f"   Connected: {'✅ Yes' if is_connected else '❌ No (might be down)'}")
                        return True
        except Exception as e:
            continue

    print(f"⚠️  Colab URL not found in file")
    print(f"   You'll need to set it via: POST /api/set-colab-url")
    return False


# ═══════════════════════════════════════════════════════════════
# HEALTH & CONFIG
# ═══════════════════════════════════════════════════════════════

@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    """Health check endpoint"""
    if request.method == 'OPTIONS':
        return '', 204

    return jsonify({
        'status': 'ok',
        'message': 'Backend server running',
        'gemini_server_1': 'ready',
        'gemini_server_2': 'ready',
        'colab_connected': colab_client.check_health() if COLAB_URL else False,
        'colab_url': COLAB_URL
    }), 200


@app.route('/api/set-colab-url', methods=['POST', 'OPTIONS'])
def set_colab_url():
    """
    Set Colab ngrok URL
    Accepts various formats:
    - Clean URL: https://your-url.ngrok-free.dev
    - NgrokTunnel format: NgrokTunnel: "https://..." -> "http://..."
    """
    if request.method == 'OPTIONS':
        return '', 204

    global COLAB_URL

    data = request.json
    raw_url = data.get('url', '').strip()

    if not raw_url:
        return jsonify({'error': 'URL required'}), 400

    # Extract clean URL from various formats
    clean_url = extract_clean_url(raw_url)

    if not clean_url.startswith('http'):
        return jsonify({
            'error': 'Invalid URL format',
            'received': raw_url,
            'tip': 'Use format: https://your-url.ngrok-free.dev'
        }), 400

    # Set URL
    colab_client.set_url(clean_url)
    COLAB_URL = clean_url

    # Test connection
    is_connected = colab_client.check_health()

    return jsonify({
        'success': True,
        'raw_input': raw_url if raw_url != clean_url else None,
        'clean_url': clean_url,
        'connected': is_connected,
        'message': 'Connected to Colab!' if is_connected else 'URL set but cannot connect'
    }), 200


# ═══════════════════════════════════════════════════════════════
# TEMPLATE ANALYSIS
# ═══════════════════════════════════════════════════════════════

@app.route('/api/analyze-script', methods=['POST', 'OPTIONS'])
def analyze_script_endpoint():
    """
    Step 1: Analyze example script with Gemini Server 1
    Extract structure and hook style

    NOTE: If quota is exceeded, returns default template instead of failing
    """
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.json
        script_content = data.get('scriptContent', '')
        script_type = data.get('scriptType', 'story')

        if not script_content or len(script_content) < 100:
            return jsonify({'error': 'Script too short (min 100 chars)'}), 400

        print(f"\n📊 Analyzing template script ({len(script_content)} chars)...")

        try:
            # Use Gemini Server 1 to analyze
            template = gemini_server_1.analyze_template_script(
                script_content,
                script_type
            )

            print(f"✅ Template extracted successfully")
            return jsonify(template), 200

        except Exception as gemini_error:
            error_str = str(gemini_error)

            # Check if it's a quota error
            if '429' in error_str or 'quota' in error_str.lower() or 'rate limit' in error_str.lower():
                print(f"⚠️ Gemini quota exceeded - returning default template")
                print(f"   Error: {error_str[:200]}...")

                # Return a basic default template based on script content
                default_template = {
                    "hookExample": script_content[:200] + "...",
                    "hookStyle": "engaging",
                    "setupLength": 20,
                    "riseLength": 40,
                    "climaxLength": 30,
                    "endLength": 10,
                    "tone": ["engaging", "narrative", "dramatic"],
                    "keyPatterns": ["Descriptive storytelling", "First-person perspective"],
                    "sentenceVariation": "Mix of short and long sentences",
                    "quotaExceeded": True,  # Flag to indicate fallback was used
                    "message": "Using default template - Gemini quota exceeded"
                }

                return jsonify(default_template), 200
            else:
                # Other error - re-raise
                raise

    except Exception as e:
        print(f"❌ Template analysis failed: {e}")
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════
# VIDEO GENERATION - NEW FLOW
# ═══════════════════════════════════════════════════════════════

def generate_video_background(data):
    """
    Background task: Orchestrate complete generation flow
    Gemini Server 1 → Gemini Server 2 → Colab
    """
    global progress_state

    try:
        print(f"\n{'='*60}")
        print(f"🎬 NEW GENERATION FLOW STARTED")
        print(f"{'='*60}")

        # Extract all options
        topic = data.get('topic', 'Untitled')
        story_type = data.get('story_type') or data.get('storytype', 'scary_horror')
        duration = int(data.get('duration', 10))
        num_scenes = int(data.get('num_scenes', 10))
        image_style = data.get('image_style', 'cinematic_film')
        template = data.get('template')  # From template analysis

        print(f"\n📋 Generation Options:")
        print(f"   Topic: {topic}")
        print(f"   Story Type: {story_type}")
        print(f"   Duration: {duration} min")
        print(f"   Scenes/Images: {num_scenes}")
        print(f"   Image Style: {image_style}")
        print(f"   Template: {'Yes' if template else 'No'}")
        print(f"   Voice: {data.get('voice_id', 'aria')}")
        print(f"   Zoom: {data.get('zoom_intensity', 5.0)}%")
        print(f"   Auto-Captions: {data.get('auto_captions', False)}")

        # ═══════════════════════════════════════════════════════════
        # STEP 1: Generate Script with Gemini Server 1
        # ═══════════════════════════════════════════════════════════
        progress_state['status'] = 'generating_script'
        progress_state['progress'] = 10
        progress_state['message'] = 'Gemini Server 1: Generating script...'

        print(f"\n{'='*60}")
        print(f"📝 STEP 1/4: GEMINI SERVER 1 - Script Generation")
        print(f"{'='*60}")

        script = gemini_server_1.generate_script_from_template(
            topic=topic,
            story_type=story_type,
            template=template,
            duration_minutes=duration,
            num_scenes=num_scenes
        )

        print(f"\n✅ Script generated!")
        print(f"   Length: {len(script)} chars")
        print(f"   Words: ~{len(script.split())}")
        print(f"   Preview: {script[:100]}...")

        # ═══════════════════════════════════════════════════════════
        # STEP 2: Generate Image Prompts with Gemini Server 2
        # ═══════════════════════════════════════════════════════════
        progress_state['status'] = 'generating_image_prompts'
        progress_state['progress'] = 30
        progress_state['message'] = 'Gemini Server 2: Generating image prompts...'

        print(f"\n{'='*60}")
        print(f"🎨 STEP 2/4: GEMINI SERVER 2 - Image Prompts")
        print(f"{'='*60}")

        # Use chunked generation for large numbers of images
        if num_scenes > 15:
            image_prompts = gemini_server_2.generate_image_prompts_chunked(
                script=script,
                num_images=num_scenes,
                story_type=story_type,
                image_style=image_style,
                chunk_size=10
            )
        else:
            image_prompts = gemini_server_2.generate_image_prompts(
                script=script,
                num_images=num_scenes,
                story_type=story_type,
                image_style=image_style
            )

        print(f"\n✅ Image prompts generated!")
        print(f"   Count: {len(image_prompts)}")
        print(f"   First prompt: {image_prompts[0][:60]}...")

        # ═══════════════════════════════════════════════════════════
        # STEP 3: Send to Colab for Video Generation
        # ═══════════════════════════════════════════════════════════
        progress_state['status'] = 'sending_to_colab'
        progress_state['progress'] = 50
        progress_state['message'] = 'Sending to Google Colab...'

        print(f"\n{'='*60}")
        print(f"🚀 STEP 3/4: SENDING TO GOOGLE COLAB")
        print(f"{'='*60}")

        if not COLAB_URL:
            raise Exception("Colab URL not set! Use /api/set-colab-url first.")

        # Prepare all options for Colab
        colab_options = {
            'topic': topic,
            'story_type': story_type,
            'duration': duration,
            'image_style': image_style,
            'voice_id': data.get('voice_id', 'aria'),
            'voice_speed': float(data.get('voice_speed', 1.0)),
            'zoom_effect': data.get('zoom_effect', True),
            'zoom_intensity': float(data.get('zoom_intensity', 5.0)),
            'auto_captions': data.get('auto_captions', False),
            'color_filter': data.get('color_filter', 'none'),
        }

        # Send to Colab
        result = colab_client.generate_complete_video(
            script=script,
            image_prompts=image_prompts,
            options=colab_options
        )

        job_id = result.get('job_id')
        progress_state['job_id'] = job_id

        print(f"\n✅ Sent to Colab!")
        print(f"   Job ID: {job_id}")

        # ═══════════════════════════════════════════════════════════
        # STEP 4: Wait for Colab to Complete
        # ═══════════════════════════════════════════════════════════
        progress_state['status'] = 'colab_processing'
        progress_state['progress'] = 60
        progress_state['message'] = 'Colab: Generating images, voice, and video...'

        print(f"\n{'='*60}")
        print(f"⏳ STEP 4/4: WAITING FOR COLAB")
        print(f"{'='*60}")

        def update_progress(status):
            """Update our progress from Colab status"""
            colab_progress = status.get('progress', 60)
            # Map Colab 0-100 to our 60-95
            progress_state['progress'] = 60 + (colab_progress * 0.35)
            progress_state['message'] = status.get('message', 'Processing in Colab...')

        # Wait for completion
        final_status = colab_client.wait_for_completion(
            job_id=job_id,
            timeout_minutes=30,
            callback=update_progress
        )

        if final_status['status'] != 'complete':
            raise Exception(f"Colab failed: {final_status.get('message', 'Unknown error')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 5: Download Video from Colab
        # ═══════════════════════════════════════════════════════════
        progress_state['status'] = 'downloading'
        progress_state['progress'] = 95
        progress_state['message'] = 'Downloading video from Colab...'

        print(f"\n⬇️  Downloading video from Colab...")

        # Generate local filename
        import re
        safe_topic = re.sub(r'[^a-zA-Z0-9_\-]', '', topic)[:50]
        output_filename = f"{safe_topic}_{job_id[:8]}_video.mp4"
        output_path = OUTPUT_DIR / output_filename

        # Download
        success = colab_client.download_video(job_id, output_path)

        if not success:
            raise Exception("Failed to download video from Colab")

        # ═══════════════════════════════════════════════════════════
        # COMPLETE!
        # ═══════════════════════════════════════════════════════════
        progress_state['status'] = 'complete'
        progress_state['progress'] = 100
        progress_state['message'] = 'Complete!'
        progress_state['video_path'] = output_filename

        print(f"\n{'='*60}")
        print(f"✅ GENERATION COMPLETE!")
        print(f"{'='*60}")
        print(f"   Video: {output_filename}")
        print(f"   Size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
        print(f"   Location: {output_path}")
        print(f"{'='*60}\n")

    except Exception as e:
        progress_state['status'] = 'error'
        progress_state['error'] = str(e)
        progress_state['message'] = f'Error: {str(e)}'
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()


@app.route('/api/generate-video', methods=['POST', 'OPTIONS'])
def generate_video():
    """
    Main endpoint: Generate video with new flow
    Gemini 1 → Gemini 2 → Colab
    """
    if request.method == 'OPTIONS':
        return '', 204

    data = request.json

    # Validate required fields
    if not data.get('topic'):
        return jsonify({'error': 'Topic is required'}), 400

    if not COLAB_URL:
        return jsonify({'error': 'Colab URL not set. Use /api/set-colab-url first.'}), 400

    # Reset progress
    global progress_state
    progress_state = {
        'status': 'starting',
        'progress': 0,
        'message': 'Starting generation...',
        'video_path': None,
        'error': None,
        'job_id': None
    }

    # Start background thread
    threading.Thread(target=generate_video_background, args=(data,), daemon=True).start()

    return jsonify({
        'success': True,
        'message': 'Generation started with new flow (Gemini 1 → Gemini 2 → Colab)'
    }), 200


@app.route('/api/progress', methods=['GET', 'OPTIONS'])
def get_progress():
    """Get current generation progress"""
    if request.method == 'OPTIONS':
        return '', 204
    return jsonify(progress_state), 200


@app.route('/api/video/<path:filename>', methods=['GET', 'OPTIONS'])
def stream_video(filename):
    """Stream completed video"""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        video_path = OUTPUT_DIR / filename
        if not video_path.exists():
            return jsonify({'error': 'Video not found'}), 404
        return send_file(str(video_path), mimetype='video/mp4')
    except FileNotFoundError:
        return jsonify({'error': 'Video not found'}), 404


# ═══════════════════════════════════════════════════════════════
# VOICES (for frontend compatibility)
# ═══════════════════════════════════════════════════════════════

@app.route('/api/voices', methods=['GET', 'OPTIONS'])
def list_voices():
    """List available voices (Coqui TTS in Colab)"""
    if request.method == 'OPTIONS':
        return '', 204

    # These will be used by Coqui TTS in Colab
    voices = {
        'aria': {'engine': 'coqui', 'name': 'Aria', 'gender': 'female', 'style': 'Natural & Warm'},
        'guy': {'engine': 'coqui', 'name': 'Guy', 'gender': 'male', 'style': 'Natural & Clear'},
        'jenny': {'engine': 'coqui', 'name': 'Jenny', 'gender': 'female', 'style': 'Cheerful'},
        'matthew': {'engine': 'coqui', 'name': 'Matthew', 'gender': 'male', 'style': 'Deep & Professional'},
    }

    return jsonify({
        'voices': voices,
        'engine': 'coqui_tts',
        'total': len(voices),
        'location': 'Google Colab'
    }), 200


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔥 NEW VIDEO GENERATOR - Gemini 1 → Gemini 2 → Colab Flow!")
    print("="*60)
    print(f"📍 Backend URL: http://localhost:5000")
    print(f"")
    print(f"🎯 NEW ARCHITECTURE:")
    print(f"   1️⃣  Gemini Server 1: Script generation (no image prompts)")
    print(f"   2️⃣  Gemini Server 2: Image prompt generation")
    print(f"   3️⃣  Google Colab: Image/voice/video generation")
    print(f"")
    print(f"📝 FEATURES:")
    print(f"   ✅ Template script analysis")
    print(f"   ✅ High-quality script generation")
    print(f"   ✅ SDXL image prompts from separate server")
    print(f"   ✅ All processing in Colab (Coqui TTS + SDXL + FFmpeg)")
    print(f"   ✅ Configurable zoom percentage")
    print(f"   ✅ TikTok-style auto-captions")
    print(f"")

    # Auto-load Colab URL from file
    print(f"🔍 Checking for Colab URL...")
    url_loaded = load_colab_url_from_file()

    if not url_loaded:
        print(f"")
        print(f"⚠️  COLAB URL NOT SET:")
        print(f"   Option 1: Add to COLAB_NGROK_URL.txt in project root")
        print(f"   Option 2: POST /api/set-colab-url with your ngrok URL")
        print(f"   Example: https://your-url.ngrok-free.dev")
    print(f"")
    print(f"🔧 ENDPOINTS:")
    print(f"   POST /api/set-colab-url - Set Colab ngrok URL")
    print(f"   POST /api/analyze-script - Analyze template (Server 1)")
    print(f"   POST /api/generate-video - Generate (1→2→Colab)")
    print(f"   GET  /api/progress - Check progress")
    print(f"   GET  /api/video/<file> - Download video")
    print(f"   GET  /health - System status")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
