"""
🎬 VIDEO COMPILER - Compiles final video from all assets
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from moviepy.editor import (
    VideoClip, ImageClip, AudioFileClip, CompositeVideoClip,
    concatenate_videoclips, ColorClip
)
from typing import List, Dict, Optional
import random

from src.editor.effects import effects
from src.editor.transitions import transitions
from src.voice.audio_processor import audio_processor
from src.utils.file_handler import file_handler
from src.utils.logger import logger


class VideoCompiler:
    """Compiles final video from images, audio, and effects"""
    
    def __init__(self):
        self.resolution = (1920, 1080)
        self.fps = 30
        self.default_zoom = 1.1
    
    def create_video_from_images(
        self,
        image_timeline: List[Dict],
        audio_path: Path,
        output_filename: str = "final_video.mp4",
        effect_type: str = "simple_zoom",
        transition_type: str = "crossfade",
        transition_duration: float = 1.0
    ) -> Path:
        """Create video from images with audio"""
        
        logger.info(f"🎬 Compiling video from {len(image_timeline)} images...")
        
        # Create clips from images
        clips = []
        
        for i, item in enumerate(image_timeline):
            logger.info(f"   Processing image {i+1}/{len(image_timeline)}: {item['image_path'].name}")
            
            # Apply effect to image
            clip = effects.apply_effect(
                item['image_path'],
                item['duration'],
                effect_type
            )
            
            # Resize to target resolution
            clip = clip.resize(self.resolution)
            
            clips.append(clip)
        
        # Apply transitions
        logger.info(f"   Applying {transition_type} transitions...")
        
        if transition_type != "none":
            video = transitions.apply_transition(
                clips,
                transition_type,
                transition_duration
            )
        else:
            video = concatenate_videoclips(clips, method="compose")
        
        # Add audio
        logger.info("   Adding audio narration...")
        audio = AudioFileClip(str(audio_path))
        video = video.set_audio(audio)
        
        # Export video
        output_path = file_handler.get_output_path(output_filename)
        logger.info(f"   Rendering video to: {output_filename}")
        
        video.write_videofile(
            str(output_path),
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile=str(file_handler.temp_dir / 'temp-audio.m4a'),
            remove_temp=True,
            preset='medium',
            threads=4
        )
        
        # Clean up
        video.close()
        audio.close()
        for clip in clips:
            clip.close()
        
        logger.success(f"✅ Video compiled successfully!")
        return output_path
    
    def create_video_with_background_music(
        self,
        image_timeline: List[Dict],
        narration_path: Path,
        music_path: Optional[Path] = None,
        output_filename: str = "final_video.mp4",
        effect_type: str = "simple_zoom",
        transition_type: str = "crossfade",
        music_volume: int = -20
    ) -> Path:
        """Create video with narration and background music"""
        
        logger.info("🎵 Creating video with background music...")
        
        # If music provided, mix it with narration
        if music_path:
            logger.info("   Mixing narration with background music...")
            audio_path = audio_processor.overlay_audio(
                narration_path,
                music_path,
                volume_adjustment=music_volume,
                loop=True
            )
        else:
            audio_path = narration_path
        
        # Create video
        return self.create_video_from_images(
            image_timeline,
            audio_path,
            output_filename,
            effect_type,
            transition_type
        )
    
    def create_slideshow(
        self,
        image_paths: List[Path],
        duration_per_image: float = 3.0,
        output_filename: str = "slideshow.mp4",
        effect_type: str = "simple_zoom",
        transition_type: str = "crossfade"
    ) -> Path:
        """Create simple slideshow from images"""
        
        logger.info(f"📸 Creating slideshow from {len(image_paths)} images...")
        
        clips = []
        
        for img_path in image_paths:
            clip = effects.apply_effect(img_path, duration_per_image, effect_type)
            clip = clip.resize(self.resolution)
            clips.append(clip)
        
        # Apply transitions
        if transition_type != "none":
            video = transitions.apply_transition(clips, transition_type, 1.0)
        else:
            video = concatenate_videoclips(clips)
        
        # Export
        output_path = file_handler.get_output_path(output_filename)
        
        video.write_videofile(
            str(output_path),
            fps=self.fps,
            codec='libx264',
            preset='medium'
        )
        
        video.close()
        for clip in clips:
            clip.close()
        
        return output_path
    
    def add_intro_outro(
        self,
        video_path: Path,
        intro_text: Optional[str] = None,
        outro_text: Optional[str] = None,
        duration: float = 3.0
    ) -> Path:
        """Add intro/outro to video"""
        
        logger.info("🎬 Adding intro/outro...")
        
        clips = []
        
        # Intro
        if intro_text:
            intro = self._create_text_clip(intro_text, duration)
            clips.append(intro)
        
        # Main video
        main_video = VideoFileClip(str(video_path))
        clips.append(main_video)
        
        # Outro
        if outro_text:
            outro = self._create_text_clip(outro_text, duration)
            clips.append(outro)
        
        # Concatenate
        final = concatenate_videoclips(clips)
        
        # Export
        output_path = file_handler.get_output_path(f"with_intro_outro_{video_path.name}")
        
        final.write_videofile(
            str(output_path),
            fps=self.fps,
            codec='libx264'
        )
        
        final.close()
        main_video.close()
        
        return output_path
    
    def _create_text_clip(self, text: str, duration: float) -> VideoClip:
        """Create a simple text clip"""
        
        # Create black background
        clip = ColorClip(
            size=self.resolution,
            color=(0, 0, 0),
            duration=duration
        )
        
        # Note: Text requires TextClip which needs ImageMagick
        # For simplicity, returning black screen
        # You can add TextClip later if ImageMagick is installed
        
        return clip
    
    def get_random_effect(self) -> str:
        """Get random effect type"""
        effects = ["simple_zoom", "zoom_in", "zoom_out", "pan_right", "pan_left", "zoom_pan"]
        return random.choice(effects)
    
    def compile_quick(
        self,
        image_paths: List[Path],
        audio_path: Path,
        output_filename: str = "quick_video.mp4"
    ) -> Path:
        """Quick compilation with default settings"""
        
        logger.info("⚡ Quick compile mode...")
        
        # Calculate durations
        from src.voice.tts_engine import get_audio_duration
        audio_duration = get_audio_duration(audio_path)
        
        duration_per_image = audio_duration / len(image_paths)
        
        # Create timeline
        timeline = []
        current_time = 0
        
        for img_path in image_paths:
            timeline.append({
                "image_path": img_path,
                "start_time": current_time,
                "end_time": current_time + duration_per_image,
                "duration": duration_per_image
            })
            current_time += duration_per_image
        
        # Compile
        return self.create_video_from_images(
            timeline,
            audio_path,
            output_filename,
            effect_type="simple_zoom",
            transition_type="crossfade",
            transition_duration=1.0
        )


video_compiler = VideoCompiler()


def create_video(
    image_timeline: List[Dict],
    audio_path: Path,
    output_filename: str = "final_video.mp4"
) -> Path:
    return video_compiler.create_video_from_images(
        image_timeline,
        audio_path,
        output_filename
    )


def compile_quick(image_paths: List[Path], audio_path: Path, output_name: str) -> Path:
    return video_compiler.compile_quick(image_paths, audio_path, output_name)


if __name__ == "__main__":
    print("\n🧪 Testing VideoCompiler...\n")
    
    compiler = VideoCompiler()
    
    print("✅ VideoCompiler ready!")
    print("\nFunctions available:")
    print("  - create_video_from_images()")
    print("  - create_video_with_background_music()")
    print("  - create_slideshow()")
    print("  - add_intro_outro()")
    print("  - compile_quick()")
    
    print("\n✅ VideoCompiler module complete!\n")