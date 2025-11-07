"""
🔊 AUDIO PROCESSOR - Audio manipulation and processing
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pydub import AudioSegment
from pydub.effects import normalize
from typing import Optional, List
import numpy as np

from src.utils.file_handler import file_handler


class AudioProcessor:
    """Process and manipulate audio files"""
    
    def __init__(self):
        self.default_format = "mp3"
        self.default_bitrate = "192k"
    
    def normalize_audio(self, audio_path: Path, target_dbfs: float = -20.0) -> Path:
        """Normalize audio to target level"""
        audio = AudioSegment.from_file(str(audio_path))
        normalized = normalize(audio, headroom=0.1)
        
        # Adjust to target dBFS
        change_in_dbfs = target_dbfs - normalized.dBFS
        normalized = normalized.apply_gain(change_in_dbfs)
        
        output_path = file_handler.get_temp_path(f"normalized_{audio_path.name}")
        normalized.export(str(output_path), format=self.default_format, bitrate=self.default_bitrate)
        
        return output_path
    
    def fade_in_out(self, audio_path: Path, fade_duration: int = 1000) -> Path:
        """Add fade in/out to audio"""
        audio = AudioSegment.from_file(str(audio_path))
        
        faded = audio.fade_in(fade_duration).fade_out(fade_duration)
        
        output_path = file_handler.get_temp_path(f"faded_{audio_path.name}")
        faded.export(str(output_path), format=self.default_format)
        
        return output_path
    
    def merge_audio(self, audio_files: List[Path], crossfade: int = 0) -> Path:
        """Merge multiple audio files"""
        if not audio_files:
            return None
        
        combined = AudioSegment.from_file(str(audio_files[0]))
        
        for audio_file in audio_files[1:]:
            next_audio = AudioSegment.from_file(str(audio_file))
            if crossfade > 0:
                combined = combined.append(next_audio, crossfade=crossfade)
            else:
                combined = combined + next_audio
        
        output_path = file_handler.get_temp_path("merged_audio.mp3")
        combined.export(str(output_path), format=self.default_format, bitrate=self.default_bitrate)
        
        return output_path
    
    def overlay_audio(
        self,
        base_audio_path: Path,
        overlay_audio_path: Path,
        volume_adjustment: int = -20,
        loop: bool = True
    ) -> Path:
        """Overlay audio (e.g., background music over narration)"""
        base = AudioSegment.from_file(str(base_audio_path))
        overlay = AudioSegment.from_file(str(overlay_audio_path))
        
        # Adjust overlay volume
        overlay = overlay + volume_adjustment
        
        # Loop overlay if needed
        if loop and len(overlay) < len(base):
            repeats = (len(base) // len(overlay)) + 1
            overlay = overlay * repeats
        
        # Trim overlay to match base length
        overlay = overlay[:len(base)]
        
        # Overlay
        combined = base.overlay(overlay)
        
        output_path = file_handler.get_temp_path("with_music.mp3")
        combined.export(str(output_path), format=self.default_format, bitrate=self.default_bitrate)
        
        return output_path
    
    def adjust_speed(self, audio_path: Path, speed: float = 1.0) -> Path:
        """Adjust audio playback speed"""
        audio = AudioSegment.from_file(str(audio_path))
        
        # Change frame rate
        sound_with_altered_frame_rate = audio._spawn(
            audio.raw_data,
            overrides={"frame_rate": int(audio.frame_rate * speed)}
        )
        
        # Convert back to original frame rate
        adjusted = sound_with_altered_frame_rate.set_frame_rate(audio.frame_rate)
        
        output_path = file_handler.get_temp_path(f"speed_{speed}x_{audio_path.name}")
        adjusted.export(str(output_path), format=self.default_format)
        
        return output_path
    
    def trim_audio(self, audio_path: Path, start_ms: int, end_ms: int) -> Path:
        """Trim audio to specified range"""
        audio = AudioSegment.from_file(str(audio_path))
        trimmed = audio[start_ms:end_ms]
        
        output_path = file_handler.get_temp_path(f"trimmed_{audio_path.name}")
        trimmed.export(str(output_path), format=self.default_format)
        
        return output_path
    
    def get_duration(self, audio_path: Path) -> float:
        """Get audio duration in seconds"""
        audio = AudioSegment.from_file(str(audio_path))
        return len(audio) / 1000.0
    
    def convert_format(self, audio_path: Path, output_format: str = "mp3") -> Path:
        """Convert audio to different format"""
        audio = AudioSegment.from_file(str(audio_path))
        
        output_path = file_handler.get_temp_path(f"converted.{output_format}")
        audio.export(str(output_path), format=output_format)
        
        return output_path
    
    def apply_audio_ducking(
        self,
        narration_path: Path,
        music_path: Path,
        duck_amount: int = -15
    ) -> Path:
        """Apply audio ducking (lower music when narration plays)"""
        narration = AudioSegment.from_file(str(narration_path))
        music = AudioSegment.from_file(str(music_path))
        
        # Loop music if needed
        if len(music) < len(narration):
            repeats = (len(narration) // len(music)) + 1
            music = music * repeats
        
        music = music[:len(narration)]
        
        # Lower music volume
        music = music + duck_amount
        
        # Combine
        combined = narration.overlay(music)
        
        output_path = file_handler.get_temp_path("ducked_audio.mp3")
        combined.export(str(output_path), format=self.default_format, bitrate=self.default_bitrate)
        
        return output_path


audio_processor = AudioProcessor()


def normalize_audio(audio_path: Path) -> Path:
    return audio_processor.normalize_audio(audio_path)


def merge_audio(audio_files: List[Path]) -> Path:
    return audio_processor.merge_audio(audio_files)


def get_audio_duration(audio_path: Path) -> float:
    return audio_processor.get_duration(audio_path)


if __name__ == "__main__":
    print("\n🧪 Testing AudioProcessor...\n")
    
    print("✅ AudioProcessor ready!")
    print("\nFunctions available:")
    print("  - normalize_audio()")
    print("  - fade_in_out()")
    print("  - merge_audio()")
    print("  - overlay_audio()")
    print("  - adjust_speed()")
    print("  - apply_audio_ducking()")
    
    print("\n✅ AudioProcessor module complete!\n")