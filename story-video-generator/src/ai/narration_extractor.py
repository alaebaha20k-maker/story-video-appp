"""
📝 NARRATION EXTRACTOR - Extracts Clean Narration from Mixed Scripts
Separates spoken narration from visual descriptions using AI analysis
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


class NarrationExtractor:
    """Analyzes scripts and extracts clean narration text"""

    def __init__(self):
        api_key = api_manager.get_key('gemini')
        if not api_key:
            raise ValueError("Gemini API key required!")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=GEMINI_SETTINGS['model'],
            generation_config={
                "temperature": 0.3,  # Low temperature for precise extraction
                "top_p": 0.9,
                "top_k": 20,
                "max_output_tokens": 8192,
            }
        )

    def extract_narration(
        self,
        script_text: str,
        num_scenes: int = 10
    ) -> List[Dict]:
        """
        Extract clean narration from script and organize into scenes

        Args:
            script_text: Raw script text (may contain mixed content)
            num_scenes: Number of scenes to create

        Returns:
            List of dicts with scene_number and narration text
        """
        logger.info(f"✅ Extracting clean narration ({num_scenes} scenes)...")

        prompt = f"""You are a script editor. Your task is to extract ONLY the narration (spoken words) from this script and organize it into {num_scenes} scenes.

SCRIPT TO ANALYZE:
{script_text}

TASK:
1. Extract ONLY the narration - the words that should be spoken by a narrator
2. Remove any visual descriptions, camera directions, or image prompts
3. Divide the narration into {num_scenes} logical scenes
4. Each scene should be a complete narrative segment

OUTPUT FORMAT (REQUIRED):
[SCENE 1]
<narration text for scene 1>

[SCENE 2]
<narration text for scene 2>

[Continue for all {num_scenes} scenes]

RULES:
- Include ONLY spoken narrative text
- NO camera angles, visual descriptions, or technical terms
- Each scene should flow naturally when spoken
- Maintain the story's narrative flow
- Keep character names and dialogue
- Write for human listening, not reading

Begin extraction:
"""

        try:
            # Generate narration extraction
            response = self.model.generate_content(prompt)
            extracted_text = response.text

            # Parse scenes
            scenes = self._parse_narration_scenes(extracted_text, num_scenes)

            logger.info(f"✅ Extracted {len(scenes)} narration scenes")

            return scenes

        except Exception as e:
            logger.error(f"❌ Narration extraction failed: {e}")
            # Fallback: split original script into scenes
            return self._fallback_split(script_text, num_scenes)

    def _parse_narration_scenes(self, text: str, num_scenes: int) -> List[Dict]:
        """Parse extracted narration into scene objects"""
        scenes = []

        # Try to find [SCENE X] markers
        scene_pattern = r'\[SCENE\s+(\d+)\]\s*(.+?)(?=\[SCENE\s+\d+\]|$)'
        matches = re.findall(scene_pattern, text, re.DOTALL | re.IGNORECASE)

        if matches and len(matches) >= num_scenes * 0.7:  # Got at least 70% of scenes
            for scene_num, narration in matches:
                scenes.append({
                    'scene_number': int(scene_num),
                    'narration': narration.strip(),
                    'char_count': len(narration.strip())
                })
        else:
            # Fallback: split by paragraphs
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            scene_length = max(len(paragraphs) // num_scenes, 1)

            for i in range(num_scenes):
                start = i * scene_length
                end = min(start + scene_length, len(paragraphs))
                scene_text = '\n\n'.join(paragraphs[start:end])

                if scene_text:
                    scenes.append({
                        'scene_number': i + 1,
                        'narration': scene_text,
                        'char_count': len(scene_text)
                    })

        return scenes[:num_scenes]  # Ensure we don't exceed requested scenes

    def _fallback_split(self, script_text: str, num_scenes: int) -> List[Dict]:
        """Fallback method if AI extraction fails"""
        logger.warning("⚠️ Using fallback narration split")

        paragraphs = [p.strip() for p in script_text.split('\n\n') if p.strip()]
        scene_length = max(len(paragraphs) // num_scenes, 1)

        scenes = []
        for i in range(num_scenes):
            start = i * scene_length
            end = min(start + scene_length, len(paragraphs))
            scene_text = '\n\n'.join(paragraphs[start:end])

            if scene_text:
                scenes.append({
                    'scene_number': i + 1,
                    'narration': scene_text,
                    'char_count': len(scene_text)
                })

        return scenes


# Global instance
narration_extractor = NarrationExtractor()
