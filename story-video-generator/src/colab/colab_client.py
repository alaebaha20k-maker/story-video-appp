"""
🔌 COLAB CLIENT - Send requests to Google Colab for video generation
All image/voice/video processing happens in Colab, not locally
"""

import requests
from typing import Dict, List, Optional
import time
from pathlib import Path


class ColabClient:
    """
    Client to communicate with Google Colab notebook
    Sends script + image prompts + options → Receives video
    """

    def __init__(self, colab_url: Optional[str] = None):
        """
        Initialize Colab client

        Args:
            colab_url: URL of Colab server (ngrok URL)
                      If None, will need to be set before use
        """
        self.colab_url = colab_url
        print(f"🔌 Colab Client initialized")
        if colab_url:
            print(f"   URL: {colab_url}")
        else:
            print(f"   ⚠️  URL not set - call set_url() before generating")

    def set_url(self, url: str):
        """Set Colab server URL (ngrok URL from notebook)"""
        self.colab_url = url.rstrip('/')
        print(f"✅ Colab URL set: {self.colab_url}")

    def check_health(self) -> bool:
        """Check if Colab server is running"""
        if not self.colab_url:
            return False

        try:
            response = requests.get(f"{self.colab_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def generate_complete_video(
        self,
        script: str,
        image_prompts: List[str],
        options: Dict
    ) -> Dict:
        """
        Send everything to Colab for video generation

        Args:
            script: Complete script from Gemini Server 1
            image_prompts: List of SDXL prompts from Gemini Server 2
            options: All generation options from frontend

        Returns:
            {
                'success': bool,
                'job_id': str,
                'message': str
            }
        """

        if not self.colab_url:
            raise Exception("Colab URL not set! Call set_url() first.")

        print(f"\n🚀 Sending to Colab...")
        print(f"   Script: {len(script)} chars")
        print(f"   Image prompts: {len(image_prompts)}")
        print(f"   Options: {len(options)} settings")

        # Prepare request payload
        payload = {
            # Script
            'script': script,

            # Image prompts from Server 2
            'image_prompts': image_prompts,

            # Visual options
            'style': options.get('image_style', 'cinematic'),
            'num_images': len(image_prompts),

            # Voice options
            'voice': options.get('voice_id', 'aria'),
            'voice_speed': options.get('voice_speed', 1.0),

            # Video effects
            'zoom_effect': options.get('zoom_effect', True),
            'zoom_intensity': options.get('zoom_intensity', 5.0),  # Percentage
            'auto_captions': options.get('auto_captions', False),
            'color_filter': options.get('color_filter', 'none'),

            # Metadata
            'topic': options.get('topic', 'Untitled'),
            'story_type': options.get('story_type', 'story'),
            'duration': options.get('duration', 10),
        }

        print(f"\n📋 Request details:")
        print(f"   Voice: {payload['voice']} @ {payload['voice_speed']}x")
        print(f"   Zoom: {payload['zoom_intensity']}% (enabled: {payload['zoom_effect']})")
        print(f"   Captions: {payload['auto_captions']}")
        print(f"   Filter: {payload['color_filter']}")

        try:
            # Send to Colab
            response = requests.post(
                f"{self.colab_url}/generate_complete_video",
                json=payload,
                timeout=30  # Longer timeout for initial request
            )

            if response.status_code != 200:
                raise Exception(f"Colab returned status {response.status_code}: {response.text}")

            result = response.json()

            print(f"\n✅ Colab accepted request!")
            print(f"   Job ID: {result.get('job_id', 'unknown')}")

            return result

        except requests.exceptions.Timeout:
            raise Exception("Colab request timed out. Is the server running?")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Cannot connect to Colab at {self.colab_url}. Check ngrok URL.")
        except Exception as e:
            raise Exception(f"Colab request failed: {str(e)}")

    def get_job_status(self, job_id: str) -> Dict:
        """
        Check status of video generation job in Colab

        Args:
            job_id: Job ID from generate_complete_video

        Returns:
            {
                'status': 'processing' | 'complete' | 'error',
                'progress': 0-100,
                'message': str,
                'video_url': str (if complete)
            }
        """

        if not self.colab_url:
            raise Exception("Colab URL not set!")

        try:
            response = requests.get(
                f"{self.colab_url}/status/{job_id}",
                timeout=5
            )

            if response.status_code != 200:
                return {
                    'status': 'error',
                    'message': f'Status check failed: {response.status_code}'
                }

            return response.json()

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Status check error: {str(e)}'
            }

    def download_video(self, job_id: str, output_path: Path) -> bool:
        """
        Download completed video from Colab

        Args:
            job_id: Job ID
            output_path: Local path to save video

        Returns:
            True if successful
        """

        if not self.colab_url:
            raise Exception("Colab URL not set!")

        print(f"\n⬇️  Downloading video from Colab...")
        print(f"   Job ID: {job_id}")
        print(f"   Saving to: {output_path}")

        try:
            response = requests.get(
                f"{self.colab_url}/download/{job_id}",
                stream=True,
                timeout=60
            )

            if response.status_code != 200:
                raise Exception(f"Download failed: {response.status_code}")

            # Create parent directory
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r   Progress: {progress:.1f}%", end='')

            print(f"\n✅ Video downloaded: {output_path.name}")
            return True

        except Exception as e:
            print(f"\n❌ Download failed: {e}")
            return False

    def wait_for_completion(
        self,
        job_id: str,
        timeout_minutes: int = 30,
        callback=None
    ) -> Dict:
        """
        Wait for video generation to complete

        Args:
            job_id: Job ID
            timeout_minutes: Maximum wait time
            callback: Optional function to call with progress updates

        Returns:
            Final status dict
        """

        print(f"\n⏳ Waiting for Colab to complete...")
        print(f"   Job ID: {job_id}")
        print(f"   Timeout: {timeout_minutes} minutes")

        start_time = time.time()
        timeout_seconds = timeout_minutes * 60

        while True:
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                return {
                    'status': 'error',
                    'message': f'Timeout after {timeout_minutes} minutes'
                }

            # Get status
            status = self.get_job_status(job_id)

            # Call callback if provided
            if callback:
                callback(status)

            # Check if done
            if status['status'] == 'complete':
                print(f"\n✅ Colab finished!")
                return status
            elif status['status'] == 'error':
                print(f"\n❌ Colab error: {status.get('message', 'Unknown')}")
                return status

            # Print progress
            progress = status.get('progress', 0)
            message = status.get('message', 'Processing...')
            print(f"\r   {message} ({progress}%)", end='')

            # Wait before next check
            time.sleep(2)


# Global instance (URL must be set before use)
colab_client = ColabClient()
