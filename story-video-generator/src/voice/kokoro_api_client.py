"""
🎤 Kokoro API Client - Connect to Remote GPU Server
"""

import requests
import base64
from pathlib import Path
from typing import Optional
import os

class KokoroAPIClient:
    """Client for remote Kokoro TTS API (running on Google Colab)"""

    # Voice mapping from user-friendly names to Kokoro voices
    VOICE_MAP = {
        'aria': 'sarah_pro',
        'guy': 'adam_pro',
        'jenny': 'nicole_pro',
        'christopher': 'michael_pro',
        'sara': 'bella_pro',
        'roger': 'adam_pro',
        'nancy': 'jessica_pro',
        'andrew': 'adam_pro',
    }

    def __init__(self, api_url: Optional[str] = None):
        """Initialize Kokoro API client

        Args:
            api_url: Base URL of the remote API (e.g., https://xyz.ngrok-free.dev)
                    If not provided, will use KOKORO_API_URL from environment
        """
        self.api_url = api_url or os.getenv('KOKORO_API_URL', '')

        if not self.api_url:
            raise ValueError(
                "Kokoro API URL not provided. Please set KOKORO_API_URL environment variable "
                "or pass api_url parameter."
            )

        # Remove trailing slash
        self.api_url = self.api_url.rstrip('/')

        # If URL doesn't have /generate_audio, add it
        if not self.api_url.endswith('/generate_audio'):
            self.api_url = f"{self.api_url}/generate_audio"

        print(f"🎤 Kokoro API Client initialized")
        print(f"   URL: {self.api_url}")

    def generate_audio(
        self,
        text: str,
        voice: str = 'aria',
        speed: float = 1.0,
        output_path: Optional[str] = None
    ) -> str:
        """Generate audio using remote Kokoro API

        Args:
            text: Text to convert to speech
            voice: Voice name (aria, guy, jenny, etc.)
            speed: Speech speed (0.5-2.0)
            output_path: Where to save audio file

        Returns:
            Path to saved audio file
        """
        if not text or len(text.strip()) == 0:
            raise ValueError("Text cannot be empty")

        # Map voice name
        mapped_voice = self.VOICE_MAP.get(voice.lower(), 'sarah_pro')

        print(f"🎤 Generating audio with Kokoro API...")
        print(f"   Voice: {voice} (mapped to {mapped_voice})")
        print(f"   Speed: {speed}x")
        print(f"   Text length: {len(text)} characters")

        try:
            # Make API request
            response = requests.post(
                self.api_url,
                json={
                    'text': text,
                    'voice': voice.lower(),
                    'speed': speed
                },
                timeout=300  # 5 minute timeout for long audio
            )

            response.raise_for_status()

            # Parse response
            data = response.json()

            if not data.get('success'):
                raise Exception(f"API returned error: {data.get('error', 'Unknown error')}")

            # Decode base64 audio
            audio_base64 = data.get('audio')
            if not audio_base64:
                raise Exception("No audio data in response")

            audio_bytes = base64.b64decode(audio_base64)

            # Default output path
            if output_path is None:
                output_dir = Path("output/temp")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / "narration.wav"

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save audio file
            with open(output_path, 'wb') as f:
                f.write(audio_bytes)

            duration = data.get('duration', 0)
            print(f"✅ Audio generated successfully!")
            print(f"   Duration: {duration:.1f} seconds")
            print(f"   Saved to: {output_path}")

            return str(output_path)

        except requests.exceptions.HTTPError as e:
            print(f"❌ Kokoro API HTTP error: {e.response.status_code}")
            try:
                error_data = e.response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Error response: {e.response.text}")
            raise Exception(f"Kokoro API error: {e.response.status_code}")

        except requests.exceptions.Timeout:
            print(f"❌ Kokoro API timeout")
            raise Exception("Kokoro API timeout - audio generation took too long")

        except requests.exceptions.ConnectionError as e:
            print(f"❌ Kokoro API connection error: {e}")
            print(f"\n💡 Troubleshooting:")
            print(f"   1. Check if Google Colab notebook is running")
            print(f"   2. Verify ngrok URL is correct: {self.api_url}")
            print(f"   3. Check internet connection")
            print(f"   4. Try restarting the Colab notebook")
            raise Exception(f"Cannot connect to Kokoro API")

        except Exception as e:
            print(f"❌ Kokoro API error: {e}")
            raise


def generate_kokoro_audio(
    text: str,
    voice: str = 'aria',
    speed: float = 1.0,
    output_path: Optional[str] = None,
    api_url: Optional[str] = None
) -> str:
    """Convenience function to generate audio

    Args:
        text: Text to convert to speech
        voice: Voice name
        speed: Speech speed
        output_path: Where to save audio
        api_url: API URL (optional, uses env var if not provided)

    Returns:
        Path to saved audio file
    """
    client = KokoroAPIClient(api_url)
    return client.generate_audio(text, voice, speed, output_path)


# Test code
if __name__ == '__main__':
    print("\n🎤 Testing Kokoro API Client\n")

    # Test with sample text
    test_text = "Welcome to Kokoro TTS! This is a test of the remote API."

    try:
        api_url = input("Enter your ngrok URL (e.g., https://xyz.ngrok-free.dev): ").strip()

        if not api_url:
            print("❌ No URL provided")
        else:
            audio_path = generate_kokoro_audio(
                text=test_text,
                voice='aria',
                speed=1.0,
                output_path='test_kokoro_api.wav',
                api_url=api_url
            )

            print(f"\n✅ Test successful! Audio saved to: {audio_path}")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
