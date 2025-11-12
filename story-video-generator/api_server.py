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
# from src.ai.image_generator import create_image_generator  # Old Pollinations
from src.ai.sdxl_remote_generator import create_image_generator  # NEW: Remote SDXL-Turbo
from src.editor.ffmpeg_compiler import FFmpegCompiler

# ✅ VOICE: KOKORO TTS (Remote API)
from src.voice.kokoro_api_client import generate_kokoro_audio, get_kokoro_voice

# ✅ CAPTIONS: SRT Generator
from src.utils.caption_generator import caption_generator

# ✅ MEDIA SOURCE MANAGER: Mix AI, Stock, Manual
from src.utils.media_source_manager import MediaSourceManager

# ✅ FIX #10: Check dependencies at startup
def check_dependencies():
    """Check if all required dependencies are installed"""
    import sys
    missing = []

    # Check critical dependencies
    try:
        import google.generativeai
    except ImportError:
        missing.append('google-generativeai (pip install google-generativeai)')

    try:
        import dotenv
    except ImportError:
        missing.append('python-dotenv (pip install python-dotenv)')

    try:
        import requests
    except ImportError:
        missing.append('requests (pip install requests)')

    try:
        import flask
    except ImportError:
        missing.append('flask (pip install flask)')

    try:
        import flask_cors
    except ImportError:
        missing.append('flask-cors (pip install flask-cors)')

    try:
        from pydub import AudioSegment
    except ImportError:
        missing.append('pydub (pip install pydub)')

    if missing:
        print("\n" + "="*70)
        print("❌ MISSING DEPENDENCIES DETECTED!")
        print("="*70)
        for dep in missing:
            print(f"  • {dep}")
        print("\n💡 Install all dependencies with:")
        print("   cd story-video-generator")
        print("   pip install -r requirements.txt")
        print("="*70 + "\n")
        sys.exit(1)
    else:
        print("✅ All dependencies installed")

