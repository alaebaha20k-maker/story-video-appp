"""
🎬 LOCAL FFMPEG VIDEO COMPILER
Process videos on your PC instead of uploading to Colab

ADVANTAGES:
- No upload needed (100x faster for large videos)
- Works offline
- Full quality
- Reliable
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Optional


def check_ffmpeg_installed() -> bool:
    """Check if FFmpeg is installed on system"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False


def escape_caption_text(text: str) -> str:
    """⚡ Escape text for FFmpeg drawtext filter"""
    # Remove ALL problematic characters
    text = text.replace("'", "")
    text = text.replace('"', "")
    text = text.replace("\\", "")
    text = text.replace(":", " -")
    text = text.replace(";", ",")
    text = text.replace("%", " percent")
    text = text.replace("&", " and ")
    text = text.replace("|", "-")
    text = text.replace("<", "")
    text = text.replace(">", "")
    text = text.replace("$", "")
    text = text.replace("#", "")
    text = text.replace("*", "")
    text = text.replace("_", " ")
    text = text.replace("@", " at ")
    text = text.replace("!", "")
    text = text.replace("?", "")
    text = text.replace("=", " equals ")
    text = text.replace("[", "")
    text = text.replace("]", "")
    text = text.replace("{", "")
    text = text.replace("}", "")
    text = text.replace("(", "")
    text = text.replace(")", "")
    text = text.replace("—", "-")
    text = text.replace("–", "-")

    # Clean up multiple spaces
    text = " ".join(text.split())

    # Limit length
    if len(text) > 50:
        text = text[:47] + "..."

    return text


def build_caption_drawtext_filter(caption_data: Dict) -> str:
    """Build FFmpeg drawtext filter from caption data"""

    # Caption style configurations
    CAPTION_STYLES = {
        'simple': {'fontsize': 48, 'fontcolor': 'white', 'borderw': 2, 'bordercolor': 'black'},
        'bold': {'fontsize': 56, 'fontcolor': 'white', 'borderw': 3, 'bordercolor': 'black'},
        'minimal': {'fontsize': 42, 'fontcolor': 'white', 'borderw': 1, 'bordercolor': 'black@0.5'},
        'cinematic': {'fontsize': 52, 'fontcolor': 'white', 'borderw': 2, 'bordercolor': 'black@0.8'},
        'horror': {'fontsize': 50, 'fontcolor': 'red', 'borderw': 3, 'bordercolor': 'black'},
        'elegant': {'fontsize': 46, 'fontcolor': 'white@0.95', 'borderw': 1, 'bordercolor': 'black@0.7'}
    }

    # Position configurations
    POSITIONS = {
        'top': "x='(w-text_w)/2':y=30",
        'bottom': "x='(w-text_w)/2':y='h-th-30'",
        'center': "x='(w-text_w)/2':y='(h-text_h)/2'"
    }

    text = escape_caption_text(caption_data.get('text', ''))
    style = caption_data.get('style', 'simple')
    position = caption_data.get('position', 'bottom')
    start_time = caption_data.get('start_time', 0)
    duration = caption_data.get('duration', 2)

    style_config = CAPTION_STYLES.get(style, CAPTION_STYLES['simple'])
    position_str = POSITIONS.get(position, POSITIONS['bottom'])

    # Build drawtext filter
    end_time = start_time + duration

    drawtext = (
        f"drawtext=text='{text}'"
        f":fontsize={style_config['fontsize']}"
        f":fontcolor={style_config['fontcolor']}"
        f":borderw={style_config['borderw']}"
        f":bordercolor={style_config['bordercolor']}"
        f":shadowx=2:shadowy=2"
        f":{position_str}"
        f":enable='between(t,{start_time},{end_time})'"
    )

    return drawtext


