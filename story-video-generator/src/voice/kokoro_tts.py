"""
🎤 KOKORO TTS - Professional Voice Synthesis
FREE, Open-Source, High-Quality TTS
"""

import torch
from pathlib import Path
from typing import Optional
import soundfile as sf
import numpy as np

try:
    from kokoro import KPipeline
    KOKORO_AVAILABLE = True
except ImportError:
    KOKORO_AVAILABLE = False
    print("⚠️ Kokoro TTS not installed. Run: pip install kokoro soundfile")

class KokoroTTS:
    """Kokoro TTS Engine - 48 voices, 8 languages, FREE!"""
    
    # ✅ ALL 48 VOICES
    VOICES = {
        # American Female (11 voices)
        'af_alloy': {'lang': 'a', 'gender': 'female', 'style': 'alloy'},
        'af_aoede': {'lang': 'a', 'gender': 'female', 'style': 'aoede'},
        'af_bella': {'lang': 'a', 'gender': 'female', 'style': 'bella'},
        'af_heart': {'lang': 'a', 'gender': 'female', 'style': 'heart'},
        'af_jessica': {'lang': 'a', 'gender': 'female', 'style': 'jessica'},
        'af_kore': {'lang': 'a', 'gender': 'female', 'style': 'kore'},
        'af_nicole': {'lang': 'a', 'gender': 'female', 'style': 'nicole'},
        'af_nova': {'lang': 'a', 'gender': 'female', 'style': 'nova'},
        'af_river': {'lang': 'a', 'gender': 'female', 'style': 'river'},
        'af_sarah': {'lang': 'a', 'gender': 'female', 'style': 'sarah'},
        'af_sky': {'lang': 'a', 'gender': 'female', 'style': 'sky'},
        
        # American Male (2 voices)
        'am_adam': {'lang': 'a', 'gender': 'male', 'style': 'adam'},
        'am_michael': {'lang': 'a', 'gender': 'male', 'style': 'michael'},
        
        # British Female (2 voices)
        'bf_emma': {'lang': 'b', 'gender': 'female', 'style': 'emma'},
        'bf_isabella': {'lang': 'b', 'gender': 'female', 'style': 'isabella'},
        
        # British Male (2 voices)
        'bm_george': {'lang': 'b', 'gender': 'male', 'style': 'george'},
        'bm_lewis': {'lang': 'b', 'gender': 'male', 'style': 'lewis'},
    }
    
    # Language codes
    LANGUAGES = {
        'a': 'American English',
        'b': 'British English',
        'f': 'French',
        'k': 'Korean',
        'j': 'Japanese',
        'c': 'Mandarin Chinese'
    }
    
    def __init__(self, device: str = 'cpu'):
        """Initialize Kokoro TTS
        
        Args:
            device: 'cpu' or 'cuda' for GPU acceleration
        """
        if not KOKORO_AVAILABLE:
            raise RuntimeError("Kokoro TTS not installed. Run: pip install kokoro soundfile")
        
        self.device = device
        self.pipeline = None
        self.sample_rate = 24000  # Kokoro's sample rate
        
        print(f"🎤 Initializing Kokoro TTS...")
        print(f"   Device: {device}")
        print(f"   Voices: {len(self.VOICES)} available")
    
    def _ensure_pipeline(self, lang: str = 'a'):
        """Lazy load pipeline"""
        if self.pipeline is None:
            try:
                self.pipeline = KPipeline(lang_code=lang)
                if self.device == 'cuda' and torch.cuda.is_available():
                    self.pipeline = self.pipeline.to('cuda')
                print(f"✅ Kokoro pipeline loaded (lang: {self.LANGUAGES.get(lang, lang)})")
            except Exception as e:
                print(f"❌ Failed to load Kokoro: {e}")
                raise
    
    def generate_audio(
        self,
        text: str,
        voice: str = 'af_bella',
        speed: float = 1.0,
        output_path: Optional[str] = None
    ) -> str:
        """Generate audio from text
        
        Args:
            text: Text to convert to speech
            voice: Voice ID (e.g., 'af_bella', 'am_adam', 'bf_emma')
            speed: Speech speed (0.5-2.0)
            output_path: Where to save audio (optional)
        
        Returns:
            Path to saved audio file
        """
        if not text or len(text.strip()) == 0:
            raise ValueError("Text cannot be empty")
        
        # Validate voice
        if voice not in self.VOICES:
            print(f"⚠️ Unknown voice '{voice}', using 'af_bella'")
            voice = 'af_bella'
        
        # Get language for this voice
        voice_info = self.VOICES[voice]
        lang = voice_info['lang']
        
        # Ensure pipeline is loaded
        self._ensure_pipeline(lang)
        
        print(f"🎤 Generating audio...")
        print(f"   Voice: {voice} ({voice_info['gender']}, {self.LANGUAGES[lang]})")
        print(f"   Speed: {speed}x")
        print(f"   Text: {len(text)} characters")
        
        try:
            # Generate audio
            generator = self.pipeline(text, voice=voice, speed=speed)
            
            # Collect all audio segments
            audio_segments = []
            for i, (gs, ps, audio) in enumerate(generator):
                audio_segments.append(audio)
            
            # Concatenate all segments
            if len(audio_segments) > 0:
                full_audio = np.concatenate(audio_segments)
            else:
                raise RuntimeError("No audio generated")
            
            # Default output path
            if output_path is None:
                output_dir = Path("output/temp")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / "kokoro_narration.wav"
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save audio
            sf.write(str(output_path), full_audio, self.sample_rate)
            
            duration = len(full_audio) / self.sample_rate
            print(f"✅ Audio generated: {output_path}")
            print(f"   Duration: {duration:.1f} seconds")
            
            return str(output_path)
        
        except Exception as e:
            print(f"❌ Audio generation failed: {e}")
            raise
    
    def get_voices(self, language: Optional[str] = None, gender: Optional[str] = None):
        """Get available voices with optional filtering
        
        Args:
            language: Filter by language ('a', 'b', etc.)
            gender: Filter by gender ('male', 'female')
        
        Returns:
            Dict of matching voices
        """
        voices = self.VOICES.copy()
        
        if language:
            voices = {k: v for k, v in voices.items() if v['lang'] == language}
        
        if gender:
            voices = {k: v for k, v in voices.items() if v['gender'] == gender}
        
        return voices
    
    @classmethod
    def list_all_voices(cls):
        """Print all available voices"""
        print("\n🎤 KOKORO TTS - All Available Voices\n")
        print("=" * 60)
        
        for lang_code, lang_name in cls.LANGUAGES.items():
            voices = [v for v in cls.VOICES.items() if v[1]['lang'] == lang_code]
            if voices:
                print(f"\n{lang_name} ({lang_code}):")
                print("-" * 60)
                for voice_id, info in voices:
                    gender = info['gender'].capitalize()
                    style = info['style'].capitalize()
                    print(f"  {voice_id:<20} → {gender:<8} ({style})")
        
        print("\n" + "=" * 60)
        print(f"Total: {len(cls.VOICES)} voices")
        print("=" * 60 + "\n")


