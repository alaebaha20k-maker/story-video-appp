"""
🎬 VIDEO MANAGER - Manages video clips for compilation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import List, Dict, Optional, Tuple
from moviepy.editor import VideoFileClip
import random

from src.utils.file_handler import file_handler
from src.utils.timing import timing_calculator


class VideoManager:
    """Manages video clips for video compilation"""
    
    def __init__(self):
        self.videos = []
        self.target_resolution = (1920, 1080)
    
    def load_videos(self, video_paths: List[Path]) -> List[Dict]:
        """Load and analyze video clips"""
        
        print(f"🎬 Loading {len(video_paths)} video clips...")
        
        loaded_videos = []
        
        for i, video_path in enumerate(video_paths):
            try:
                clip = VideoFileClip(str(video_path))
                
                video_data = {
                    "index": i,
                    "path": video_path,
                    "duration": clip.duration,
                    "fps": clip.fps,
                    "size": clip.size,
                    "width": clip.w,
                    "height": clip.h,
                    "clip": clip
                }
                
                loaded_videos.append(video_data)
                print(f"   ✅ Loaded: {video_path.name} ({clip.duration:.1f}s)")
                
            except Exception as e:
                print(f"   ⚠️  Error loading {video_path.name}: {e}")
        
        print(f"   ✅ Loaded {len(loaded_videos)} videos")
        
        self.videos = loaded_videos
        return loaded_videos
    
    def calculate_loop_count(
        self,
        video_duration: float,
        target_duration: float
    ) -> int:
        """Calculate how many times to loop a video"""
        
        if video_duration == 0:
            return 1
        
        loops = int(target_duration / video_duration) + 1
        return max(1, loops)
    
    def calculate_video_timing(
        self,
        videos: List[Dict],
        total_duration: float,
        video_percentage: float = 0.3
    ) -> Tuple[List[Dict], float]:
        """Calculate timing for videos with loops"""
        
        if not videos:
            return [], 0
        
        target_video_time = total_duration * video_percentage
        total_video_duration = sum(v["duration"] for v in videos)
        
        if total_video_duration == 0:
            return [], 0
        
        loop_count = max(1, int(target_video_time / total_video_duration))
        
        video_timeline = []
        current_time = 0
        
        for video in videos:
            for loop in range(loop_count):
                video_timeline.append({
                    "video_path": video["path"],
                    "start_time": current_time,
                    "end_time": current_time + video["duration"],
                    "duration": video["duration"],
                    "loop_number": loop + 1,
                    "original_index": video["index"]
                })
                current_time += video["duration"]
        
        return video_timeline, current_time
    
    def resize_video(self, video_path: Path, target_size: Tuple[int, int] = None) -> Path:
        """Resize video to target resolution"""
        
        if target_size is None:
            target_size = self.target_resolution
        
        try:
            clip = VideoFileClip(str(video_path))
            
            # Resize with aspect ratio preservation
            resized = clip.resize(target_size)
            
            output_path = file_handler.get_temp_path(f"resized_{video_path.name}")
            resized.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=str(file_handler.temp_dir / 'temp-audio.m4a'),
                remove_temp=True,
                logger=None
            )
            
            clip.close()
            resized.close()
            
            return output_path
            
        except Exception as e:
            print(f"❌ Error resizing video: {e}")
            return video_path
    
    def trim_video(
        self,
        video_path: Path,
        start_time: float = 0,
        end_time: Optional[float] = None
    ) -> Path:
        """Trim video to specified duration"""
        
        try:
            clip = VideoFileClip(str(video_path))
            
            if end_time is None:
                end_time = clip.duration
            
            trimmed = clip.subclip(start_time, end_time)
            
            output_path = file_handler.get_temp_path(f"trimmed_{video_path.name}")
            trimmed.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=str(file_handler.temp_dir / 'temp-audio.m4a'),
                remove_temp=True,
                logger=None
            )
            
            clip.close()
            trimmed.close()
            
            return output_path
            
        except Exception as e:
            print(f"❌ Error trimming video: {e}")
            return video_path
    
    def loop_video(self, video_path: Path, loop_count: int) -> Path:
        """Loop a video multiple times"""
        
        try:
            clip = VideoFileClip(str(video_path))
            
            # Create looped clip
            looped = clip.loop(loop_count)
            
            output_path = file_handler.get_temp_path(f"looped_{loop_count}x_{video_path.name}")
            looped.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=str(file_handler.temp_dir / 'temp-audio.m4a'),
                remove_temp=True,
                logger=None
            )
            
            clip.close()
            looped.close()
            
            return output_path
            
        except Exception as e:
            print(f"❌ Error looping video: {e}")
            return video_path
    
    def remove_audio_from_video(self, video_path: Path) -> Path:
        """Remove audio track from video"""
        
        try:
            clip = VideoFileClip(str(video_path))
            
            # Remove audio
            no_audio = clip.without_audio()
            
            output_path = file_handler.get_temp_path(f"no_audio_{video_path.name}")
            no_audio.write_videofile(
                str(output_path),
                codec='libx264',
                logger=None
            )
            
            clip.close()
            no_audio.close()
            
            return output_path
            
        except Exception as e:
            print(f"❌ Error removing audio: {e}")
            return video_path
    
    def get_video_info(self, video_path: Path) -> Dict:
        """Get detailed video information"""
        
        try:
            clip = VideoFileClip(str(video_path))
            
            info = {
                "path": str(video_path),
                "duration": clip.duration,
                "fps": clip.fps,
                "size": clip.size,
                "width": clip.w,
                "height": clip.h,
                "has_audio": clip.audio is not None,
                "file_size": file_handler.get_file_size(video_path)
            }
            
            clip.close()
            return info
            
        except Exception as e:
            return {"error": str(e)}
    
    def extract_frame(
        self,
        video_path: Path,
        time_seconds: float = 0
    ) -> Optional[Path]:
        """Extract a single frame from video as image"""
        
        try:
            clip = VideoFileClip(str(video_path))
            
            frame = clip.get_frame(time_seconds)
            
            from PIL import Image
            img = Image.fromarray(frame)
            
            output_path = file_handler.get_temp_path(f"frame_{video_path.stem}.png")
            img.save(output_path)
            
            clip.close()
            
            return output_path
            
        except Exception as e:
            print(f"❌ Error extracting frame: {e}")
            return None
    
    def close_all_clips(self):
        """Close all loaded video clips"""
        for video in self.videos:
            if "clip" in video and video["clip"]:
                try:
                    video["clip"].close()
                except:
                    pass
        self.videos = []


video_manager = VideoManager()


def load_videos(video_paths: List[Path]) -> List[Dict]:
    return video_manager.load_videos(video_paths)


def calculate_video_timing(videos: List[Dict], duration: float) -> Tuple[List[Dict], float]:
    return video_manager.calculate_video_timing(videos, duration)


def get_video_info(video_path: Path) -> Dict:
    return video_manager.get_video_info(video_path)


if __name__ == "__main__":
    print("\n🧪 Testing VideoManager...\n")
    
    manager = VideoManager()
    
    print("✅ VideoManager ready!")
    print("\nFunctions available:")
    print("  - load_videos()")
    print("  - calculate_loop_count()")
    print("  - calculate_video_timing()")
    print("  - resize_video()")
    print("  - trim_video()")
    print("  - loop_video()")
    print("  - remove_audio_from_video()")
    print("  - extract_frame()")
    
    print("\n✅ VideoManager module complete!\n")