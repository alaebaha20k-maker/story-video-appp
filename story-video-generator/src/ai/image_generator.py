"""
🎨 ULTRA IMAGE GENERATOR - Professional quality, all styles
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import requests
import time
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
import threading

from src.ai.ultra_image_prompts import create_prompt_builder
from src.utils.file_handler import file_handler
from src.utils.logger import logger


class UltraImageGenerator:
    """Generate professional images with FLUX.1 Schnell - highest quality"""
    
    def __init__(self, image_style: str = "cinematic_film", story_type: str = "scary_horror"):
        self.prompt_builder = create_prompt_builder(image_style, story_type)
        self.image_style = image_style
        self.story_type = story_type
        self.model = "FLUX.1 Schnell"  # Using FLUX.1 Schnell for superior quality
    
    def register_characters(self, characters: Dict[str, str]):
        """Register characters for consistency"""
        for name, description in characters.items():
            self.prompt_builder.register_character(name, description)
    
    def generate_scene_image(
        self,
        scene_description: str,
        scene_number: int,
        scene_type: str = "establishing",
        characters: List[str] = None
    ) -> Optional[Dict]:
        """Generate single scene image using FLUX.1 Schnell"""
        
        # Build professional prompt
        prompt_data = self.prompt_builder.build_scene_prompt(
            scene_description,
            scene_type,
            characters
        )
        
        logger.info(f"   Generating scene {scene_number} ({scene_type}) with FLUX.1 Schnell...")
        
        # Use Pollinations AI with FLUX.1 Schnell model for higher quality
        try:
            # FLUX.1 Schnell parameters for best quality
            params = {
                'model': 'flux',
                'width': 1024,
                'height': 1024,
                'nologo': 'true',
                'enhance': 'true'
            }
            
            # Build URL with FLUX.1 Schnell
            base_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt_data['prompt'])}"
            param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            url = f"{base_url}?{param_string}"
            
            response = requests.get(url, timeout=180)  # 3-minute timeout for FLUX.1 Schnell (high quality takes time!)
            
            if response.status_code == 200:
                filename = f"scene_{scene_number:03d}.png"
                filepath = file_handler.save_binary(
                    response.content,
                    filename,
                    file_handler.temp_dir
                )
                
                logger.success(f"      ✅ Generated (FLUX.1 Schnell): {filename}")
                
                return {
                    "filepath": str(filepath),
                    "scene_number": scene_number,
                    "prompt": prompt_data['prompt'],
                    "style": self.image_style,
                    "model": "FLUX.1 Schnell"
                }
        
        except Exception as e:
            logger.error(f"      ❌ Failed: {e}")
        
        return None
    
    def _generate_single_scene(self, scene, scene_index: int, characters: Dict[str, str] = None) -> Optional[Dict]:
        """Helper method to generate a single scene (used for parallel processing)"""
        
        # Handle both dict and string inputs (for backward compatibility)
        if isinstance(scene, str):
            scene = {
                'image_description': scene,
                'content': scene,
                'scene_number': scene_index + 1
            }
        elif not isinstance(scene, dict):
            logger.error(f"      ❌ Invalid scene type: {type(scene)}")
            return None
        
        # Determine scene type from description
        desc_lower = scene.get('image_description', '').lower()
        
        if 'character' in desc_lower or 'face' in desc_lower:
            scene_type = 'character_closeup'
        elif 'location' in desc_lower or 'establishing' in desc_lower:
            scene_type = 'establishing'
        elif 'action' in desc_lower or 'running' in desc_lower:
            scene_type = 'action'
        elif 'detail' in desc_lower or 'close' in desc_lower:
            scene_type = 'detail'
        else:
            scene_type = 'atmospheric'
        
        # Extract character names from scene
        scene_chars = []
        if characters:
            for char_name in characters.keys():
                if char_name.lower() in scene.get('content', '').lower():
                    scene_chars.append(char_name)
        
        # Generate image
        return self.generate_scene_image(
            scene.get('image_description', scene.get('content', 'scene')),
            scene.get('scene_number', scene_index + 1),
            scene_type,
            scene_chars if scene_chars else None
        )
    
    def generate_batch(
        self,
        scenes: List[Dict],
        characters: Dict[str, str] = None
    ) -> List[Dict]:
        """⚡ Generate images for all scenes - PARALLEL PROCESSING FOR SPEED!"""
        
        logger.info(f"🎨 Generating {len(scenes)} images...")
        logger.info(f"   Model: {self.model} (High Quality)")
        logger.info(f"   Style: {self.image_style}")
        logger.info(f"   Niche: {self.story_type}")
        logger.info(f"   🚀 Using PARALLEL processing for 10x speedup!")
        
        # Register characters
        if characters:
            self.register_characters(characters)
            logger.info(f"   Characters: {', '.join(characters.keys())}")
        
        start_time = time.time()
        
        # ⚡ PARALLEL IMAGE GENERATION - Generate all images at once!
        images = []
        
        # Use ThreadPoolExecutor to generate all images in parallel
        # Max workers = 10 (all images at once for maximum speed!)
        with ThreadPoolExecutor(max_workers=min(10, len(scenes))) as executor:
            # Submit all tasks
            futures = []
            for i, scene in enumerate(scenes):
                future = executor.submit(self._generate_single_scene, scene, i, characters)
                futures.append(future)
            
            # Collect results as they complete
            for i, future in enumerate(futures):
                try:
                    image_data = future.result(timeout=240)  # 4-minute timeout per image (FLUX.1 Schnell can be slow!)
                    if image_data:
                        images.append(image_data)
                except Exception as e:
                    logger.error(f"      ❌ Scene {i+1} failed: {e}")
        
        duration = time.time() - start_time
        logger.success(f"✅ Generated {len(images)}/{len(scenes)} images in {duration:.1f}s ⚡")
        
        # Only show average if we generated images
        if len(images) > 0:
            logger.info(f"   Average: {duration/len(images):.1f}s per image (parallel!)")
        else:
            logger.error(f"   ⚠️  No images generated - check prompts and API connection")
        
        return images


# Quick function
def create_image_generator(image_style: str, story_type: str) -> UltraImageGenerator:
    """Create image generator with chosen styles"""
    return UltraImageGenerator(image_style, story_type)


# Default global instance for backward compatibility
image_generator = UltraImageGenerator()