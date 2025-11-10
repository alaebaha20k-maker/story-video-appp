"""
🎬 MEDIA SOURCE MANAGER - Mix AI, Stock, and Manual Media
Allows flexible ordering and priority of different media sources
"""

from pathlib import Path
from typing import List, Dict, Optional
import requests
from io import BytesIO
from PIL import Image


class MediaSourceManager:
    """Manages multiple media sources with custom ordering"""

    def __init__(self):
        self.sources = {
            'ai': [],      # AI-generated images
            'stock': [],   # Stock media (Pexels)
            'manual': [],  # User-uploaded images/videos
        }
        self.priority_order = ['ai', 'stock', 'manual']  # Default order

    def set_priority_order(self, order: List[str]):
        """
        Set custom priority order for media sources

        Args:
            order: List like ['stock', 'ai', 'manual'] or ['manual', 'stock', 'ai']
        """
        valid_sources = ['ai', 'stock', 'manual']

        # Validate order
        for source in order:
            if source not in valid_sources:
                raise ValueError(f"Invalid source: {source}. Must be one of {valid_sources}")

        self.priority_order = order
        print(f"📋 Media priority set: {' → '.join(order)}")

    def add_ai_images(self, image_paths: List[Path]):
        """Add AI-generated images"""
        self.sources['ai'] = [
            {
                'type': 'ai',
                'path': str(path),
                'source': 'sdxl-turbo'
            }
            for path in image_paths
        ]
        print(f"🤖 Added {len(image_paths)} AI images")

    def add_stock_media(self, media_items: List[Dict]):
        """
        Add stock media from Pexels

        Args:
            media_items: List of dicts with 'url', 'type' (image/video)
        """
        self.sources['stock'] = [
            {
                'type': 'stock',
                'url': item['url'],
                'media_type': item.get('type', 'image'),
                'source': 'pexels'
            }
            for item in media_items
        ]
        print(f"📸 Added {len(media_items)} stock items")

    def add_manual_uploads(self, file_paths: List[Path]):
        """Add manually uploaded files"""
        self.sources['manual'] = [
            {
                'type': 'manual',
                'path': str(path),
                'source': 'user_upload'
            }
            for path in file_paths
        ]
        print(f"📁 Added {len(file_paths)} manual uploads")

    def download_stock_media(self, output_dir: Path) -> List[Path]:
        """Download stock media to local files"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        downloaded = []

        for i, item in enumerate(self.sources['stock']):
            try:
                url = item['url']

                # Download
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                # Determine file extension
                media_type = item.get('media_type', 'image')
                ext = 'mp4' if media_type == 'video' else 'jpg'

                # Save
                filename = f"stock_{i:03d}.{ext}"
                filepath = output_dir / filename

                with open(filepath, 'wb') as f:
                    f.write(response.content)

                downloaded.append(filepath)
                print(f"   ✅ Downloaded: {filename}")

            except Exception as e:
                print(f"   ⚠️  Failed to download stock item {i}: {e}")
                continue

        return downloaded

    def merge_sources(
        self,
        num_scenes: int,
        download_stock: bool = True,
        stock_output_dir: Optional[Path] = None
    ) -> List[Dict]:
        """
        Merge all sources according to priority order

        Args:
            num_scenes: Total number of scenes needed
            download_stock: Whether to download stock media
            stock_output_dir: Where to save downloaded stock media

        Returns:
            List of media items in priority order
        """
        print(f"\n🎬 Merging media sources...")
        print(f"   Priority: {' → '.join(self.priority_order)}")
        print(f"   Scenes needed: {num_scenes}")

        # Download stock media if needed
        if download_stock and self.sources['stock']:
            if stock_output_dir is None:
                stock_output_dir = Path("output/temp/stock")

            stock_paths = self.download_stock_media(stock_output_dir)

            # Update stock sources with local paths
            for i, path in enumerate(stock_paths):
                if i < len(self.sources['stock']):
                    self.sources['stock'][i]['path'] = str(path)

        # Collect all sources in priority order
        merged = []

        for source_type in self.priority_order:
            items = self.sources.get(source_type, [])
            merged.extend(items)

        # Limit to num_scenes
        merged = merged[:num_scenes]

        # If we don't have enough, repeat what we have
        if len(merged) < num_scenes:
            while len(merged) < num_scenes:
                # Repeat the entire merged list
                merged.extend(merged[:num_scenes - len(merged)])

        print(f"   ✅ Merged: {len(merged)} media items")

        # Show breakdown
        breakdown = {}
        for item in merged:
            item_type = item['type']
            breakdown[item_type] = breakdown.get(item_type, 0) + 1

        for source_type, count in breakdown.items():
            print(f"      {source_type.upper()}: {count}")

        return merged

    def get_image_paths(self, merged_sources: List[Dict]) -> List[Path]:
        """Extract image paths from merged sources"""
        paths = []

        for item in merged_sources:
            if 'path' in item:
                paths.append(Path(item['path']))
            else:
                print(f"   ⚠️  No path for {item['type']} item")

        return paths

    def interleave_sources(
        self,
        pattern: str = "ai,stock,manual",
        repeat: int = 1
    ) -> List[str]:
        """
        Create interleaved pattern of sources

        Args:
            pattern: Comma-separated pattern like "ai,stock,ai,manual"
            repeat: How many times to repeat the pattern

        Returns:
            List of source types in interleaved order

        Example:
            pattern="ai,stock,ai" repeat=2
            Result: ['ai', 'stock', 'ai', 'ai', 'stock', 'ai']
        """
        sources = [s.strip() for s in pattern.split(',')]
        interleaved = sources * repeat

        print(f"🔀 Interleaved pattern: {pattern} (x{repeat})")

        return interleaved

    def apply_interleaved_pattern(
        self,
        pattern: str,
        num_scenes: int,
        download_stock: bool = True
    ) -> List[Dict]:
        """
        Apply interleaved pattern to create mixed media sequence

        Args:
            pattern: Pattern like "ai,stock,manual" or "stock,ai,ai"
            num_scenes: Total scenes needed
            download_stock: Whether to download stock

        Returns:
            List of media items following the pattern
        """
        # Create pattern sequence
        pattern_list = [s.strip() for s in pattern.split(',')]

        # Repeat pattern to cover all scenes
        full_pattern = []
        while len(full_pattern) < num_scenes:
            full_pattern.extend(pattern_list)
        full_pattern = full_pattern[:num_scenes]

        print(f"\n🎨 Applying pattern: {pattern}")
        print(f"   Full sequence: {full_pattern[:10]}..." if len(full_pattern) > 10 else f"   Full sequence: {full_pattern}")

        # Download stock if needed
        if download_stock and self.sources['stock']:
            stock_dir = Path("output/temp/stock")
            stock_paths = self.download_stock_media(stock_dir)

            for i, path in enumerate(stock_paths):
                if i < len(self.sources['stock']):
                    self.sources['stock'][i]['path'] = str(path)

        # Build sequence following pattern
        result = []
        source_indices = {'ai': 0, 'stock': 0, 'manual': 0}

        for source_type in full_pattern:
            items = self.sources.get(source_type, [])

            if not items:
                # No items of this type, skip
                continue

            # Get next item from this source (cycle through)
            idx = source_indices[source_type] % len(items)
            result.append(items[idx])
            source_indices[source_type] += 1

        print(f"   ✅ Generated {len(result)} items following pattern")

        return result

    def get_stats(self) -> Dict:
        """Get statistics about loaded sources"""
        return {
            'ai_count': len(self.sources['ai']),
            'stock_count': len(self.sources['stock']),
            'manual_count': len(self.sources['manual']),
            'total': sum(len(items) for items in self.sources.values()),
            'priority_order': self.priority_order
        }


# Global instance
media_source_manager = MediaSourceManager()
