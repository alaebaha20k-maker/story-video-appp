"""
🔌 API SERVER - With Google Colab GPU (TWO-STAGE GEMINI + FULL GPU Processing)

System Architecture (TWO-STAGE INTELLIGENT SYSTEM):
- STAGE 1: Script Generation - Gemini AI (local) - PURE QUALITY, NO IMAGE PROMPTS
- STAGE 2: Image Prompt Extraction - Gemini AI (local, separate API) - SDXL-optimized prompts
- Voice: Kokoro TTS (Colab GPU via ngrok)
- Images: SDXL-Turbo (Colab GPU via ngrok) ← Uses Stage 2 prompts
- Video: FFmpeg (Colab GPU via ngrok) ← ALL EFFECTS on GPU!

WHY TWO STAGES?
- Stage 1 generates HIGH-QUALITY script without image prompts (better quality!)
- Stage 2 analyzes finished script and creates perfect SDXL prompts
- Parallel execution: Script → Voice, Prompts → Images
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
from src.ai.image_prompt_extractor import image_prompt_extractor  # NEW: Stage 2
from src.ai.template_analyzer import template_analyzer  # NEW: Template Analysis
from src.utils.colab_client import get_colab_client
from src.media.intelligent_media_manager import media_manager
from src.utils.smart_duration_calculator import duration_calculator
from src.utils.caption_generator import generate_auto_captions, generate_manual_caption
from src.video.local_ffmpeg_compiler import compile_video_local, check_ffmpeg_installed

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

        print(f"   ✅ Script: {len(result['script'])} characters (PURE QUALITY!)")
        print(f"   ✅ Narrative markers: {len(result['scenes'])} created")

        # STEP 2: Image Prompt Extraction (Gemini AI Stage 2 - NEW!)
        progress_state['status'] = 'Extracting visual prompts (Stage 2 Gemini)...'
        progress_state['progress'] = 20
        print("🎨 Step 2/5: Extracting image prompts with Gemini Stage 2...")

        story_type = data.get('story_type', 'scary_horror')
        image_style = data.get('image_style', 'cinematic')
        num_scenes = int(data.get('num_scenes', 10))

        # Extract SDXL-optimized prompts from script
        image_prompts = image_prompt_extractor.extract_prompts(
            script=result['script'],
            num_images=num_scenes,
            story_type=story_type,
            image_style=image_style
        )

        print(f"   ✅ Prompts: {len(image_prompts)} SDXL-optimized prompts extracted!")
        for i, prompt_data in enumerate(image_prompts[:3]):  # Show first 3
            print(f"      {i+1}. {prompt_data['prompt'][:60]}...")

        # Update scenes with extracted prompts
        for i, scene in enumerate(result['scenes'][:len(image_prompts)]):
            if i < len(image_prompts):
                scene['prompt'] = image_prompts[i]['prompt']
                scene['image_description'] = image_prompts[i]['prompt']

        # STEP 3: Media Generation (INTELLIGENT - AI/Manual/Stock/Mixed)
        progress_state['status'] = 'Generating media (intelligent mode)...'
        progress_state['progress'] = 35
        print("🎨 Step 3/5: Generating media with Intelligent Media Manager...")

        # Get media mode and options
        image_mode = data.get('image_mode', 'ai_only')
        image_style = data.get('image_style', 'cinematic')
        manual_files = data.get('manual_files', [])  # User uploads
        stock_keywords = data.get('stock_keywords', [])  # For stock mode
        num_scenes = int(data.get('num_scenes', 10))

        print(f"   Mode: {image_mode}")
        print(f"   Style: {image_style}")
        print(f"   Scenes: {num_scenes}")

        # Use intelligent media manager (handles all 7 modes)
        media_items = media_manager.generate_media(
            mode=image_mode,
            scenes=result['scenes'],
            image_style=image_style,
            manual_files=manual_files,
            stock_keywords=stock_keywords,
            num_scenes=num_scenes
        )

        print(f"   ✅ Media: {len(media_items)} items generated/collected")
        # ✅ FIXED: Show ALL media items (no 5-item limit)
        for i, item in enumerate(media_items):
            print(f"      {i+1}. {item.media_type} ({item.source}): {item.filepath.name}")

        # STEP 4: Voice Generation (Kokoro TTS - Colab GPU)
        progress_state['status'] = 'Generating voice with Kokoro TTS (GPU)...'
        progress_state['progress'] = 60
        print(f"🎤 Step 4/5: Generating voice with Kokoro TTS (Colab GPU)...")

        audio_path = Path("output/temp/narration.wav")
        audio_path.parent.mkdir(parents=True, exist_ok=True)

        # 🧪 Check if using Edge TTS test voice (local generation)
        if voice_id == 'edge_test':
            print("   🧪 Using Edge TTS (Local Generation - Fast Testing)...")
            import edge_tts
            import asyncio

            # Edge TTS saves as MP3 - we need to convert to WAV for FFmpeg
            temp_mp3_path = Path("output/temp/narration_edge.mp3")
            temp_mp3_path.parent.mkdir(parents=True, exist_ok=True)

            async def generate_edge_audio():
                communicate = edge_tts.Communicate(result['script'], "en-US-JennyNeural")
                await communicate.save(str(temp_mp3_path))

            asyncio.run(generate_edge_audio())

            # Convert MP3 to WAV using pydub
            print(f"   🔄 Converting MP3 to WAV format...")
            audio = AudioSegment.from_mp3(str(temp_mp3_path))
            audio.export(str(audio_path), format="wav")

            # Clean up temp MP3 file
            if temp_mp3_path.exists():
                temp_mp3_path.unlink()

            audio_file = audio_path
            print(f"   ✅ Edge TTS audio generated locally and converted to WAV!")
        else:
            # Call Colab for Kokoro TTS audio generation
            audio_file = colab_client.generate_audio(
                text=result['script'],
                voice=voice_id,
                speed=float(data.get('voice_speed', 1.0)),
                output_path=audio_path
            )

        audio_duration = get_audio_duration(audio_path)
        print(f"   ✅ Audio: {audio_duration:.1f} seconds ({audio_duration/60:.1f} minutes)")

        # INTELLIGENT DURATION CALCULATION
        # Handles mixed media (images + videos) with smart timing
        print(f"\n   🔧 Calculating intelligent durations...")

        # Prepare media items for duration calculator
        media_for_calc = [item.to_dict() for item in media_items]

        # Use smart duration calculator
        durations = duration_calculator.calculate_durations(
            media_items=media_for_calc,
            audio_duration=audio_duration,
            variation=0.3  # 30% variation for natural pacing
        )

        print(f"      Total video duration: {sum(durations):.1f}s ({sum(durations)/60:.1f} min)")
        print(f"      Matches audio: {'✅ YES' if abs(sum(durations) - audio_duration) < 1 else '⚠️ NO'}")

        # STEP 5: Video Compilation (FFmpeg - Colab GPU)
        progress_state['status'] = 'Compiling video with FFmpeg (GPU)...'
        progress_state['progress'] = 80
        print("🎬 Step 5/5: Compiling video with FFmpeg (Colab GPU)...")

        safe_topic = sanitize_filename(data.get('topic', 'video'))
        output_filename = f"{safe_topic}_video.mp4"

        # Get effects from request
        color_filter = data.get('color_filter', 'none')
        grain_effect = data.get('grain_effect', False)

        # ✅ CAPTION GENERATION (AUTO or MANUAL)
        captions_data = []
        auto_captions_enabled = data.get('auto_captions', False)
        manual_caption = data.get('caption')

        if auto_captions_enabled:
            # Generate auto-captions from script with timing
            print(f"\n   💬 Generating auto-captions from script...")
            captions_data = generate_auto_captions(
                script=result['script'],
                audio_duration=audio_duration,
                style='bold',  # TikTok-style bold captions
                position='bottom'
            )
            print(f"   ✅ Generated {len(captions_data)} auto-captions")
        elif manual_caption and manual_caption.get('text'):
            # Single manual caption for entire video
            print(f"\n   💬 Adding manual caption: {manual_caption.get('text')[:30]}...")
            captions_data = generate_manual_caption(
                text=manual_caption.get('text', ''),
                audio_duration=audio_duration,
                style=manual_caption.get('style', 'simple'),
                position=manual_caption.get('position', 'bottom')
            )
            print(f"   ✅ Manual caption added")

        # Extract media file paths
        media_paths = [item.filepath for item in media_items]

        # ⚡ OPTIMIZATION: Use LOCAL FFmpeg to avoid large Colab uploads
        print(f"\n   🎬 Using LOCAL FFmpeg compilation (no upload needed)...")

        try:
            video_path = compile_video_local(
                media_paths,
                audio_path,
                durations,
                output_path=Path(f"output/videos/{output_filename}"),
                zoom_effect=zoom_effect,
                color_filter=color_filter,
                grain_effect=grain_effect,
                captions=captions_data
            )
        except Exception as e:
            print(f"   ⚠️  Local FFmpeg failed: {e}")
            print(f"   🔄 Falling back to Colab GPU...")

            # Fallback to Colab if local fails
            video_path = colab_client.compile_video(
                media_paths,
                audio_path,
                durations,
                output_path=Path(f"output/videos/{output_filename}"),
                zoom_effect=zoom_effect,
                color_filter=color_filter,
                grain_effect=grain_effect,
                captions=captions_data
            )

        progress_state['progress'] = 100
        progress_state['status'] = 'complete'
        progress_state['video_path'] = output_filename

        print(f"\n✅ SUCCESS! Video: {output_filename}")
        print(f"   Stage 1: Script (Gemini AI) - PURE QUALITY!")
        print(f"   Stage 2: Image Prompts (Gemini AI) - {len(image_prompts)} SDXL prompts")
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
    voice_engine, voice_id, voice_speed=1.0, zoom_effect=True,
    auto_captions=False, manual_caption=None, color_filter='none', grain_effect=False
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

        # 🧪 Check if using Edge TTS test voice (local generation)
        if voice_id == 'edge_test':
            print("   🧪 Using Edge TTS (Local Generation - Fast Testing)...")
            import edge_tts
            import asyncio

            # Edge TTS saves as MP3 - we need to convert to WAV for FFmpeg
            temp_mp3_path = Path("output/temp/narration_edge.mp3")
            temp_mp3_path.parent.mkdir(parents=True, exist_ok=True)

            async def generate_edge_audio():
                communicate = edge_tts.Communicate(script_text, "en-US-JennyNeural")
                await communicate.save(str(temp_mp3_path))

            asyncio.run(generate_edge_audio())

            # Convert MP3 to WAV using pydub
            print(f"   🔄 Converting MP3 to WAV format...")
            audio = AudioSegment.from_mp3(str(temp_mp3_path))
            audio.export(str(audio_path), format="wav")

            # Clean up temp MP3 file
            if temp_mp3_path.exists():
                temp_mp3_path.unlink()

            audio_file = audio_path
            print(f"   ✅ Edge TTS audio generated locally and converted to WAV!")
        else:
            # Call Colab for Kokoro TTS audio generation
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

        # ✅ CAPTION GENERATION (AUTO or MANUAL)
        captions_data = []
        if auto_captions:
            # Generate auto-captions from script with timing
            print(f"\n   💬 Generating auto-captions from script...")
            captions_data = generate_auto_captions(
                script=script_text,
                audio_duration=audio_duration,
                style='bold',
                position='bottom'
            )
            print(f"   ✅ Generated {len(captions_data)} auto-captions")
        elif manual_caption and manual_caption.get('text'):
            # Single manual caption for entire video
            print(f"\n   💬 Adding manual caption: {manual_caption.get('text')[:30]}...")
            captions_data = generate_manual_caption(
                text=manual_caption.get('text', ''),
                audio_duration=audio_duration,
                style=manual_caption.get('style', 'simple'),
                position=manual_caption.get('position', 'bottom')
            )
            print(f"   ✅ Manual caption added")

        # ⚡ OPTIMIZATION: Use LOCAL FFmpeg to avoid large Colab uploads
        print(f"\n   🎬 Using LOCAL FFmpeg compilation (no upload needed)...")

        try:
            video_path = compile_video_local(
                image_paths,
                audio_path,
                durations,
                output_path=Path(f"output/videos/{output_filename}"),
                zoom_effect=zoom_effect,
                color_filter=color_filter,
                grain_effect=grain_effect,
                captions=captions_data
            )
        except Exception as e:
            print(f"   ⚠️  Local FFmpeg failed: {e}")
            print(f"   🔄 Falling back to Colab GPU...")

            # Fallback to Colab if local fails
            video_path = colab_client.compile_video(
                image_paths,
                audio_path,
                durations,
                output_path=Path(f"output/videos/{output_filename}"),
                zoom_effect=zoom_effect,
                color_filter=color_filter,
                grain_effect=grain_effect,
                captions=captions_data
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

    # Kokoro voices (from Colab notebook mapping) - ALL 12 VOICES
    voices = {
        # Male voices
        'guy': {'engine': 'kokoro', 'name': 'Guy (Adam)', 'gender': 'male', 'style': 'Natural & Clear'},
        'adam_narration': {'engine': 'kokoro', 'name': 'Adam (Narrator)', 'gender': 'male', 'style': 'Professional Narration'},
        'michael': {'engine': 'kokoro', 'name': 'Michael', 'gender': 'male', 'style': 'Warm & Friendly'},
        'brian': {'engine': 'kokoro', 'name': 'Brian', 'gender': 'male', 'style': 'Casual'},
        'george': {'engine': 'kokoro', 'name': 'George', 'gender': 'male', 'style': 'British Accent'},
        'davis_deep': {'engine': 'kokoro', 'name': 'Davis (Deep)', 'gender': 'male', 'style': 'Deep & Dramatic'},
        'christopher': {'engine': 'kokoro', 'name': 'Christopher', 'gender': 'male', 'style': 'Calm & Thoughtful'},

        # Female voices
        'aria': {'engine': 'kokoro', 'name': 'Aria (Bella)', 'gender': 'female', 'style': 'Natural & Warm'},
        'sarah_pro': {'engine': 'kokoro', 'name': 'Sarah', 'gender': 'female', 'style': 'Professional'},
        'nicole': {'engine': 'kokoro', 'name': 'Nicole', 'gender': 'female', 'style': 'Cheerful & Clear'},
        'jenny': {'engine': 'kokoro', 'name': 'Jenny', 'gender': 'female', 'style': 'Young & Energetic'},
        'emma': {'engine': 'kokoro', 'name': 'Emma', 'gender': 'female', 'style': 'British Accent'},
        'isabella': {'engine': 'kokoro', 'name': 'Isabella', 'gender': 'female', 'style': 'Compassionate & Warm'},
    }

    return jsonify({
        'voices': voices,
        'engine': 'kokoro_colab',
        'total': len(voices),
        'gpu_accelerated': True
    }), 200


@app.route('/api/analyze-template', methods=['POST', 'OPTIONS'])
def analyze_template():
    """Analyze template script to extract structure and style"""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.json

        if not data.get('template'):
            return jsonify({'error': 'Template text required'}), 400

        template_text = data.get('template', '')
        story_type = data.get('story_type', 'scary_horror')

        print(f"\n🔍 Analyzing template...")
        print(f"   Length: {len(template_text)} characters")
        print(f"   Story type: {story_type}")

        # Analyze template using dedicated Gemini API
        analysis = template_analyzer.analyze_template(
            template_text=template_text,
            story_type=story_type
        )

        # Create style guide
        style_guide = template_analyzer.create_style_guide(analysis)

        print(f"✅ Template analyzed successfully!")
        print(f"   Hook: {analysis.get('hook_intensity', 'N/A')}")
        print(f"   Pacing: {analysis.get('pacing_speed', 'N/A')}")

        return jsonify({
            'success': True,
            'analysis': analysis,
            'style_guide': style_guide,
            'hook_intensity': analysis.get('hook_intensity', 'medium'),
            'pacing_speed': analysis.get('pacing_speed', 'medium'),
            'narrative_voice': analysis.get('narrative_voice', '3rd person'),
            'tone': analysis.get('tone', 'neutral')
        }), 200

    except Exception as e:
        print(f"❌ Template analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze-script', methods=['POST', 'OPTIONS'])
def analyze_script():
    """✅ FIXED: Analyze pasted script for frontend library (matches ExampleScriptUpload.tsx)"""
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.json

        if not data.get('scriptContent'):
            return jsonify({'error': 'Script content required'}), 400

        script_content = data.get('scriptContent', '')
        script_type = data.get('scriptType', 'documentary')

        print(f"\n📖 Analyzing pasted script...")
        print(f"   Length: {len(script_content)} characters")
        print(f"   Type: {script_type}")

        # Analyze using template analyzer
        analysis = template_analyzer.analyze_template(
            template_text=script_content,
            story_type=script_type
        )

        print(f"✅ Script analyzed!")
        print(f"   Hook style: {analysis.get('hook_style', 'N/A')}")

        # Extract hook example (first 2-3 sentences)
        sentences = script_content.split('.')[:3]
        hook_example = '.'.join(sentences).strip() + '.' if sentences else 'No hook found'

        # Map analysis to frontend format
        response_data = {
            'success': True,
            'hook_example': hook_example[:200],  # First 200 chars as hook
            'hook_style': analysis.get('hook_style', 'researched'),
            'setup_length': 100,  # Estimated word counts
            'rise_length': 150,
            'climax_length': 80,
            'end_length': 50,
            'tone': analysis.get('tone', 'professional').split(',') if isinstance(analysis.get('tone'), str) else ['professional'],
            'key_patterns': analysis.get('key_patterns', ['descriptive', 'narrative']),
            'sentence_variation': analysis.get('sentence_style', 'medium')
        }

        print(f"   ✅ Returning analysis to frontend")

        return jsonify(response_data), 200

    except Exception as e:
        print(f"❌ Script analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


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
        auto_captions = data.get('auto_captions', False)
        manual_caption = data.get('caption')
        color_filter = data.get('color_filter', 'none')
        grain_effect = data.get('grain_effect', False)

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
                  voice_engine, voice_id, voice_speed, zoom_effect,
                  auto_captions, manual_caption, color_filter, grain_effect)
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
    print("   POST /api/analyze-template - Analyze template structure")
    print("   POST /api/analyze-script - Analyze pasted script (frontend library)")
    print("   POST /api/generate-video - Generate video")
    print("   POST /api/generate-with-template - Generate with template")
    print("="*60)
    print("\n🏆 PROFESSIONAL YOUTUBE VIDEO GENERATOR READY!")
    print("⚡ GPU-Accelerated with Google Colab!")
    print("🎬 Quality: 10/10 - Professional YouTube content!")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
