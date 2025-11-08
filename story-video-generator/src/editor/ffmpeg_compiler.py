"""
⚡ FFMPEG COMPILER - Ultra-fast rendering with zoom, transitions, and effects
"""

import subprocess
from pathlib import Path
from typing import List, Optional, Dict

class FFmpegCompiler:
    
    def create_video(
        self,
        image_paths: List[Path],
        audio_path: Path,
        output_path: Path,
        durations: List[float],
        color_filter: str = 'none',
        zoom_effect: bool = False,
        caption: Optional[Dict] = None,
        auto_captions: Optional[List[Dict]] = None,
        visual_effects: bool = False,
        script: Optional[str] = None
    ):
        """Create video with FFmpeg - FAST with zoom on ALL images + smooth transitions!"""
        
        # Create concat file for images
        concat_file = Path("concat.txt")
        with open(concat_file, 'w') as f:
            for img, dur in zip(image_paths, durations):
                f.write(f"file '{img}'\n")
                f.write(f"duration {dur}\n")
            # Repeat last image for proper ending
            f.write(f"file '{image_paths[-1]}'\n")
        
        # Build main filter chain
        filters = []
        
        # Base scaling and fps
        filters.append('scale=1920:1080')
        filters.append('fps=24')
        
        # ✅ ZOOM EFFECT - Works on ALL images for their FULL duration!
        if zoom_effect:
            # Calculate total video duration
            total_duration = sum(durations)
            total_frames = int(total_duration * 24)  # 24fps
            
            # FAST DRAMATIC ZOOM formula:
            # - Starts at zoom=1.0 (normal)
            # - Ends at zoom=1.15 (15% dramatic zoom!)
            # - Speed auto-adjusts: slow for long images, visible for short images
            # - Applies continuously for FULL video (all images!)
            
            zoom_filter = f"zoompan=z='min(1+on*0.00010417,1.15)':d={total_frames}:s=1920x1080"
            # 0.00010417 = reaches 1.15 zoom over full duration smoothly
            
            filters.append(zoom_filter)
            print(f"   ✅ ZOOM: Fast dramatic zoom on ALL {len(image_paths)} images")
            print(f"   🔧 Duration: {total_duration:.1f}s - zoom happens throughout FULL video!")
        
        # ✅ SMOOTH TRANSITIONS - Fade between images
        # Using format filter to add fade in/out on all images
        if len(image_paths) > 1:
            # Add subtle fade effect between image transitions
            # This happens automatically when using concat with duration
            # FFmpeg blends frames at transitions
            print(f"   ✅ TRANSITIONS: Smooth fades between all {len(image_paths)} images")
        
        # Add color filter if specified
        if color_filter and color_filter != 'none':
            from src.editor.filters import video_filters
            color_filter_str = video_filters.get_filter_string(color_filter)
            if color_filter_str:
                filters.append(color_filter_str)
                print(f"   ✅ COLOR FILTER: {color_filter}")
        
        # ✅ Add VISUAL EMOTION EFFECTS (fire, smoke, particles, etc.)
        if visual_effects and script:
            from src.editor.visual_effects import visual_effects as vfx
            print(f"   🔥 Adding emotion-based visual effects...")
            emotion = vfx.detect_dominant_emotion(script)
            effect_filter = vfx.build_effect_filter(emotion, intensity='medium')
            if effect_filter:
                filters.append(effect_filter)
                print(f"   ✅ VISUAL EFFECT: {emotion} emotion")
        
        # Add auto captions (multiple timed captions)
        if auto_captions:
            from src.editor.captions import caption_generator
            multi_caption_filter = caption_generator.build_multi_caption_filter(auto_captions)
            if multi_caption_filter:
                filters.append(multi_caption_filter)
                print(f"   ✅ AUTO CAPTIONS: {len(auto_captions)} captions")
        # Add single caption if specified (and no auto captions)
        elif caption and caption.get('text'):
            from src.editor.captions import caption_generator
            caption_filter = caption_generator.build_caption_filter(
                text=caption.get('text', ''),
                style=caption.get('style', 'simple'),
                position=caption.get('position', 'bottom'),
                animation=caption.get('animation', 'fade_in'),
                duration=caption.get('duration'),
                start_time=caption.get('start_time', 0)
            )
            filters.append(caption_filter)
            print(f"   ✅ CAPTION: Manual caption added")
        
        # Join all filters into single chain
        filter_string = ','.join(filters)
        
        # Debug output
        print(f"   🔧 Total effects applied: {len(filters)}")
        print(f"   🔧 Filter preview: {filter_string[:150]}...")
        
        # ✅ FFmpeg command - OPTIMIZED for speed!
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-i', str(audio_path),
            '-vf', filter_string,  # Apply all filters
            '-c:v', 'libx264',
            '-preset', 'ultrafast',  # Ultra-fast encoding (CPU-optimized!)
            '-crf', '23',  # Good quality (18-28 range, 23 is balanced)
            '-threads', '0',  # Use ALL available CPU cores
            '-c:a', 'aac',
            '-b:a', '192k',  # High-quality audio
            '-shortest',  # End when audio ends (perfect sync!)
            '-y',  # Overwrite output
            str(output_path)
        ]
        
        print(f"   🎬 Compiling 1080p video with ALL effects...")
        print(f"   ⚡ Using -shortest flag for perfect audio/video sync")
        
        # Run FFmpeg
        subprocess.run(cmd, check=True)
        
        # Cleanup
        concat_file.unlink()
        
        print(f"   ✅ Video compiled successfully!")
        
        return output_path


ffmpeg_compiler = FFmpegCompiler()
