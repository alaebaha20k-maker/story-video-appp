"""
🎞️ TRANSITIONS - Video transitions between clips
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from moviepy.editor import VideoClip, ImageClip, concatenate_videoclips, CompositeVideoClip
from moviepy.video.fx import fadein, fadeout
from typing import List


class Transitions:
    """Transitions between video clips"""
    
    def __init__(self):
        self.default_duration = 1.0
    
    def crossfade(
        self,
        clip1: VideoClip,
        clip2: VideoClip,
        duration: float = 1.0
    ) -> VideoClip:
        """Crossfade transition between two clips"""
        
        # Fade out first clip
        clip1 = clip1.fadeout(duration)
        
        # Fade in second clip
        clip2 = clip2.fadein(duration)
        
        # Overlap them
        clip2 = clip2.set_start(clip1.duration - duration)
        
        # Composite
        final = CompositeVideoClip([clip1, clip2])
        
        return final
    
    def fade_transition(
        self,
        clip1: VideoClip,
        clip2: VideoClip,
        fade_duration: float = 1.0
    ) -> VideoClip:
        """Simple fade transition (fade out then fade in)"""
        
        clip1 = clip1.fadeout(fade_duration)
        clip2 = clip2.fadein(fade_duration)
        
        return concatenate_videoclips([clip1, clip2])
    
    def concatenate_with_crossfade(
        self,
        clips: List[VideoClip],
        crossfade_duration: float = 1.0
    ) -> VideoClip:
        """Concatenate multiple clips with crossfade transitions"""
        
        if not clips:
            return None
        
        if len(clips) == 1:
            return clips[0]
        
        # First clip
        result = clips[0].fadeout(crossfade_duration)
        
        # Add remaining clips with crossfade
        for i in range(1, len(clips)):
            clip = clips[i]
            
            # Fade in current clip
            clip = clip.fadein(crossfade_duration)
            
            # Set start time to overlap with previous clip
            clip = clip.set_start(result.duration - crossfade_duration)
            
            # If it's not the last clip, fade it out
            if i < len(clips) - 1:
                clip = clip.fadeout(crossfade_duration)
            
            # Composite
            result = CompositeVideoClip([result, clip])
        
        return result
    
    def concatenate_simple(
        self,
        clips: List[VideoClip],
        method: str = "compose"
    ) -> VideoClip:
        """Simple concatenation without transitions"""
        
        return concatenate_videoclips(clips, method=method)
    
    def apply_transition(
        self,
        clips: List[VideoClip],
        transition_type: str = "crossfade",
        duration: float = 1.0
    ) -> VideoClip:
        """Apply transition based on type"""
        
        if not clips:
            return None
        
        if len(clips) == 1:
            return clips[0]
        
        if transition_type == "crossfade":
            return self.concatenate_with_crossfade(clips, duration)
        elif transition_type == "fade":
            result = clips[0].fadeout(duration)
            for clip in clips[1:]:
                clip = clip.fadein(duration)
                result = concatenate_videoclips([result, clip])
            return result
        elif transition_type == "none":
            return self.concatenate_simple(clips)
        else:
            return self.concatenate_with_crossfade(clips, duration)


transitions = Transitions()


def apply_transition(clips: List[VideoClip], transition_type: str, duration: float) -> VideoClip:
    return transitions.apply_transition(clips, transition_type, duration)


def crossfade(clip1: VideoClip, clip2: VideoClip, duration: float = 1.0) -> VideoClip:
    return transitions.crossfade(clip1, clip2, duration)


if __name__ == "__main__":
    print("\n🧪 Testing Transitions...\n")
    
    trans = Transitions()
    
    print("✅ Transitions ready!")
    print("\nAvailable transitions:")
    print("  - crossfade")
    print("  - fade")
    print("  - none (simple concatenation)")
    
    print("\n✅ Transitions module complete!\n")