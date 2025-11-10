"""
🎨 Hybrid Image Generator - Supports both Local and Remote GPU
Automatically uses remote SDXL-Turbo API if available, falls back to local otherwise
"""

import os
from pathlib import Path
from typing import List, Dict, Optional

from src.utils.logger import logger


class HybridImageGenerator:
    """Generate images using remote GPU (if available) or local fallback"""

    def __init__(self, image_style: str = "cinematic_film", story_type: str = "scary_horror"):
        self.image_style = image_style
        self.story_type = story_type

        # Check if remote API is available
        self.sdxl_api_url = os.getenv('SDXL_API_URL', '').strip()

        if self.sdxl_api_url:
            logger.info(f"🚀 Using Remote GPU: SDXL-Turbo API")
            logger.info(f"   URL: {self.sdxl_api_url}")
            self.use_remote = True

            # Import remote client
            try:
                from src.ai.sdxl_turbo_client import SDXLTurboClient
                self.remote_client = SDXLTurboClient(self.sdxl_api_url)
            except Exception as e:
                logger.error(f"   ❌ Failed to initialize remote client: {e}")
                logger.info(f"   Falling back to local generation")
                self.use_remote = False
        else:
            logger.info(f"🎨 Using Local Generation: Pollinations AI")
            self.use_remote = False

        # Initialize local generator as fallback
        if not self.use_remote:
            from src.ai.image_generator import UltraImageGenerator
            self.local_generator = UltraImageGenerator(image_style, story_type)

    def register_characters(self, characters: Dict[str, str]):
        """Register characters for consistency"""
        if not self.use_remote and hasattr(self, 'local_generator'):
            self.local_generator.register_characters(characters)

    def generate_scene_image(
        self,
        scene_description: str,
        scene_number: int,
        scene_type: str = "establishing",
        characters: List[str] = None
    ) -> Optional[Dict]:
        """Generate single scene image"""

        if self.use_remote:
            return self._generate_remote(scene_description, scene_number)
        else:
            return self.local_generator.generate_scene_image(
                scene_description, scene_number, scene_type, characters
            )

    def _generate_remote(self, scene_description: str, scene_number: int) -> Optional[Dict]:
        """Generate image using remote SDXL-Turbo API"""
        try:
            # Build prompt with style and story type
            from src.ai.ultra_image_prompts import create_prompt_builder

            prompt_builder = create_prompt_builder(self.image_style, self.story_type)
            prompt_data = prompt_builder.build_scene_prompt(scene_description, "establishing", None)
            prompt = prompt_data['prompt']

            logger.info(f"   Generating scene {scene_number} with Remote GPU...")

            # Generate image
            filename = f"scene_{scene_number:03d}.png"
            output_path = Path("output/temp") / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)

            image_path = self.remote_client.generate_image(
                prompt=prompt,
                output_path=str(output_path)
            )

            logger.success(f"      ✅ Generated (Remote GPU): {filename}")

            return {
                "filepath": image_path,
                "scene_number": scene_number,
                "prompt": prompt,
                "style": self.image_style,
                "model": "SDXL-Turbo (Remote GPU)"
            }

        except Exception as e:
            logger.error(f"      ❌ Remote generation failed: {e}")
            logger.error(f"      ❌ SDXL-Turbo API error: 500 ❌")
            return None

    def generate_batch(
        self,
        scenes: List[Dict],
        characters: Dict[str, str] = None
    ) -> List[Dict]:
        """Generate images for all scenes"""

        if self.use_remote:
            logger.info(f"🎨 Generating {len(scenes)} images with Remote GPU (SDXL-Turbo)...")
        else:
            logger.info(f"🎨 Generating {len(scenes)} images locally...")

        if self.use_remote:
            return self._generate_batch_remote(scenes, characters)
        else:
            return self.local_generator.generate_batch(scenes, characters)

    def _generate_batch_remote(
        self,
        scenes: List[Dict],
        characters: Dict[str, str] = None
    ) -> List[Dict]:
        """Generate batch using remote API with parallel processing"""
        from concurrent.futures import ThreadPoolExecutor
        import time

        logger.info(f"   Model: SDXL-Turbo (Remote GPU)")
        logger.info(f"   Style: {self.image_style}")
        logger.info(f"   Niche: {self.story_type}")
        logger.info(f"   🚀 Using PARALLEL processing for 10x speedup!")

        start_time = time.time()

        images = []
        failed_scenes = []

        # Use ThreadPoolExecutor for parallel generation
        with ThreadPoolExecutor(max_workers=min(10, len(scenes))) as executor:
            futures = []
            for i, scene in enumerate(scenes):
                future = executor.submit(self._generate_single_scene_remote, scene, i, characters)
                futures.append(future)

            # Collect results
            for i, future in enumerate(futures):
                try:
                    image_data = future.result(timeout=240)
                    if image_data:
                        images.append(image_data)
                        logger.info(f"      ✅ Image {i+1}/{len(scenes)}: {image_data['filepath']}")
                    else:
                        logger.error(f"      ❌ Scene {i+1} returned None!")
                        failed_scenes.append(i)
                except Exception as e:
                    logger.error(f"      ❌ Scene {i+1} failed: {e}")
                    failed_scenes.append(i)

        duration = time.time() - start_time
        logger.success(f"✅ Generated {len(images)}/{len(scenes)} images with SDXL-Turbo (Remote GPU)")

        if len(images) < len(scenes):
            logger.error(f"   ⚠️  WARNING: {len(scenes) - len(images)}/{len(scenes)} images failed to generate!")
            logger.error(f"   ⚠️ Failed scenes: {failed_scenes}")
            logger.error(f"   ⚠️ This will cause video to have repeated images!")

        if len(images) > 0:
            logger.info(f"   Average: {duration/len(images):.1f}s per image")

        return images

    def _generate_single_scene_remote(self, scene, scene_index: int, characters: Dict[str, str] = None) -> Optional[Dict]:
        """Helper to generate single scene remotely"""

        # Handle both dict and string inputs
        if isinstance(scene, str):
            scene = {
                'image_description': scene,
                'content': scene,
                'scene_number': scene_index + 1
            }
        elif not isinstance(scene, dict):
            logger.error(f"      ❌ Invalid scene type: {type(scene)}")
            return None

        return self.generate_scene_image(
            scene.get('image_description', scene.get('content', 'scene')),
            scene.get('scene_number', scene_index + 1),
            'establishing',
            None
        )


def create_image_generator(image_style: str, story_type: str) -> HybridImageGenerator:
    """Create hybrid image generator (auto-detects remote/local)"""
    return HybridImageGenerator(image_style, story_type)
