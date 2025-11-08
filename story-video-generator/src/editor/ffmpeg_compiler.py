"""
⚡ FFMPEG COMPILER - Ultra-fast GPU rendering with zoom effects
"""

import subprocess
from pathlib import Path
from typing import List
import os

class FFmpegCompiler:

    def create_video(
        self,
        image_paths: List[Path],
        audio_path: Path,
        output_path: Path,
        durations: List[float],
        enable_zoom: bool = True
    ):
        """Create video with FFmpeg - FAST with zoom effects!"""

        print(f"🎬 Creating video with {len(image_paths)} images...")
        if enable_zoom:
            print("   ✨ Zoom effects: ENABLED")

        # Create individual video clips with zoom for each image
        temp_clips = []
        temp_dir = Path("output/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)

        for i, (img, dur) in enumerate(zip(image_paths, durations)):
            temp_clip = temp_dir / f"clip_{i:03d}.mp4"

            if enable_zoom:
                # Ken Burns effect: smooth zoom in
                # zoompan filter: zoom from 1.0 to 1.1 over duration
                zoom_filter = (
                    f"zoompan=z='min(zoom+0.0015,1.1)':d={int(dur*24)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=24,"
                    f"fade=t=in:st=0:d=0.5,fade=t=out:st={dur-0.5}:d=0.5"
                )
            else:
                zoom_filter = "scale=1920:1080,fps=24"

            cmd = [
                'ffmpeg',
                '-loop', '1',
                '-i', str(img),
                '-vf', zoom_filter,
                '-t', str(dur),
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-pix_fmt', 'yuv420p',
                '-y',
                str(temp_clip)
            ]

            subprocess.run(cmd, check=True, capture_output=True)
            temp_clips.append(temp_clip)
            print(f"   ✅ Processed {i+1}/{len(image_paths)}: {img.name}")

        # Create concat file for all clips
        concat_file = temp_dir / "concat.txt"
        with open(concat_file, 'w') as f:
            for clip in temp_clips:
                f.write(f"file '{clip.absolute()}'\n")

        # Concatenate all clips and add audio
        print("   🎵 Adding audio and merging clips...")
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-i', str(audio_path),
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-shortest',
            '-y',
            str(output_path)
        ]

        subprocess.run(cmd, check=True)

        # Cleanup temp files
        concat_file.unlink()
        for clip in temp_clips:
            clip.unlink()

        print(f"   ✅ Video created: {output_path.name}")

        return output_path

ffmpeg_compiler = FFmpegCompiler()