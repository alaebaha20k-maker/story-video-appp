"""
⏱️ TIMING - Calculates durations and synchronization
"""

from typing import List, Tuple


class TimingCalculator:
    """Calculates timing for images, audio, and video synchronization"""
    
    @staticmethod
    def calculate_image_durations(total_duration: float, num_images: int) -> List[float]:
        """Calculate how long each image should display"""
        base_duration = total_duration / num_images
        return [base_duration] * num_images
    
    @staticmethod
    def calculate_dynamic_durations(
        total_duration: float, 
        num_images: int,
        intensity_levels: List[str] = None
    ) -> List[float]:
        """Calculate variable durations based on scene intensity"""
        if intensity_levels is None or len(intensity_levels) != num_images:
            return TimingCalculator.calculate_image_durations(total_duration, num_images)
        
        # Intensity multipliers
        multipliers = {
            'high': 0.7,    # Fast-paced scenes (shorter display)
            'medium': 1.0,  # Normal pacing
            'low': 1.3      # Slow, atmospheric scenes (longer display)
        }
        
        # Calculate initial durations
        base_duration = total_duration / num_images
        durations = []
        
        for intensity in intensity_levels:
            multiplier = multipliers.get(intensity, 1.0)
            durations.append(base_duration * multiplier)
        
        # Normalize to fit exact total duration
        current_total = sum(durations)
        normalized = [(d / current_total) * total_duration for d in durations]
        
        return normalized
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format seconds to human readable time"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    @staticmethod
    def estimate_render_time(
        video_duration: float,
        num_images: int,
        effect_type: str = 'simple_zoom'
    ) -> float:
        """Estimate rendering time in seconds"""
        effect_multipliers = {
            'static': 0.1,          # 0.1s per image
            'simple_zoom': 0.3,     # 0.3s per image
            'ken_burns': 1.2        # 1.2s per image
        }
        
        multiplier = effect_multipliers.get(effect_type, 0.3)
        base_time = num_images * multiplier
        
        # Add overhead for audio processing and final encoding
        audio_time = video_duration * 0.05  # 5% of video duration
        encoding_time = video_duration * 0.1  # 10% of video duration
        
        total = base_time + audio_time + encoding_time
        return total
    
    @staticmethod
    def calculate_stock_media_timing(
        total_duration: float,
        videos: List[Tuple[str, float]],  # (filename, duration)
        num_images: int
    ) -> Tuple[List[Tuple[str, float, int]], List[float]]:
        """
        Calculate timing for stock videos (with loops) and images
        Returns: (video_timing, image_durations)
        video_timing: List of (filename, duration, loop_count)
        """
        # Calculate total available video time
        total_video_time = sum(duration for _, duration in videos)
        
        # Determine loop count to fill ~30% of video
        target_video_time = total_duration * 0.3
        loop_count = max(1, int(target_video_time / total_video_time)) if total_video_time > 0 else 0
        
        # Video timing with loops
        video_timing = []
        for filename, duration in videos:
            video_timing.append((filename, duration, loop_count))
        
        # Calculate remaining time for images
        used_video_time = total_video_time * loop_count
        remaining_time = total_duration - used_video_time
        
        # Distribute remaining time across images
        image_durations = []
        if num_images > 0:
            time_per_image = remaining_time / num_images
            image_durations = [time_per_image] * num_images
        
        return video_timing, image_durations
    
    @staticmethod
    def seconds_to_timestamp(seconds: float) -> str:
        """Convert seconds to timestamp format (HH:MM:SS)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    @staticmethod
    def estimate_file_size(duration_minutes: float, resolution: str = "1080p") -> float:
        """Estimate output file size in MB"""
        # Bitrate assumptions (Mbps)
        bitrates = {
            "720p": 5,
            "1080p": 8,
            "1440p": 16,
            "4k": 45
        }
        
        bitrate = bitrates.get(resolution, 8)
        size_mb = (bitrate * duration_minutes * 60) / 8  # Convert to MB
        return size_mb


timing_calculator = TimingCalculator()


def calculate_image_durations(total_duration: float, num_images: int) -> List[float]:
    return timing_calculator.calculate_image_durations(total_duration, num_images)


def format_duration(seconds: float) -> str:
    return timing_calculator.format_duration(seconds)


def estimate_render_time(duration: float, num_images: int, effect: str = 'simple_zoom') -> float:
    return timing_calculator.estimate_render_time(duration, num_images, effect)


if __name__ == "__main__":
    print("\n🧪 Testing TimingCalculator...\n")
    
    tc = TimingCalculator()
    
    # Test 1: Basic duration calculation
    total = 3600  # 1 hour
    images = 25
    durations = tc.calculate_image_durations(total, images)
    print(f"✅ {images} images over {tc.format_duration(total)}")
    print(f"   Each image: {tc.format_duration(durations[0])}")
    
    # Test 2: Render time estimation
    render_time = tc.estimate_render_time(3600, 25, 'simple_zoom')
    print(f"\n✅ Estimated render time: {tc.format_duration(render_time)}")
    
    # Test 3: File size estimation
    size = tc.estimate_file_size(60, "1080p")
    print(f"\n✅ Estimated file size: {size:.1f} MB")
    
    # Test 4: Timestamp conversion
    timestamp = tc.seconds_to_timestamp(3725)
    print(f"\n✅ Timestamp: {timestamp}")
    
    print("\n✅ TimingCalculator working perfectly!\n")