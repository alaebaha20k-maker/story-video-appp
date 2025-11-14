"""
🌐 COLAB CLIENT - Interface to Google Colab GPU Server
Handles calls to Kokoro TTS + SDXL-Turbo via ngrok
"""

import requests
import base64
from pathlib import Path
from typing import List, Dict, Optional
import time

# Import config
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import COLAB_SERVER_URL, COLAB_ENDPOINTS


class ColabClient:
    """Client for Google Colab GPU Server (Kokoro TTS + SDXL-Turbo)"""

    def __init__(self, server_url: str = None):
        """
        Initialize Colab client

        Args:
            server_url: Ngrok URL (e.g., https://xxxx.ngrok-free.app)
                       If None, uses COLAB_SERVER_URL from config
        """
        self.server_url = server_url or COLAB_SERVER_URL

        if 'your-ngrok-url-here' in self.server_url:
            raise ValueError(
                "❌ Please update COLAB_SERVER_URL in config/__init__.py with your ngrok URL!\n"
                "   Run the Colab notebook to get the URL, then update config/__init__.py line 13"
            )

        print(f"🌐 Colab Client initialized")
        print(f"   Server: {self.server_url}")

    def check_health(self) -> bool:
        """
        Check if Colab server is running

        Returns:
            bool: True if server is healthy
        """
        try:
            url = f"{self.server_url}{COLAB_ENDPOINTS['health']}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Colab server healthy!")
                print(f"   Device: {data.get('device', 'unknown')}")
                print(f"   GPU: {data.get('gpu', 'None')}")
                return True
            else:
                print(f"⚠️ Colab server returned status {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to Colab server: {e}")
            print(f"   Make sure:")
            print(f"   1. Colab notebook is running")
            print(f"   2. ngrok URL is correct in config/__init__.py")
            print(f"   3. Internet connection is working")
            return False

    def generate_audio(
        self,
        text: str,
        voice: str = 'guy',
        speed: float = 1.0,
        output_path: Optional[Path] = None
    ) -> str:
        """
        Generate audio using Kokoro TTS on Colab GPU

        Args:
            text: Text to convert to speech
            voice: Voice ID (guy, aria, sarah, etc.)
            speed: Speech speed (0.5-2.0)
            output_path: Where to save audio file (optional)

        Returns:
            str: Path to saved audio file
        """
        print(f"\n🎤 Generating audio with Kokoro TTS (Colab GPU)...")
        print(f"   Voice: {voice}")
        print(f"   Speed: {speed}x")
        print(f"   Text: {len(text)} characters")

        try:
            url = f"{self.server_url}{COLAB_ENDPOINTS['generate_audio']}"

            payload = {
                'text': text,
                'voice': voice,
                'speed': speed
            }

            # Call Colab endpoint
            response = requests.post(
                url,
                json=payload,
                timeout=300  # 5 minutes (TTS can be slow for long texts)
            )

            if response.status_code != 200:
                raise RuntimeError(f"Colab returned error {response.status_code}: {response.text}")

            # Save audio file
            if output_path is None:
                output_dir = Path("output/temp")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / "kokoro_narration.wav"

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write audio data
            with open(output_path, 'wb') as f:
                f.write(response.content)

            file_size = output_path.stat().st_size
            print(f"✅ Audio generated!")
            print(f"   File: {output_path}")
            print(f"   Size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")

            return str(output_path)

        except Exception as e:
            print(f"❌ Audio generation failed: {e}")
            raise

    def generate_image(
        self,
        prompt: str,
        style: str = 'cinematic',
        output_path: Optional[Path] = None
    ) -> str:
        """
        Generate single image using SDXL-Turbo on Colab GPU

        Args:
            prompt: Image description
            style: Style preset (cinematic, realistic, etc.)
            output_path: Where to save image (optional)

        Returns:
            str: Path to saved image file
        """
        print(f"\n🎨 Generating image with SDXL-Turbo (Colab GPU)...")
        print(f"   Prompt: {prompt[:60]}...")
        print(f"   Style: {style}")

        try:
            url = f"{self.server_url}{COLAB_ENDPOINTS['generate_image']}"

            payload = {
                'prompt': prompt,
                'style': style
            }

            # Call Colab endpoint
            response = requests.post(
                url,
                json=payload,
                timeout=120  # 2 minutes
            )

            if response.status_code != 200:
                raise RuntimeError(f"Colab returned error {response.status_code}: {response.text}")

            # Save image file
            if output_path is None:
                output_dir = Path("output/temp")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / "sdxl_image.png"

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write image data
            with open(output_path, 'wb') as f:
                f.write(response.content)

            file_size = output_path.stat().st_size
            print(f"✅ Image generated (1920x1080)!")
            print(f"   File: {output_path}")
            print(f"   Size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")

            return str(output_path)

        except Exception as e:
            print(f"❌ Image generation failed: {e}")
            raise

    def generate_images_batch(
        self,
        scenes: List[Dict],
        style: str = 'cinematic'
    ) -> List[Dict]:
        """
        Generate multiple images in batch using SDXL-Turbo on Colab GPU

        Args:
            scenes: List of scene dictionaries with 'description' or 'image_description'
            style: Style preset

        Returns:
            List of dicts with image paths and metadata
        """
        print(f"\n🎨 Generating {len(scenes)} images with SDXL-Turbo (Colab GPU)...")
        print(f"   Style: {style}")
        print(f"   Resolution: 1920x1080 (16:9)")

        try:
            url = f"{self.server_url}{COLAB_ENDPOINTS['generate_images_batch']}"

            # Prepare scenes payload
            scenes_payload = []
            for scene in scenes:
                # Get description from either 'image_description' or 'description'
                description = scene.get('image_description') or scene.get('description', '')
                scenes_payload.append({'description': description})

            payload = {
                'scenes': scenes_payload,
                'style': style
            }

            # Call Colab endpoint
            print(f"   📡 Calling Colab server...")
            start_time = time.time()

            response = requests.post(
                url,
                json=payload,
                timeout=600  # 10 minutes for batch
            )

            elapsed = time.time() - start_time

            if response.status_code != 200:
                raise RuntimeError(f"Colab returned error {response.status_code}: {response.text}")

            data = response.json()
            results_data = data.get('results', [])

            # Process results and save images
            output_dir = Path("output/temp")
            output_dir.mkdir(parents=True, exist_ok=True)

            results = []

            for i, result in enumerate(results_data, 1):
                if not result.get('success'):
                    print(f"   ❌ Image {i}/{len(results_data)} failed: {result.get('error')}")
                    results.append({
                        'success': False,
                        'filepath': None,
                        'error': result.get('error')
                    })
                    continue

                # Decode base64 image
                image_base64 = result.get('image_data')
                image_bytes = base64.b64decode(image_base64)

                # Save to file
                image_path = output_dir / f"scene_{i:03d}.png"
                with open(image_path, 'wb') as f:
                    f.write(image_bytes)

                file_size = len(image_bytes)
                print(f"   ✅ Image {i}/{len(results_data)}: {image_path.name} ({file_size:,} bytes)")

                results.append({
                    'success': True,
                    'filepath': str(image_path),
                    'size_bytes': file_size,
                    'resolution': '1920x1080',
                    'scene_index': i - 1
                })

            success_count = len([r for r in results if r.get('success')])
            total_size = sum(r.get('size_bytes', 0) for r in results)

            print(f"\n✅ Batch complete!")
            print(f"   Success: {success_count}/{len(scenes)} images")
            print(f"   Total size: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
            print(f"   Time: {elapsed:.1f} seconds")
            print(f"   Speed: {elapsed/len(scenes):.1f} sec/image")

            return results

        except Exception as e:
            print(f"❌ Batch generation failed: {e}")
            raise


# Singleton instance
_colab_client = None

def get_colab_client(server_url: str = None) -> ColabClient:
    """
    Get or create Colab client instance

    Args:
        server_url: Optional ngrok URL override

    Returns:
        ColabClient instance
    """
    global _colab_client

    if _colab_client is None or server_url is not None:
        _colab_client = ColabClient(server_url)

    return _colab_client


# Test function
if __name__ == '__main__':
    print("\n🧪 Testing Colab Client...\n")

    try:
        client = get_colab_client()

        # Test health
        print("\n1. Testing health check...")
        if client.check_health():
            print("   ✅ Server is healthy!\n")
        else:
            print("   ❌ Server is not responding\n")
            exit(1)

        # Test audio generation
        print("\n2. Testing audio generation...")
        audio_path = client.generate_audio(
            text="Hello, this is a test of Kokoro TTS running on Google Colab GPU.",
            voice='guy',
            speed=1.0
        )
        print(f"   ✅ Audio saved to: {audio_path}\n")

        # Test single image
        print("\n3. Testing single image generation...")
        image_path = client.generate_image(
            prompt="A beautiful sunset over mountains",
            style='cinematic'
        )
        print(f"   ✅ Image saved to: {image_path}\n")

        # Test batch images
        print("\n4. Testing batch image generation...")
        scenes = [
            {'description': 'A dark forest at night'},
            {'description': 'A haunted house on a hill'}
        ]
        results = client.generate_images_batch(scenes, style='cinematic')
        print(f"   ✅ Generated {len(results)} images\n")

        print("\n✅ All tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
