"""
🚀 GOOGLE COLAB - COMPLETE CODE (READY TO PASTE!)
==================================================

✅ T4 GPU Enabled (you already did this!)
✅ Ngrok Token Configured (your token is in the code)
✅ All dependencies included

INSTRUCTIONS:
1. Copy ALL the code below
2. Paste into Google Colab cells (run each cell in order)
3. Wait for ngrok URL
4. Update backend config.py with the URL
5. Start your backend and frontend

Let's go! 🚀
"""

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 1: INSTALL DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════════

print("📦 Installing dependencies...\n")

# Core dependencies
!pip install -q flask flask-cors pyngrok

# Kokoro TTS
!pip install -q kokoro-onnx

# SDXL-Turbo (Diffusers)
!pip install -q diffusers transformers accelerate

# Torch (GPU support)
!pip install -q torch torchvision --index-url https://download.pytorch.org/whl/cu121

print("\n✅ Dependencies installed!")


# ═══════════════════════════════════════════════════════════════════════════════
# CELL 2: SETUP GPU & IMPORTS
# ═══════════════════════════════════════════════════════════════════════════════

import os
import gc
import torch
import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pyngrok import ngrok
from pathlib import Path
from threading import Thread

# GPU Detection
if torch.cuda.is_available():
    device = 'cuda'
    gpu_name = torch.cuda.get_device_name(0)
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f"✅ GPU ENABLED: {gpu_name}")
    print(f"💾 GPU Memory: {gpu_memory:.1f} GB")
    print(f"🔥 CUDA Version: {torch.version.cuda}")
else:
    device = 'cpu'
    print("⚠️  WARNING: GPU NOT DETECTED - Running on CPU (SLOW!)")
    print("⚠️  Please enable GPU: Runtime → Change runtime type → GPU")

print(f"\n🚀 Device: {device}")

# Create output directory
output_dir = Path('/content/outputs')
output_dir.mkdir(exist_ok=True)

print(f"📁 Output directory: {output_dir}")


# ═══════════════════════════════════════════════════════════════════════════════
# CELL 3: MEMORY MANAGEMENT (On-Demand Model Loading)
# ═══════════════════════════════════════════════════════════════════════════════

# Global model holders (loaded on-demand)
tts_pipeline = None
img_pipeline = None

def clear_gpu_memory():
    """Clear GPU memory to make room for other models"""
    global tts_pipeline, img_pipeline

    if tts_pipeline is not None:
        del tts_pipeline
        tts_pipeline = None
        print("   🗑️  Unloaded TTS model")

    if img_pipeline is not None:
        del img_pipeline
        img_pipeline = None
        print("   🗑️  Unloaded Image model")

    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

def load_tts_model():
    """Load Kokoro TTS model (unload image model first)"""
    global tts_pipeline, img_pipeline

    if tts_pipeline is not None:
        return tts_pipeline

    print("\n🎤 Loading Kokoro TTS...")

    # Unload image model if loaded
    if img_pipeline is not None:
        print("   ⚠️  Unloading image model to free memory...")
        clear_gpu_memory()

    from kokoro import KPipeline
    tts_pipeline = KPipeline(lang_code='a')  # 'a' = American English

    print("   ✅ Kokoro TTS loaded!")
    return tts_pipeline

def load_image_model():
    """Load SDXL-Turbo model (unload TTS model first)"""
    global tts_pipeline, img_pipeline

    if img_pipeline is not None:
        return img_pipeline

    print("\n🎨 Loading SDXL-Turbo...")

    # Unload TTS model if loaded
    if tts_pipeline is not None:
        print("   ⚠️  Unloading TTS model to free memory...")
        clear_gpu_memory()

    from diffusers import AutoPipelineForText2Image

    img_pipeline = AutoPipelineForText2Image.from_pretrained(
        "stabilityai/sdxl-turbo",
        torch_dtype=torch.float16 if device == 'cuda' else torch.float32,
        variant="fp16" if device == 'cuda' else None
    )

    if device == 'cuda':
        img_pipeline = img_pipeline.to(device)
        # Memory optimization
        img_pipeline.enable_attention_slicing()
        img_pipeline.enable_vae_slicing()
        print("   ⚡ Memory optimization enabled (attention + VAE slicing)")

    print("   ✅ SDXL-Turbo loaded!")
    return img_pipeline

