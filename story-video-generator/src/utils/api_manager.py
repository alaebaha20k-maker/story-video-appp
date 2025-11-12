"""
🔌 API MANAGER - Manages API keys and handles fallbacks with automatic rotation
"""

import os
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()


class APIManager:
    """Manages API keys and provides fallback strategies with automatic rotation"""

    # ✅ MULTIPLE GEMINI API KEYS - Automatic Rotation!
    GEMINI_API_KEYS = [
        "AIzaSyC3lCI117uyVbJkFOXI6BffwlUCLSdYIH0",  # Key 1
        "AIzaSyCLAEQSW3P1E499fxvw7i9k1ZELGdZIdrw",  # Key 2
        "AIzaSyArtYUT_GHyEsHDT1oxNbBocHlGEGWTXfo"   # Key 3
    ]

    def __init__(self):
        self.keys = {
            'gemini': self.GEMINI_API_KEYS[0],  # Default to first key
            'together': os.getenv('TOGETHER_API_KEY'),
            'fal': os.getenv('FAL_API_KEY'),
            'pexels': os.getenv('PEXELS_API_KEY')
        }

        # ✅ Track current Gemini key index for rotation
        self.current_gemini_key_index = 0

        self.image_api_priority = ['together', 'fal', 'pollinations']
        self.current_image_api = 0

        self.usage_counts = {
            'gemini': 0,
            'together': 0,
            'fal': 0,
            'pexels': 0
        }

    def get_key(self, service: str) -> Optional[str]:
        """Get API key for a service"""
        key = self.keys.get(service)
        if not key or key.startswith('your_'):
            return None
        return key

    def get_all_gemini_keys(self) -> List[str]:
        """Get all available Gemini API keys"""
        return self.GEMINI_API_KEYS.copy()

    def get_next_gemini_key(self) -> str:
        """Get next Gemini API key in rotation"""
        key = self.GEMINI_API_KEYS[self.current_gemini_key_index]
        self.current_gemini_key_index = (self.current_gemini_key_index + 1) % len(self.GEMINI_API_KEYS)
        return key

    def get_current_gemini_key(self) -> str:
        """Get current Gemini API key without rotating"""
        return self.GEMINI_API_KEYS[self.current_gemini_key_index]

    def has_key(self, service: str) -> bool:
        """Check if API key exists"""
        return self.get_key(service) is not None

    def get_image_api(self) -> str:
        """Get current image generation API"""
        return self.image_api_priority[self.current_image_api]

    def fallback_image_api(self) -> Optional[str]:
        """Switch to next image API"""
        self.current_image_api += 1
        if self.current_image_api >= len(self.image_api_priority):
            return None
        return self.image_api_priority[self.current_image_api]

    def reset_image_api(self):
        """Reset to primary image API"""
        self.current_image_api = 0

    def increment_usage(self, service: str):
        """Track API usage"""
        if service in self.usage_counts:
            self.usage_counts[service] += 1

    def get_usage(self, service: str) -> int:
        """Get usage count for service"""
        return self.usage_counts.get(service, 0)

    def check_required_keys(self) -> Dict[str, bool]:
        """Check which required keys are present"""
        return {
            'gemini': len(self.GEMINI_API_KEYS) > 0,
            'image_api': self.has_key('together') or self.has_key('fal'),
            'pexels': self.has_key('pexels')
        }

    def get_missing_keys(self) -> List[str]:
        """Get list of missing required keys"""
        missing = []
        if len(self.GEMINI_API_KEYS) == 0:
            missing.append('GEMINI_API_KEY')
        if not self.has_key('together') and not self.has_key('fal'):
            missing.append('TOGETHER_API_KEY or FAL_API_KEY')
        return missing


api_manager = APIManager()


def get_api_key(service: str) -> Optional[str]:
    return api_manager.get_key(service)


def has_api_key(service: str) -> bool:
    return api_manager.has_key(service)


if __name__ == "__main__":
    print("\n🧪 Testing APIManager...\n")

    manager = APIManager()

    print("API Keys Status:")
    status = manager.check_required_keys()
    for key, present in status.items():
        icon = "✅" if present else "❌"
        print(f"  {icon} {key}: {present}")

    print(f"\n✅ Gemini Keys Available: {len(manager.GEMINI_API_KEYS)}")
    print("   Testing rotation:")
    for i in range(5):
        key = manager.get_next_gemini_key()
        print(f"   Key {i+1}: ...{key[-8:]}")

    missing = manager.get_missing_keys()
    if missing:
        print(f"\n⚠️  Missing keys: {', '.join(missing)}")
    else:
        print("\n✅ All required keys present!")

    print(f"\n📊 Current image API: {manager.get_image_api()}")

    print("\n✅ APIManager working!\n")