# Run dependency check
check_dependencies()

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
    """✅ FIX #6: Get voice ID for Kokoro TTS with validation"""

    # Default to 'guy' if not provided
    if not voice_id:
        voice_id = 'guy'
        print(f"   ℹ️  No voice specified, using default: {voice_id}")

    # Use the Kokoro voice mapper
    kokoro_voice = get_kokoro_voice(voice_id)

    # ✅ Validate that voice mapping succeeded
    if not kokoro_voice:
        print(f"   ⚠️  WARNING: Unknown voice '{voice_id}', falling back to 'sarah_pro'")
        kokoro_voice = 'sarah_pro'
        voice_id = 'aria'  # Use frontend equivalent

    print(f"   🔧 Voice mapping validated: {voice_id} → {kokoro_voice} ✓")
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

        # ✅ FIX #3: Check Colab server health before starting generation
        print("🔍 Checking Colab GPU server status...")
        try:
            from config import COLAB_SERVER_URL
            health_response = requests.get(
                f"{COLAB_SERVER_URL}/health",
                timeout=5
            )
            if not health_response.ok:
                raise Exception("Colab server not responding")

            server_status = health_response.json()
            print(f"✅ Colab server ready: {server_status.get('gpu', 'Unknown GPU')}")
            print(f"   Models loaded: TTS={server_status.get('models_loaded', {}).get('tts', False)}, Image={server_status.get('models_loaded', {}).get('image', False)}")
        except requests.exceptions.Timeout:
            error_msg = "⏱️ Colab GPU server timeout. Please check if Google Colab notebook is running."
            print(f"❌ {error_msg}")
            progress_state['status'] = 'error'
            progress_state['error'] = 'Colab GPU server is not responding. Please start the Google Colab notebook and ensure it\'s running.'
            return
        except requests.exceptions.ConnectionError:
            error_msg = "🔌 Cannot connect to Colab GPU server. Please start the Google Colab notebook."
            print(f"❌ {error_msg}")
            progress_state['status'] = 'error'
            progress_state['error'] = 'Colab GPU server is not running. Please:\n1. Open Google Colab notebook\n2. Run all cells\n3. Copy the ngrok URL\n4. Update config/__init__.py with the new URL'
            return
        except Exception as e:
            error_msg = f"❌ Colab server check failed: {e}"
            print(error_msg)
            progress_state['status'] = 'error'
            progress_state['error'] = f'Colab GPU server error: {str(e)}'
            return

        # Get voice from user (Kokoro TTS)
        voice_id = get_voice_id(data.get('voice_id'))
        zoom_effect = data.get('zoom_effect', True)
        # ✅ FIXED: Frontend sends 'auto_captions', not 'enable_captions'
        enable_captions = data.get('auto_captions', False)

        # ✅ NEW: Get color filter and caption options
        color_filter = data.get('color_filter', 'none')
        caption_data = data.get('caption', {})
        caption_style = caption_data.get('style', 'simple') if caption_data else 'simple'
        caption_position = caption_data.get('position', 'bottom') if caption_data else 'bottom'

        print(f"🎤 Voice Engine: KOKORO TTS (Remote GPU)")
        print(f"🎤 Voice ID: {voice_id}")
        print(f"🎬 Zoom Effect: {'ENABLED' if zoom_effect else 'DISABLED'}")
        print(f"📝 Auto Captions: {'ENABLED' if enable_captions else 'DISABLED'}")
        if color_filter != 'none':
            print(f"🎨 Color Filter: {color_filter}")
        if enable_captions:
            print(f"   Caption Style: {caption_style}, Position: {caption_position}")

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
        # ✅ FIX #9: Add progress updates during image generation
        num_images = data.get('num_scenes', 10)
        progress_state['status'] = f'Generating {num_images} images with SDXL-Turbo GPU...'
        progress_state['progress'] = 30
        print(f"🎨 Step 2/4: Generating {num_images} images...")
        print(f"   ⏱️  This may take 40-80 seconds (GPU processes images sequentially)")

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

            # ✅ Update progress during generation
            progress_state['status'] = f'Generating images (0/{num_images})...'
            images = image_gen.generate_batch(scenes_with_prompts, characters)
            progress_state['status'] = f'Images generated ({len([i for i in images if i])}/{num_images})'
        else:
            # Standard mode - use original scenes
            progress_state['status'] = f'Generating images (0/{num_images})...'
            images = image_gen.generate_batch(result['scenes'], characters)
            progress_state['status'] = f'Images generated ({len([i for i in images if i])}/{num_images})'

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

        # Generate captions if enabled
        caption_srt_path = None
        if enable_captions:
            progress_state['status'] = 'Generating captions...'
            progress_state['progress'] = 75
            print("📝 Generating captions with voice sync...")

            caption_srt_path = Path("output/temp/captions.srt")
            caption_srt_path.parent.mkdir(parents=True, exist_ok=True)

            caption_generator.generate_srt(
                text=narration_text,
                audio_duration=audio_duration,
                output_path=str(caption_srt_path)
            )

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
            zoom_effect=zoom_effect,
            caption_srt_path=str(caption_srt_path) if caption_srt_path else None,
            color_filter=color_filter,  # ✅ NEW: Color filter
            caption_style=caption_style,  # ✅ NEW: Caption style
            caption_position=caption_position  # ✅ NEW: Caption position
        )
        
        progress_state['progress'] = 100
        progress_state['status'] = 'complete'
        progress_state['video_path'] = output_filename

        print(f"\n✅ SUCCESS! Video: {output_filename}")
        print(f"   Voice Engine: Kokoro TTS (Remote GPU)")
        print(f"   Voice: {voice_id}")
        print(f"   Zoom Effect: {'ENABLED' if zoom_effect else 'DISABLED'}")
        print(f"   Auto Captions: {'ENABLED' if enable_captions else 'DISABLED'}\n")
        
    except Exception as e:
        progress_state['status'] = 'error'
        progress_state['error'] = str(e)
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()


