"""
🎨 ULTIMATE IMAGE MANAGER - All 3 Modes Complete
AI Images + Manual Images + Stock Media + Hybrid
Production-Ready, Full Features
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import requests
import time
from typing import Dict, List, Optional
from enum import Enum

from src.ai.ultra_image_prompts import create_prompt_builder
from src.utils.file_handler import file_handler
from src.utils.logger import logger


class ImageMode(Enum):
    """Image generation modes"""
    AI_ONLY = "ai_only"
    MANUAL_ONLY = "manual_only"
    STOCK_ONLY = "stock_only"
    AI_MANUAL = "ai_manual"
    AI_STOCK = "ai_stock"
    MANUAL_STOCK = "manual_stock"
    ALL_THREE = "all_three"


class UltimateImageManager:
    """Master image manager - all 3 modes"""
    
    def __init__(self, image_style: str = "cinematic_film", story_type: str = "scary_horror"):
        self.image_style = image_style
        self.story_type = story_type
        self.prompt_builder = create_prompt_builder(image_style, story_type)
        
        from src.utils.api_manager import api_manager
        self.pexels_api_key = api_manager.get_key('pexels')
        self.pexels_base_url = "https://api.pexels.com/v1"
        
        self.current_mode = None
        self.ai_images = []
        self.manual_images = []
        self.stock_videos = []
        self.stock_images = []
        
        logger.info(f"🎨 Image Manager initialized")
        logger.info(f"   Style: {image_style}")
        logger.info(f"   Niche: {story_type}")
    
    def process_images(self, scenes: List[Dict], mode: str = "ai_only", characters: Dict[str, str] = None, video_duration: float = None, manual_image_paths: List[str] = None, stock_video_keywords: List[str] = None, stock_image_keywords: List[str] = None) -> List[Dict]:
        """Process images based on chosen mode"""
        
        logger.info(f"\n📊 PROCESSING IMAGES")
        logger.info(f"   Mode: {mode.upper()}")
        logger.info(f"   Scenes: {len(scenes)}")
        
        self.current_mode = ImageMode[mode.upper()]
        
        if characters:
            for name, desc in characters.items():
                self.prompt_builder.register_character(name, desc)
            logger.info(f"   Characters: {', '.join(characters.keys())}")
        
        if mode == "ai_only":
            return self._process_ai_only(scenes)
        elif mode == "manual_only":
            if not manual_image_paths:
                logger.error("❌ Manual mode requires image paths!")
                return []
            return self._process_manual_only(manual_image_paths, scenes)
        elif mode == "stock_only":
            if not video_duration:
                logger.error("❌ Stock mode requires video_duration!")
                return []
            return self._process_stock_only(scenes, video_duration, stock_video_keywords, stock_image_keywords)
        elif mode == "ai_manual":
            return self._process_ai_manual(scenes, manual_image_paths)
        elif mode == "ai_stock":
            if not video_duration:
                logger.error("❌ Hybrid mode requires video_duration!")
                return []
            return self._process_ai_stock(scenes, video_duration, stock_video_keywords, stock_image_keywords)
        elif mode == "manual_stock":
            if not video_duration:
                logger.error("❌ Hybrid mode requires video_duration!")
                return []
            return self._process_manual_stock(scenes, video_duration, manual_image_paths, stock_video_keywords, stock_image_keywords)
        elif mode == "all_three":
            if not video_duration:
                logger.error("❌ Hybrid mode requires video_duration!")
                return []
            return self._process_all_three(scenes, video_duration, manual_image_paths, stock_video_keywords, stock_image_keywords)
        else:
            logger.error(f"❌ Unknown mode: {mode}")
            return []
    
    def _process_ai_only(self, scenes: List[Dict]) -> List[Dict]:
        """Generate all images with AI (Pollinations)"""
        
        logger.info("\n🤖 MODE A: AI IMAGES ONLY")
        logger.info(f"   Generating {len(scenes)} images...")
        
        images = []
        
        for i, scene in enumerate(scenes):
            logger.info(f"   [{i+1}/{len(scenes)}] Generating scene {scene['scene_number']}...")
            
            try:
                scene_type = self._determine_scene_type(scene.get('image_description', ''))
                prompt_data = self.prompt_builder.build_scene_prompt(scene.get('image_description', scene.get('content', 'scene')), scene_type)
                
                image_data = self._generate_pollinations(prompt_data['prompt'], scene['scene_number'])
                
                if image_data:
                    images.append(image_data)
                    logger.success(f"      ✅ Scene {scene['scene_number']}")
                else:
                    logger.error(f"      ❌ Failed to generate")
                
                time.sleep(1)
            
            except Exception as e:
                logger.error(f"      Error: {e}")
        
        self.ai_images = images
        logger.success(f"\n✅ Generated {len(images)}/{len(scenes)} AI images")
        
        return images
    
    def _generate_pollinations(self, prompt: str, scene_number: int) -> Optional[Dict]:
        """Generate image with Pollinations (FREE)"""
        
        try:
            prompt_encoded = requests.utils.quote(prompt)
            url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&model=flux"
            
            response = requests.get(url, timeout=60)
            
            if response.status_code == 200:
                filename = f"scene_{scene_number:03d}_ai.png"
                filepath = file_handler.save_binary(response.content, filename, file_handler.temp_dir)
                
                return {
                    "filepath": str(filepath),
                    "scene_number": scene_number,
                    "prompt": prompt[:200],
                    "source": "ai_pollinations",
                    "type": "image"
                }
        
        except Exception as e:
            logger.error(f"Pollinations error: {e}")
        
        return None
    
    def _process_manual_only(self, manual_paths: List[str], scenes: List[Dict]) -> List[Dict]:
        """Use manually provided image paths"""
        
        logger.info("\n👤 MODE B: MANUAL IMAGES ONLY")
        logger.info(f"   Using {len(manual_paths)} manual images")
        
        images = []
        
        for i, path in enumerate(manual_paths):
            try:
                path = Path(path)
                
                if not path.exists():
                    logger.error(f"   ❌ File not found: {path}")
                    continue
                
                filename = f"scene_{i+1:03d}_manual.png"
                with open(path, 'rb') as f:
                    filepath = file_handler.save_binary(f.read(), filename, file_handler.temp_dir)
                
                images.append({
                    "filepath": str(filepath),
                    "scene_number": i + 1,
                    "source": "manual_upload",
                    "original_path": str(path),
                    "type": "image"
                })
                
                logger.success(f"   ✅ Loaded: {path.name}")
            
            except Exception as e:
                logger.error(f"   Error loading {path}: {e}")
        
        self.manual_images = images
        logger.success(f"\n✅ Loaded {len(images)} manual images")
        
        return images
    
    def _process_stock_only(self, scenes: List[Dict], video_duration: float, video_keywords: List[str] = None, image_keywords: List[str] = None) -> List[Dict]:
        """Download and use stock media from Pexels"""
        
        logger.info("\n📹 MODE C: STOCK MEDIA ONLY")
        logger.info(f"   Video duration: {video_duration:.1f}s")
        
        if not self.pexels_api_key:
            logger.error("❌ Pexels API key required!")
            return []
        
        media = []
        
        logger.info("   Searching for videos...")
        if video_keywords:
            videos = self._search_pexels_videos(video_keywords)
        else:
            videos = self._search_pexels_videos([scene.get('image_description', '')[:50] for scene in scenes[:3]])
        
        logger.info("   Searching for images...")
        if image_keywords:
            images = self._search_pexels_images(image_keywords)
        else:
            images = self._search_pexels_images([scene.get('image_description', '')[:50] for scene in scenes[:3]])
        
        media = self._combine_stock_media(videos, images, video_duration)
        
        self.stock_videos = [m for m in media if m['type'] == 'video']
        self.stock_images = [m for m in media if m['type'] == 'image']
        
        logger.success(f"\n✅ Got {len(self.stock_videos)} videos + {len(self.stock_images)} images")
        
        return media
    
    def _search_pexels_videos(self, keywords: List[str]) -> List[Dict]:
        """Search for stock videos on Pexels"""
        
        videos = []
        
        for keyword in keywords[:5]:
            try:
                keyword = keyword.strip()
                if not keyword or len(keyword) < 2:
                    continue
                
                headers = {"Authorization": self.pexels_api_key}
                url = f"{self.pexels_base_url}/videos/search"
                params = {"query": keyword, "per_page": 3, "page": 1}
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for video in data.get('videos', []):
                        try:
                            video_file = video['video_files'][0]
                            video_url = video_file['link']
                            
                            video_response = requests.get(video_url, timeout=30)
                            if video_response.status_code == 200:
                                filename = f"stock_video_{len(videos)+1}.mp4"
                                filepath = file_handler.save_binary(video_response.content, filename, file_handler.temp_dir)
                                
                                videos.append({
                                    "filepath": str(filepath),
                                    "source": "pexels",
                                    "type": "video",
                                    "duration": video_file.get('duration', 10),
                                    "keyword": keyword
                                })
                                
                                logger.info(f"      ✅ Downloaded video: {filename}")
                        
                        except Exception as e:
                            logger.error(f"      Error downloading video: {e}")
                
                time.sleep(1)
            
            except Exception as e:
                logger.error(f"   Error searching videos for '{keyword}': {e}")
        
        return videos
    
    def _search_pexels_images(self, keywords: List[str]) -> List[Dict]:
        """Search for stock images on Pexels"""
        
        images = []
        
        for keyword in keywords[:5]:
            try:
                keyword = keyword.strip()
                if not keyword or len(keyword) < 2:
                    continue
                
                headers = {"Authorization": self.pexels_api_key}
                url = f"{self.pexels_base_url}/search"
                params = {"query": keyword, "per_page": 5, "page": 1}
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for photo in data.get('photos', []):
                        try:
                            image_url = photo['src']['large']
                            
                            img_response = requests.get(image_url, timeout=30)
                            if img_response.status_code == 200:
                                filename = f"stock_image_{len(images)+1}.jpg"
                                filepath = file_handler.save_binary(img_response.content, filename, file_handler.temp_dir)
                                
                                images.append({
                                    "filepath": str(filepath),
                                    "source": "pexels",
                                    "type": "image",
                                    "keyword": keyword
                                })
                                
                                logger.info(f"      ✅ Downloaded image: {filename}")
                        
                        except Exception as e:
                            logger.error(f"      Error downloading image: {e}")
                
                time.sleep(1)
            
            except Exception as e:
                logger.error(f"   Error searching images for '{keyword}': {e}")
        
        return images
    
    def _combine_stock_media(self, videos: List[Dict], images: List[Dict], total_duration: float) -> List[Dict]:
        """Combine videos and images with smart timing"""
        
        logger.info(f"   Combining {len(videos)} videos + {len(images)} images")
        
        media = []
        
        video_percentage = 0.3
        video_time = total_duration * video_percentage
        image_time = total_duration * (1 - video_percentage)
        
        if videos:
            total_video_duration = sum(v.get('duration', 10) for v in videos)
            loop_count = max(1, int(video_time / total_video_duration))
            
            for video in videos:
                video['loops'] = loop_count
                media.append(video)
                logger.info(f"      Video: {loop_count}x loop")
        
        if images:
            time_per_image = image_time / len(images) if images else 0
            
            for i, image in enumerate(images):
                image['duration'] = time_per_image
                media.append(image)
                logger.info(f"      Image: {time_per_image:.1f}s")
        
        return media
    
    def _process_ai_manual(self, scenes: List[Dict], manual_paths: List[str]) -> List[Dict]:
        """Mix AI + Manual images"""
        
        logger.info("\n🔄 MODE: AI + MANUAL MIX")
        
        ai_images = self._process_ai_only(scenes[:len(scenes)//2])
        manual_images = self._process_manual_only(manual_paths, scenes[len(scenes)//2:])
        
        combined = ai_images + manual_images
        logger.success(f"\n✅ Combined: {len(ai_images)} AI + {len(manual_images)} Manual")
        
        return combined
    
    def _process_ai_stock(self, scenes: List[Dict], video_duration: float, stock_video_keywords: List[str], stock_image_keywords: List[str]) -> List[Dict]:
        """Mix AI + Stock media"""
        
        logger.info("\n🔄 MODE: AI + STOCK MIX")
        
        ai_images = self._process_ai_only(scenes[:len(scenes)//2])
        stock = self._process_stock_only(scenes[len(scenes)//2:], video_duration * 0.5, stock_video_keywords, stock_image_keywords)
        
        combined = ai_images + stock
        logger.success(f"\n✅ Combined: {len(ai_images)} AI + {len(stock)} Stock")
        
        return combined
    
    def _process_manual_stock(self, scenes: List[Dict], video_duration: float, manual_paths: List[str], stock_video_keywords: List[str], stock_image_keywords: List[str]) -> List[Dict]:
        """Mix Manual + Stock media"""
        
        logger.info("\n🔄 MODE: MANUAL + STOCK MIX")
        
        manual = self._process_manual_only(manual_paths, scenes[:len(manual_paths)])
        stock = self._process_stock_only(scenes[len(manual_paths):], video_duration * 0.5, stock_video_keywords, stock_image_keywords)
        
        combined = manual + stock
        logger.success(f"\n✅ Combined: {len(manual)} Manual + {len(stock)} Stock")
        
        return combined
    
    def _process_all_three(self, scenes: List[Dict], video_duration: float, manual_paths: List[str], stock_video_keywords: List[str], stock_image_keywords: List[str]) -> List[Dict]:
        """Mix all three: AI + Manual + Stock"""
        
        logger.info("\n🔄 MODE: ALL THREE MIX (AI + MANUAL + STOCK)")
        
        third = len(scenes) // 3
        
        ai_images = self._process_ai_only(scenes[:third])
        manual = self._process_manual_only(manual_paths[:third], scenes[third:2*third])
        stock = self._process_stock_only(scenes[2*third:], video_duration * 0.4, stock_video_keywords, stock_image_keywords)
        
        combined = ai_images + manual + stock
        logger.success(f"\n✅ Combined: {len(ai_images)} AI + {len(manual)} Manual + {len(stock)} Stock")
        
        return combined
    
    def _determine_scene_type(self, description: str) -> str:
        """Determine scene type from description"""
        
        desc_lower = description.lower()
        
        if any(w in desc_lower for w in ['character', 'face', 'person', 'man', 'woman']):
            return 'character_closeup'
        elif any(w in desc_lower for w in ['location', 'room', 'house', 'street', 'forest']):
            return 'establishing'
        elif any(w in desc_lower for w in ['action', 'running', 'moving', 'fight', 'jump']):
            return 'action'
        elif any(w in desc_lower for w in ['detail', 'close', 'object', 'door', 'window']):
            return 'detail'
        else:
            return 'atmospheric'
    
    def get_all_images(self) -> List[Dict]:
        """Get all processed images"""
        return self.ai_images + self.manual_images + self.stock_images + self.stock_videos
    
    def get_summary(self) -> Dict:
        """Get processing summary"""
        return {
            "mode": self.current_mode.value if self.current_mode else None,
            "total_images": len(self.get_all_images()),
            "ai_images": len(self.ai_images),
            "manual_images": len(self.manual_images),
            "stock_videos": len(self.stock_videos),
            "stock_images": len(self.stock_images)
        }


def create_image_manager(image_style: str, story_type: str) -> UltimateImageManager:
    """Create image manager instance"""
    return UltimateImageManager(image_style, story_type)


if __name__ == "__main__":
    print("\n🧪 Testing Ultimate Image Manager...\n")
    
    manager = UltimateImageManager("cinematic_film", "scary_horror")
    
    print("📋 AVAILABLE MODES:")
    for mode in ImageMode:
        print(f"   - {mode.value}")
    
    print("\n✅ Image Manager ready!\n")
    # Global instance
image_manager = ImageManager()