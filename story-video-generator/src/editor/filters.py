"""
🎨 VIDEO FILTERS - Fast color grading and visual effects using FFmpeg
"""

from typing import Dict, List, Optional


class VideoFilters:
    """Fast video filters using FFmpeg - no performance hit"""
    
    # Preset color filters (optimized for speed)
    FILTER_PRESETS = {
        'none': '',
        'cinematic': 'eq=contrast=1.1:brightness=0.05:saturation=1.2',
        'warm': 'eq=contrast=1.05:brightness=0.1:saturation=1.3,colortemperature=6500',
        'cool': 'eq=contrast=1.05:brightness=-0.05:saturation=1.1,colortemperature=9500',
        'vibrant': 'eq=contrast=1.2:saturation=1.5',
        'vintage': 'eq=contrast=0.9:brightness=0.15:saturation=0.8',
        'noir': 'eq=contrast=1.3:brightness=-0.1,hue=s=0',  # Black and white
        'sunset': 'eq=contrast=1.1:brightness=0.1:saturation=1.4,colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131',
        'dramatic': 'eq=contrast=1.3:brightness=-0.1:saturation=1.2',
        'soft': 'eq=contrast=0.9:brightness=0.1:saturation=0.9,unsharp=5:5:0.5:5:5:0.0',
        'sharp': 'unsharp=5:5:1.5:5:5:0.0',
        'horror': 'eq=contrast=1.3:brightness=-0.2:saturation=0.7',
        'anime': 'eq=contrast=1.2:saturation=1.6,unsharp=3:3:1.0:3:3:0.0'
    }
    
    def __init__(self):
        self.default_filter = 'none'
    
    def get_filter_string(self, filter_name: str = 'none') -> str:
        """Get FFmpeg filter string for preset"""
        return self.FILTER_PRESETS.get(filter_name, '')
    
    def build_filter_chain(
        self,
        base_filters: List[str],
        color_filter: str = 'none',
        zoom_effect: bool = False,
        zoom_intensity: float = 1.05
    ) -> str:
        """Build complete FFmpeg filter chain"""
        
        filters = base_filters.copy()
        
        # Add zoom effect (Ken Burns style)
        if zoom_effect:
            # Smooth zoom in over the clip duration
            zoom_filter = f"zoompan=z='min(zoom+0.0015,{zoom_intensity})':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080"
            filters.append(zoom_filter)
        
        # Add color grading filter
        color_filter_str = self.get_filter_string(color_filter)
        if color_filter_str:
            filters.append(color_filter_str)
        
        # Join all filters
        return ','.join([f for f in filters if f])
    
    def get_available_filters(self) -> Dict[str, str]:
        """Get list of available filter presets with descriptions"""
        return {
            'none': 'No filter (original colors)',
            'cinematic': 'Cinema look - enhanced contrast and saturation',
            'warm': 'Warm tones - cozy feeling',
            'cool': 'Cool tones - blue/professional look',
            'vibrant': 'Vibrant colors - pop and energy',
            'vintage': 'Vintage look - nostalgic feel',
            'noir': 'Black and white - classic drama',
            'sunset': 'Golden hour - warm sunset tones',
            'dramatic': 'High contrast - intense mood',
            'soft': 'Soft and dreamy - romantic feel',
            'sharp': 'Sharp and crisp - clear details',
            'horror': 'Dark and desaturated - eerie mood',
            'anime': 'Vibrant and sharp - anime style'
        }


# Global instance
video_filters = VideoFilters()


def get_filter_string(filter_name: str = 'none') -> str:
    """Quick function to get filter string"""
    return video_filters.get_filter_string(filter_name)


def get_available_filters() -> Dict[str, str]:
    """Quick function to list filters"""
    return video_filters.get_available_filters()


if __name__ == "__main__":
    print("\n🎨 Testing Video Filters...\n")
    
    filters = VideoFilters()
    
    print("✅ Available Filters:")
    for name, description in filters.get_available_filters().items():
        print(f"   {name:<15} - {description}")
    
    print("\n✅ Example Filter Chains:")
    print(f"   Cinematic: {filters.get_filter_string('cinematic')}")
    print(f"   Horror: {filters.get_filter_string('horror')}")
    
    print("\n✅ Video Filters module complete!\n")
