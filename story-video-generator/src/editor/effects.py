"""
✨ EFFECTS - Visual effects for images and videos
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from moviepy.editor import ImageClip, CompositeVideoClip
from moviepy.video.fx import resize
import numpy as np
from typing import Tuple, Optional

from src.utils.file_handler import file_handler


class Effects:
    """Visual effects for video creation"""
    
    def __init__(self):
        self.default_resolution = (1920, 1080)
    
    def apply_simple_zoom(
        self,
        image_path: Path,
        duration: float,
        zoom_factor: float = 1.1,
        direction: str = "in"
    ) -> ImageClip:
        """Apply simple zoom effect (FAST)"""
        
        clip = ImageClip(str(image_path)).set_duration(duration)
        
        if direction == "in":
            # Zoom in: start 100%, end 110%
            clip = clip.resize(lambda t: 1 + (zoom_factor - 1) * (t / duration))
        elif direction == "out":
            # Zoom out: start 110%, end 100%
            clip = clip.resize(lambda t: zoom_factor - (zoom_factor - 1) * (t / duration))
        else:
            # Static
            pass
        
        return clip
    
    def apply_pan(
        self,
        image_path: Path,
        duration: float,
        direction: str = "right"
    ) -> ImageClip:
        """Apply pan effect"""
        
        clip = ImageClip(str(image_path)).set_duration(duration)
        clip = clip.resize(1.2)  # Scale up to allow panning
        
        w, h = self.default_resolution
        
        if direction == "right":
            clip = clip.set_position(lambda t: (-100 * t / duration, 'center'))
        elif direction == "left":
            clip = clip.set_position(lambda t: (100 * t / duration, 'center'))
        elif direction == "up":
            clip = clip.set_position(lambda t: ('center', -100 * t / duration))
        elif direction == "down":
            clip = clip.set_position(lambda t: ('center', 100 * t / duration))
        
        return clip
    
    def apply_zoom_pan(
        self,
        image_path: Path,
        duration: float,
        zoom_factor: float = 1.2
    ) -> ImageClip:
        """Combine zoom and pan (Ken Burns style but simplified)"""
        
        clip = ImageClip(str(image_path)).set_duration(duration)
        
        # Zoom
        clip = clip.resize(lambda t: 1 + (zoom_factor - 1) * (t / duration))
        
        # Pan slightly
        clip = clip.set_position(lambda t: (-50 * t / duration, -30 * t / duration))
        
        return clip
    
    def apply_static(self, image_path: Path, duration: float) -> ImageClip:
        """No effect, just static image"""
        
        clip = ImageClip(str(image_path)).set_duration(duration)
        return clip
    
    def apply_effect(
        self,
        image_path: Path,
        duration: float,
        effect_type: str = "simple_zoom"
    ) -> ImageClip:
        """Apply effect based on type"""
        
        if effect_type == "simple_zoom":
            return self.apply_simple_zoom(image_path, duration)
        elif effect_type == "zoom_in":
            return self.apply_simple_zoom(image_path, duration, direction="in")
        elif effect_type == "zoom_out":
            return self.apply_simple_zoom(image_path, duration, direction="out")
        elif effect_type == "pan_right":
            return self.apply_pan(image_path, duration, direction="right")
        elif effect_type == "pan_left":
            return self.apply_pan(image_path, duration, direction="left")
        elif effect_type == "zoom_pan":
            return self.apply_zoom_pan(image_path, duration)
        elif effect_type == "static":
            return self.apply_static(image_path, duration)
        else:
            return self.apply_simple_zoom(image_path, duration)
    
    def apply_fade_in(self, clip: ImageClip, duration: float = 1.0) -> ImageClip:
        """Apply fade in effect"""
        return clip.fadein(duration)
    
    def apply_fade_out(self, clip: ImageClip, duration: float = 1.0) -> ImageClip:
        """Apply fade out effect"""
        return clip.fadeout(duration)
    
    def apply_fade_in_out(
        self,
        clip: ImageClip,
        fade_duration: float = 1.0
    ) -> ImageClip:
        """Apply both fade in and fade out"""
        return clip.fadein(fade_duration).fadeout(fade_duration)


effects = Effects()


def apply_effect(image_path: Path, duration: float, effect_type: str) -> ImageClip:
    return effects.apply_effect(image_path, duration, effect_type)


if __name__ == "__main__":
    print("\n🧪 Testing Effects...\n")
    
    fx = Effects()
    
    print("✅ Effects ready!")
    print("\nAvailable effects:")
    print("  - simple_zoom")
    print("  - zoom_in")
    print("  - zoom_out")
    print("  - pan_right/left")
    print("  - zoom_pan")
    print("  - static")
    
    print("\n✅ Effects module complete!\n")