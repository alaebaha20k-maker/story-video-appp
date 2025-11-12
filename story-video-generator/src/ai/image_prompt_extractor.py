"""
🎨 IMAGE PROMPT EXTRACTOR - Generates Detailed Visual Prompts from Scripts
Creates professional AI-ready image prompts from narrative text
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import List, Dict
import re

from src.utils.logger import logger


class ImagePromptExtractor:
    """Extracts image prompts directly from script text (no API calls)"""

    def __init__(self):
        logger.info("🎨 Image Prompt Extractor initialized (script extraction mode)")
        print(f"   📝 Mode: Direct extraction from script (no API calls)")

    def generate_prompts(
        self,
        script_text: str,
        num_scenes: int = 10,
        image_style: str = "cinematic_film",
        story_type: str = "scary_horror"
    ) -> List[Dict]:
        """
        Extract image prompts directly from script (no API calls)

        Args:
            script_text: Full narrative script
            num_scenes: Number of image prompts to extract
            image_style: Visual style (cinematic_film, anime_style, etc.)
            story_type: Story type for mood/atmosphere

        Returns:
            List of dicts with scene_number and detailed image_prompt
        """
        logger.info(f"🎨 Extracting {num_scenes} image prompts from script...")

        # Style descriptions for enhancing extracted prompts
        style_map = {
            "cinematic_film": "cinematic, professional film photography, dramatic lighting",
            "documentary_real": "photojournalism, documentary, authentic",
            "anime_style": "anime art, Japanese animation, vibrant",
            "horror_creepy": "horror, dark and ominous, terrifying",
            "comic_book": "comic book art, graphic novel, bold",
            "oil_painting": "oil painting, fine art, rich textures",
            "historical_photo": "vintage photograph, historical",
            "sci_fi_future": "futuristic sci-fi, cyberpunk, neon",
            "fantasy_epic": "epic fantasy, magical, majestic",
            "sketch_drawing": "pencil sketch, hand-drawn",
            "watercolor": "watercolor painting, soft",
            "3d_render": "3D CGI, photorealistic rendering",
            "retro_vintage": "retro vintage, 70s/80s",
            "dark_noir": "film noir, high contrast"
        }

        style_suffix = style_map.get(image_style, "professional, high quality")

        # Extract prompts from script - split into sentences
        sentences = re.split(r'[.!?]+', script_text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        # Select evenly spaced sentences
        if len(sentences) >= num_scenes:
            step = len(sentences) // num_scenes
            selected_sentences = [sentences[i * step] for i in range(num_scenes)]
        else:
            # Repeat if not enough sentences
            selected_sentences = (sentences * ((num_scenes // len(sentences)) + 1))[:num_scenes]

        # Create image prompts from selected sentences
        prompts = []
        for i, sentence in enumerate(selected_sentences):
            # Take first 60 words from sentence
            words = sentence.split()[:60]
            base_prompt = ' '.join(words)

            # Enhance with style
            enhanced_prompt = f"{base_prompt}, {style_suffix}, detailed"

            prompts.append({
                'scene_number': i + 1,
                'image_prompt': enhanced_prompt,
                'char_count': len(enhanced_prompt)
            })

        logger.info(f"✅ Extracted {len(prompts)} image prompts from script")
        return prompts


# Global instance
image_prompt_extractor = ImagePromptExtractor()
