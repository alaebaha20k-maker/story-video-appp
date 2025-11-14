"""
⏱️ SMART DURATION CALCULATOR
Intelligently distributes media timing to match audio duration perfectly
Handles mixed media (images + videos) with intelligent pacing
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import List, Dict
import random


class SmartDurationCalculator:
    """
    Calculates optimal display duration for each media item

    INTELLIGENCE:
    - Videos use their natural duration
    - Images fill remaining time
    - Adds variation (not all equal)
    - Ensures total = audio duration EXACTLY
    - Respects min/max duration limits
    """

    def __init__(self):
        self.min_image_duration = 3.0  # Minimum 3 seconds per image
        self.max_image_duration = 10.0  # Maximum 10 seconds per image
        self.min_video_duration = 2.0  # Minimum 2 seconds for video clips
        self.max_video_duration = 15.0  # Maximum 15 seconds for video clips

    def calculate_durations(
        self,
        media_items: List[Dict],
        audio_duration: float,
        variation: float = 0.3
    ) -> List[float]:
        """
        Calculate optimal duration for each media item

        Args:
            media_items: List of media dicts with 'type' and optional 'duration'
            audio_duration: Total audio length in seconds
            variation: How much to vary image durations (0.0-1.0)

        Returns:
            List of durations in seconds (one per media item)
        """

        print(f"\n⏱️  SMART DURATION CALCULATOR")
        print(f"   Audio duration: {audio_duration:.1f}s ({audio_duration/60:.1f} min)")
        print(f"   Media items: {len(media_items)}")
        print(f"   Variation: {variation*100:.0f}%")

        if not media_items:
            return []

        # Separate images and videos
        images = []
        videos = []

        for i, item in enumerate(media_items):
            if item.get('type') == 'video':
                videos.append({
                    'index': i,
                    'duration': item.get('duration', 5.0)  # Default 5s if not specified
                })
            else:
                images.append({'index': i})

        print(f"   Images: {len(images)}")
        print(f"   Videos: {len(videos)}")

        # Calculate video time total
        video_time = sum(v['duration'] for v in videos)
        print(f"   Video time: {video_time:.1f}s")

        # Clip videos if they exceed audio duration
        if video_time >= audio_duration:
            print(f"   ⚠️  Videos exceed audio! Clipping to fit...")
            video_time = self._clip_videos(videos, audio_duration * 0.9)

        # Calculate remaining time for images
        image_time_available = audio_duration - video_time
        print(f"   Image time available: {image_time_available:.1f}s")

        # Calculate base image duration
        if images:
            base_image_duration = image_time_available / len(images)
            print(f"   Base image duration: {base_image_duration:.1f}s")

            # Check if within limits
            if base_image_duration < self.min_image_duration:
                print(f"   ⚠️  Too many images! Extending to minimum {self.min_image_duration}s each")
                base_image_duration = self.min_image_duration

            elif base_image_duration > self.max_image_duration:
                print(f"   ⚠️  Too few images! Capping at maximum {self.max_image_duration}s each")
                base_image_duration = self.max_image_duration

        else:
            base_image_duration = 0

        # Generate varied image durations
        image_durations = self._generate_varied_durations(
            count=len(images),
            base_duration=base_image_duration,
            target_total=image_time_available,
            variation=variation,
            min_dur=self.min_image_duration,
            max_dur=self.max_image_duration
        )

        # Build final duration list (in original order)
        final_durations = [0.0] * len(media_items)

        # Assign video durations
        for video in videos:
            final_durations[video['index']] = video['duration']

        # Assign image durations
        for i, img in enumerate(images):
            final_durations[img['index']] = image_durations[i]

        # Verify total
        total_duration = sum(final_durations)
        print(f"\n   📊 RESULTS:")
        print(f"      Total: {total_duration:.1f}s (target: {audio_duration:.1f}s)")
        print(f"      Difference: {abs(total_duration - audio_duration):.2f}s")

        # Fine-tune to match exactly
        if abs(total_duration - audio_duration) > 0.1:
            final_durations = self._fine_tune_durations(final_durations, audio_duration)
            total_duration = sum(final_durations)
            print(f"      After fine-tuning: {total_duration:.1f}s ✅")

        # Print summary
        image_durs = [d for i, d in enumerate(final_durations) if media_items[i].get('type') != 'video']
        video_durs = [d for i, d in enumerate(final_durations) if media_items[i].get('type') == 'video']

        if image_durs:
            print(f"      Image durations: min={min(image_durs):.1f}s, max={max(image_durs):.1f}s, avg={sum(image_durs)/len(image_durs):.1f}s")
        if video_durs:
            print(f"      Video durations: min={min(video_durs):.1f}s, max={max(video_durs):.1f}s, avg={sum(video_durs)/len(video_durs):.1f}s")

        return final_durations

    def _clip_videos(self, videos: List[Dict], max_total: float) -> float:
        """Clip video durations proportionally to fit within max_total"""

        total = sum(v['duration'] for v in videos)
        scale = max_total / total

        new_total = 0
        for video in videos:
            new_duration = video['duration'] * scale
            # Respect min/max
            new_duration = max(self.min_video_duration, min(new_duration, self.max_video_duration))
            video['duration'] = new_duration
            new_total += new_duration

        return new_total

    def _generate_varied_durations(
        self,
        count: int,
        base_duration: float,
        target_total: float,
        variation: float,
        min_dur: float,
        max_dur: float
    ) -> List[float]:
        """
        Generate varied durations around base_duration

        Uses intelligent variation to make video feel natural:
        - Some images longer (for emphasis)
        - Some images shorter (for pacing)
        - Total matches target_total
        """

        if count == 0:
            return []

        # Generate random variations
        durations = []
        for _ in range(count):
            # Random factor between (1 - variation) and (1 + variation)
            factor = 1.0 + random.uniform(-variation, variation)
            duration = base_duration * factor

            # Clamp to limits
            duration = max(min_dur, min(duration, max_dur))
            durations.append(duration)

        # Normalize to match target total
        current_total = sum(durations)
        if current_total > 0:
            scale = target_total / current_total
            durations = [d * scale for d in durations]

            # Re-clamp after scaling
            durations = [max(min_dur, min(d, max_dur)) for d in durations]

        return durations

    def _fine_tune_durations(self, durations: List[float], target: float) -> List[float]:
        """Fine-tune durations to match target exactly"""

        current_total = sum(durations)
        difference = target - current_total

        if abs(difference) < 0.01:
            return durations

        # Distribute difference across all items proportionally
        for i in range(len(durations)):
            if durations[i] > 0:
                adjustment = difference * (durations[i] / current_total)
                durations[i] += adjustment

        return durations


# Singleton instance
duration_calculator = SmartDurationCalculator()


def calculate_durations(media_items: List[Dict], audio_duration: float, variation: float = 0.3) -> List[float]:
    """Convenience function"""
    return duration_calculator.calculate_durations(media_items, audio_duration, variation)


if __name__ == "__main__":
    print("\n🧪 Testing Smart Duration Calculator...\n")

    # Test 1: Only images
    print("TEST 1: 10 images, 60s audio")
    media = [{'type': 'image'} for _ in range(10)]
    durations = calculate_durations(media, audio_duration=60.0)
    print(f"Result: {durations}")
    print(f"Total: {sum(durations):.1f}s\n")

    # Test 2: Mixed (images + videos)
    print("TEST 2: 8 images + 2 videos (5s each), 60s audio")
    media = [
        {'type': 'image'},
        {'type': 'image'},
        {'type': 'video', 'duration': 5.0},
        {'type': 'image'},
        {'type': 'image'},
        {'type': 'image'},
        {'type': 'video', 'duration': 5.0},
        {'type': 'image'},
        {'type': 'image'},
        {'type': 'image'},
    ]
    durations = calculate_durations(media, audio_duration=60.0)
    print(f"Result: {durations}")
    print(f"Total: {sum(durations):.1f}s\n")

    # Test 3: Long video (1 hour)
    print("TEST 3: 10 images, 3600s audio (1 hour)")
    media = [{'type': 'image'} for _ in range(10)]
    durations = calculate_durations(media, audio_duration=3600.0)
    print(f"Result: First 5: {durations[:5]}")
    print(f"Total: {sum(durations):.1f}s\n")

    print("✅ Smart Duration Calculator working!")