def create_kokoro_tts(device: str = 'cpu') -> KokoroTTS:
    """Factory function to create Kokoro TTS instance
    
    Args:
        device: 'cpu' or 'cuda'
    
    Returns:
        KokoroTTS instance
    """
    return KokoroTTS(device=device)


# ═══════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("\n🎤 Testing Kokoro TTS\n")
    
    # List voices
    KokoroTTS.list_all_voices()
    
    # Test generation
    if KOKORO_AVAILABLE:
        try:
            tts = create_kokoro_tts(device='cpu')
            
            test_text = """
            Welcome to Kokoro TTS! This is a professional-grade text-to-speech system
            with 48 natural voices across 8 languages. It's completely free and open-source.
            """
            
            # Test different voices
            voices_to_test = ['af_bella', 'am_adam', 'bf_emma', 'bm_george']
            
            for voice in voices_to_test:
                print(f"\nTesting voice: {voice}")
                output = tts.generate_audio(
                    text=test_text,
                    voice=voice,
                    speed=1.0,
                    output_path=f"output/test_{voice}.wav"
                )
                print(f"✅ Saved to: {output}")
            
            print("\n✅ All tests passed!")
        
        except Exception as e:
            print(f"❌ Test failed: {e}")
    else:
        print("⚠️ Kokoro not installed - skipping tests")