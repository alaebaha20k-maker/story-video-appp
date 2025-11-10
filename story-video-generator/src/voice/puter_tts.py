"""
🎤 PUTER TTS - FREE & UNLIMITED Text-to-Speech API!
Perfect for YouTube videos - No API key, No limits!
"""

import requests
from pathlib import Path
from typing import Optional, List
import time

class PuterTTS:
    """Puter TTS Engine - Free, Unlimited, High Quality!"""
    
    # ✅ Puter TTS Voices (Multiple options for different styles)
    VOICES = {
        # MALE VOICES
        'matthew': {
            'name': 'Matthew',
            'gender': 'male',
            'style': 'Natural & Clear',
            'best_for': 'General narration, documentaries'
        },
        'joey': {
            'name': 'Joey',
            'gender': 'male',
            'style': 'Young & Energetic',
            'best_for': 'Gaming, entertainment'
        },
        'brian': {
            'name': 'Brian',
            'gender': 'male',
            'style': 'Professional',
            'best_for': 'Business, formal content'
        },
        'justin': {
            'name': 'Justin',
            'gender': 'male',
            'style': 'Casual & Friendly',
            'best_for': 'Vlogs, tutorials'
        },
        
        # FEMALE VOICES
        'joanna': {
            'name': 'Joanna',
            'gender': 'female',
            'style': 'Natural & Warm',
            'best_for': 'Stories, lifestyle'
        },
        'salli': {
            'name': 'Salli',
            'gender': 'female',
            'style': 'Professional & Clear',
            'best_for': 'Education, tutorials'
        },
        'kimberly': {
            'name': 'Kimberly',
            'gender': 'female',
            'style': 'Young & Energetic',
            'best_for': 'Adventure, action'
        },
        'ivy': {
            'name': 'Ivy',
            'gender': 'female',
            'style': 'Soft & Friendly',
            'best_for': 'General content'
        },
    }
    
    def __init__(self):
        """Initialize Puter TTS - No API key needed!"""
        self.api_url = 'https://api.puter.com/drivers/call'
        
        print(f"🎤 Puter TTS initialized")
        print(f"   ✅ FREE & UNLIMITED!")
        print(f"   ✅ No API key required!")
        print(f"   Available voices: {len(self.VOICES)} professional voices")
    
    def generate_audio(
        self,
        text: str,
        voice: str = 'matthew',
        output_path: Optional[str] = None
    ) -> str:
        """Generate audio from text using Puter TTS
        
        Args:
            text: Text to convert to speech
            voice: Voice ID (lowercase, e.g., 'matthew', 'joanna')
            output_path: Where to save MP3 file
        
        Returns:
            Path to generated MP3 file
        """
        
        print(f"\n🎤 Generating audio with Puter TTS (FREE & UNLIMITED)...")
        print(f"   Voice: {voice.title()}")
        print(f"   Text length: {len(text)} characters")
        
        # ✅ For long texts (60-min videos!), use chunking!
        if len(text) > 3000:  # More than ~3000 chars = use chunking
            print(f"   🚀 Text is long, using chunking for reliability...")
            return self._generate_long_audio_chunked(text, voice, output_path)
        
        start_time = time.time()
        
        try:
            # Get voice info
            voice_info = self.VOICES.get(voice.lower())
            if not voice_info:
                print(f"   ⚠️  Voice '{voice}' not found, using Matthew (default)")
                voice_info = self.VOICES['matthew']
                voice = 'matthew'
            
            voice_name = voice_info['name']
            
            print(f"   Using: {voice_name} ({voice_info['style']})")
            print(f"   Best for: {voice_info['best_for']}")
            
            # Prepare Puter API request
            headers = {
                'Content-Type': 'application/json'
            }
            
            payload = {
                'interface': 'puter-tts',
                'driver': 'aws-polly',
                'method': 'speak',
                'args': {
                    'text': text,
                    'voice': voice_name  # Capitalized name
                }
            }
            
            # Make API call to Puter
            print(f"   📡 Calling Puter TTS API (FREE!)...")
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=120
            )
            
            if not response.ok:
                error_msg = response.text[:500]
                print(f"   ❌ API Error: {response.status_code}")
                print(f"   Details: {error_msg}")
                raise Exception(f"❌ Puter TTS API error {response.status_code}: {error_msg}")
            
            # Get audio data
            audio_data = response.content
            
            if len(audio_data) == 0:
                raise Exception("❌ No audio data received from Puter API!")
            
            # Default output path
            if output_path is None:
                output_dir = Path("output/temp")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / "puter_narration.mp3"
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write MP3 file
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            duration = time.time() - start_time
            
            print(f"✅ Audio generated with Puter TTS!")
            print(f"   File: {output_path}")
            print(f"   Size: {len(audio_data) / 1024:.1f} KB")
            print(f"   Generation time: {duration:.1f} seconds")
            print(f"   💰 Cost: $0 (FREE & UNLIMITED!)")
            
            return str(output_path)
        
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"❌ PUTER TTS GENERATION FAILED!")
            print(f"{'='*60}")
            print(f"Error: {e}")
            print(f"\n💡 Troubleshooting:")
            print(f"   1. Check internet connection")
            print(f"   2. Verify api.puter.com is accessible")
            print(f"   3. Try a different voice")
            print(f"   4. Check text length (try shorter text)")
            print(f"{'='*60}\n")
            raise
    
    def _generate_long_audio_chunked(
        self,
        text: str,
        voice: str,
        output_path: Optional[str]
    ) -> str:
        """Generate audio for long texts using chunking - FAST & RELIABLE!"""
        from pydub import AudioSegment
        
        print(f"   📝 Splitting long text into chunks...")
        
        # Split into ~3000 char chunks at sentence boundaries
        chunks = self._split_text_smart(text, max_chars=3000)
        print(f"   Split into {len(chunks)} chunks for reliability")
        
        # Get voice info
        voice_info = self.VOICES.get(voice.lower(), self.VOICES['matthew'])
        voice_name = voice_info['name']
        
        # Generate each chunk
        chunk_files = []
        temp_dir = Path("output/temp/voice_chunks")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        for i, chunk in enumerate(chunks):
            print(f"   🎤 Generating chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...")
            
            # Generate this chunk
            chunk_file = temp_dir / f"chunk_{i:03d}.mp3"
            
            try:
                # Prepare Puter API request for chunk
                headers = {'Content-Type': 'application/json'}
                payload = {
                    'interface': 'puter-tts',
                    'driver': 'aws-polly',
                    'method': 'speak',
                    'args': {
                        'text': chunk,
                        'voice': voice_name
                    }
                }
                
                response = requests.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=120
                )
                
                if response.ok and len(response.content) > 0:
                    # Save chunk
                    with open(chunk_file, 'wb') as f:
                        f.write(response.content)
                    chunk_files.append(chunk_file)
                    print(f"      ✅ Chunk {i+1} generated ({len(response.content) / 1024:.1f} KB)")
                else:
                    print(f"      ⚠️  Chunk {i+1} failed, skipping...")
                    
            except Exception as e:
                print(f"      ⚠️  Chunk {i+1} error: {e}")
        
        if len(chunk_files) == 0:
            raise Exception("❌ No audio chunks generated! All chunks failed!")
        
        print(f"   🔗 Combining {len(chunk_files)} audio chunks...")
        
        # Combine chunks using PyDub
        combined = AudioSegment.empty()
        for chunk_file in chunk_files:
            try:
                audio_chunk = AudioSegment.from_mp3(str(chunk_file))
                combined += audio_chunk
            except Exception as e:
                print(f"      ⚠️  Failed to load {chunk_file}: {e}")
        
        # Default output path
        if output_path is None:
            output_dir = Path("output/temp")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / "puter_narration.mp3"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Export combined audio
        combined.export(str(output_path), format="mp3", bitrate="192k")
        
        # Cleanup temp files
        for chunk_file in chunk_files:
            chunk_file.unlink()
        
        print(f"✅ Long audio generated!")
        print(f"   File: {output_path}")
        print(f"   Chunks: {len(chunk_files)}")
        print(f"   💰 Cost: $0 (FREE!)")
        
        return str(output_path)
    
    def _split_text_smart(self, text: str, max_chars: int = 3000) -> List[str]:
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
        
        return chunks if chunks else [text]
    
    def get_voices(self, gender: Optional[str] = None):
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
        print("\n🎤 PUTER TTS VOICES (FREE & UNLIMITED!):")
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
        print("✅ All voices are FREE with UNLIMITED usage!")
        print("💰 No API key required - No costs - No limits!")
        print("🎬 Good quality for YouTube videos!")
        print("="*60 + "\n")


def create_puter_tts() -> PuterTTS:
    """Create Puter TTS instance - No API key needed!"""
    return PuterTTS()


# Test if module is run directly
if __name__ == "__main__":
    print("🔍 Testing Puter TTS...")
    
    # List voices
    PuterTTS.list_all_voices()
    
    # Create instance (no API key needed!)
    try:
        tts = create_puter_tts()
        print("✅ Puter TTS ready - FREE & UNLIMITED!")
        
        # Test generation
        print("\n🧪 Generating test audio...")
        audio_path = tts.generate_audio(
            "Hello! This is a test of Puter TTS. It's free and unlimited!",
            voice='matthew',
            output_path='test_puter.mp3'
        )
        print(f"✅ Test audio saved: {audio_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
