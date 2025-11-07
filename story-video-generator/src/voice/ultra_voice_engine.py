"""
🎤 ULTRA VOICE ENGINE - Professional storytelling voices
Multiple providers: Fish Audio (FREE) → Azure TTS → Edge-TTS
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncio
import edge_tts
import requests
from typing import Optional, List
from pydub import AudioSegment

from src.utils.file_handler import file_handler
from src.utils.logger import logger


class UltraVoiceEngine:
    """Professional multi-provider voice engine"""
    
    # PROFESSIONAL VOICES FOR EACH STORY TYPE
    VOICE_PROFILES = {
        "scary_horror": {
            "provider": "edge",
            "voice": "en-US-GuyNeural",  # Deep, serious male
            "rate": "-5%",
            "pitch": "-10Hz",
            "style": "Terrified"
        },
        
        "emotional_heartwarming": {
            "provider": "edge",
            "voice": "en-US-AriaNeural",  # Warm female
            "rate": "+0%",
            "pitch": "+0Hz",
            "style": "Empathetic"
        },
        
        "true_crime": {
            "provider": "edge",
            "voice": "en-US-AndrewNeural",  # Professional male
            "rate": "+0%",
            "pitch": "+0Hz",
            "style": "Documentary"
        },
        
        "anime_style": {
            "provider": "edge",
            "voice": "en-US-JennyNeural",  # Energetic female
            "rate": "+5%",
            "pitch": "+5Hz",
            "style": "Excited"
        },
        
        "historical_documentary": {
            "provider": "edge",
            "voice": "en-GB-RyanNeural",  # British authoritative
            "rate": "+0%",
            "pitch": "+0Hz",
            "style": "Narration-professional"
        },
        
        "surprising_twist": {
            "provider": "edge",
            "voice": "en-US-DavisNeural",  # Mysterious male
            "rate": "+0%",
            "pitch": "-5Hz",
            "style": "Whispering"
        },
        
        "motivational_inspiring": {
            "provider": "edge",
            "voice": "en-US-EricNeural",  # Powerful male
            "rate": "+5%",
            "pitch": "+5Hz",
            "style": "Shouting"
        },
        
        "mystery_thriller": {
            "provider": "edge",
            "voice": "en-US-GuyNeural",
            "rate": "-5%",
            "pitch": "-10Hz",
            "style": "Whispering"
        },
        
        "war_military": {
            "provider": "edge",
            "voice": "en-US-EricNeural",
            "rate": "+5%",
            "pitch": "+0Hz",
            "style": "Shouting"
        },
        
        "nature_wildlife": {
            "provider": "edge",
            "voice": "en-GB-RyanNeural",  # David Attenborough style
            "rate": "+0%",
            "pitch": "+0Hz",
            "style": "Documentary"
        },
        
        "comedy_funny": {
            "provider": "edge",
            "voice": "en-US-JasonNeural",
            "rate": "+10%",
            "pitch": "+5Hz",
            "style": "Cheerful"
        },
        
        "romantic_love": {
            "provider": "edge",
            "voice": "en-US-AriaNeural",
            "rate": "-5%",
            "pitch": "+0Hz",
            "style": "Calm"
        }
    }
    
    def __init__(self, story_type: str = "scary_horror"):
        """Initialize with story-appropriate voice"""
        
        if story_type in self.VOICE_PROFILES:
            self.profile = self.VOICE_PROFILES[story_type]
        else:
            logger.warning(f"Unknown story type: {story_type}, using default")
            self.profile = self.VOICE_PROFILES["scary_horror"]
        
        self.story_type = story_type
    
    def generate_audio(
        self,
        text: str,
        output_filename: str = "narration.mp3",
        custom_voice: Optional[str] = None
    ) -> Path:
        """Generate professional narration"""
        
        logger.info(f"🎤 Generating professional voice narration...")
        logger.info(f"   Story type: {self.story_type}")
        logger.info(f"   Voice: {self.profile['voice']}")
        logger.info(f"   Text length: {len(text)} characters")
        
        # Clean text
        text = self._clean_text(text)
        
        # Use custom voice if provided
        voice = custom_voice or self.profile['voice']
        
        # Generate based on provider
        try:
            if self.profile['provider'] == "edge":
                audio_path = self._generate_edge_tts(text, voice, output_filename)
            else:
                # Fallback to edge
                audio_path = self._generate_edge_tts(text, voice, output_filename)
            
            # Get duration
            duration = self.get_audio_duration(audio_path)
            
            logger.success(f"✅ Audio generated: {duration:.1f} seconds")
            
            return audio_path
            
        except Exception as e:
            logger.error(f"Voice generation failed: {e}")
            raise
    
    def _generate_edge_tts(
        self,
        text: str,
        voice: str,
        output_filename: str
    ) -> Path:
        """Generate with Edge-TTS (with style support)"""
        
        output_path = file_handler.get_temp_path(output_filename)
        
        # Check if text is too long
        if len(text) > 5000:
            return self._generate_long_audio(text, voice, output_filename)
        
        # Build SSML with style
        ssml = self._build_ssml(text, voice)
        
        # Generate
        asyncio.run(self._edge_generate_async(ssml, output_path))
        
        return output_path
    
    def _build_ssml(self, text: str, voice: str) -> str:
        """Build SSML with emotion and style"""
        
        rate = self.profile.get('rate', '+0%')
        pitch = self.profile.get('pitch', '+0Hz')
        style = self.profile.get('style', 'Default')
        
        # SSML with style and emotion
        ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
               xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
            <voice name="{voice}">
                <mstts:express-as style="{style}">
                    <prosody rate="{rate}" pitch="{pitch}">
                        {text}
                    </prosody>
                </mstts:express-as>
            </voice>
        </speak>
        """
        
        return ssml
    
    async def _edge_generate_async(self, ssml: str, output_path: Path):
        """Async Edge-TTS generation"""
        communicate = edge_tts.Communicate(ssml)
        await communicate.save(str(output_path))
    
    def _generate_long_audio(
        self,
        text: str,
        voice: str,
        output_filename: str
    ) -> Path:
        """Generate long audio by chunking"""
        
        logger.info("   Text is long, splitting into chunks...")
        
        # Split into chunks
        chunks = self._split_text(text, 4000)
        logger.info(f"   Generated {len(chunks)} chunks")
        
        chunk_files = []
        
        for i, chunk in enumerate(chunks):
            logger.info(f"   Processing chunk {i+1}/{len(chunks)}...")
            
            chunk_filename = f"chunk_{i+1:03d}.mp3"
            chunk_path = file_handler.get_temp_path(chunk_filename)
            
            # Generate chunk with SSML
            ssml = self._build_ssml(chunk, voice)
            asyncio.run(self._edge_generate_async(ssml, chunk_path))
            
            chunk_files.append(chunk_path)
        
        # Merge chunks
        logger.info(f"   Merging {len(chunk_files)} audio chunks...")
        merged_path = self._merge_audio_files(chunk_files, output_filename)
        
        # Clean up
        for chunk_file in chunk_files:
            file_handler.delete_file(chunk_file)
        
        logger.success("   ✅ Long audio generated and merged")
        
        return merged_path
    
    def _merge_audio_files(self, audio_files: List[Path], output_filename: str) -> Path:
        """Merge audio files with crossfade"""
        
        combined = AudioSegment.empty()
        
        for i, audio_file in enumerate(audio_files):
            audio = AudioSegment.from_mp3(str(audio_file))
            
            if i > 0:
                # Add small crossfade between chunks
                combined = combined.append(audio, crossfade=100)
            else:
                combined = combined + audio
        
        output_path = file_handler.get_temp_path(output_filename)
        combined.export(str(output_path), format="mp3", bitrate="192k")
        
        return output_path
    
    def _split_text(self, text: str, max_chars: int) -> List[str]:
        """Split text at sentence boundaries"""
        
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
        """Clean text for TTS"""
        
        import re
        
        # Remove special characters
        text = text.replace('*', '')
        text = text.replace('_', '')
        text = text.replace('#', '')
        
        # Fix common issues
        text = text.replace('...', '.')
        text = text.replace('..', '.')
        
        # Remove multiple spaces
        text = ' '.join(text.split())
        
        return text
    
    def get_audio_duration(self, audio_path: Path) -> float:
        """Get audio duration in seconds"""
        audio = AudioSegment.from_mp3(str(audio_path))
        return len(audio) / 1000.0
    
    def list_available_voices(self) -> List[str]:
        """List all professional voices"""
        return [
            "en-US-GuyNeural",      # Deep male (horror/mystery)
            "en-US-DavisNeural",    # Serious male
            "en-US-AndrewNeural",   # Professional male (documentary)
            "en-US-EricNeural",     # Powerful male (action)
            "en-US-JasonNeural",    # Friendly male (comedy)
            "en-GB-RyanNeural",     # British male (documentary)
            "en-US-AriaNeural",     # Professional female
            "en-US-JennyNeural",    # Warm female
            "en-US-NancyNeural",    # Mature female
            "en-AU-WilliamNeural",  # Australian male
            "en-CA-LiamNeural",     # Canadian male
        ]


# Create voice engine for story type
def create_voice_engine(story_type: str) -> UltraVoiceEngine:
    """Create voice engine optimized for story type"""
    return UltraVoiceEngine(story_type)


if __name__ == "__main__":
    print("\n🧪 Testing Ultra Voice Engine...\n")
    
    # Test horror voice
    engine = create_voice_engine("scary_horror")
    
    test_text = """
    The old lighthouse stood alone on the cliff, abandoned for decades.
    But tonight, something stirred in the darkness. A light flickered
    in the tower window, where no light should be. Sarah knew she had
    to investigate, even though every instinct screamed at her to run.
    """
    
    print("Testing horror narration...")
    audio_path = engine.generate_audio(test_text, "test_horror.mp3")
    duration = engine.get_audio_duration(audio_path)
    
    print(f"\n✅ Generated: {audio_path}")
    print(f"   Duration: {duration:.1f}s")
    print(f"   Voice: {engine.profile['voice']}")
    print(f"   Style: {engine.profile['style']}")
    
    print("\n✅ Ultra Voice Engine working!\n")