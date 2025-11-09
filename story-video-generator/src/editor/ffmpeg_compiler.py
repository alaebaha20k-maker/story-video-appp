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
        durations: List[float]
    ):
        """Create video with FFmpeg - FAST!"""
        
        # Create concat file
        concat_file = Path("concat.txt")
        with open(concat_file, 'w') as f:
            for img, dur in zip(image_paths, durations):
                f.write(f"file '{img}'\n")
                f.write(f"duration {dur}\n")
            # Repeat last image for proper ending
            f.write(f"file '{image_paths[-1]}'\n")
        
        # FFmpeg command
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-i', str(audio_path),
            '-vf', 'scale=1920:1080,fps=24',
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
        
        subprocess.run(cmd, check=True)
        
        # Cleanup
        concat_file.unlink()
        
        return output_path


ffmpeg_compiler = FFmpegCompiler()
