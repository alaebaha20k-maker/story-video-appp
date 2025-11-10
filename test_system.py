#!/usr/bin/env python3
"""
🧪 SYSTEM TEST SUITE
Verifies all components are working correctly
"""

import requests
import time
import json

# Configuration
COLAB_URL = "https://contemplable-suzy-unfussing.ngrok-free.dev"
BACKEND_URL = "http://localhost:5000"

print("="*70)
print("🧪 STARTING SYSTEM TESTS")
print("="*70)

def test_colab_server():
    """Test Google Colab server"""
    print("\n📡 Testing Colab Server...")

    try:
        # Test home endpoint
        response = requests.get(f"{COLAB_URL}/", timeout=10)
        if response.status_code == 200:
            print("   ✅ Colab server is running")
            data = response.json()
            print(f"   ✅ Memory optimized: {data.get('memory_optimized', False)}")
            print(f"   ✅ GPU available: {data.get('gpu', False)}")
        else:
            print(f"   ❌ Colab server returned {response.status_code}")
            return False

        # Test audio endpoint
        print("\n   Testing audio generation...")
        audio_response = requests.post(
            f"{COLAB_URL}/generate_audio",
            json={"text": "Test audio", "voice": "sarah_pro", "speed": 1.0},
            timeout=30
        )
        if audio_response.status_code == 200:
            print(f"   ✅ Audio generation works ({len(audio_response.content)} bytes)")
        else:
            print(f"   ❌ Audio generation failed: {audio_response.status_code}")
            return False

        # Test image endpoint
        print("\n   Testing image generation...")
        image_response = requests.post(
            f"{COLAB_URL}/generate_image",
            json={"prompt": "test image", "style": "cinematic_film", "width": 512, "height": 512},
            timeout=60
        )
        if image_response.status_code == 200:
            print(f"   ✅ Image generation works ({len(image_response.content)} bytes)")
        else:
            print(f"   ❌ Image generation failed: {image_response.status_code}")
            return False

        print("\n✅ Colab server: ALL TESTS PASSED")
        return True

    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to Colab server")
        print("   Make sure your Colab notebook is running!")
        return False
    except Exception as e:
        print(f"   ❌ Colab test failed: {e}")
        return False

def test_backend_server():
    """Test local backend server"""
    print("\n🖥️ Testing Backend Server...")

    try:
        # Test health endpoint
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Backend server is running")
            print(f"   ✅ Voice engine: {data.get('voice_engine', 'unknown')}")
        else:
            print(f"   ❌ Backend server returned {response.status_code}")
            return False

        # Test voices endpoint
        print("\n   Testing voices endpoint...")
        voices_response = requests.get(f"{BACKEND_URL}/api/voices", timeout=5)
        if voices_response.status_code == 200:
            voices = voices_response.json()
            print(f"   ✅ Voices endpoint works ({voices.get('total', 0)} voices)")
        else:
            print(f"   ❌ Voices endpoint failed: {voices_response.status_code}")
            return False

        # Test progress endpoint
        print("\n   Testing progress endpoint...")
        progress_response = requests.get(f"{BACKEND_URL}/api/progress", timeout=5)
        if progress_response.status_code == 200:
            print("   ✅ Progress endpoint works")
        else:
            print(f"   ❌ Progress endpoint failed: {progress_response.status_code}")
            return False

        print("\n✅ Backend server: ALL TESTS PASSED")
        return True

    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to backend server")
        print("   Make sure you run: python api_server.py")
        return False
    except Exception as e:
        print(f"   ❌ Backend test failed: {e}")
        return False

def test_integration():
    """Test Colab + Backend integration"""
    print("\n🔗 Testing Integration...")

    try:
        # Start a minimal generation
        print("\n   Starting test video generation...")
        gen_response = requests.post(
            f"{BACKEND_URL}/api/generate-video",
            json={
                "topic": "System Test",
                "num_scenes": 2,
                "voice_id": "aria",
                "zoom_effect": False,
                "enable_captions": False
            },
            timeout=10
        )

        if gen_response.status_code == 200:
            print("   ✅ Generation started successfully")

            # Wait a bit
            time.sleep(5)

            # Check progress
            progress_response = requests.get(f"{BACKEND_URL}/api/progress", timeout=5)
            if progress_response.status_code == 200:
                progress = progress_response.json()
                print(f"   ✅ Progress: {progress.get('status', 'unknown')} ({progress.get('progress', 0)}%)")
                print("   ✨ Integration test PASSED (generation running)")
                return True
            else:
                print("   ⚠️  Could not check progress")
                return False
        else:
            print(f"   ❌ Generation failed to start: {gen_response.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        return False

def test_media_mixing():
    """Test media source mixing feature"""
    print("\n🎨 Testing Media Source Mixing...")

    try:
        response = requests.post(
            f"{BACKEND_URL}/api/generate-mixed-media",
            json={
                "topic": "Mixed Media Test",
                "num_scenes": 3,
                "media_config": {
                    "priority": ["ai"],
                    "generate_ai": True,
                    "stock_items": [],
                    "manual_files": []
                }
            },
            timeout=10
        )

        if response.status_code == 200:
            print("   ✅ Mixed media endpoint works")
            return True
        else:
            print(f"   ❌ Mixed media failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ Media mixing test failed: {e}")
        return False

# Run all tests
print("\n" + "="*70)
print("🏁 RUNNING ALL TESTS")
print("="*70)

results = {
    "Colab Server": test_colab_server(),
    "Backend Server": test_backend_server(),
    "Integration": test_integration(),
    "Media Mixing": test_media_mixing()
}

# Summary
print("\n" + "="*70)
print("📊 TEST RESULTS")
print("="*70)

for test_name, passed in results.items():
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"   {test_name}: {status}")

all_passed = all(results.values())

print("\n" + "="*70)
if all_passed:
    print("🎉 ALL TESTS PASSED - SYSTEM IS 100% OPERATIONAL!")
else:
    print("⚠️  SOME TESTS FAILED - CHECK ERRORS ABOVE")
print("="*70)

exit(0 if all_passed else 1)
