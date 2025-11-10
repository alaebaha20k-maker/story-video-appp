"""
🎤 TTS ENGINE - Text-to-Speech using Edge-TTS
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncio
import edge_tts
from typing import Optional, List
from pydub import AudioSegment
import io

from config.settings import VOICE_SETTINGS
from src.utils.file_handler import file_handler


class TTSEngine:
    """Text-to-Speech engine using Microsoft Edge-TTS (FREE, unlimited)"""
    
    def __init__(self, voice: Optional[str] = None):
        self.voice = voice or VOICE_SETTINGS['default_voice']
        self.rate = VOICE_SETTINGS['rate']
        self.volume = VOICE_SETTINGS['volume']
        self.chunk_size = 1000  # ⚡ ULTRA-SMALL chunks for MAXIMUM parallelism = SUPER FAST!
    
    async def _generate_audio_async(self, text: str, output_path: str):
        """Generate audio asynchronously"""
        communicate = edge_tts.Communicate(
            text,
            self.voice,
            rate=self.rate,
            volume=self.volume
        )
        await communicate.save(output_path)
    
    def generate_audio(self, text: str, filename: str = "narration.mp3") -> Path:
        """Generate audio from text"""
        
        print(f"🎤 Generating voice narration...")
        print(f"   Voice: {self.voice}")
        print(f"   Text length: {len(text)} characters")
        
        # Clean text for TTS
        text = self._clean_text(text)
        
        # ⚡ AGGRESSIVE PARALLEL: Always use parallel for texts >800 chars
        if len(text) > 800:
            return self._generate_long_audio(text, filename)
        
        # For very short text (<800 chars), generate directly
        output_path = file_handler.get_temp_path(filename)
        asyncio.run(self._generate_audio_async(text, str(output_path)))
        print(f"   ✅ Audio saved: {filename}")
        return output_path
    
    def _generate_long_audio(self, text: str, filename: str) -> Path:
        """Generate audio for long text by chunking - PARALLEL VERSION"""
        
        print(f"   🚀 Using ULTRA-AGGRESSIVE parallel processing...")
        
        # Split text into chunks
        chunks = self._split_text(text, self.chunk_size)
        print(f"   Generated {len(chunks)} chunks")
        print(f"   🚀 Generating {len(chunks)} chunks in PARALLEL for 10x+ speedup...")
        
        # Generate audio for all chunks in parallel
        chunk_files = asyncio.run(self._generate_chunks_parallel(chunks))
        
        # Merge all chunks
        print(f"   Merging {len(chunk_files)} audio chunks...")
        merged_path = self._merge_audio_files(chunk_files, filename)
        
        # Clean up chunk files
        for chunk_file in chunk_files:
            file_handler.delete_file(chunk_file)
        
        print(f"   ✅ Long audio generated and merged")
        return merged_path
    
    async def _generate_chunks_parallel(self, chunks: List[str]) -> List[Path]:
        """Generate multiple audio chunks in parallel using asyncio.gather"""
        
        # Create tasks for all chunks
        tasks = []
        chunk_paths = []
        
        for i, chunk in enumerate(chunks):
            chunk_filename = f"chunk_{i+1:03d}.mp3"
            chunk_path = file_handler.get_temp_path(chunk_filename)
            chunk_paths.append(chunk_path)
            
            # Create async task
            task = self._generate_audio_async(chunk, str(chunk_path))
            tasks.append(task)
        
        # Execute all tasks in parallel
        await asyncio.gather(*tasks)
        
        return chunk_paths
    
    def _merge_audio_files(self, audio_files: List[Path], output_filename: str) -> Path:
        """Merge multiple audio files into one"""
        
        combined = AudioSegment.empty()
        
        for audio_file in audio_files:
            audio = AudioSegment.from_mp3(str(audio_file))
            combined += audio
        
        output_path = file_handler.get_temp_path(output_filename)
        combined.export(str(output_path), format="mp3")
        
        return output_path
    
    def _split_text(self, text: str, max_chars: int) -> List[str]:
        """Split text into chunks at sentence boundaries"""
        
        # Split by sentences
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() + '.' for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_chars:
                current_chunk += " " + sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean text for better TTS output"""
        
        # Remove scene markers
        import re
        text = re.sub(r'\[SCENE\s+\d+\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'IMAGE:.*?\n', '', text, flags=re.IGNORECASE)
        
        # Remove multiple spaces
        text = ' '.join(text.split())
        
        # Remove special characters that TTS doesn't handle well
        text = text.replace('*', '')
        text = text.replace('_', '')
        text = text.replace('#', '')
        
        return text
    
    def get_audio_duration(self, audio_path: Path) -> float:
        """Get duration of audio file in seconds"""
        audio = AudioSegment.from_mp3(str(audio_path))
        return len(audio) / 1000.0  # Convert ms to seconds
    
    def set_voice(self, voice: str):
        """Change the voice"""
        self.voice = voice
    
    def list_available_voices(self) -> List[str]:
        """List available voices (popular ones)"""
        return [
            "en-US-GuyNeural",           # Deep male (best for horror/mystery)
            "en-US-DavisNeural",         # Serious male
            "en-GB-RyanNeural",          # British male
            "en-US-EricNeural",          # Mature male
            "en-US-JennyNeural",         # Female
            "en-US-AriaNeural",          # Female
            "en-AU-WilliamNeural",       # Australian male
            "en-CA-LiamNeural",          # Canadian male
        ]


# Global instance
tts_engine = TTSEngine()


def generate_audio(text: str, filename: str = "narration.mp3") -> Path:
    """Quick function to generate audio"""
    return tts_engine.generate_audio(text, filename)


def get_audio_duration(audio_path: Path) -> float:
    """Quick function to get audio duration"""
    return tts_engine.get_audio_duration(audio_path)


if __name__ == "__main__":
    print("\n🧪 Testing TTSEngine...\n")
    
    try:
        engine = TTSEngine()
        
        # Test short text
        test_text = """
        In the winter of 1959, nine experienced hikers ventured into 
        the Ural Mountains. None of them would return alive. What 
        happened on that frozen peak remains one of history's darkest 
        mysteries.
        """
        
        print("Testing short text generation...")
        audio_path = engine.generate_audio(test_text, "test_short.mp3")
        duration = engine.get_audio_duration(audio_path)
        
        print(f"\n✅ Audio generated!")
        print(f"   File: {audio_path}")
        print(f"   Duration: {duration:.1f} seconds")
        
        # List available voices
        voices = engine.list_available_voices()
        print(f"\n✅ Available voices ({len(voices)}):")
        for voice in voices[:3]:
            print(f"   - {voice}")
        
        print("\n✅ TTSEngine working perfectly!\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n⚠️  Make sure edge-tts is installed:")
        print("   pip install edge-tts pydub")