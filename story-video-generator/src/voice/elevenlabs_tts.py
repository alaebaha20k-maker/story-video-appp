"""
🎤 ELEVENLABS TTS - Human-Like Voices for YouTube!
The BEST TTS for professional video content
"""

import os
import requests
from pathlib import Path
from typing import Optional, List, Dict
import time

class ElevenLabsTTS:
    """ElevenLabs TTS Engine - 99% Human-Like Quality!"""
    
    # ✅ BEST VOICES for YouTube (Professional & Natural)
    VOICES = {
        # MALE VOICES (Deep & Professional)
        'adam': {
            'id': '21m00Tcm4TlvDq8ikWAM',
            'name': 'Adam',
            'gender': 'male',
            'style': 'Deep & Narrative',
            'best_for': 'Documentaries, serious content'
        },
        'antoni': {
            'id': 'ErXwobaYiN019PkySvjV',
            'name': 'Antoni',
            'gender': 'male',
            'style': 'Young & Energetic',
            'best_for': 'Gaming, entertainment'
        },
        'josh': {
            'id': 'TxGEqnHWrfWFTfGW9XjX',
            'name': 'Josh',
            'gender': 'male',
            'style': 'Casual & Friendly',
            'best_for': 'Vlogs, tutorials'
        },
        'arnold': {
            'id': 'VR6AewLTigWG4xSOukaG',
            'name': 'Arnold',
            'gender': 'male',
            'style': 'Authoritative & Clear',
            'best_for': 'News, business'
        },
        
        # FEMALE VOICES (Natural & Engaging)
        'bella': {
            'id': 'EXAVITQu4vr4xnSDxMaL',
            'name': 'Bella',
            'gender': 'female',
            'style': 'Soft & Warm',
            'best_for': 'Stories, lifestyle'
        },
        'elli': {
            'id': 'MF3mGyEYCl7XYWbV9V6O',
            'name': 'Elli',
            'gender': 'female',
            'style': 'Young & Energetic',
            'best_for': 'Adventure, action'
        },
        'charlotte': {
            'id': 'XB0fDUnXU5powFXDhCwa',
            'name': 'Charlotte',
            'gender': 'female',
            'style': 'Professional & Clear',
            'best_for': 'Education, tutorials'
        },
        'sarah': {
            'id': 'EXAVITQu4vr4xnSDxMaL',
            'name': 'Sarah',
            'gender': 'female',
            'style': 'Natural & Friendly',
            'best_for': 'General content'
        },
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize ElevenLabs TTS
        
        Args:
            api_key: ElevenLabs API key (or set ELEVENLABS_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise ValueError("ElevenLabs API key required! Get free key at: https://elevenlabs.io/")
        
        self.api_url = 'https://api.elevenlabs.io/v1/text-to-speech'
        
        print(f"🎤 ElevenLabs TTS initialized")
        print(f"   Available voices: {len(self.VOICES)} professional voices")
        print(f"   Quality: 99% human-like! Perfect for YouTube!")
    
    def generate_audio(
        self,
        text: str,
        voice: str = 'adam',
        output_path: Optional[str] = None,
        stability: float = 0.5,
        similarity_boost: float = 0.75
    ) -> str:
        """Generate human-like audio from text
        
        Args:
            text: Text to convert to speech
            voice: Voice ID (lowercase, e.g., 'adam', 'bella')
            output_path: Where to save MP3 file
            stability: Voice stability (0-1, higher = more stable)
            similarity_boost: Voice similarity (0-1, higher = more consistent)
        
        Returns:
            Path to generated MP3 file
        """
        
        print(f"\n🎤 Generating human-like audio with ElevenLabs...")
        print(f"   Voice: {voice.title()}")
        print(f"   Text length: {len(text)} characters")
        
        start_time = time.time()
        
        try:
            # Get voice ID
            voice_info = self.VOICES.get(voice.lower())
            if not voice_info:
                print(f"   ⚠️  Voice '{voice}' not found, using Adam (default)")
                voice_info = self.VOICES['adam']
            
            voice_id = voice_info['id']
            voice_name = voice_info['name']
            
            print(f"   Using: {voice_name} ({voice_info['style']})")
            print(f"   Best for: {voice_info['best_for']}")
            
            # Prepare API request
            url = f"{self.api_url}/{voice_id}"
            
            headers = {
                'xi-api-key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'text': text,
                'model_id': 'eleven_monolingual_v1',  # Fast & high quality
                'voice_settings': {
                    'stability': stability,
                    'similarity_boost': similarity_boost
                }
            }
            
            # Make API call
            print(f"   📡 Calling ElevenLabs API...")
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            
            if not response.ok:
                error_msg = response.text[:500]
                print(f"   ❌ API Error: {response.status_code}")
                print(f"   Details: {error_msg}")
                
                # Check for common errors
                if response.status_code == 401:
                    raise Exception("❌ Invalid API key! Get your key at: https://elevenlabs.io/")
                elif response.status_code == 429:
                    raise Exception("❌ Rate limit exceeded! Upgrade plan or wait.")
                elif response.status_code == 400:
                    raise Exception(f"❌ Bad request: {error_msg}")
                else:
                    raise Exception(f"❌ API error {response.status_code}: {error_msg}")
            
            # Save audio
            audio_data = response.content
            
            if len(audio_data) == 0:
                raise Exception("❌ No audio data received from API!")
            
            # Default output path
            if output_path is None:
                output_dir = Path("output/temp")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / "elevenlabs_narration.mp3"
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write MP3 file
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            duration = time.time() - start_time
            
            print(f"✅ Human-like audio generated!")
            print(f"   File: {output_path}")
            print(f"   Size: {len(audio_data) / 1024:.1f} KB")
            print(f"   Generation time: {duration:.1f} seconds")
            print(f"   🎬 YouTube-ready quality!")
            
            return str(output_path)
        
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"❌ ELEVENLABS GENERATION FAILED!")
            print(f"{'='*60}")
            print(f"Error: {e}")
            print(f"\n💡 Troubleshooting:")
            print(f"   1. Check API key at: https://elevenlabs.io/")
            print(f"   2. Verify you have credits/quota remaining")
            print(f"   3. Check text length (max ~5000 chars per request)")
            print(f"   4. Try a different voice")
            print(f"{'='*60}\n")
            raise
    
    def get_voices(self, gender: Optional[str] = None) -> List[Dict]:
        """Get available voices
        
        Args:
            gender: Filter by gender ('male' or 'female')
        
        Returns:
            List of voice info dictionaries
        """
        voices = []
        for voice_id, voice_info in self.VOICES.items():
            if gender is None or voice_info['gender'] == gender.lower():
                voices.append({
                    'id': voice_id,
                    'name': voice_info['name'],
                    'gender': voice_info['gender'],
                    'style': voice_info['style'],
                    'best_for': voice_info['best_for']
                })
        return voices
    
    @classmethod
    def list_all_voices(cls):
        """Print all available voices"""
        print("\n🎤 ELEVENLABS VOICES (YouTube-Ready!):")
        print("="*60)
        
        male_voices = [(k, v) for k, v in cls.VOICES.items() if v['gender'] == 'male']
        female_voices = [(k, v) for k, v in cls.VOICES.items() if v['gender'] == 'female']
        
        print("\n👨 MALE VOICES:")
        for voice_id, voice_info in male_voices:
            print(f"   {voice_id:12} - {voice_info['name']:12} | {voice_info['style']:20} | {voice_info['best_for']}")
        
        print("\n👩 FEMALE VOICES:")
        for voice_id, voice_info in female_voices:
            print(f"   {voice_id:12} - {voice_info['name']:12} | {voice_info['style']:20} | {voice_info['best_for']}")
        
        print("\n" + "="*60)
        print("✅ All voices sound 99% HUMAN - Perfect for YouTube!")
        print("💰 FREE: 10 minutes/month | STARTER: $5/month = 30 minutes")
        print("🔗 Get API key: https://elevenlabs.io/")
        print("="*60 + "\n")


def create_elevenlabs_tts(api_key: Optional[str] = None) -> ElevenLabsTTS:
    """Create ElevenLabs TTS instance"""
    return ElevenLabsTTS(api_key=api_key)


# Test if module is run directly
if __name__ == "__main__":
    print("🔍 Testing ElevenLabs TTS...")
    
    # List voices
    ElevenLabsTTS.list_all_voices()
    
    # Try to create instance
    try:
        tts = create_elevenlabs_tts()
        print("✅ ElevenLabs TTS ready!")
    except ValueError as e:
        print(f"⚠️  {e}")
        print("\n💡 To use ElevenLabs:")
        print("   1. Get free API key: https://elevenlabs.io/")
        print("   2. Set environment variable:")
        print("      export ELEVENLABS_API_KEY='your_key_here'")
        print("   3. Or add to .env file:")
        print("      ELEVENLABS_API_KEY=your_key_here")