def compile_video_local(
    media_paths: List[Path],
    audio_path: Path,
    durations: List[float],
    output_path: Path,
    zoom_effect: bool = True,
    color_filter: str = 'none',
    grain_effect: bool = False,
    captions: Optional[List[Dict]] = None
) -> Path:
    """
    ⚡ LOCAL VIDEO COMPILATION - No Colab upload needed!

    Args:
        media_paths: List of image/video paths
        audio_path: Path to audio file
        durations: Duration for each media item
        output_path: Where to save final video
        zoom_effect: Enable zoom effect
        color_filter: Color filter (none, warm, cool, vintage, cinematic)
        grain_effect: Enable grain effect
        captions: List of caption dicts with timing

    Returns:
        Path to compiled video
    """

    print(f"\n🎬 Compiling video with LOCAL FFmpeg...")
    print(f"   Media: {len(media_paths)} items")
    print(f"   Zoom: {'ON' if zoom_effect else 'OFF'}")
    print(f"   Color Filter: {color_filter}")
    print(f"   Grain: {'ON' if grain_effect else 'OFF'}")
    if captions:
        print(f"   💬 Captions: {len(captions)} captions")

    # Check FFmpeg
    if not check_ffmpeg_installed():
        raise RuntimeError("FFmpeg not installed! Install from https://ffmpeg.org/download.html")

    # Detect media types
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    video_extensions = {'.mp4', '.mov', '.avi', '.webm'}

    temp_dir = Path("output/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)

    # STEP 1: Process each media item with effects
    processed_paths = []
    print(f"   🎨 Processing {len(media_paths)} media items...")

    for i, (media_path, duration) in enumerate(zip(media_paths, durations)):
        media_path = Path(media_path)
        processed_path = temp_dir / f"processed_{i:03d}.mp4"

        media_type = 'image' if media_path.suffix.lower() in image_extensions else 'video'

        # Build filter chain
        filters = []

        # Always scale and pad to 1920x1080
        filters.append("scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2")

        # Zoom effect (SLOW but looks good)
        if zoom_effect:
            if media_type == 'image':
                filters.append("zoompan=z='min(zoom+0.0015,1.1)':d=1:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):s=1920x1080")
            else:
                filters.append("zoompan=z='min(1+0.0015*on,1.05)':d=1:s=1920x1080")

        # Color filter
        if color_filter == 'warm':
            filters.append("eq=saturation=1.2:brightness=0.05,colorbalance=rs=0.1:gs=0:bs=-0.1")
        elif color_filter == 'cool':
            filters.append("eq=saturation=1.1:brightness=-0.02,colorbalance=rs=-0.1:gs=0:bs=0.1")
        elif color_filter == 'vintage':
            filters.append("curves=vintage,vignette=PI/4")
        elif color_filter == 'cinematic':
            filters.append("eq=contrast=1.1:saturation=0.9,colorbalance=rs=0.05:bs=-0.05")

        # Grain effect (VERY SLOW)
        if grain_effect:
            filters.append("noise=alls=10:allf=t+u")

        # FPS for images
        if media_type == 'image':
            filters.append("fps=24")

        video_filter = ','.join(filters)

        # Encode video clip
        if media_type == 'image':
            cmd = [
                'ffmpeg', '-y', '-loop', '1', '-i', str(media_path),
                '-t', str(duration),
                '-vf', video_filter,
                '-c:v', 'libx264', '-preset', 'veryfast',
                '-pix_fmt', 'yuv420p',
                str(processed_path)
            ]
        else:
            cmd = [
                'ffmpeg', '-y', '-i', str(media_path),
                '-t', str(duration),
                '-vf', video_filter,
                '-c:v', 'libx264', '-preset', 'veryfast',
                '-c:a', 'copy',
                str(processed_path)
            ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"      ✅ {i+1}/{len(media_paths)}: {media_type}")
        else:
            print(f"      ⚠️  {i+1}/{len(media_paths)}: FFmpeg error")

        processed_paths.append(processed_path)

    # STEP 2: Concatenate all clips
    print(f"   🎬 Concatenating {len(processed_paths)} clips...")
    concat_file = temp_dir / "concat.txt"
    with open(concat_file, 'w') as f:
        for path in processed_paths:
            f.write(f"file '{path.absolute()}'\n")

    temp_video_path = temp_dir / "temp_video.mp4"

    cmd = [
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', str(concat_file),
        '-c:v', 'copy',
        str(temp_video_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Concatenation failed: {result.stderr[:200]}")

    # STEP 3: Add captions if provided
    if captions and len(captions) > 0:
        print(f"   💬 Adding {len(captions)} captions...")

        # Build all drawtext filters
        caption_filters = []
        for caption in captions:
            drawtext = build_caption_drawtext_filter(caption)
            caption_filters.append(drawtext)

        # Combine all caption filters
        all_caption_filters = ','.join(caption_filters)

        # Apply captions
        captioned_video_path = temp_dir / "captioned_video.mp4"

        cmd = [
            'ffmpeg', '-y', '-i', str(temp_video_path),
            '-vf', all_caption_filters,
            '-c:v', 'libx264', '-preset', 'veryfast',
            '-c:a', 'copy',
            str(captioned_video_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Captions added!")
            temp_video_path = captioned_video_path
        else:
            print(f"   ⚠️  Caption rendering failed, continuing without captions...")

    # STEP 4: Add audio
    print(f"   🎵 Adding audio...")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        'ffmpeg', '-y',
        '-i', str(temp_video_path),
        '-i', str(audio_path),
        '-c:v', 'copy',
        '-c:a', 'aac', '-b:a', '192k',
        '-shortest',
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Audio merge failed: {result.stderr[:200]}")

    # Cleanup
    for path in processed_paths + [concat_file, temp_video_path]:
        if Path(path).exists():
            Path(path).unlink()

    print(f"   ✅ Video compiled: {output_path.name}")
    return output_path


# Test function
if __name__ == '__main__':
    print("Testing LOCAL FFmpeg compiler...")

    if check_ffmpeg_installed():
        print("✅ FFmpeg is installed!")
    else:
        print("❌ FFmpeg NOT installed!")
