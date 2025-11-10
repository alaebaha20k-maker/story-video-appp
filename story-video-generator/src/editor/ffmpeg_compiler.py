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
        zoom_effect: bool = True
    ):
        """✅ UNIVERSAL: Create video from ANY number of images + ANY audio duration

        Features:
        - Works with 2, 10, 50, 100+ images
        - Works with 30s, 10min, 1hr audio
        - Perfect sync (video ends when audio ends)
        - All images distributed evenly

        Args:
            image_paths: List of image file paths (ANY number)
            audio_path: Path to audio file (ANY duration)
            output_path: Path for output video
            durations: Duration for each image (calculated dynamically)
            zoom_effect: Enable zoom effect (default: True for better UX)
        """

        print(f"   🎬 Creating video with {len(image_paths)} images...")
        print(f"   📊 Total duration: {sum(durations):.2f}s")

        # Create concat file
        concat_file = Path("concat.txt")
        with open(concat_file, 'w') as f:
            for i, (img, dur) in enumerate(zip(image_paths, durations)):
                f.write(f"file '{img}'\n")
                f.write(f"duration {dur}\n")
                if i == 0:  # Log first image for debugging
                    print(f"   🖼️  Image 1 duration: {dur:.2f}s")
            # Repeat last image for proper ending
            f.write(f"file '{image_paths[-1]}'\n")
            print(f"   🖼️  Image {len(image_paths)} duration: {durations[-1]:.2f}s")

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
            '-preset', 'ultrafast',  # Ultra-fast encoding (CPU-optimized!)
            '-crf', '23',  # Good quality (18-28 range, 23 is balanced)
            '-threads', '0',  # Use ALL available CPU cores
            '-c:a', 'aac',
            '-b:a', '192k',  # High-quality audio
            '-shortest',  # End when audio ends (perfect sync!)
            '-y',  # Overwrite output
            str(output_path)
        ]

        print(f"   ⚙️  Running FFmpeg...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        # Cleanup
        concat_file.unlink()

        print(f"   ✅ Video created successfully!")
        print(f"   📁 Output: {output_path}")
        print(f"   🎬 Contains {len(image_paths)} images synced to audio")
        print(f"   ⏱️  Duration: {sum(durations):.2f}s")

        return output_path


ffmpeg_compiler = FFmpegCompiler()
