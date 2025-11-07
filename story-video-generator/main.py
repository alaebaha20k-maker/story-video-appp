"""
🎥 AI VIDEO GENERATOR - Main Application
Generates full AI videos from topics using GPT-4 + DALL-E + Edge-TTS + MoviePy
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from typing import Optional, List
import json

from config.settings import VIDEO_SETTINGS
from src.ai.script_generator import script_generator
from src.ai.image_generator import image_generator
from src.voice.tts_engine import tts_engine
from src.media.image_manager import image_manager
from src.editor.video_compiler import video_compiler
from src.utils.logger import logger
from src.utils.file_handler import file_handler


class VideoGenerator:
    """Main video generation orchestrator"""
    
    def __init__(self):
        self.script = None
        self.images = []
        self.audio_path = None
        self.video_path = None
    
    def generate_video(
        self,
        topic: str,
        num_scenes: int = 10,
        style: str = "horror",
        voice: Optional[str] = None,
        effect_type: str = "simple_zoom",
        transition_type: str = "crossfade"
    ) -> Path:
        """Generate complete video from topic"""
        
        logger.header("🎥 AI VIDEO GENERATOR")
        logger.info(f"Topic: {topic}")
        logger.info(f"Scenes: {num_scenes}")
        logger.info(f"Style: {style}")
        logger.divider()
        
        # Step 1: Generate script
        logger.step("STEP 1: Generating Script")
        self.script = script_generator.generate_script(
            topic=topic,
            num_scenes=num_scenes,
            style=style
        )
        
        if not self.script:
            logger.error("Failed to generate script")
            return None
        
        logger.success(f"Script generated: {len(self.script)} characters")
        logger.divider()
        
        # Step 2: Generate images
        logger.step("STEP 2: Generating Images")
        
        # Extract image prompts from script
        import re
        image_prompts = re.findall(r'IMAGE:\s*(.+?)(?:\n|$)', self.script, re.IGNORECASE)
        
        if not image_prompts:
            logger.warning("No image prompts found, creating generic prompts...")
            image_prompts = [f"{topic} scene {i+1}" for i in range(num_scenes)]
        
        logger.info(f"Found {len(image_prompts)} image prompts")
        
        # Generate images
        image_paths = image_generator.generate_images_batch(
            prompts=image_prompts,
            style=style
        )
        
        if not image_paths:
            logger.error("Failed to generate images")
            return None
        
        logger.success(f"Generated {len(image_paths)} images")
        self.images = image_paths
        logger.divider()
        
        # Step 3: Resize images
        logger.step("STEP 3: Processing Images")
        resized_images = image_manager.batch_resize_images(image_paths)
        logger.success(f"Resized {len(resized_images)} images")
        logger.divider()
        
        # Step 4: Generate voice narration
        logger.step("STEP 4: Generating Voice Narration")
        
        if voice:
            tts_engine.set_voice(voice)
        
        # Clean script for TTS (remove image prompts)
        narration_text = re.sub(r'IMAGE:.*?\n', '', self.script, flags=re.IGNORECASE)
        narration_text = re.sub(r'\[SCENE\s+\d+\]', '', narration_text, flags=re.IGNORECASE)
        
        self.audio_path = tts_engine.generate_audio(
            text=narration_text,
            filename="narration.mp3"
        )
        
        audio_duration = tts_engine.get_audio_duration(self.audio_path)
        logger.success(f"Audio generated: {audio_duration:.1f} seconds")
        logger.divider()
        
        # Step 5: Create image timeline
        logger.step("STEP 5: Creating Timeline")
        
        image_timeline = image_manager.assign_images_to_timeline(
            resized_images,
            audio_duration
        )
        
        logger.info(f"Timeline created with {len(image_timeline)} segments")
        for i, segment in enumerate(image_timeline[:3]):
            logger.info(f"   Segment {i+1}: {segment['duration']:.1f}s")
        if len(image_timeline) > 3:
            logger.info(f"   ... and {len(image_timeline) - 3} more")
        logger.divider()
        
        # Step 6: Compile video
        logger.step("STEP 6: Compiling Final Video")
        
        output_filename = f"{topic.replace(' ', '_')[:30]}_video.mp4"
        
        self.video_path = video_compiler.create_video_from_images(
            image_timeline=image_timeline,
            audio_path=self.audio_path,
            output_filename=output_filename,
            effect_type=effect_type,
            transition_type=transition_type,
            transition_duration=1.0
        )
        
        logger.divider()
        logger.header("✅ VIDEO GENERATION COMPLETE!")
        logger.success(f"Video saved: {self.video_path}")
        logger.info(f"Duration: {audio_duration:.1f} seconds")
        logger.info(f"Scenes: {len(image_timeline)}")
        logger.divider()
        
        return self.video_path
    
    def generate_from_custom_script(
        self,
        script_file: Path,
        num_images: int = 10,
        style: str = "cinematic"
    ) -> Path:
        """Generate video from existing script file"""
        
        logger.info(f"📄 Loading script from: {script_file}")
        
        with open(script_file, 'r', encoding='utf-8') as f:
            script = f.read()
        
        self.script = script
        
        # Extract topic from script (first line or filename)
        topic = script_file.stem
        
        # Continue with generation
        return self.generate_video(
            topic=topic,
            num_scenes=num_images,
            style=style
        )
    
    def save_script(self, filename: str = "script.txt"):
        """Save generated script to file"""
        if self.script:
            script_path = file_handler.get_output_path(filename)
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(self.script)
            logger.info(f"💾 Script saved: {script_path}")
            return script_path
        return None
    
    def get_project_info(self) -> dict:
        """Get information about current project"""
        return {
            "script_length": len(self.script) if self.script else 0,
            "num_images": len(self.images),
            "audio_path": str(self.audio_path) if self.audio_path else None,
            "video_path": str(self.video_path) if self.video_path else None,
            "audio_duration": tts_engine.get_audio_duration(self.audio_path) if self.audio_path else 0
        }


def quick_generate(topic: str, num_scenes: int = 10, style: str = "cinematic"):
    """Quick video generation with default settings"""
    
    generator = VideoGenerator()
    video_path = generator.generate_video(
        topic=topic,
        num_scenes=num_scenes,
        style=style
    )
    
    # Save script
    generator.save_script(f"{topic.replace(' ', '_')}_script.txt")
    
    return video_path


def interactive_mode():
    """Interactive CLI mode"""
    
    logger.header("🎥 AI VIDEO GENERATOR - Interactive Mode")
    
    print("\nWelcome! Let's create an AI-generated video.\n")
    
    # Get user input
    topic = input("📝 Enter video topic: ").strip()
    
    if not topic:
        print("❌ Topic cannot be empty")
        return
    
    print("\n🎨 Available styles:")
    styles = ["horror", "mystery", "cinematic", "documentary", "fantasy", "sci-fi", "nature"]
    for i, style in enumerate(styles, 1):
        print(f"   {i}. {style}")
    
    style_choice = input(f"\nChoose style (1-{len(styles)}, default=1): ").strip()
    style = styles[int(style_choice) - 1] if style_choice.isdigit() and 1 <= int(style_choice) <= len(styles) else "horror"
    
    num_scenes = input("\n🎬 Number of scenes (default=10): ").strip()
    num_scenes = int(num_scenes) if num_scenes.isdigit() else 10
    
    print("\n🎙️ Available voices:")
    voices = tts_engine.list_available_voices()
    for i, voice in enumerate(voices[:5], 1):
        print(f"   {i}. {voice}")
    
    voice_choice = input(f"\nChoose voice (1-{len(voices[:5])}, default=1): ").strip()
    voice = voices[int(voice_choice) - 1] if voice_choice.isdigit() and 1 <= int(voice_choice) <= 5 else None
    
    print("\n" + "="*60)
    print(f"🎥 Generating video...")
    print(f"   Topic: {topic}")
    print(f"   Style: {style}")
    print(f"   Scenes: {num_scenes}")
    print("="*60 + "\n")
    
    # Generate
    generator = VideoGenerator()
    video_path = generator.generate_video(
        topic=topic,
        num_scenes=num_scenes,
        style=style,
        voice=voice
    )
    
    if video_path:
        # Save script
        generator.save_script(f"{topic.replace(' ', '_')}_script.txt")
        
        print("\n" + "="*60)
        print("🎉 SUCCESS!")
        print(f"📹 Video: {video_path}")
        print("="*60 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Video Generator")
    parser.add_argument("--topic", type=str, help="Video topic")
    parser.add_argument("--scenes", type=int, default=10, help="Number of scenes")
    parser.add_argument("--style", type=str, default="cinematic", help="Video style")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive or not args.topic:
        interactive_mode()
    else:
        quick_generate(args.topic, args.scenes, args.style)