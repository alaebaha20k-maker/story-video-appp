"""
🎨 IMAGE PROMPT EXTRACTOR - Generates Detailed Visual Prompts from Scripts
Creates professional AI-ready image prompts from narrative text
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import google.generativeai as genai
from typing import List, Dict
import re

from config.settings import GEMINI_SETTINGS
from src.utils.api_manager import api_manager
from src.utils.logger import logger


class ImagePromptExtractor:
    """Generates detailed image prompts for AI image generation"""

    def __init__(self):
        api_key = api_manager.get_key('gemini')
        if not api_key:
            raise ValueError("Gemini API key required!")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=GEMINI_SETTINGS['model'],
            generation_config={
                "temperature": 0.7,  # Creative but controlled
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )

    def generate_prompts(
        self,
        script_text: str,
        num_scenes: int = 10,
        image_style: str = "cinematic_film",
        story_type: str = "scary_horror"
    ) -> List[Dict]:
        """
        Generate detailed image prompts from script

        Args:
            script_text: Full narrative script
            num_scenes: Number of image prompts to generate
            image_style: Visual style (cinematic_film, anime_style, etc.)
            story_type: Story type for mood/atmosphere

        Returns:
            List of dicts with scene_number and detailed image_prompt
        """
        logger.info(f"🎨 Generating {num_scenes} detailed image prompts ({image_style})...")

        # Map image styles to descriptive terms
        style_descriptions = {
            "cinematic_film": "cinematic movie still, professional film photography, dramatic lighting",
            "documentary_real": "photojournalism, documentary photography, authentic real-life scene",
            "anime_style": "anime art style, Japanese animation, vibrant colors, expressive",
            "horror_creepy": "horror cinematography, dark and ominous, terrifying atmosphere",
            "comic_book": "comic book art, graphic novel style, bold lines, dynamic composition",
            "oil_painting": "classical oil painting, fine art, rich textures, masterpiece quality",
            "historical_photo": "vintage photograph, historical documentation, aged and authentic",
            "sci_fi_future": "futuristic sci-fi, cyberpunk aesthetic, advanced technology, neon lights",
            "fantasy_epic": "epic fantasy art, magical and mythical, grand and majestic",
            "sketch_drawing": "pencil sketch, hand-drawn illustration, artistic linework",
            "watercolor": "watercolor painting, soft washes, artistic and delicate",
            "3d_render": "3D rendered CGI, photorealistic rendering, detailed modeling",
            "retro_vintage": "retro vintage style, 70s/80s aesthetic, nostalgic feel",
            "dark_noir": "film noir, black and white, high contrast, detective movie aesthetic"
        }

        style_desc = style_descriptions.get(image_style, "professional photography, high quality")

        # Map story types to atmosphere
        atmosphere_map = {
            "scary_horror": "dark and terrifying, ominous shadows, eerie atmosphere, unsettling mood",
            "emotional_heartwarming": "warm and touching, soft lighting, emotional depth, hopeful atmosphere",
            "true_crime": "gritty and realistic, documentary style, authentic locations, serious tone",
            "mystery_thriller": "suspenseful and tense, mysterious shadows, dramatic angles, noir atmosphere",
            "historical_documentary": "authentic historical setting, period-accurate details, documentary realism",
            "supernatural_paranormal": "otherworldly and mystical, supernatural elements, eerie and mysterious",
            "adventure_survival": "wild and untamed, natural environments, action-oriented, epic scale",
            "sci_fi_future": "futuristic and technological, advanced civilization, sci-fi elements",
            "fantasy_magical": "magical and enchanted, fantasy elements, wonderous and mythical",
            "comedy_funny": "lighthearted and playful, bright colors, comedic timing, expressive",
            "romantic_love": "romantic and intimate, soft lighting, emotional connection, beautiful",
            "war_military": "intense combat, military equipment, battlefield chaos, heroic and gritty",
            "motivational_inspiring": "triumphant and uplifting, inspiring visuals, hope and determination",
            "anime_style": "anime aesthetic, vibrant and expressive, Japanese animation style"
        }

        atmosphere = atmosphere_map.get(story_type, "dramatic atmosphere, professional quality")

        prompt = f"""You are a professional visual director for AI image generation. Analyze this script and create {num_scenes} detailed image prompts.

