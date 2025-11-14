# 🎬 COLAB NOTEBOOK UPDATE - Mixed Media Support

## What Changed?

The backend now supports **INTELLIGENT MEDIA MIXING**:
- Images from SDXL-Turbo ✅
- User-uploaded images ✅
- User-uploaded videos ✅
- Stock photos from Pexels ✅
- Stock videos from Pexels ✅
- ANY combination of the above ✅

## Colab `/compile_video` Endpoint Update Needed

### Current Payload Format (OLD):
```python
{
    'images': [base64_img1, base64_img2, ...],  # Only images
    'audio': base64_audio,
    'durations': [5.0, 5.0, 5.0, ...],
    'effects': {
        'zoom_effect': True,
        'color_filter': 'cinematic',
        'grain_effect': False,
        'captions': {}
    }
}
```

### New Payload Format (UPDATED):
```python
{
    'media': [base64_media1, base64_media2, ...],     # Images AND videos
    'media_types': ['image', 'video', 'image', ...],  # Type of each item
    'audio': base64_audio,
    'durations': [5.0, 3.5, 7.2, ...],               # Intelligent durations
    'effects': {
        'zoom_effect': True,
        'color_filter': 'cinematic',
        'grain_effect': False,
        'captions': {}
    }
}
```

## Changes Required in Colab Notebook

### 1. Update `/compile_video` Endpoint

**Location:** Cell with Flask endpoint definitions

**OLD CODE:**
```python
@app.route('/compile_video', methods=['POST'])
def compile_video():
    data = request.json
    images_data = data['images']      # Only images
    audio_data = data['audio']
    durations = data['durations']
    effects = data.get('effects', {})

    # ... rest of code
```

**NEW CODE:**
```python
@app.route('/compile_video', methods=['POST'])
def compile_video():
    data = request.json
    media_data = data['media']              # Changed: media instead of images
    media_types = data['media_types']       # NEW: type of each media item
    audio_data = data['audio']
    durations = data['durations']
    effects = data.get('effects', {})

    # ... rest of code
```

### 2. Update FFmpeg Compilation Logic

**You need to handle BOTH images and videos:**

