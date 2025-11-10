"""
🎨 SDXL-TURBO REMOTE IMAGE GENERATOR - GPU-Powered via Google Colab
Connects to remote SDXL-Turbo API for ultra-fast high-quality image generation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import requests
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
import threading

from src.ai.ultra_image_prompts import create_prompt_builder
from src.utils.file_handler import file_handler
from src.utils.logger import logger


# Remote SDXL-Turbo API endpoint (Google Colab + ngrok)
SDXL_API_URL = "https://contemplable-suzy-unfussing.ngrok-free.dev/generate_image"


# Image style mapping to SDXL-Turbo style modifiers
# Updated to match Google Colab server styles
STYLE_MODIFIERS = {
    # Colab Server Styles (14 styles)
    'cinematic_film': 'cinematic film photography, movie scene, epic composition, professional color grading',
    'documentary_real': 'documentary photography, photorealistic, natural lighting, real world scene, authentic',
    'anime_style': 'anime style, detailed anime art, vibrant colors, japanese animation style',
    'horror_creepy': 'dark horror atmosphere, ominous lighting, disturbing scene, nightmare fuel, creepy',
    'comic_book': 'comic book style, bold lines, dynamic composition, pop art colors, graphic novel',
    'historical_photo': 'historical photograph, vintage authentic, period accurate, archival quality',
    'sci_fi_future': 'sci-fi concept art, futuristic, technological, neon lighting, cyberpunk aesthetic',
    'dark_noir': 'film noir style, dramatic shadows, high contrast, moody atmosphere, dark aesthetic',
    'fantasy_epic': 'fantasy art, magical atmosphere, ethereal lighting, mystical scene, epic scale',
    'render_3d': '3D render, CGI, highly detailed, professional 3D graphics, photorealistic rendering',
    'sketch_drawing': 'pencil sketch, hand drawn, artistic line work, sketch art style',
    'watercolor': 'watercolor painting, soft colors, artistic brushwork, paper texture',
    'oil_painting': 'oil painting, traditional art, brushstroke texture, classical style',
    'retro_vintage': 'vintage photography, retro aesthetic, aged film look, nostalgic atmosphere',

    # Legacy support (for backward compatibility)
    'cinematic': 'cinematic film still, dramatic lighting, 35mm photograph, film grain, highly detailed',
    'realistic': 'photorealistic, ultra detailed, 8k uhd, high quality photograph, professional photography',
    'artistic': 'artistic masterpiece, painterly style, vibrant colors, creative composition',
    'anime': 'anime style, detailed anime art, vibrant colors, japanese animation style',
    'cartoon': 'cartoon illustration, vibrant colors, clean lines, stylized art',
    'comic': 'comic book style, bold lines, dynamic composition, pop art colors',
    'fantasy': 'fantasy art, magical atmosphere, ethereal lighting, mystical scene',
    'sci_fi': 'sci-fi concept art, futuristic, technological, neon lighting, cyberpunk aesthetic',
    'horror': 'dark horror atmosphere, ominous lighting, disturbing scene, nightmare fuel',
    'vintage': 'vintage photography, retro aesthetic, aged film look, nostalgic atmosphere',
    'neon': 'neon lights, vibrant colors, glowing elements, cyberpunk cityscape',
}


class SDXLRemoteGenerator:
    """Generate images using remote SDXL-Turbo API - GPU-powered quality"""

    def __init__(self, image_style: str = "cinematic_film", story_type: str = "scary_horror"):
        self.prompt_builder = create_prompt_builder(image_style, story_type)
        self.image_style = image_style
        self.story_type = story_type
        self.model = "SDXL-Turbo (Remote GPU)"
        self.style_modifier = STYLE_MODIFIERS.get(image_style, STYLE_MODIFIERS['cinematic_film'])

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
        """Generate single scene image using remote SDXL-Turbo"""

        # Build professional prompt
        prompt_data = self.prompt_builder.build_scene_prompt(
            scene_description,
            scene_type,
            characters
        )

        # Enhance prompt with style modifier
        enhanced_prompt = f"{prompt_data['prompt']}, {self.style_modifier}"

        logger.info(f"   Generating scene {scene_number} ({scene_type}) with SDXL-Turbo (Remote GPU)...")

        try:
            # Call remote SDXL-Turbo API
            payload = {
                "prompt": enhanced_prompt,
                "style": self.image_style,
                "width": 1920,
                "height": 1080
            }

            response = requests.post(
                SDXL_API_URL,
                json=payload,
                timeout=120,  # 2-minute timeout for GPU generation
                headers={"Content-Type": "application/json"}
            )

            response.raise_for_status()

            # Save image
            filename = f"scene_{scene_number:03d}.png"
            filepath = file_handler.save_binary(
                response.content,
                filename,
                file_handler.temp_dir
            )

            logger.success(f"      ✅ Generated (SDXL-Turbo GPU): {filename}")

            return {
                "filepath": str(filepath),
                "scene_number": scene_number,
                "prompt": enhanced_prompt,
                "style": self.image_style,
                "model": "SDXL-Turbo (Remote GPU)"
            }

        except requests.exceptions.Timeout:
            logger.error(f"      ⏱️  SDXL-Turbo API timeout for scene {scene_number}")
        except requests.exceptions.ConnectionError:
            logger.error(f"      🔌 Cannot connect to SDXL-Turbo API (check if server is running)")
        except requests.exceptions.HTTPError as e:
            logger.error(f"      ❌ SDXL-Turbo API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"      ❌ Failed to generate scene {scene_number}: {e}")

        return None

    def _generate_single_scene(self, scene, scene_index: int, characters: Dict[str, str] = None) -> Optional[Dict]:
        """Helper method to generate a single scene (used for parallel processing)"""

        # Handle both dict and string inputs
        if isinstance(scene, str):
            scene = {
                'image_description': scene,
                'content': scene,
                'scene_number': scene_index + 1
            }

        # Extract scene description
        scene_description = scene.get('image_description') or scene.get('content', '')
        scene_type = scene.get('scene_type', 'establishing')
        scene_number = scene.get('scene_number', scene_index + 1)

        # Get characters if any
        character_list = scene.get('characters', []) if isinstance(scene, dict) else []

        return self.generate_scene_image(
            scene_description,
            scene_number,
            scene_type,
            character_list
        )

    def generate_batch(
        self,
        scenes: List[Dict],
        characters: Dict[str, str] = None,
        max_workers: int = 10
    ) -> List[Optional[Dict]]:
        """Generate multiple images in parallel using remote SDXL-Turbo API"""

        # Register characters
        if characters:
            self.register_characters(characters)

        logger.info(f"\n🚀 Using PARALLEL processing with SDXL-Turbo (Remote GPU) for {len(scenes)}x speedup!")

        # Extract character info
        if characters:
            character_names = list(characters.keys())[:3]
            logger.info(f"   Characters: {', '.join(character_names)}")

        # Generate images in parallel
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for scene_index, scene in enumerate(scenes):
                future = executor.submit(self._generate_single_scene, scene, scene_index, characters)
                futures.append(future)

            # Collect results
            for future in futures:
                result = future.result()
                results.append(result)

        # Count successes and failures
        successful = sum(1 for r in results if r is not None)
        failed = len(results) - successful

        logger.success(f"\n✅ Generated {successful}/{len(scenes)} images with SDXL-Turbo (Remote GPU)")

        if failed > 0:
            logger.warning(f"⚠️  WARNING: {failed}/{len(scenes)} images failed to generate!")
            failed_indices = [i for i, r in enumerate(results) if r is None]
            logger.warning(f"   Failed scenes: {failed_indices}")
            logger.warning(f"   This will cause video to have repeated images!")

        return results


def create_image_generator(image_style: str = "cinematic_film", story_type: str = "scary_horror") -> SDXLRemoteGenerator:
    """Factory function to create SDXL-Turbo remote image generator"""
    return SDXLRemoteGenerator(image_style, story_type)