SCRIPT:
{script_text}

VISUAL REQUIREMENTS:
- Style: {style_desc}
- Atmosphere: {atmosphere}
- Number of scenes: {num_scenes}

TASK:
Create {num_scenes} image prompts that capture the KEY VISUAL MOMENTS of this story. Each prompt must be DETAILED and AI-ready (for Flux, Midjourney, Pollinations).

EACH IMAGE PROMPT MUST INCLUDE:
1. **Camera Angle**: (wide shot, close-up, medium shot, aerial view, POV, etc.)
2. **Subject/Scene**: (what we see - characters, locations, objects)
3. **Setting/Environment**: (where it takes place)
4. **Lighting**: (dramatic, soft, dark, golden hour, etc.)
5. **Mood/Atmosphere**: (based on story type)
6. **Color Palette**: (warm tones, cool blues, desaturated, vibrant, etc.)
7. **Art Style**: (already specified: {style_desc})
8. **Composition Details**: (specific visual elements that make it compelling)

OUTPUT FORMAT (REQUIRED):
[IMAGE 1]
<detailed 40-60 word image prompt>

[IMAGE 2]
<detailed 40-60 word image prompt>

[Continue for all {num_scenes} images]

EXAMPLE GOOD PROMPT:
"Wide-angle establishing shot of a gothic Victorian mansion on a cliff at dusk, dramatic purple and orange sunset, overgrown ivy covering weathered stone walls, broken windows, ominous storm clouds gathering, {style_desc}, {atmosphere}, desaturated colors with warm highlights, cinematic composition"

EXAMPLE BAD PROMPT:
"A scary house"

Generate {num_scenes} professional image prompts now:
"""

        try:
            # Generate image prompts
            response = self.model.generate_content(prompt)
            generated_text = response.text

            # Parse prompts
            prompts = self._parse_image_prompts(generated_text, num_scenes)

            logger.info(f"✅ Generated {len(prompts)} detailed image prompts")

            return prompts

        except Exception as e:
            logger.error(f"L Image prompt generation failed: {e}")
            # Fallback: create generic prompts
            return self._fallback_prompts(script_text, num_scenes, image_style, story_type)

    def _parse_image_prompts(self, text: str, num_scenes: int) -> List[Dict]:
        """Parse generated image prompts into structured data"""
        prompts = []

        # Try to find [IMAGE X] markers
        prompt_pattern = r'\[IMAGE\s+(\d+)\]\s*(.+?)(?=\[IMAGE\s+\d+\]|$)'
        matches = re.findall(prompt_pattern, text, re.DOTALL | re.IGNORECASE)

        if matches and len(matches) >= num_scenes * 0.7:  # Got at least 70% of prompts
            for img_num, prompt_text in matches:
                prompts.append({
                    'scene_number': int(img_num),
                    'image_prompt': prompt_text.strip(),
                    'char_count': len(prompt_text.strip())
                })
        else:
            # Fallback: split by paragraphs or lines
            lines = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 20]

            for i in range(min(num_scenes, len(lines))):
                if lines[i]:
                    prompts.append({
                        'scene_number': i + 1,
                        'image_prompt': lines[i],
                        'char_count': len(lines[i])
                    })

        # Ensure we have enough prompts
        while len(prompts) < num_scenes:
            prompts.append({
                'scene_number': len(prompts) + 1,
                'image_prompt': f"Scene {len(prompts) + 1} from the story, professional photography, cinematic composition",
                'char_count': 50
            })

        return prompts[:num_scenes]  # Ensure we don't exceed requested scenes

    def _fallback_prompts(
        self,
        script_text: str,
        num_scenes: int,
        image_style: str,
        story_type: str
    ) -> List[Dict]:
        """Generate simple fallback prompts if AI generation fails"""
        logger.warning("⚠️ Using fallback image prompts")

        # Extract first words from script to get context
        words = script_text.split()[:100]
        context = ' '.join(words)

        prompts = []
        for i in range(num_scenes):
            prompt_text = f"{image_style} style, scene {i+1} from {story_type} story, {context[:100]}..."
            prompts.append({
                'scene_number': i + 1,
                'image_prompt': prompt_text,
                'char_count': len(prompt_text)
            })

        return prompts


# Global instance
image_prompt_extractor = ImagePromptExtractor()