print("✅ Memory management functions ready!")
print("   📌 Models load on-demand to save memory")
print("   📌 Automatic unloading when switching models")


# ═══════════════════════════════════════════════════════════════════════════════
# CELL 4: VOICE MAPPING (Kokoro TTS)
# ═══════════════════════════════════════════════════════════════════════════════

# Voice mapping: Backend voice names → Kokoro voice codes
VOICE_MAPPING = {
    # Male voices (backend → Kokoro)
    'guy': 'af_adam',
    'adam_narration': 'af_adam',
    'adam_business': 'af_adam',
    'michael': 'af_michael',
    'george_gb': 'af_michael',
    'brian': 'af_adam',
    'andrew': 'af_adam',
    'christopher': 'af_michael',
    'george': 'af_michael',
    'joey': 'af_adam',

    # Female voices (backend → Kokoro)
    'aria': 'af_bella',
    'sarah_pro': 'af_sarah',
    'sarah_natural': 'af_sarah',
    'nicole': 'af_nicole',
    'emma_gb': 'af_bella',
    'jenny': 'af_nicole',
    'sara': 'af_sarah',
    'jane': 'af_nicole',
    'libby': 'af_bella',
    'emma': 'af_bella',
    'ivy': 'af_bella'
}

print("✅ Voice mapping configured:")
print("   Backend voices → Kokoro voices")
for key, value in list(VOICE_MAPPING.items())[:8]:
    print(f"   {key:20} → {value}")


# ═══════════════════════════════════════════════════════════════════════════════
# CELL 5: FLASK API SERVER
# ═══════════════════════════════════════════════════════════════════════════════

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────────────────────────
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'device': device,
        'gpu': torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None',
        'models_loaded': {
            'tts': tts_pipeline is not None,
            'image': img_pipeline is not None
        }
    })

# ─────────────────────────────────────────────────────────────────────────────
# Endpoint 1: Generate Audio (Kokoro TTS)
# ─────────────────────────────────────────────────────────────────────────────
@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    """Generate audio using Kokoro TTS"""
    try:
        data = request.json
        text = data.get('text', '')
        voice = data.get('voice', 'guy')
        speed = float(data.get('speed', 1.0))

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Map voice to Kokoro voice code
        kokoro_voice = VOICE_MAPPING.get(voice, 'af_adam')

        print(f"\n🎤 Generating audio: {voice} → {kokoro_voice}")
        print(f"   Text: {text[:50]}...")

        # Load TTS model
        pipeline = load_tts_model()

        # Generate audio
        audio_path = output_dir / f"audio_{hash(text)}.wav"

        pipeline(
            text,
            voice=kokoro_voice,
            speed=speed,
            output=str(audio_path)
        )

        print(f"   ✅ Audio generated: {audio_path.name}")

        return send_file(
            audio_path,
            mimetype='audio/wav',
            as_attachment=True,
            download_name=audio_path.name
        )

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return jsonify({'error': str(e)}), 500

