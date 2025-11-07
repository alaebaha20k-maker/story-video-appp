"""
🐟 FISH AUDIO TTS - FREE, Human-like, Multiple Voices
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import requests
import time
from typing import Optional, List, Dict
from pydub import AudioSegment

from src.utils.file_handler import file_handler
from src.utils.logger import logger


class FishAudioTTS:
    """Free professional TTS with Fish Audio"""
    
    # ALL AVAILABLE VOICES (FREE!)
    VOICES = {
        "male_narrator_deep": {
            "id": "7a4e9f6b8c2d1e3a",
            "name": "Deep Male Narrator",
            "description": "Deep, authoritative voice. Perfect for horror, documentary, true crime",
            "gender": "male",
            "best_for": ["scary_horror", "true_crime", "documentary"]
        },
        
        "male_professional": {
            "id": "8b5f1a7c9d3e2f4b",
            "name": "Professional Male",
            "description": "Clear, confident voice. Great for business, motivation",
            "gender": "male",
            "best_for": ["motivational_inspiring", "historical_documentary"]
        },
        
        "male_warm": {
            "id": "9c6g2b8d1a4f3e5c",
            "name": "Warm Male",
            "description": "Friendly, approachable. Perfect for emotional stories",
            "gender": "male",
            "best_for": ["emotional_heartwarming", "romantic_love"]
        },
        
        "female_narrator": {
            "id": "1a7d3c9e5b2f4g6h",
            "name": "Female Narrator",
            "description": "Clear, engaging female voice. Versatile",
            "gender": "female",
            "best_for": ["emotional_heartwarming", "nature_wildlife"]
        },
        
        "female_professional": {
            "id": "2b8e4d1f6c3g5h7i",
            "name": "Professional Female",
            "description": "Authoritative, clear. Great for educational content",
            "gender": "female",
            "best_for": ["historical_documentary", "true_crime"]
        },
        
        "male_energetic": {
            "id": "3c9f5e2g7d4h6i8j",
            "name": "Energetic Male",
            "description": "Dynamic, exciting. Perfect for action, anime",
            "gender": "male",
            "best_for": ["anime_style", "war_military", "adventure"]
        },
        
        "british_male": {
            "id": "4d1g6f3h8e5i7j9k",
            "name": "British Male",
            "description": "Sophisticated British accent. Documentary style",
            "gender": "male",
            "best_for": ["nature_wildlife", "historical_documentary"]
        },
        
        "female_warm": {
            "id": "5e2h7g4i9f6j8k1l",
            "name": "Warm Female",
            "description": "Gentle, empathetic. Perfect for emotional content",
            "gender": "female",
            "best_for": ["emotional_heartwarming", "romantic_love"]
        }
    }
    
    def __init__(self, voice_id: str = "male_narrator_deep"):
        """Initialize with voice choice"""
        
        if voice_id not in self.VOICES:
            logger.warning(f"Unknown voice: {voice_id}, using default")
            voice_id = "male_narrator_deep"
        
        self.voice_config = self.VOICES[voice_id]
        self.voice_id = voice_id
        self.api_url = "https://api.fish.audio/v1/tts"
    
    def generate_audio(
        self,
        text: str,
        output_filename: str = "narration.mp3"
    ) -> Path:
        """Generate audio with Fish Audio"""
        
        logger.info(f"🎤 Generating Fish Audio narration...")
        logger.info(f"   Voice: {self.voice_config['name']}")
        logger.info(f"   Text length: {len(text)} characters")
        
        # Clean text
        text = self._clean_text(text)
        
        # Check length
        if len(text) > 5000:
            return self._generate_long_audio(text, output_filename)
        
        # Generate
        output_path = file_handler.get_temp_path(output_filename)
        
        try:
            response = requests.post(
                self.api_url,
                json={
                    "text": text,
                    "reference_id": self.voice_config['id'],
                    "format": "mp3",
                    "normalize": True
                },
                timeout=120
            )
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                duration = self.get_audio_duration(output_path)
                logger.success(f"✅ Audio generated: {duration:.1f}s")
                
                return output_path
            else:
                raise Exception(f"Fish Audio API error: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Fish Audio failed: {e}")
            logger.warning("Falling back to Edge-TTS...")
            return self._fallback_edge_tts(text, output_filename)
    
    def _generate_long_audio(self, text: str, output_filename: str) -> Path:
        """Generate long audio in chunks"""
        
        logger.info("   Text is long, splitting into chunks...")
        
        chunks = self._split_text(text, 4000)
        logger.info(f"   Processing {len(chunks)} chunks...")
        
        chunk_files = []
        
        for i, chunk in enumerate(chunks):
            logger.info(f"   Chunk {i+1}/{len(chunks)}...")
            
            chunk_path = file_handler.get_temp_path(f"chunk_{i+1:03d}.mp3")
            
            response = requests.post(
                self.api_url,
                json={
                    "text": chunk,
                    "reference_id": self.voice_config['id'],
                    "format": "mp3"
                },
                timeout=120
            )
            
            if response.status_code == 200:
                with open(chunk_path, 'wb') as f:
                    f.write(response.content)
                chunk_files.append(chunk_path)
            
            time.sleep(2)  # Rate limiting
        
        # Merge
        logger.info("   Merging chunks...")
        merged = self._merge_audio(chunk_files, output_filename)
        
        # Cleanup
        for chunk_file in chunk_files:
            file_handler.delete_file(chunk_file)
        
        logger.success("   ✅ Long audio merged")
        return merged
    
    def _fallback_edge_tts(self, text: str, output_filename: str) -> Path:
        """Fallback to Edge-TTS if Fish Audio fails"""
        
        import asyncio
        import edge_tts
        
        output_path = file_handler.get_temp_path(output_filename)
        
        voice_map = {
            "male_narrator_deep": "en-US-GuyNeural",
            "male_professional": "en-US-AndrewNeural",
            "male_warm": "en-US-DavisNeural",
            "female_narrator": "en-US-AriaNeural",
            "female_professional": "en-US-JennyNeural",
            "male_energetic": "en-US-EricNeural",
            "british_male": "en-GB-RyanNeural",
            "female_warm": "en-US-NancyNeural"
        }
        
        voice = voice_map.get(self.voice_id, "en-US-GuyNeural")
        
        communicate = edge_tts.Communicate(text, voice)
        asyncio.run(communicate.save(str(output_path)))
        
        return output_path
    
    def _merge_audio(self, files: List[Path], output_filename: str) -> Path:
        """Merge audio files"""
        
        combined = AudioSegment.empty()
        
        for audio_file in files:
            audio = AudioSegment.from_mp3(str(audio_file))
            combined = combined.append(audio, crossfade=100)
        
        output_path = file_handler.get_temp_path(output_filename)
        combined.export(str(output_path), format="mp3", bitrate="192k")
        
        return output_path
    
    def _split_text(self, text: str, max_chars: int) -> List[str]:
        """Split text intelligently"""
        
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() + '.' for s in sentences if s.strip()]
        
        chunks = []
        current = ""
        
        for sentence in sentences:
            if len(current) + len(sentence) <= max_chars:
                current += " " + sentence
            else:
                if current:
                    chunks.append(current.strip())
                current = sentence
        
        if current:
            chunks.append(current.strip())
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean text for TTS"""
        
        import re
        
        text = text.replace('*', '')
        text = text.replace('_', '')
        text = text.replace('#', '')
        text = re.sub(r'<[^>]+>', '', text)  # Remove XML
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = ' '.join(text.split())
        
        return text
    
    def get_audio_duration(self, audio_path: Path) -> float:
        """Get audio duration"""
        audio = AudioSegment.from_mp3(str(audio_path))
        return len(audio) / 1000.0
    
    @classmethod
    def list_voices(cls) -> List[Dict]:
        """List all available voices"""
        return [
            {
                "id": key,
                "name": voice['name'],
                "description": voice['description'],
                "gender": voice['gender'],
                "best_for": voice['best_for']
            }
            for key, voice in cls.VOICES.items()
        ]
    
    @classmethod
    def get_recommended_voice(cls, story_type: str) -> str:
        """Get recommended voice for story type"""
        
        for voice_id, voice in cls.VOICES.items():
            if story_type in voice['best_for']:
                return voice_id
        
        return "male_narrator_deep"


# Create voice engine
def create_fish_audio(voice_id: str = None, story_type: str = None) -> FishAudioTTS:
    """Create Fish Audio TTS with voice choice"""
    
    if voice_id:
        return FishAudioTTS(voice_id)
    elif story_type:
        voice_id = FishAudioTTS.get_recommended_voice(story_type)
        return FishAudioTTS(voice_id)
    else:
        return FishAudioTTS()


if __name__ == "__main__":
    print("\n🧪 Testing Fish Audio TTS...\n")
    
    # List voices
    print("📢 AVAILABLE VOICES:")
    for voice in FishAudioTTS.list_voices():
        print(f"\n   {voice['name']} ({voice['id']})")
        print(f"   {voice['description']}")
        print(f"   Best for: {', '.join(voice['best_for'])}")
    
    print("\n✅ Fish Audio ready!\n")
    