```python
def compile_video_with_effects(media_data, media_types, audio_data, durations, effects):
    """
    Compile video from MIXED MEDIA (images + videos)

    Args:
        media_data: List of base64-encoded media (images AND videos)
        media_types: List of 'image' or 'video' for each item
        audio_data: Base64-encoded audio
        durations: Duration for each media item
        effects: Effects dict (zoom, color, grain, captions)
    """

    # Save audio
    audio_path = '/tmp/audio.wav'
    with open(audio_path, 'wb') as f:
        f.write(base64.b64decode(audio_data))

    # Save and process each media item
    media_files = []

    for i, (media_b64, media_type, duration) in enumerate(zip(media_data, media_types, durations)):
        if media_type == 'image':
            # Handle IMAGE
            img_path = f'/tmp/media_{i:03d}.png'
            with open(img_path, 'wb') as f:
                f.write(base64.b64decode(media_b64))

            # Convert image to video clip with duration
            clip_path = f'/tmp/clip_{i:03d}.mp4'

            # Build FFmpeg filter for THIS image
            filters = []

            # Zoom effect (Ken Burns)
            if effects.get('zoom_effect', True):
                filters.append("zoompan=z='min(zoom+0.0015,1.1)':d=1:fps=30:s=1920x1080")

            # Color filter
            color_filter = effects.get('color_filter', 'none')
            if color_filter == 'warm':
                filters.append("eq=saturation=1.2:brightness=0.05,colorbalance=rs=0.1:gs=-0.05:bs=-0.1")
            elif color_filter == 'cool':
                filters.append("eq=saturation=1.1:brightness=-0.02,colorbalance=rs=-0.1:bs=0.1")
            elif color_filter == 'vintage':
                filters.append("curves=vintage,vignette=PI/4")
            elif color_filter == 'cinematic':
                filters.append("eq=contrast=1.1:saturation=0.9,colorbalance=rs=0.05:bs=0.05")

            # Grain effect
            if effects.get('grain_effect', False):
                filters.append("noise=alls=10:allf=t+u")

            # Combine filters
            filter_str = ','.join(filters) if filters else 'scale=1920:1080'

            # Create video clip from image
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', img_path,
                '-vf', filter_str,
                '-t', str(duration),
                '-r', '30',
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                clip_path
            ]
            subprocess.run(cmd, check=True)
            media_files.append(clip_path)

        elif media_type == 'video':
            # Handle VIDEO
            video_path = f'/tmp/media_{i:03d}.mp4'
            with open(video_path, 'wb') as f:
                f.write(base64.b64decode(media_b64))

            # Process video clip with effects
            clip_path = f'/tmp/clip_{i:03d}.mp4'

            # Build FFmpeg filter for THIS video
            filters = []

            # Trim/extend to match duration
            filters.append(f"trim=duration={duration},setpts=PTS-STARTPTS")

            # Zoom effect (applies to video too!)
            if effects.get('zoom_effect', True):
                filters.append("zoompan=z='min(zoom+0.0015,1.1)':d=1:fps=30:s=1920x1080")

            # Color filter (same as images)
            color_filter = effects.get('color_filter', 'none')
            if color_filter == 'warm':
                filters.append("eq=saturation=1.2:brightness=0.05,colorbalance=rs=0.1:gs=-0.05:bs=-0.1")
            elif color_filter == 'cool':
                filters.append("eq=saturation=1.1:brightness=-0.02,colorbalance=rs=-0.1:bs=0.1")
            elif color_filter == 'vintage':
                filters.append("curves=vintage,vignette=PI/4")
            elif color_filter == 'cinematic':
                filters.append("eq=contrast=1.1:saturation=0.9,colorbalance=rs=0.05:bs=0.05")

            # Grain effect (same as images)
            if effects.get('grain_effect', False):
                filters.append("noise=alls=10:allf=t+u")

            # Ensure 1920x1080
            filters.append("scale=1920:1080")

            filter_str = ','.join(filters)

            # Process video clip
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-vf', filter_str,
                '-t', str(duration),
                '-r', '30',
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                clip_path
            ]
            subprocess.run(cmd, check=True)
            media_files.append(clip_path)

    # Concatenate all clips
    concat_file = '/tmp/concat_list.txt'
    with open(concat_file, 'w') as f:
        for clip_path in media_files:
            f.write(f"file '{clip_path}'\\n")

    # Merge clips and add audio
    output_path = '/tmp/final_video.mp4'
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_file,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-strict', 'experimental',
        output_path
    ]
    subprocess.run(cmd, check=True)

    # Read and return video
    with open(output_path, 'rb') as f:
        video_bytes = f.read()

    return video_bytes
```

## Testing

### Test 1: Only Images (Existing)
```python
{
    'media': [img1, img2, img3],
    'media_types': ['image', 'image', 'image'],
    'audio': audio,
    'durations': [5.0, 5.0, 5.0],
    'effects': {}
}
```

### Test 2: Only Videos (New)
```python
{
    'media': [vid1, vid2],
    'media_types': ['video', 'video'],
    'audio': audio,
    'durations': [10.0, 15.0],
    'effects': {}
}
```

### Test 3: Mixed (New - MOST IMPORTANT)
```python
{
    'media': [img1, vid1, img2, img3, vid2],
    'media_types': ['image', 'video', 'image', 'image', 'video'],
    'audio': audio,
    'durations': [5.0, 8.0, 6.0, 4.0, 10.0],  # Total: 33s
    'effects': {
        'zoom_effect': True,
        'color_filter': 'cinematic',
        'grain_effect': True
    }
}
```

## Summary of Backend Changes

**What's New:**
1. ✅ Intelligent Media Manager (`src/media/intelligent_media_manager.py`)
   - Handles all 7 modes (ai_only, manual_only, stock_only, mixes)
   - Integrates Pexels stock downloader
   - Supports user uploads

2. ✅ Smart Duration Calculator (`src/utils/smart_duration_calculator.py`)
   - Calculates perfect timing for mixed media
   - Videos use natural duration
   - Images fill remaining time intelligently
   - Total ALWAYS matches audio duration

3. ✅ Updated api_server.py
   - Uses intelligent media manager
   - Uses smart duration calculator
   - Sends mixed media to Colab

4. ✅ Updated colab_client.py
   - `compile_video()` now accepts `media_paths` (not `image_paths`)
   - Detects image vs video
   - Sends `media` + `media_types` arrays

**What Colab Needs:**
- Update `/compile_video` endpoint to handle `media` + `media_types`
- Process both images AND videos
- Apply ALL effects to both media types
- Concatenate clips correctly

## Ready to Update Colab? 🚀

Copy the FFmpeg logic above into your Colab notebook and test!