# ─────────────────────────────────────────────────────────────────────────────
# Endpoint 2: Generate Single Image (SDXL-Turbo)
# ─────────────────────────────────────────────────────────────────────────────
@app.route('/generate_image', methods=['POST'])
def generate_image():
    """Generate a single image using SDXL-Turbo"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        style = data.get('style', 'cinematic')

        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400

        # Add style to prompt
        full_prompt = f"{prompt}, {style} style, high quality, detailed"

        print(f"\n🎨 Generating image...")
        print(f"   Prompt: {full_prompt[:70]}...")

        # Load image model
        pipeline = load_image_model()

        # Generate image
        image = pipeline(
            prompt=full_prompt,
            num_inference_steps=4,  # SDXL-Turbo optimized steps
            guidance_scale=0.0,     # SDXL-Turbo doesn't need guidance
            height=1080,
            width=1920
        ).images[0]

        # Save image
        image_path = output_dir / f"image_{hash(prompt)}.png"
        image.save(image_path)

        print(f"   ✅ Image generated: {image_path.name}")

        return send_file(
            image_path,
            mimetype='image/png',
            as_attachment=True,
            download_name=image_path.name
        )

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return jsonify({'error': str(e)}), 500

# ─────────────────────────────────────────────────────────────────────────────
# Endpoint 3: Generate Batch Images (SDXL-Turbo)
# ─────────────────────────────────────────────────────────────────────────────
@app.route('/generate_images_batch', methods=['POST'])
def generate_images_batch():
    """Generate multiple images in batch"""
    try:
        data = request.json
        scenes = data.get('scenes', [])
        style = data.get('style', 'cinematic')

        if not scenes:
            return jsonify({'error': 'No scenes provided'}), 400

        print(f"\n🎨 Generating {len(scenes)} images in batch...")

        # Load image model once
        pipeline = load_image_model()

        results = []

        for i, scene in enumerate(scenes, 1):
            prompt = scene.get('description', '')
            if not prompt:
                results.append({'error': 'No prompt', 'image_path': None})
                continue

            full_prompt = f"{prompt}, {style} style, high quality, detailed"

            print(f"   [{i}/{len(scenes)}] {prompt[:50]}...")

            try:
                # Generate image
                image = pipeline(
                    prompt=full_prompt,
                    num_inference_steps=4,
                    guidance_scale=0.0,
                    height=1080,
                    width=1920
                ).images[0]

                # Save image
                image_path = output_dir / f"batch_{i}_{hash(prompt)}.png"
                image.save(image_path)

                results.append({
                    'success': True,
                    'image_path': str(image_path),
                    'scene_index': i - 1
                })

                # Clear cache periodically
                if i % 5 == 0 and torch.cuda.is_available():
                    torch.cuda.empty_cache()

            except Exception as e:
                print(f"      ❌ Error: {e}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'scene_index': i - 1
                })

        print(f"   ✅ Batch complete: {len([r for r in results if r.get('success')])}/{len(scenes)} successful")

        return jsonify({'results': results})

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return jsonify({'error': str(e)}), 500

print("\n✅ Flask API configured with 4 endpoints:")
print("   /health               - Health check")
print("   /generate_audio       - Kokoro TTS (single)")
print("   /generate_image       - SDXL-Turbo (single)")
print("   /generate_images_batch - SDXL-Turbo (batch)")


# ═══════════════════════════════════════════════════════════════════════════════
# CELL 6: NGROK SETUP (Public URL) - YOUR TOKEN IS ALREADY HERE!
# ═══════════════════════════════════════════════════════════════════════════════

print("\n🔑 Setting up Ngrok...")

# Your Ngrok auth token (already configured!)
NGROK_AUTH_TOKEN = "35HuufK0IT26RER84mcvIbRjrog_7grjZvuDXtRPYL5hWLNCK"

ngrok.set_auth_token(NGROK_AUTH_TOKEN)
print("✅ Ngrok token configured!")


# ═══════════════════════════════════════════════════════════════════════════════
# CELL 7: START SERVER - THIS IS THE FINAL CELL!
# ═══════════════════════════════════════════════════════════════════════════════

def run_server():
    """Run Flask server in background thread"""
    app.run(port=5000, debug=False, use_reloader=False)

# Start Flask in background
print("\n🚀 Starting Flask server...")
server_thread = Thread(target=run_server, daemon=True)
server_thread.start()

# Wait for server to start
import time
time.sleep(3)

# Start Ngrok tunnel
print("🌐 Starting Ngrok tunnel...")
public_url = ngrok.connect(5000, bind_tls=True)

print("\n" + "═" * 80)
print("🎉 SERVER RUNNING!")
print("═" * 80)
print(f"\n📡 Public URL: {public_url.public_url}")
print(f"🖥️  Local URL:  http://localhost:5000")
print(f"\n🎮 Device: {device.upper()}")
if torch.cuda.is_available():
    print(f"🔥 GPU: {torch.cuda.get_device_name(0)}")
    print(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

print("\n📌 API Endpoints:")
print(f"   {public_url.public_url}/health")
print(f"   {public_url.public_url}/generate_audio")
print(f"   {public_url.public_url}/generate_image")
print(f"   {public_url.public_url}/generate_images_batch")

print("\n" + "═" * 80)
print("🔧 COPY THIS URL AND UPDATE YOUR BACKEND:")
print("═" * 80)
print(f"\n   Edit: story-video-generator/config.py")
print(f"   Change: COLAB_SERVER_URL = '{public_url.public_url}'")
print("\n" + "═" * 80)

print("\n💡 Server will run until you stop this cell or disconnect from Colab")
print("═" * 80)

# Keep server running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Server stopped!")
