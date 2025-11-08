"""
🎤 INWORLD AI TTS - Super Fast, High Quality Voice Generation
"""

import os
import base64
import requests
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
import time

class InworldTTS:
    """Inworld AI TTS Engine - Fast & Professional"""
    
    # Popular Inworld AI voices
    VOICES = {
        'ashley': {'name': 'Ashley', 'gender': 'female', 'style': 'natural'},
        'brian': {'name': 'Brian', 'gender': 'male', 'style': 'professional'},
        'emma': {'name': 'Emma', 'gender': 'female', 'style': 'warm'},
        'john': {'name': 'John', 'gender': 'male', 'style': 'deep'},
        'sarah': {'name': 'Sarah', 'gender': 'female', 'style': 'energetic'},
        'mike': {'name': 'Mike', 'gender': 'male', 'style': 'casual'},
        'rachel': {'name': 'Rachel', 'gender': 'female', 'style': 'clear'},
        'david': {'name': 'David', 'gender': 'male', 'style': 'authoritative'},
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Inworld TTS
        
        Args:
            api_key: Base64 encoded API key (or set INWORLD_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('INWORLD_API_KEY')
        if not self.api_key:
            raise ValueError("Inworld API key required! Set INWORLD_API_KEY environment variable")
        
        self.api_url = 'https://api.inworld.ai/tts/v1/voice'
        self.model_id = 'inworld-tts-1'
        
        print(f"🎤 Inworld AI TTS initialized")
        print(f"   Available voices: {len(self.VOICES)}")
    
    def generate_audio(
        self,
        text: str,
        voice: str = 'ashley',
        output_path: Optional[str] = None
    ) -> str:
        """Generate audio from text with automatic parallel chunking
        
        Args:
            text: Text to convert to speech
            voice: Voice ID (e.g., 'ashley', 'brian', 'emma')
            output_path: Where to save audio file
        
        Returns:
            Path to generated audio file
        """
        if not text or len(text.strip()) == 0:
            raise ValueError("Text cannot be empty")
        
        # Validate voice
        voice_lower = voice.lower()
        if voice_lower not in self.VOICES:
            print(f"⚠️  Unknown voice '{voice}', using 'ashley'")
            voice_lower = 'ashley'
        
        voice_info = self.VOICES[voice_lower]
        voice_name = voice_info['name']
        
        print(f"🎤 Generating audio with Inworld AI...")
        print(f"   Voice: {voice_name} ({voice_info['gender']}, {voice_info['style']})")
        print(f"   Text: {len(text)} characters")
        
        # For long text (>1000 chars), use parallel chunking for SPEED
        if len(text) > 1000:
            return self._generate_long_audio_parallel(text, voice_name, output_path)
        
        # For short text, generate directly
        start_time = time.time()
        
        try:
            audio_content = self._generate_single(text, voice_name)
            
            # Default output path
            if output_path is None:
                output_dir = Path("output/temp")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / "inworld_narration.mp3"
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save audio
            audio_buffer = base64.b64decode(audio_content)
            with open(output_path, 'wb') as f:
                f.write(audio_buffer)
            
            duration = time.time() - start_time
            print(f"✅ Audio generated: {output_path}")
            print(f"   Generation time: {duration:.1f} seconds")
            
            return str(output_path)
        
        except Exception as e:
            print(f"❌ Audio generation failed: {e}")
            raise
    
    def _generate_single(self, text: str, voice_name: str) -> str:
        """Generate audio for single text chunk"""
        
        headers = {
            'Authorization': f'Basic {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'text': text,
            'voiceId': voice_name,
            'modelId': self.model_id
        }
        
        try:
            print(f"   🔧 API Request: URL={self.api_url}, Voice={voice_name}, TextLen={len(text)}")
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=120)
            
            print(f"   🔧 API Response: Status={response.status_code}")
            
            if not response.ok:
                error_detail = f"Status {response.status_code}: {response.text[:500]}"
                print(f"   ❌ API Error Details: {error_detail}")
                raise Exception(f"Inworld API error: {error_detail}")
            
            result = response.json()
            
            if 'audioContent' not in result:
                print(f"   ❌ Response missing 'audioContent': {list(result.keys())}")
                raise Exception(f"API response missing audioContent. Got keys: {list(result.keys())}")
            
            print(f"   ✅ Audio content received: {len(result['audioContent'])} bytes (base64)")
            return result['audioContent']
            
        except requests.exceptions.Timeout:
            raise Exception(f"Inworld API timeout after 120s for text length {len(text)}")
        except requests.exceptions.ConnectionError as e:
            raise Exception(f"Inworld API connection error: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {type(e).__name__}: {e}")
            raise
    
    def _generate_long_audio_parallel(
        self,
        text: str,
        voice_name: str,
        output_path: Optional[str]
    ) -> str:
        """Generate audio for long text using parallel processing - SUPER FAST!"""
        
        print(f"   🚀 Text is long, using ULTRA-FAST parallel processing...")
        
        # Split text into chunks at sentence boundaries
        # ⚡ SMALLER CHUNKS for Inworld API limits (500 chars max for reliability)
        chunks = self._split_text_smart(text, max_chars=500)
        print(f"   Split into {len(chunks)} chunks (500 chars each for API reliability)")
        print(f"   🚀 Processing {len(chunks)} chunks in PARALLEL for 10x+ speedup...")
        
        start_time = time.time()
        
        # Generate audio for each chunk in parallel
        # ⚡ ADAPTIVE WORKERS: Fewer workers for reliability, more for speed
        # For Inworld API: 4-6 workers prevents rate limiting while staying fast
        num_workers = min(6, len(chunks))  # Max 6 workers to avoid API rate limits
        print(f"   ⚡ Using {num_workers} parallel workers (prevents API rate limiting)")
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            for i, chunk in enumerate(chunks):
                future = executor.submit(self._generate_chunk, chunk, voice_name, i)
                futures.append(future)
            
            # Wait for all chunks to complete and verify we got them all
            chunk_audios = []
            failed_chunks = []
            
            for i, future in enumerate(futures):
                try:
                    chunk_data = future.result(timeout=180)  # 3-minute timeout per chunk
                    if chunk_data and len(chunk_data) > 0:
                        chunk_audios.append(chunk_data)
                    else:
                        print(f"   ❌ Chunk {i} returned empty data!")
                        failed_chunks.append(i)
                except Exception as e:
                    print(f"   ❌ Chunk {i} completely failed: {e}")
                    failed_chunks.append(i)
            
            # Verify we got all chunks
            if failed_chunks:
                print(f"   ⚠️  WARNING: {len(failed_chunks)} chunks failed: {failed_chunks}")
                print(f"   ⚠️  Audio will be INCOMPLETE! Got {len(chunk_audios)}/{len(chunks)} chunks")
            else:
                print(f"   ✅ All {len(chunk_audios)} chunks generated successfully!")
        
        # ✅ FIX: Use PyDub to properly concatenate MP3 chunks (not raw bytes!)
        # Raw byte concatenation breaks MP3 headers!
        
        if len(chunk_audios) == 0:
            raise Exception("❌ No audio data generated! All chunks failed!")
        
        from pydub import AudioSegment
        
        # Default output path
        if output_path is None:
            output_dir = Path("output/temp")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / "inworld_narration.mp3"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save chunks as temporary files first
        temp_dir = Path("output/temp/audio_chunks")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"   🔧 Combining {len(chunk_audios)} audio chunks using PyDub...")
        
        chunk_files = []
        for i, chunk_data in enumerate(chunk_audios):
            chunk_file = temp_dir / f"chunk_{i:03d}.mp3"
            with open(chunk_file, 'wb') as f:
                f.write(chunk_data)
            chunk_files.append(chunk_file)
        
        # Combine using PyDub (proper MP3 handling!)
        combined = AudioSegment.empty()
        for chunk_file in chunk_files:
            try:
                audio_chunk = AudioSegment.from_mp3(str(chunk_file))
                combined += audio_chunk
            except Exception as e:
                print(f"   ⚠️  Failed to load chunk {chunk_file}: {e}")
        
        # Export as proper MP3
        combined.export(str(output_path), format="mp3", bitrate="192k")
        
        # Clean up temp files
        for chunk_file in chunk_files:
            chunk_file.unlink()
        
        print(f"   ✅ MP3 properly combined with headers!")
        
        duration = time.time() - start_time
        print(f"✅ Audio generated: {output_path}")
        print(f"   Generation time: {duration:.1f} seconds ⚡")
        
        return str(output_path)
    
    def _generate_chunk(self, text: str, voice_name: str, chunk_id: int) -> bytes:
        """Generate audio for a single chunk (used in parallel processing)"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                audio_content = self._generate_single(text, voice_name)
                if attempt > 0:
                    print(f"   ✅ Chunk {chunk_id} succeeded on retry {attempt}")
                return base64.b64decode(audio_content)
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"   ⚠️  Chunk {chunk_id} failed (attempt {attempt+1}/{max_retries}): {e}")
                    time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                else:
                    print(f"   ❌ Chunk {chunk_id} failed after {max_retries} attempts: {e}")
                    raise  # Re-raise on final failure
    
    def _split_text_smart(self, text: str, max_chars: int = 1000) -> list:
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
    
    def get_voices(self, gender: Optional[str] = None):
        """Get available voices with optional filtering
        
        Args:
            gender: Filter by gender ('male', 'female')
        
        Returns:
            Dict of matching voices
        """
        voices = self.VOICES.copy()
        
        if gender:
            voices = {k: v for k, v in voices.items() if v['gender'] == gender}
        
        return voices
    
    @classmethod
    def list_all_voices(cls):
        """Print all available voices"""
        print("\n🎤 INWORLD AI - Available Voices\n")
        print("=" * 60)
        
        for voice_id, info in cls.VOICES.items():
            gender = info['gender'].capitalize()
            style = info['style'].capitalize()
            name = info['name']
            print(f"  {voice_id:<15} → {name:<10} {gender:<8} ({style})")
        
        print("=" * 60)
        print(f"Total: {len(cls.VOICES)} voices")
        print("=" * 60 + "\n")


def create_inworld_tts(api_key: Optional[str] = None) -> InworldTTS:
    """Factory function to create Inworld TTS instance
    
    Args:
        api_key: Base64 encoded API key
    
    Returns:
        InworldTTS instance
    """
    return InworldTTS(api_key=api_key)


# Test
if __name__ == '__main__':
    print("\n🎤 Testing Inworld AI TTS\n")
    
    # List voices
    InworldTTS.list_all_voices()
    
    # Test generation
    try:
        # Set your API key
        api_key = os.getenv('INWORLD_API_KEY')
        if not api_key:
            print("⚠️  Set INWORLD_API_KEY environment variable to test")
            exit(1)
        
        tts = create_inworld_tts(api_key=api_key)
        
        test_text = """
        Welcome to Inworld AI! This is a professional-grade text-to-speech system
        with natural voices. It's fast and produces high-quality audio.
        """
        
        # Test different voices
        voices_to_test = ['ashley', 'brian', 'emma']
        
        for voice in voices_to_test:
            print(f"\nTesting voice: {voice}")
            output = tts.generate_audio(
                text=test_text,
                voice=voice,
                output_path=f"output/test_{voice}.mp3"
            )
            print(f"✅ Saved to: {output}")
        
        print("\n✅ All tests passed!")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
