# -*- coding: utf-8 -*-
"""
🎬 AI Video Generator - UPDATED FOR BACKEND INTEGRATION
Receives requests from backend with script + image prompts + options
Uses Coqui TTS + SDXL + FFmpeg
"""

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 1: INSTALL EVERYTHING
# ═══════════════════════════════════════════════════════════════════════════════
import sys
print(f"Python: {sys.version}\n")

if sys.version_info >= (3, 12):
    print("Installing Python 3.10...")
    !pip install -q condacolab
    import condacolab
    condacolab.install()
    print("⚠️  Runtime restarting - Run this cell again after restart!")
else:
    print("Installing packages...\n")
    !apt-get update -qq && apt-get install -y -qq ffmpeg
    !pip install -q flask flask-cors pyngrok requests torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    !pip install -q TTS soundfile numpy scipy diffusers transformers accelerate safetensors pillow opencv-python-headless
    print("\n✅ All installed! Run Cell 2")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 2: IMPORTS
# ═══════════════════════════════════════════════════════════════════════════════
import sys, subprocess

def check(pkg, imp=None):
    try: __import__(imp or pkg.replace('-','_'))
    except: subprocess.run([sys.executable,'-m','pip','install','-q',pkg]); print(f"Installed {pkg}")

check('flask'); check('flask-cors','flask_cors'); check('pyngrok'); check('torch'); check('pillow','PIL')

import torch, json, io, gc, time, base64
from pathlib import Path
from PIL import Image
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pyngrok import ngrok
from threading import Thread

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"GPU: {torch.cuda.get_device_name(0) if device=='cuda' else 'None'}")

output_dir = Path('/content/outputs')
output_dir.mkdir(exist_ok=True)
print("✅ Ready")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 3: SDXL IMAGE MODEL (NOT FLUX!)
# ═══════════════════════════════════════════════════════════════════════════════
print("Loading SDXL model...")
from diffusers import StableDiffusionXLPipeline

img_pipeline = None

def load_sdxl():
    global img_pipeline
    if not img_pipeline:
        print("Loading DreamShaper XL (SDXL model)...")
        img_pipeline = StableDiffusionXLPipeline.from_pretrained(
            "Lykon/dreamshaper-xl-1-0",
            torch_dtype=torch.float16,
            variant="fp16"
        ).to(device)
        img_pipeline.enable_xformers_memory_efficient_attention()
        print("✅ SDXL model loaded!")
    return img_pipeline

def gen_img(prompt):
    """Generate image using SDXL"""
    p = load_sdxl()
    return p(
        prompt=prompt,
        num_inference_steps=25,
        height=1024,
        width=1024
    ).images[0]

print("✅ SDXL ready")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 4: COQUI TTS (NOT EDGE-TTS!)
# ═══════════════════════════════════════════════════════════════════════════════
import sys
import subprocess

# Check Python version and install correct TTS
print(f"Python version: {sys.version_info.major}.{sys.version_info.minor}")

try:
    import TTS
    print("TTS already installed")
