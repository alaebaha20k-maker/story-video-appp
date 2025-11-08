"""
🔍 INWORLD API DIAGNOSTIC TOOL
Test your Inworld AI credentials and available voices
"""

import os
import requests
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials
INWORLD_JWT_KEY = os.getenv('INWORLD_JWT_KEY', 'bMyt2B6JztQUliqlBm6HHdQCcAbsJXnJ')
INWORLD_JWT_SECRET = os.getenv('INWORLD_JWT_SECRET', 'siWpw2isZJkLIE6llDql2yi2D5xAyT7qQYop4he0X1seZ8ZksvCDzS1gWJcccIyD')

print("="*60)
print("🔍 INWORLD API DIAGNOSTIC TEST")
print("="*60)

# Test 1: Check credentials
print("\n📋 STEP 1: Checking Credentials...")
print(f"   JWT Key: {INWORLD_JWT_KEY[:20]}...")
print(f"   JWT Secret: {INWORLD_JWT_SECRET[:20]}...")

# Generate Base64 API key
credentials = f"{INWORLD_JWT_KEY}:{INWORLD_JWT_SECRET}"
api_key_base64 = base64.b64encode(credentials.encode()).decode()
print(f"   Base64 API Key: {api_key_base64[:40]}...")

# Test 2: Try a simple API call with Ashley voice
print("\n📋 STEP 2: Testing API Call with 'Ashley' voice...")

test_voices = ['Ashley', 'Emma', 'Sarah', 'Rachel', 'Brandon', 'Christopher', 'Daniel', 'Ethan']

for voice in test_voices:
    print(f"\n   Testing voice: {voice}...")
    
    url = 'https://api.inworld.ai/tts/v1/voice'
    headers = {
        'Authorization': f'Basic {api_key_base64}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'text': 'Hello, this is a test.',
        'voiceId': voice,
        'modelId': 'inworld-tts-1'
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"      Status Code: {response.status_code}")
        
        if response.ok:
            result = response.json()
            if 'audioContent' in result:
                print(f"      ✅ SUCCESS! Audio received: {len(result['audioContent'])} bytes")
                # Save test audio
                audio_data = base64.b64decode(result['audioContent'])
                test_file = f'test_{voice.lower()}.mp3'
                with open(test_file, 'wb') as f:
                    f.write(audio_data)
                print(f"      ✅ Saved to: {test_file}")
            else:
                print(f"      ❌ No audioContent in response: {list(result.keys())}")
        else:
            print(f"      ❌ ERROR: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print(f"      ❌ TIMEOUT after 30 seconds")
    except Exception as e:
        print(f"      ❌ EXCEPTION: {e}")

# Test 3: Check if endpoint is correct
print("\n📋 STEP 3: Checking API Endpoint...")
print(f"   Using endpoint: https://api.inworld.ai/tts/v1/voice")
print(f"   Method: POST")
print(f"   Headers: Authorization (Basic), Content-Type (JSON)")

print("\n" + "="*60)
print("🎯 DIAGNOSTIC COMPLETE")
print("="*60)
print("\n💡 NEXT STEPS:")
print("   1. Check results above")
print("   2. If ALL voices fail → Credentials invalid")
print("   3. If SOME voices work → Use those voice names!")
print("   4. If authentication fails → Check JWT key/secret")
print("="*60)
