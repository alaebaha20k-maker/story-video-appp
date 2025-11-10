"""
🚀 IMAGE CACHE - Smart caching for faster video generation
Avoids regenerating similar images for long videos (1+ hour)
"""

import hashlib
import json
from pathlib import Path
from typing import Optional, Dict
import shutil


class ImageCache:
    """Cache generated images to speed up regeneration"""

    def __init__(self, cache_dir: str = "cache/images"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.cache_dir / "index.json"
        self.index = self._load_index()

    def _load_index(self) -> Dict:
        """Load cache index from disk"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_index(self):
        """Save cache index to disk"""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)

    def _get_cache_key(self, prompt: str, style: str) -> str:
        """Generate unique cache key from prompt and style"""
        combined = f"{prompt}|{style}"
        return hashlib.md5(combined.encode()).hexdigest()

    def get(self, prompt: str, style: str) -> Optional[Path]:
        """Get cached image if available"""
        cache_key = self._get_cache_key(prompt, style)

        if cache_key in self.index:
            cached_path = Path(self.index[cache_key])
            if cached_path.exists():
                print(f"   ♻️  Using cached image (instant!)")
                return cached_path

        return None

    def put(self, prompt: str, style: str, image_path: Path) -> Path:
        """Cache an image for future use"""
        cache_key = self._get_cache_key(prompt, style)

        # Copy to cache directory
        cache_filename = f"{cache_key}.png"
        cached_path = self.cache_dir / cache_filename

        shutil.copy2(image_path, cached_path)

        # Update index
        self.index[cache_key] = str(cached_path)
        self._save_index()

        return cached_path

    def clear(self):
        """Clear all cached images"""
        for file in self.cache_dir.glob("*.png"):
            file.unlink()
        self.index = {}
        self._save_index()
        print("✅ Image cache cleared")

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_images = len(list(self.cache_dir.glob("*.png")))
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.png"))

        return {
            "total_images": total_images,
            "total_size_mb": total_size / (1024 * 1024),
            "cache_dir": str(self.cache_dir)
        }


# Global instance
image_cache = ImageCache()
