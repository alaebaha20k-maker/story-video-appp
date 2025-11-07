"""
📝 CAPTIONS - Fast text overlays with effects using FFmpeg
"""

from typing import Optional, List, Dict
from pathlib import Path


class CaptionGenerator:
    """Generate captions with effects using FFmpeg drawtext - FAST"""
    
    # Caption styles (optimized for readability and speed)
    CAPTION_STYLES = {
        'simple': {
            'fontsize': 48,
            'fontcolor': 'white',
            'borderw': 2,
            'bordercolor': 'black',
            'shadowx': 2,
            'shadowy': 2
        },
        'bold': {
            'fontsize': 56,
            'fontcolor': 'white',
            'borderw': 3,
            'bordercolor': 'black',
            'shadowx': 3,
            'shadowy': 3
        },
        'minimal': {
            'fontsize': 42,
            'fontcolor': 'white',
            'borderw': 1,
            'bordercolor': 'black@0.5',
            'shadowx': 1,
            'shadowy': 1
        },
        'cinematic': {
            'fontsize': 52,
            'fontcolor': 'white',
            'borderw': 2,
            'bordercolor': 'black@0.8',
            'shadowx': 4,
            'shadowy': 4
        },
        'horror': {
            'fontsize': 50,
            'fontcolor': 'red',
            'borderw': 3,
            'bordercolor': 'black',
            'shadowx': 5,
            'shadowy': 5
        },
        'elegant': {
            'fontsize': 46,
            'fontcolor': 'white@0.95',
            'borderw': 1,
            'bordercolor': 'black@0.7',
            'shadowx': 2,
            'shadowy': 2
        }
    }
    
    # Animation effects
    ANIMATION_EFFECTS = {
        'fade_in': "alpha='if(lt(t,1),t,1)'",  # Fade in over 1 second
        'fade_out': "alpha='if(gt(t,{duration}-1),{duration}-t,1)'",  # Fade out last 1 second
        'slide_up': "y='h-th-20-t*30'",  # Slide up from bottom
        'slide_down': "y='20+t*30'",  # Slide down from top
        'typewriter': "text_shaping=1",  # Simple typewriter (limited in FFmpeg)
        'pulse': "fontsize='48+sin(t)*4'",  # Pulsing text size
        'none': ""
    }
    
    def __init__(self):
        self.default_style = 'simple'
        self.default_position = 'bottom'
    
    def build_caption_filter(
        self,
        text: str,
        style: str = 'simple',
        position: str = 'bottom',
        animation: str = 'fade_in',
        duration: Optional[float] = None,
        start_time: float = 0,
        font_file: Optional[str] = None
    ) -> str:
        """Build FFmpeg drawtext filter for caption"""
        
        # Get style settings
        style_config = self.CAPTION_STYLES.get(style, self.CAPTION_STYLES['simple'])
        
        # Position calculations
        positions = {
            'top': "x='(w-text_w)/2':y=30",
            'bottom': "x='(w-text_w)/2':y='h-th-30'",
            'center': "x='(w-text_w)/2':y='(h-text_h)/2'",
            'top_left': "x=30:y=30",
            'top_right': "x='w-text_w-30':y=30",
            'bottom_left': "x=30:y='h-th-30'",
            'bottom_right': "x='w-text_w-30':y='h-th-30'"
        }
        
        position_str = positions.get(position, positions['bottom'])
        
        # Build base filter
        filter_parts = [
            f"drawtext=text='{self._escape_text(text)}'",
            f"fontsize={style_config['fontsize']}",
            f"fontcolor={style_config['fontcolor']}",
            f"borderw={style_config['borderw']}",
            f"bordercolor={style_config['bordercolor']}",
            f"shadowx={style_config['shadowx']}",
            f"shadowy={style_config['shadowy']}",
            position_str
        ]
        
        # Add font if specified
        if font_file:
            filter_parts.append(f"fontfile='{font_file}'")
        
        # Add animation
        anim = self.ANIMATION_EFFECTS.get(animation, '')
        if anim and duration:
            anim = anim.format(duration=duration)
            filter_parts.append(anim)
        
        # Add timing
        if start_time > 0:
            filter_parts.append(f"enable='gte(t,{start_time})'")
        if duration:
            filter_parts.append(f"enable='between(t,{start_time},{start_time + duration})'")
        
        return ':'.join(filter_parts)
    
    def build_multi_caption_filter(
        self,
        captions: List[Dict]
    ) -> str:
        """Build filter for multiple captions with different timings"""
        
        caption_filters = []
        
        for caption in captions:
            filter_str = self.build_caption_filter(
                text=caption.get('text', ''),
                style=caption.get('style', 'simple'),
                position=caption.get('position', 'bottom'),
                animation=caption.get('animation', 'fade_in'),
                duration=caption.get('duration'),
                start_time=caption.get('start_time', 0)
            )
            caption_filters.append(filter_str)
        
        # Chain multiple drawtext filters
        return ','.join(caption_filters)
    
    def _escape_text(self, text: str) -> str:
        """Escape special characters for FFmpeg"""
        # FFmpeg drawtext special characters
        text = text.replace("'", "\\'")
        text = text.replace(":", "\\:")
        text = text.replace("%", "\\%")
        return text
    
    def get_available_styles(self) -> Dict[str, str]:
        """Get available caption styles with descriptions"""
        return {
            'simple': 'Simple white text with black outline',
            'bold': 'Bold large text with strong outline',
            'minimal': 'Clean minimal look',
            'cinematic': 'Professional cinema style',
            'horror': 'Red text for horror themes',
            'elegant': 'Subtle elegant appearance'
        }
    
    def get_available_animations(self) -> Dict[str, str]:
        """Get available animation effects"""
        return {
            'none': 'No animation - static text',
            'fade_in': 'Fade in at the start',
            'fade_out': 'Fade out at the end',
            'slide_up': 'Slide up from bottom',
            'slide_down': 'Slide down from top',
            'pulse': 'Pulsing size effect'
        }


# Global instance
caption_generator = CaptionGenerator()


def build_caption_filter(text: str, style: str = 'simple', position: str = 'bottom') -> str:
    """Quick function to build caption filter"""
    return caption_generator.build_caption_filter(text, style, position)


def get_available_styles() -> Dict[str, str]:
    """Quick function to list styles"""
    return caption_generator.get_available_styles()


if __name__ == "__main__":
    print("\n📝 Testing Caption Generator...\n")
    
    captions = CaptionGenerator()
    
    print("✅ Available Styles:")
    for name, description in captions.get_available_styles().items():
        print(f"   {name:<12} - {description}")
    
    print("\n✅ Available Animations:")
    for name, description in captions.get_available_animations().items():
        print(f"   {name:<12} - {description}")
    
    print("\n✅ Example Caption Filter:")
    example = captions.build_caption_filter(
        "This is a test caption",
        style='cinematic',
        position='bottom',
        animation='fade_in'
    )
    print(f"   {example[:100]}...")
    
    print("\n✅ Caption Generator module complete!\n")
