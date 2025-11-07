#!/usr/bin/env python3
"""
🚀 QUICK LAUNCHER - Easy video generation
"""

import sys
from pathlib import Path

# Make sure we can import from the project
sys.path.insert(0, str(Path(__file__).parent))

print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         🎬 AI VIDEO GENERATOR - QUICK START              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")

print("1. Generate a video (Interactive)")
print("2. Exit")
print()

choice = input("Choose option (1-2): ").strip()

if choice == "1":
    topic = input("\n📝 Enter video topic: ").strip()
    if topic:
        print(f"\n🎬 Generating video about: {topic}")
        print("⏳ This will take 5-10 minutes...\n")
        
        # Simple generation
        from src.ai.script_generator import ScriptGenerator
        from src.ai.image_generator import ImageGenerator
        from src.voice.tts_engine import TTSEngine
        from src.editor.video_compiler import VideoCompiler
        from src.media.image_manager import ImageManager
        from src.utils.logger import logger
        
        try:
            # Step 1: Generate script
            logger.info("📝 Step 1/4: Generating script...")
            script_gen = ScriptGenerator()
            result = script_gen.generate_script(
                title=topic,
                plot=f"Create an engaging story about {topic}",
                length="30k",
                niche="horror_paranormal"
            )
            logger.success(f"Script generated: {result['character_count']} characters")
            
            # Step 2: Generate images
            logger.info("🎨 Step 2/4: Generating images...")
            image_gen = ImageGenerator("horror_paranormal")
            scene_descriptions = [scene['image_description'] for scene in result['scenes']]
            images = image_gen.generate_images(scene_descriptions[:10])  # First 10 scenes
            logger.success(f"Generated {len(images)} images")
            
            # Step 3: Generate voice
            logger.info("🎤 Step 3/4: Generating voice...")
            tts = TTSEngine()
            audio_path = tts.generate_audio(result['script'], "narration.mp3")
            duration = tts.get_audio_duration(audio_path)
            logger.success(f"Audio generated: {duration:.1f} seconds")
            
            # Step 4: Compile video
            logger.info("🎬 Step 4/4: Compiling video...")
            img_manager = ImageManager()
            image_paths = [img['filepath'] for img in images if img]
            timeline = img_manager.assign_images_to_timeline(image_paths, duration)
            
            compiler = VideoCompiler()
            video_path = compiler.create_video_from_images(
                timeline,
                audio_path,
                f"{topic.replace(' ', '_')}.mp4"
            )
            
            logger.success(f"✅ VIDEO COMPLETE: {video_path}")
            
        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Topic cannot be empty")
else:
    print("👋 Goodbye!")