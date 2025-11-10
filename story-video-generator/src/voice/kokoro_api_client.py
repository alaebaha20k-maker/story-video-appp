"""
🎤 KOKORO TTS API CLIENT - Remote GPU-Powered Voice Generation
Connects to Google Colab-hosted Kokoro TTS API via ngrok
"""

import requests
from pathlib import Path
from typing import Dict, Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.logger import logger
from config import KOKORO_API_URL

# Remote Kokoro API endpoint (Google Colab + ngrok)
# URL is loaded from config.py - update config.py with your ngrok URL!

# Voice Mapping: Frontend Voice IDs → Kokoro API Voices
# Maps frontend options to Google Colab Kokoro API voices
VOICE_MAPPING = {
    # Male Voices
    'guy': 'adam_narration',           # Default male → Adam Narration
    'andrew': 'adam_narration',        # Male Clear → Adam Narration
    'christopher': 'michael',          # Male Friendly → Michael
    'brian': 'adam_business',          # Male British → Adam Business
    'george': 'george_gb',             # Male Deep → George GB

    # Female Voices
    'aria': 'sarah_pro',               # Default female → Sarah Pro
    'jenny': 'nicole',                 # Female Friendly → Nicole
    'sara': 'sarah_natural',           # Female Clear → Sarah Natural
    'jane': 'nicole',                  # Female Warm → Nicole
    'libby': 'emma_gb',                # Female British → Emma GB
    'emma': 'emma_gb',                 # Female Expressive → Emma GB
}


def get_kokoro_voice(edge_voice_id: str) -> str:
    """
    Map Edge TTS voice ID to Kokoro API voice

    Args:
        edge_voice_id: Frontend voice identifier (guy, aria, christopher, etc.)

    Returns:
        Kokoro API voice name (adam_narration, sarah_pro, nicole, etc.)
    """
    kokoro_voice = VOICE_MAPPING.get(edge_voice_id.lower(), 'sarah_pro')
    logger.info(f"🎭 Voice mapping: {edge_voice_id} → {kokoro_voice}")
    return kokoro_voice


def generate_kokoro_audio(
    text: str,
    voice: str,
    speed: float = 1.0,
    output_path: str = "output.wav",
    timeout: int = 600
) -> str:
    """
    Generate audio using Remote Kokoro TTS API (Google Colab GPU)

    Args:
        text: Text to convert to speech
        voice: Frontend voice ID (will be mapped to Kokoro voice)
        speed: Voice speed (0.5 - 2.0, default 1.0)
        output_path: Where to save the WAV file
        timeout: Request timeout in seconds (default 600 = 10 minutes)

    Returns:
        Path to generated audio file

    Raises:
        requests.exceptions.RequestException: If API call fails
        ValueError: If response is invalid
    """
    try:
        # Map voice ID
        kokoro_voice = get_kokoro_voice(voice)

        # Clamp speed to valid range
        speed = max(0.5, min(2.0, speed))

        logger.info(f"🎤 Generating audio with Kokoro API...")
        logger.info(f"   Voice: {kokoro_voice} (speed: {speed}x)")
        logger.info(f"   Text length: {len(text)} characters")

        # Prepare request
        payload = {
            "text": text,
            "voice": kokoro_voice,
            "speed": speed
        }

        # POST to Kokoro API
        response = requests.post(
            KOKORO_API_URL,
            json=payload,
            timeout=timeout,
            headers={
                "Content-Type": "application/json"
            }
        )

        # Check response
        response.raise_for_status()  # Raise exception for 4xx/5xx status codes

        # Validate response content
        if not response.content:
            raise ValueError("Empty response from Kokoro API")

        # Save WAV file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(response.content)

        file_size = output_path.stat().st_size
        logger.info(f"✅ Audio generated: {output_path} ({file_size:,} bytes)")

        return str(output_path)

    except requests.exceptions.Timeout:
        logger.error(f"⏱️ Kokoro API timeout after {timeout}s")
        raise Exception(f"Kokoro API request timed out after {timeout} seconds")

    except requests.exceptions.ConnectionError:
        logger.error("🔌 Failed to connect to Kokoro API (check ngrok URL)")
        raise Exception("Cannot connect to Kokoro API - check if Google Colab server is running")

    except requests.exceptions.HTTPError as e:
        logger.error(f"❌ Kokoro API HTTP error: {e.response.status_code}")
        try:
            error_detail = e.response.json()
            logger.error(f"   Error details: {error_detail}")
        except:
            logger.error(f"   Response: {e.response.text[:200]}")
        raise Exception(f"Kokoro API error: {e.response.status_code}")

    except Exception as e:
        logger.error(f"❌ Kokoro API generation failed: {e}")
        raise


def check_kokoro_api_health() -> bool:
    """
    Check if Kokoro API is accessible

    Returns:
        True if API is reachable, False otherwise
    """
    try:
        # Try to connect to the API with a short timeout
        response = requests.get(
            KOKORO_API_URL.replace('/generate_audio', '/health'),  # Try health endpoint
            timeout=5
        )
        return response.ok
    except:
        # If health endpoint doesn't exist, try a minimal generate request
        try:
            response = requests.post(
                KOKORO_API_URL,
                json={"text": "test", "voice": "sarah_pro", "speed": 1.0},
                timeout=10
            )
            return response.ok
        except:
            return False


def get_available_voices() -> Dict[str, str]:
    """
    Get available Kokoro voices

    Returns:
        Dictionary mapping voice IDs to descriptions
    """
    return {
        'am_adam': 'American Male - Deep',
        'am_michael': 'American Male - Friendly',
        'af_sarah': 'American Female - Clear',
        'af_nicole': 'American Female - Warm',
        'bf_emma': 'British Female - Professional',
        'bm_george': 'British Male - Authoritative'
    }


# Test function
if __name__ == "__main__":
    print("🎤 Kokoro TTS API Client Test")
    print(f"API URL: {KOKORO_API_URL}")
    print("\n📋 Voice Mapping:")
    for edge_voice, kokoro_voice in VOICE_MAPPING.items():
        print(f"  {edge_voice:15} → {kokoro_voice}")

    print("\n🔍 Testing API connection...")
    if check_kokoro_api_health():
        print("✅ Kokoro API is accessible")
    else:
        print("❌ Cannot reach Kokoro API")

    print("\n🎭 Available Kokoro Voices:")
    for voice_id, description in get_available_voices().items():
        print(f"  {voice_id:15} - {description}")
