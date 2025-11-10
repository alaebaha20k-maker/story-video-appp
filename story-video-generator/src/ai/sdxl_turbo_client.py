"""
🎨 SDXL-Turbo API Client - Connect to Remote GPU Server
"""

import requests
import base64
from pathlib import Path
from typing import Optional
import os
from PIL import Image
import io

class SDXLTurboClient:
    """Client for remote SDXL-Turbo API (running on Google Colab)"""

    def __init__(self, api_url: Optional[str] = None):
        """Initialize SDXL-Turbo API client

        Args:
            api_url: Base URL of the remote API (e.g., https://xyz.ngrok-free.dev)
                    If not provided, will use SDXL_API_URL from environment
        """
        self.api_url = api_url or os.getenv('SDXL_API_URL', '')

        if not self.api_url:
            raise ValueError(
                "SDXL API URL not provided. Please set SDXL_API_URL environment variable "
                "or pass api_url parameter."
            )

        # Remove trailing slash
        self.api_url = self.api_url.rstrip('/')

        # If URL doesn't have /generate_image, add it
        if not self.api_url.endswith('/generate_image'):
            self.api_url = f"{self.api_url}/generate_image"

        print(f"🎨 SDXL-Turbo API Client initialized")
        print(f"   URL: {self.api_url}")

    def generate_image(
        self,
        prompt: str,
        output_path: Optional[str] = None
    ) -> str:
        """Generate image using remote SDXL-Turbo API

        Args:
            prompt: Text prompt for image generation
            output_path: Where to save image file

        Returns:
            Path to saved image file
        """
        if not prompt or len(prompt.strip()) == 0:
            raise ValueError("Prompt cannot be empty")

        print(f"🎨 Generating image with SDXL-Turbo...")
        print(f"   Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")

        try:
            # Make API request
            response = requests.post(
                self.api_url,
                json={'prompt': prompt},
                timeout=180  # 3 minute timeout
            )

            response.raise_for_status()

            # Parse response
            data = response.json()

            if not data.get('success'):
                raise Exception(f"API returned error: {data.get('error', 'Unknown error')}")

            # Decode base64 image
            image_base64 = data.get('image')
            if not image_base64:
                raise Exception("No image data in response")

            image_bytes = base64.b64decode(image_base64)

            # Default output path
            if output_path is None:
                output_dir = Path("output/temp")
                output_dir.mkdir(parents=True, exist_ok=True)
                # Use timestamp for unique filename
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                output_path = output_dir / f"image_{timestamp}.png"

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save image file
            image = Image.open(io.BytesIO(image_bytes))
            image.save(output_path, format='PNG')

            print(f"✅ Image generated successfully!")
            print(f"   Size: {image.size[0]}x{image.size[1]}")
            print(f"   Saved to: {output_path}")

            return str(output_path)

        except requests.exceptions.HTTPError as e:
            print(f"❌ ❌ SDXL-Turbo API error: {e.response.status_code} ❌")
            try:
                error_data = e.response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Error response: {e.response.text}")
            raise Exception(f"SDXL-Turbo API error: {e.response.status_code}")

        except requests.exceptions.Timeout:
            print(f"❌ SDXL-Turbo API timeout")
            raise Exception("SDXL-Turbo API timeout - image generation took too long")

        except requests.exceptions.ConnectionError as e:
            print(f"❌ SDXL-Turbo API connection error: {e}")
            print(f"\n💡 Troubleshooting:")
            print(f"   1. Check if Google Colab notebook is running")
            print(f"   2. Verify ngrok URL is correct: {self.api_url}")
            print(f"   3. Check internet connection")
            print(f"   4. Try restarting the Colab notebook")
            raise Exception(f"Cannot connect to SDXL-Turbo API")

        except Exception as e:
            print(f"❌ SDXL-Turbo API error: {e}")
            raise


def generate_sdxl_image(
    prompt: str,
    output_path: Optional[str] = None,
    api_url: Optional[str] = None
) -> str:
    """Convenience function to generate image

    Args:
        prompt: Text prompt for image generation
        output_path: Where to save image
        api_url: API URL (optional, uses env var if not provided)

    Returns:
        Path to saved image file
    """
    client = SDXLTurboClient(api_url)
    return client.generate_image(prompt, output_path)


# Test code
if __name__ == '__main__':
    print("\n🎨 Testing SDXL-Turbo API Client\n")

    # Test with sample prompt
    test_prompt = "A beautiful sunset over mountains, cinematic lighting, 8k, highly detailed"

    try:
        api_url = input("Enter your ngrok URL (e.g., https://xyz.ngrok-free.dev): ").strip()

        if not api_url:
            print("❌ No URL provided")
        else:
            image_path = generate_sdxl_image(
                prompt=test_prompt,
                output_path='test_sdxl_api.png',
                api_url=api_url
            )

            print(f"\n✅ Test successful! Image saved to: {image_path}")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
