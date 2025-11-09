"""
⚡ FFMPEG COMPILER - Ultra-fast GPU rendering
"""

import subprocess
from pathlib import Path
from typing import List

class FFmpegCompiler:

    def create_video(
        self,
        image_paths: List[Path],
        audio_path: Path,
        output_path: Path,
        durations: List[float],
        zoom_effect: bool = True
    ):
        """Create video with FFmpeg - FAST!

        Args:
            image_paths: List of image file paths
            audio_path: Path to audio file
            output_path: Path for output video
            durations: Duration for each image
            zoom_effect: Enable zoom effect (default: True for better UX)
        """

        # Create concat file
        concat_file = Path("concat.txt")
        with open(concat_file, 'w') as f:
            for img, dur in zip(image_paths, durations):
                f.write(f"file '{img}'\n")
                f.write(f"duration {dur}\n")
            # Repeat last image
            f.write(f"file '{image_paths[-1]}'\n")

        # Build video filter based on zoom_effect setting
        if zoom_effect:
            # Zoom effect: gentle zoom in for cinematic feel
            video_filter_parts = (
                "scale=1920:1080,"
                "zoompan=z='min(zoom+0.0015,1.1)':d=1:"
                "x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):s=1920x1080,"
                "fps=24"
            )
            video_filter = ''.join(video_filter_parts)
        else:
            # No zoom: simple scale
            video_filter = 'scale=1920:1080,fps=24'

        # FFmpeg command
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-i', str(audio_path),
            '-vf', video_filter,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-c:a', 'aac',
            '-shortest',
            '-y',
            str(output_path)
        ]

        subprocess.run(cmd, check=True)
        concat_file.unlink()

        return output_path

ffmpeg_compiler = FFmpegCompiler()
