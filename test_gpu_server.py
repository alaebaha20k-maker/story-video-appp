#!/usr/bin/env python3
"""
🧪 Test GPU Server Connection
Quick test script to verify your Google Colab GPU server is working
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "story-video-generator"))

print("\n" + "="*60)
print("🧪 Testing GPU Server Connection")
print("="*60 + "\n")

# Step 1: Check environment variables
print("📋 Step 1: Checking environment variables...")

sdxl_url = os.getenv('SDXL_API_URL', '').strip()
kokoro_url = os.getenv('KOKORO_API_URL', '').strip()

if not sdxl_url and not kokoro_url:
    print("❌ No API URLs found in environment!")
    print("\n💡 Please set environment variables:")
    print("   - SDXL_API_URL")
    print("   - KOKORO_API_URL")
    print("\nOr create a .env file with these variables.")
    print("See .env.example for format.")
    sys.exit(1)

if sdxl_url:
    print(f"✅ SDXL_API_URL: {sdxl_url}")
else:
    print("⚠️  SDXL_API_URL not set (will use local generation)")

if kokoro_url:
    print(f"✅ KOKORO_API_URL: {kokoro_url}")
else:
    print("⚠️  KOKORO_API_URL not set (will use Edge-TTS)")

# Step 2: Test health endpoint
if sdxl_url or kokoro_url:
    print("\n📡 Step 2: Testing health endpoint...")

    import requests

    # Extract base URL
    test_url = sdxl_url or kokoro_url
    base_url = test_url.rsplit('/', 1)[0]
    health_url = f"{base_url}/health"

    try:
        response = requests.get(health_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        print(f"✅ Server is running!")
        print(f"   Status: {data.get('status', 'unknown')}")
        print(f"   Device: {data.get('device', 'unknown')}")

        services = data.get('services', {})
        if services:
            print(f"   Services:")
            for service, status in services.items():
                print(f"     - {service}: {status}")

    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server!")
        print(f"\n💡 Troubleshooting:")
        print(f"   1. Make sure Google Colab notebook is running")
        print(f"   2. Check if ngrok URL is correct")
        print(f"   3. Try accessing the URL in your browser: {health_url}")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Health check failed: {e}")
        sys.exit(1)

# Step 3: Test image generation
if sdxl_url:
    print("\n🎨 Step 3: Testing image generation...")

    try:
        from src.ai.sdxl_turbo_client import generate_sdxl_image

        test_prompt = "A beautiful sunset over mountains, cinematic, 8k"
        print(f"   Prompt: {test_prompt}")

        image_path = generate_sdxl_image(
            prompt=test_prompt,
            output_path="test_output/test_image.png",
            api_url=sdxl_url
        )

        print(f"✅ Image generation test PASSED!")
        print(f"   Saved to: {image_path}")

    except Exception as e:
        print(f"❌ Image generation test FAILED: {e}")
        sys.exit(1)
else:
    print("\n⏭️  Step 3: Skipping image test (SDXL_API_URL not set)")

# Step 4: Test voice generation
if kokoro_url:
    print("\n🎤 Step 4: Testing voice generation...")

    try:
        from src.voice.kokoro_api_client import generate_kokoro_audio

        test_text = "Hello! This is a test of the Kokoro TTS API."
        print(f"   Text: {test_text}")

        audio_path = generate_kokoro_audio(
            text=test_text,
            voice='aria',
            speed=1.0,
            output_path="test_output/test_audio.wav",
            api_url=kokoro_url
        )

        print(f"✅ Voice generation test PASSED!")
        print(f"   Saved to: {audio_path}")

    except Exception as e:
        print(f"❌ Voice generation test FAILED: {e}")
        sys.exit(1)
else:
    print("\n⏭️  Step 4: Skipping voice test (KOKORO_API_URL not set)")

# Final results
print("\n" + "="*60)
print("🎉 ALL TESTS PASSED!")
print("="*60)
print("\nYour GPU server is working correctly!")
print("You can now generate videos with GPU acceleration.")
print("\n💡 Next steps:")
print("   1. Update api_server.py to use hybrid_image_generator")
print("   2. Run: python api_server.py")
print("   3. Generate videos and enjoy the speed!")
print("="*60 + "\n")
