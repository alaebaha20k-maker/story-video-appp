"""
🧠 INTELLIGENT MEDIA MANAGER
Handles ALL 7 media modes with smart mixing of AI, manual, and stock media
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import List, Dict, Optional, Tuple
import random
from src.media.stock_downloader import stock_downloader
from src.utils.colab_client import get_colab_client


class MediaItem:
    """Represents a single media item (image or video)"""

    def __init__(self, filepath: Path, media_type: str, source: str, duration: Optional[float] = None):
        self.filepath = filepath
        self.media_type = media_type  # 'image' or 'video'
        self.source = source  # 'ai', 'manual', 'stock'
        self.duration = duration  # For videos, None for images

    def to_dict(self) -> Dict:
        return {
            'filepath': str(self.filepath),
            'type': self.media_type,
            'source': self.source,
            'duration': self.duration
        }


class IntelligentMediaManager:
    """
    Manages media generation/collection for ALL 7 modes:
    1. ai_only - 100% AI-generated (SDXL-Turbo)
    2. manual_only - 100% user uploads
    3. stock_only - 100% Pexels stock
    4. ai_manual - 50/50 mix of AI + manual
    5. ai_stock - Mix of AI + stock
    6. manual_stock - Mix of manual + stock
    7. all_mix - AI + manual + stock combined
    """

    def __init__(self):
        self.colab_client = get_colab_client()

    def generate_media(
        self,
        mode: str,
        scenes: List[Dict],
        image_style: str = 'cinematic',
        manual_files: Optional[List[Dict]] = None,
        stock_keywords: Optional[List[str]] = None,
        num_scenes: int = 10
    ) -> List[MediaItem]:
        """
        Main entry point - generates/collects media based on mode

        Args:
            mode: One of 7 modes (ai_only, manual_only, stock_only, etc.)
            scenes: Script scenes (for AI generation)
            image_style: Style for AI images
            manual_files: User-uploaded files (images + videos)
            stock_keywords: Keywords for stock media search
            num_scenes: Total scenes needed

        Returns:
            List of MediaItem objects with filepaths and metadata
        """

        print(f"\n🎨 INTELLIGENT MEDIA MANAGER")
        print(f"   Mode: {mode}")
        print(f"   Scenes: {num_scenes}")
        print(f"   Manual files: {len(manual_files) if manual_files else 0}")
        print(f"   Stock keywords: {len(stock_keywords) if stock_keywords else 0}")

        if mode == 'ai_only':
            return self._generate_ai_only(scenes, image_style)

        elif mode == 'manual_only':
            return self._use_manual_only(manual_files, num_scenes)

        elif mode == 'stock_only':
            return self._download_stock_only(stock_keywords, scenes, num_scenes)

        elif mode == 'ai_manual':
            return self._mix_ai_manual(scenes, image_style, manual_files, num_scenes)

        elif mode == 'ai_stock':
            return self._mix_ai_stock(scenes, image_style, stock_keywords, num_scenes)

        elif mode == 'manual_stock':
            return self._mix_manual_stock(manual_files, stock_keywords, num_scenes)

        elif mode == 'all_mix':
            return self._mix_all_three(scenes, image_style, manual_files, stock_keywords, num_scenes)

        else:
            print(f"⚠️ Unknown mode '{mode}', defaulting to ai_only")
            return self._generate_ai_only(scenes, image_style)

    # ═══════════════════════════════════════════════════════════
    # MODE 1: AI ONLY
    # ═══════════════════════════════════════════════════════════

    def _generate_ai_only(self, scenes: List[Dict], style: str) -> List[MediaItem]:
        """Generate all images with SDXL-Turbo on Colab GPU"""

        print(f"\n🤖 MODE: AI Only (SDXL-Turbo)")

        # Call Colab for batch generation
        results = self.colab_client.generate_images_batch(scenes, style=style)

        media_items = []
        for result in results:
            if result.get('success'):
                media_items.append(MediaItem(
                    filepath=Path(result['filepath']),
                    media_type='image',
                    source='ai',
                    duration=None
                ))

        print(f"✅ Generated {len(media_items)} AI images")
        return media_items

    # ═══════════════════════════════════════════════════════════
    # MODE 2: MANUAL ONLY
    # ═══════════════════════════════════════════════════════════

    def _use_manual_only(self, manual_files: List[Dict], num_scenes: int) -> List[MediaItem]:
        """Use ONLY user-uploaded files"""

        print(f"\n👤 MODE: Manual Only")

        if not manual_files:
            raise ValueError("❌ Manual mode requires uploaded files!")

        media_items = []
        for file_data in manual_files[:num_scenes]:
            media_items.append(MediaItem(
                filepath=Path(file_data['filepath']),
                media_type=file_data.get('type', 'image'),
                source='manual',
                duration=file_data.get('duration')  # Videos have duration
            ))

        # If not enough manual files, loop them
        while len(media_items) < num_scenes:
            for file_data in manual_files:
                if len(media_items) >= num_scenes:
                    break
                media_items.append(MediaItem(
                    filepath=Path(file_data['filepath']),
                    media_type=file_data.get('type', 'image'),
                    source='manual',
                    duration=file_data.get('duration')
                ))

        print(f"✅ Using {len(media_items)} manual files")
        return media_items[:num_scenes]

    # ═══════════════════════════════════════════════════════════
    # MODE 3: STOCK ONLY
    # ═══════════════════════════════════════════════════════════

    def _download_stock_only(self, keywords: List[str], scenes: List[Dict], num_scenes: int) -> List[MediaItem]:
        """Download ONLY stock media from Pexels"""

        print(f"\n📹 MODE: Stock Only (Pexels)")

        if not keywords:
            # Extract keywords from scene descriptions
            keywords = [scene.get('description', '')[:30] for scene in scenes[:5]]
            print(f"   Auto-generated {len(keywords)} keywords from scenes")

        media_items = []

        # Mix of videos and photos (60% videos, 40% photos for more dynamic content)
        num_videos = int(num_scenes * 0.6)
        num_photos = num_scenes - num_videos

        # Download videos
        print(f"   Downloading {num_videos} stock videos...")
        videos = stock_downloader.search_and_download_videos(keywords, max_per_keyword=3)

        for video in videos[:num_videos]:
            media_items.append(MediaItem(
                filepath=video['filepath'],
                media_type='video',
                source='stock',
                duration=video.get('duration', 5.0)
            ))

        # Download photos
        print(f"   Downloading {num_photos} stock photos...")
        photos = stock_downloader.search_and_download_photos(keywords, max_per_keyword=2)

        for photo in photos[:num_photos]:
            media_items.append(MediaItem(
                filepath=photo,
                media_type='image',
                source='stock',
                duration=None
            ))

        # Shuffle for variety
        random.shuffle(media_items)

        print(f"✅ Downloaded {len(media_items)} stock media items")
        return media_items[:num_scenes]

    # ═══════════════════════════════════════════════════════════
    # MODE 4: AI + MANUAL MIX
    # ═══════════════════════════════════════════════════════════

    def _mix_ai_manual(self, scenes: List[Dict], style: str, manual_files: List[Dict], num_scenes: int) -> List[MediaItem]:
        """50/50 mix of AI-generated and manual uploads"""

        print(f"\n🔄 MODE: AI + Manual Mix (50/50)")

        num_ai = num_scenes // 2
        num_manual = num_scenes - num_ai

        # Generate AI images
        print(f"   Generating {num_ai} AI images...")
        ai_items = self._generate_ai_only(scenes[:num_ai], style)

        # Use manual files
        print(f"   Using {num_manual} manual files...")
        manual_items = self._use_manual_only(manual_files, num_manual)

        # Interleave for better variety
        media_items = []
        for i in range(max(len(ai_items), len(manual_items))):
            if i < len(ai_items):
                media_items.append(ai_items[i])
            if i < len(manual_items):
                media_items.append(manual_items[i])

        print(f"✅ Mixed {len(media_items)} media items")
        return media_items[:num_scenes]

    # ═══════════════════════════════════════════════════════════
    # MODE 5: AI + STOCK MIX
    # ═══════════════════════════════════════════════════════════

    def _mix_ai_stock(self, scenes: List[Dict], style: str, keywords: List[str], num_scenes: int) -> List[MediaItem]:
        """Mix of AI-generated images and stock media"""

        print(f"\n🔄 MODE: AI + Stock Mix")

        num_ai = int(num_scenes * 0.6)  # 60% AI
        num_stock = num_scenes - num_ai  # 40% stock

        # Generate AI
        print(f"   Generating {num_ai} AI images...")
        ai_items = self._generate_ai_only(scenes[:num_ai], style)

        # Download stock
        print(f"   Downloading {num_stock} stock items...")
        stock_items = self._download_stock_only(keywords, scenes, num_stock)

        # Interleave
        media_items = []
        for i in range(max(len(ai_items), len(stock_items))):
            if i < len(ai_items):
                media_items.append(ai_items[i])
            if i < len(stock_items):
                media_items.append(stock_items[i])

        print(f"✅ Mixed {len(media_items)} media items")
        return media_items[:num_scenes]

    # ═══════════════════════════════════════════════════════════
    # MODE 6: MANUAL + STOCK MIX
    # ═══════════════════════════════════════════════════════════

    def _mix_manual_stock(self, manual_files: List[Dict], keywords: List[str], num_scenes: int) -> List[MediaItem]:
        """Mix of manual uploads and stock media"""

        print(f"\n🔄 MODE: Manual + Stock Mix")

        num_manual = num_scenes // 2
        num_stock = num_scenes - num_manual

        # Use manual
        print(f"   Using {num_manual} manual files...")
        manual_items = self._use_manual_only(manual_files, num_manual)

        # Download stock
        print(f"   Downloading {num_stock} stock items...")
        stock_items = self._download_stock_only(keywords, [], num_stock)

        # Interleave
        media_items = []
        for i in range(max(len(manual_items), len(stock_items))):
            if i < len(manual_items):
                media_items.append(manual_items[i])
            if i < len(stock_items):
                media_items.append(stock_items[i])

        print(f"✅ Mixed {len(media_items)} media items")
        return media_items[:num_scenes]

    # ═══════════════════════════════════════════════════════════
    # MODE 7: ALL THREE MIX
    # ═══════════════════════════════════════════════════════════

    def _mix_all_three(self, scenes: List[Dict], style: str, manual_files: List[Dict], keywords: List[str], num_scenes: int) -> List[MediaItem]:
        """Ultimate mix: AI + Manual + Stock"""

        print(f"\n🔄 MODE: All Three Mix (AI + Manual + Stock)")

        num_ai = int(num_scenes * 0.4)      # 40% AI
        num_manual = int(num_scenes * 0.3)  # 30% manual
        num_stock = num_scenes - num_ai - num_manual  # 30% stock

        # Generate/collect each type
        print(f"   Generating {num_ai} AI images...")
        ai_items = self._generate_ai_only(scenes[:num_ai], style)

        print(f"   Using {num_manual} manual files...")
        manual_items = self._use_manual_only(manual_files, num_manual) if manual_files else []

        print(f"   Downloading {num_stock} stock items...")
        stock_items = self._download_stock_only(keywords, scenes, num_stock) if keywords else []

        # Combine and shuffle for maximum variety
        media_items = ai_items + manual_items + stock_items
        random.shuffle(media_items)

        print(f"✅ Mixed {len(media_items)} media items (AI: {len(ai_items)}, Manual: {len(manual_items)}, Stock: {len(stock_items)})")
        return media_items[:num_scenes]


# Singleton instance
media_manager = IntelligentMediaManager()


def generate_media(mode: str, **kwargs) -> List[MediaItem]:
    """Convenience function to use the media manager"""
    return media_manager.generate_media(mode, **kwargs)


if __name__ == "__main__":
    print("\n🧪 Testing Intelligent Media Manager...\n")

    # Test AI only
    scenes = [{'description': 'A dark forest'}, {'description': 'A haunted house'}]

    print("Test 1: AI Only")
    media = generate_media('ai_only', scenes=scenes, image_style='cinematic', num_scenes=2)
    print(f"Result: {len(media)} items\n")

    print("✅ Intelligent Media Manager ready!")