def generate_with_template_background(topic, story_type, template, research_data, duration, num_scenes, voice_engine, voice_id, voice_speed=1.0,
zoom_effect=True, enable_captions=False, color_filter='none', caption_style='simple', caption_position='bottom'):
    """✅ Background generation with template + research + voice selection + zoom effect + captions + color filters"""
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
        print(f"📝 Auto Captions: {'ENABLED' if enable_captions else 'DISABLED'}")
        
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

        progress_state['progress'] = 45
        progress_state['status'] = 'generating_image_prompts'

        # ✅ NEW: Generate DETAILED image prompts using Gemini API
        print("🤖 Generating high-quality image prompts with Gemini AI...")
        from src.utils.gemini_prompt_generator import gemini_generator

        try:
            gemini_prompts = gemini_generator.generate_image_prompts(
                script=script_text,
                num_images=num_scenes,
                style='cinematic'  # Match image style
            )

            # Convert Gemini prompts to scene dictionaries
            scenes = []
            for i, prompt in enumerate(gemini_prompts):
                scenes.append({
                    'image_description': prompt,  # Detailed Gemini-generated prompt
                    'content': prompt,
                    'scene_number': i + 1
                })

            print(f"   ✅ Created {len(scenes)} AI-generated image prompts")

        except Exception as e:
            print(f"   ⚠️  Gemini error: {e}")
            print(f"   🔄 Falling back to scene extraction...")

            # Fallback: Use scenes from result if available
            if 'scenes' in result and result['scenes']:
                scenes = result['scenes'][:num_scenes]
                print(f"   Using {len(scenes)} scenes from script generator")
            else:
                # Last resort: Extract from script
                story_parts = script_text.split('.')[:num_scenes]
                scenes = []
                for i, part in enumerate(story_parts):
                    if part.strip():
                        scenes.append({
                            'image_description': f"{part.strip()[:100]}, cinematic style",
                            'content': part.strip()[:100],
                            'scene_number': i + 1
                        })

        progress_state['progress'] = 50
        progress_state['status'] = 'generating_images'

        print("🎨 Generating images with AI prompts...")

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

        # Generate captions if enabled
        caption_srt_path = None
        if enable_captions:
            progress_state['status'] = 'Generating captions...'
            progress_state['progress'] = 75
            print("📝 Generating captions with voice sync...")

            caption_srt_path = Path("output/temp/captions_template.srt")
            caption_srt_path.parent.mkdir(parents=True, exist_ok=True)

            caption_generator.generate_srt(
                text=script_text,
                audio_duration=audio_duration,
                output_path=str(caption_srt_path)
            )

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
            zoom_effect=zoom_effect,
            caption_srt_path=str(caption_srt_path) if caption_srt_path else None,
            color_filter=color_filter,  # ✅ NEW: Color filter
            caption_style=caption_style,  # ✅ NEW: Caption style
            caption_position=caption_position  # ✅ NEW: Caption position
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
        print(f"   Captions: {'ENABLED' if enable_captions else 'DISABLED'}")
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
        enable_captions = data.get('enable_captions', False)  # Default: False

        print(f"\n🎬 Generating with template: {topic}")
        print(f"   Type: {story_type}")
        print(f"   Scenes: {num_scenes}")
        print(f"   Template: {'Yes' if template else 'No'}")
        print(f"   Research: {'Yes' if research_data else 'No'}")
        print(f"   Voice Engine: {voice_engine}")
        print(f"   Voice ID: {voice_id}")
        print(f"   Voice Speed: {voice_speed}x")
        print(f"   Zoom Effect: {'ENABLED' if zoom_effect else 'DISABLED'}")
        print(f"   Captions: {'ENABLED' if enable_captions else 'DISABLED'}")

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
            args=(topic, story_type, template, research_data, duration, num_scenes, voice_engine, voice_id, voice_speed, zoom_effect, enable_captions)
        )
        thread.start()

        return jsonify({
            'success': True,
            'message': 'Generation started',
            'used_template': template is not None,
            'used_research': research_data is not None,
            'voice_engine': voice_engine,
            'zoom_effect': zoom_effect,
            'enable_captions': enable_captions
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
# MEDIA SOURCE MIXING (AI + Stock + Manual)
# ═══════════════════════════════════════════════════════════════

@app.route('/api/generate-mixed-media', methods=['POST', 'OPTIONS'])
def generate_mixed_media():
    """✅ Generate video with mixed media sources (AI + Stock + Manual)"""
    if request.method == 'OPTIONS':
        return '', 204

    global progress_state

    try:
        data = request.json

        if not data.get('topic'):
            return jsonify({'error': 'Topic required'}), 400

        # Extract config
        topic = data.get('topic', '')
        story_type = data.get('story_type', 'scary_horror')
        num_scenes = int(data.get('num_scenes', 10))
        voice_id = data.get('voice_id', 'aria')
        voice_speed = float(data.get('voice_speed', 1.0))
        zoom_effect = data.get('zoom_effect', True)
        enable_captions = data.get('enable_captions', False)
        image_style = data.get('image_style', 'cinematic_film')

        # Media source config
        media_config = data.get('media_config', {})
        priority_order = media_config.get('priority', ['ai', 'stock', 'manual'])
        pattern = media_config.get('pattern', None)  # Optional interleave pattern

        # Source data
        stock_items = media_config.get('stock_items', [])  # URLs from Pexels
        manual_files = media_config.get('manual_files', [])  # Uploaded file paths
        generate_ai = media_config.get('generate_ai', True)

        print(f"\n🎬 Generating MIXED MEDIA video: {topic}")
        print(f"   Priority: {' → '.join(priority_order)}")
        if pattern:
            print(f"   Pattern: {pattern}")
        print(f"   Scenes: {num_scenes}")
        print(f"   AI: {'Yes' if generate_ai else 'No'}")
        print(f"   Stock: {len(stock_items)} items")
        print(f"   Manual: {len(manual_files)} files")

        progress_state = {
            'status': 'generating',
            'progress': 0,
            'video_path': None,
            'error': None,
            'voice_engine': 'kokoro',
            'voice_id': voice_id,
        }

        # Start background generation
        thread = threading.Thread(
            target=generate_mixed_media_background,
            args=(
                topic, story_type, num_scenes, voice_id, voice_speed,
                zoom_effect, enable_captions, image_style,
                priority_order, pattern, stock_items, manual_files, generate_ai
            )
        )
        thread.start()

        return jsonify({
            'success': True,
            'message': 'Mixed media generation started',
            'media_config': {
                'priority': priority_order,
                'pattern': pattern,
                'ai': generate_ai,
                'stock_count': len(stock_items),
                'manual_count': len(manual_files)
            }
        }), 200

    except Exception as e:
        print(f"❌ Mixed media generation failed: {e}")
        return jsonify({'error': str(e)}), 500


def generate_mixed_media_background(
    topic, story_type, num_scenes, voice_id, voice_speed,
    zoom_effect, enable_captions, image_style,
    priority_order, pattern, stock_items, manual_files, generate_ai,
    color_filter='none', caption_style='simple', caption_position='bottom'
):
    """Background worker for mixed media generation with color filters and caption styles"""
    global progress_state

    try:
        progress_state['status'] = 'generating_script'
        progress_state['progress'] = 10

        print(f"📝 Step 1/5: Generating script...")

        # Generate script
        result = enhanced_script_generator.generate_with_template(
            topic=topic,
            story_type=story_type,
            template=None,
            research_data=None,
            duration_minutes=num_scenes / 6,  # Estimate
            num_scenes=num_scenes
        )

        script_text = result['script']
        scenes = result.get('scenes', [])

        progress_state['progress'] = 30

        # Initialize media manager
        manager = MediaSourceManager()
        manager.set_priority_order(priority_order)

        # Generate AI images if requested
        if generate_ai:
            progress_state['status'] = 'generating_ai_images'
            progress_state['progress'] = 40
            print(f"🎨 Step 2/5: Generating AI images...")

            generator = create_image_generator(image_style, story_type)
            ai_results = generator.generate_batch(scenes)

            ai_paths = [Path(r['filepath']) for r in ai_results if r]
            manager.add_ai_images(ai_paths)

        # Add stock media
        if stock_items:
            progress_state['status'] = 'processing_stock'
            progress_state['progress'] = 50
            print(f"📸 Step 3/5: Processing stock media...")

            manager.add_stock_media(stock_items)

        # Add manual uploads
        if manual_files:
            progress_state['status'] = 'processing_manual'
            progress_state['progress'] = 55
            print(f"📁 Step 3.5/5: Processing manual uploads...")

            manual_paths = [Path(f) for f in manual_files]
            manager.add_manual_uploads(manual_paths)

        # Merge sources
        progress_state['status'] = 'merging_sources'
        progress_state['progress'] = 60
        print(f"🔀 Step 4/5: Merging media sources...")

        if pattern:
            # Use interleaved pattern
            merged_sources = manager.apply_interleaved_pattern(
                pattern=pattern,
                num_scenes=num_scenes,
                download_stock=True
            )
        else:
            # Use priority order
            merged_sources = manager.merge_sources(
                num_scenes=num_scenes,
                download_stock=True
            )

        # Get final image paths
        image_paths = manager.get_image_paths(merged_sources)

        print(f"   ✅ Final: {len(image_paths)} images ready")

        # Generate audio
        progress_state['status'] = 'generating_audio'
        progress_state['progress'] = 70
        print(f"🎤 Step 5/5: Generating audio...")

        audio_path = Path("output/temp/narration.wav")
        audio_path.parent.mkdir(parents=True, exist_ok=True)

        generate_audio_kokoro(
            text=script_text,
            voice=voice_id,
            speed=voice_speed,
            output_path=str(audio_path)
        )

        audio_duration = get_audio_duration(audio_path)

        # Calculate durations
        time_per_image = audio_duration / len(image_paths)
        durations = [time_per_image] * len(image_paths)

        # Generate captions if requested
        caption_srt_path = None
        if enable_captions:
            progress_state['status'] = 'generating_captions'
            progress_state['progress'] = 75
            print(f"📝 Generating captions...")

            caption_srt_path = Path("output/temp/captions.srt")
            caption_srt_path.parent.mkdir(parents=True, exist_ok=True)

            caption_generator.generate_srt(
                text=script_text,
                audio_duration=audio_duration,
                output_path=str(caption_srt_path)
            )

        # Compile video
        progress_state['status'] = 'compiling_video'
        progress_state['progress'] = 80
        print(f"🎬 Compiling video...")

        compiler = FFmpegCompiler()
        safe_topic = sanitize_filename(topic)
        output_filename = f"{safe_topic}_mixed.mp4"

        video_path = compiler.create_video(
            image_paths,
            str(audio_path),
            Path(f"output/videos/{output_filename}"),
            durations,
            zoom_effect=zoom_effect,
            caption_srt_path=str(caption_srt_path) if caption_srt_path else None,
            color_filter=color_filter,  # ✅ NEW: Color filter
            caption_style=caption_style,  # ✅ NEW: Caption style
            caption_position=caption_position  # ✅ NEW: Caption position
        )

        progress_state['progress'] = 100
        progress_state['status'] = 'complete'
        progress_state['video_path'] = output_filename

        # Show stats
        stats = manager.get_stats()
        print(f"\n✅ SUCCESS! Mixed media video: {output_filename}")
        print(f"   AI images: {stats['ai_count']}")
        print(f"   Stock media: {stats['stock_count']}")
        print(f"   Manual uploads: {stats['manual_count']}")
        print(f"   Zoom: {'ENABLED' if zoom_effect else 'DISABLED'}")
        print(f"   Captions: {'ENABLED' if enable_captions else 'DISABLED'}\n")

    except Exception as e:
        progress_state['status'] = 'error'
        progress_state['error'] = str(e)
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()


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
    print("🎨 IMAGES: SDXL-Turbo (Remote GPU - Google Colab)")
    print("   - Ultra-fast GPU generation")
    print("   - 1920x1080 HD quality")
    print("   - All frontend styles supported")
    print("   - Unique per scene")
    
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
    print("⚡ 100% GPU-POWERED: Kokoro TTS + SDXL-Turbo (Remote Colab)")
    print("🎤 Voice: Kokoro TTS (6 GPU voices)")
    print("🎨 Images: SDXL-Turbo (GPU accelerated)")
    print("📝 Scripts: Gemini AI (Google)")
    print("🚀 Fast: 2-5 minutes for 10-60 minute videos")
    print("🎬 Quality: 10/10 - Professional YouTube content!")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)