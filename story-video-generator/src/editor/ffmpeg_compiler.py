"""
⚡ FFMPEG COMPILER - Ultra-fast rendering with filters and captions
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
        auto_captions: Optional[List[Dict]] = None
    ):
        """Create video with FFmpeg - FAST with filters and captions!"""
        
        # Create concat file
        concat_file = Path("concat.txt")
        with open(concat_file, 'w') as f:
            for img, dur in zip(image_paths, durations):
                f.write(f"file '{img}'\n")
                f.write(f"duration {dur}\n")
            # Repeat last image
            f.write(f"file '{image_paths[-1]}'\n")
        
        # Build filter chain
        filters = ['scale=1920:1080', 'fps=24']
        
        # Add zoom effect if enabled
        if zoom_effect:
            # Simple constant zoom (Ken Burns style) - FAST
            filters.append("zoompan=z='min(zoom+0.0015,1.05)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080")
        
        # Add color filter if specified
        if color_filter and color_filter != 'none':
            from src.editor.filters import video_filters
            color_filter_str = video_filters.get_filter_string(color_filter)
            if color_filter_str:
                filters.append(color_filter_str)
        
        # Add auto captions (multiple timed captions) - PRIORITY
        if auto_captions:
            from src.editor.captions import caption_generator
            multi_caption_filter = caption_generator.build_multi_caption_filter(auto_captions)
            if multi_caption_filter:
                filters.append(multi_caption_filter)
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
        
        # Join all filters
        filter_string = ','.join(filters)
        
        # FFmpeg command - OPTIMIZED for CPU speed with filters
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-i', str(audio_path),
            '-vf', filter_string,
            '-c:v', 'libx264',
            '-preset', 'ultrafast',  # Ultra-fast encoding (3-5x faster)
            '-crf', '23',  # Maintain quality with CRF
            '-threads', '0',  # Use all available CPU threads
            '-c:a', 'aac',
            '-b:a', '192k',  # Good audio bitrate
            '-shortest',
            '-y',
            str(output_path)
        ]
        
        subprocess.run(cmd, check=True)
        concat_file.unlink()
        
        return output_path

ffmpeg_compiler = FFmpegCompiler()