except:
    if sys.version_info >= (3, 12):
        # Python 3.12+ needs the maintained fork
        print("Installing coqui-tts (Python 3.12 compatible fork)...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'coqui-tts', 'soundfile'], check=True)
    else:
        # Python 3.9-3.11 uses original
        print("Installing TTS...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'TTS', 'soundfile'], check=True)
    print("TTS installed!")

tts_model = None

# Voice mapping for Coqui VCTK
VOICES = {
    'guy': 'p226',
    'adam': 'p226',
    'matthew': 'p226',
    'aria': 'p229',
    'sarah': 'p231',
    'nicole': 'p233',
    'jenny': 'p228',
    'emma': 'p230'
}

def get_voice(v):
    return VOICES.get(v.lower() if isinstance(v, str) else 'aria', 'p229')

def load_tts():
    global tts_model
    if not tts_model:
        from TTS.api import TTS as TTSModel
        print("Loading Coqui TTS model...")
        tts_model = TTSModel("tts_models/en/vctk/vits").to(device)
        print("✅ Coqui TTS model loaded!")
    return tts_model

def gen_voice(text, voice, path):
    """Generate voice using Coqui TTS"""
    load_tts().tts_to_file(
        text=text,
        speaker=get_voice(voice),
        file_path=path
    )
    return path

print("✅ Coqui TTS ready")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 5: AUTO-CAPTIONS (TIKTOK STYLE)
# ═══════════════════════════════════════════════════════════════════════════════
def create_caption_filter(script_text, audio_duration):
    """Create FFmpeg drawtext filter for word-by-word captions"""

    words = script_text.split()
    time_per_word = audio_duration / len(words)

    filters = []
    current_time = 0.0

    for word in words:
        # Escape special characters
        word_escaped = word.replace("'", "\\'").replace('"', '\\"')

        # TikTok-style caption
        filter_text = (
            f"drawtext="
            f"text='{word_escaped}':"
            f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            f"fontsize=72:"
            f"fontcolor=white:"
            f"borderw=4:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h-150:"
            f"enable='between(t,{current_time:.3f},{current_time + time_per_word:.3f})'"
        )
        filters.append(filter_text)

        current_time += time_per_word

    return ','.join(filters) if filters else None

print("✅ Caption system ready")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 6: FLASK SERVER
# ═══════════════════════════════════════════════════════════════════════════════
app = Flask(__name__)
CORS(app)

@app.route('/health')
def health():
    return jsonify({
        "ok": True,
        "gpu": device == 'cuda',
        "model": "SDXL DreamShaper XL",
        "tts": "Coqui TTS (VCTK)",
        "status": "ready"
    })

@app.route('/generate_complete_video', methods=['POST'])
def gen_video():
    """
    Receive from backend:
    - script (from Gemini Server 1)
    - image_prompts (from Gemini Server 2)
    - options (all settings)
    """
    try:
        data = request.get_json(force=True)
        import uuid
        jid = str(uuid.uuid4())
        wd = output_dir / jid
        wd.mkdir()

        print(f"\n{'='*60}")
        print(f"🎬 NEW VIDEO REQUEST")
        print(f"{'='*60}")
        print(f"Job ID: {jid}")

        # Extract data from backend
        script = data.get('script', '')
        image_prompts = data.get('image_prompts', [])
        options = data

        print(f"Script: {len(script)} chars")
        print(f"Image Prompts: {len(image_prompts)}")
        print(f"Options:")
        print(f"  - Voice: {options.get('voice', 'aria')}")
        print(f"  - Zoom: {options.get('zoom_intensity', 5.0)}%")
        print(f"  - Auto-Captions: {options.get('auto_captions', False)}")
        print(f"  - Filter: {options.get('color_filter', 'none')}")

        # ═══════════════════════════════════════════════════════════
        # STEP 1: Generate Images using SDXL
        # ═══════════════════════════════════════════════════════════
        print(f"\n🎨 Generating {len(image_prompts)} images with SDXL...")

        for i, prompt in enumerate(image_prompts):
            print(f"  Image {i+1}/{len(image_prompts)}: {prompt[:50]}...")
            img = gen_img(prompt)
            img.save(wd / f"{i:04d}.png")
            print(f"    ✅ Saved")

        # ═══════════════════════════════════════════════════════════
        # STEP 2: Generate Voice using Coqui TTS
        # ═══════════════════════════════════════════════════════════
        print(f"\n🎤 Generating voice with Coqui TTS...")

        voice_id = options.get('voice', 'aria')
        ap = wd / "voice.wav"
        gen_voice(script, voice_id, str(ap))

        print(f"  ✅ Voice generated")

        # Get audio duration
        import soundfile as sf
        audio_data, sample_rate = sf.read(str(ap))
        audio_duration = len(audio_data) / sample_rate
        print(f"  Duration: {audio_duration:.1f} seconds")

        # ═══════════════════════════════════════════════════════════
        # STEP 3: Compile Video with FFmpeg
        # ═══════════════════════════════════════════════════════════
        print(f"\n🎬 Compiling video with FFmpeg...")

        op = wd / "final.mp4"

        # Build video filter
        filters = []

        # Zoom effect
        zoom_enabled = options.get('zoom_effect', True)
        zoom_intensity = float(options.get('zoom_intensity', 5.0))

        if zoom_enabled:
            # Convert percentage to zoom rate
            time_per_image = audio_duration / len(image_prompts)
            zoom_rate = (zoom_intensity / 100) / time_per_image
            max_zoom = 1.0 + (zoom_intensity / 100)

            zoom_filter = (
                f"scale=1920:1080,"
                f"zoompan=z='min(zoom+{zoom_rate},{max_zoom})':d=1:"
                f"x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):s=1920x1080,"
                f"fps=30"
            )
            filters.append(zoom_filter)
        else:
            filters.append("scale=1920:1080,fps=30")

        # Auto-captions
        if options.get('auto_captions', False):
            print(f"  Adding TikTok-style captions...")
            caption_filter = create_caption_filter(script, audio_duration)
            if caption_filter:
                filters.append(caption_filter)

        # Combine filters
        vf = ','.join(filters)

        # Run FFmpeg
        import subprocess
        cmd = [
            'ffmpeg', '-y',
            '-hwaccel', 'cuda',
            '-framerate', '30',
            '-pattern_type', 'glob',
            '-i', str(wd / '*.png'),
            '-i', str(ap),
            '-vf', vf,
            '-c:v', 'h264_nvenc',
            '-b:v', '10M',
            '-c:a', 'aac',
            '-s', '1920x1080',
            '-shortest',
            str(op)
        ]

        subprocess.run(cmd, check=True, capture_output=True)

        print(f"  ✅ Video compiled!")
        print(f"  File: {op}")
        print(f"  Size: {op.stat().st_size / 1024 / 1024:.1f} MB")

        # ═══════════════════════════════════════════════════════════
        # DONE!
        # ═══════════════════════════════════════════════════════════
        print(f"\n{'='*60}")
        print(f"✅ VIDEO COMPLETE!")
        print(f"{'='*60}\n")

        return jsonify({
            "success": True,
            "job_id": jid
        })

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/status/<jid>')
def status(jid):
    """Check if video is ready"""
    v = output_dir / jid / "final.mp4"
    if v.exists():
        return jsonify({
            "status": "complete",
            "progress": 100,
            "message": "Video ready!"
        })
    else:
        return jsonify({
            "status": "processing",
            "progress": 50,
            "message": "Generating..."
        })

@app.route('/download/<jid>')
def dl(jid):
    """Download completed video"""
    v = output_dir / jid / "final.mp4"
    return send_file(str(v), mimetype='video/mp4') if v.exists() else (jsonify({"error": "not found"}), 404)

print("✅ Server ready")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 7: START SERVER
# ═══════════════════════════════════════════════════════════════════════════════

YOUR_NGROK_TOKEN = "35HuufK0IT26RER84mcvIbRjrog_7grjZvuDXtRPYL5hWLNCK"

# Start ngrok tunnel
from pyngrok import ngrok
ngrok.set_auth_token(YOUR_NGROK_TOKEN)
url = ngrok.connect(5001)

print("\n" + "="*80)
print(f"🌐 COLAB SERVER RUNNING AT: {url}")
print("="*80)
print(f"\n✅ UPDATED ARCHITECTURE:")
print(f"   Backend → Sends script + image_prompts + options → This Colab server")
print(f"   This server:")
print(f"     1. Generates images with SDXL (not Flux)")
print(f"     2. Generates voice with Coqui TTS (not Edge-TTS)")
print(f"     3. Compiles video with FFmpeg (with zoom + captions)")
print(f"     4. Returns video to backend")
print(f"\n🔧 COPY THIS URL TO BACKEND:")
print(f"   POST http://localhost:5000/api/set-colab-url")
print(f"   Body: {{'url': '{url}'}}")
print("="*80 + "\n")

# Start Flask server
try:
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
except KeyboardInterrupt:
    print("\n✅ Server stopped")
