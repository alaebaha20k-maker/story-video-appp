"""
📝 CLEAN SCRIPT GENERATOR - NO Image Prompts in Script
Generates high-quality scripts WITHOUT image descriptions
Image prompts are generated separately AFTER script creation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import google.generativeai as genai
from typing import Dict, List, Optional
import re

from config.settings import GEMINI_SETTINGS
from config.story_types import STORY_TYPES
from src.utils.api_manager import api_manager
from src.utils.logger import logger


class CleanScriptGenerator:
    """Generate HIGH-QUALITY scripts WITHOUT image prompts for perfect TTS"""

    def __init__(self):
        api_key = api_manager.get_key('gemini')
        if not api_key:
            raise ValueError("Gemini API key required!")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=GEMINI_SETTINGS['model'],
            generation_config={
                "temperature": 0.75,
                "top_p": 0.92,
                "top_k": 50,
                "max_output_tokens": 16384,
            }
        )

        print(f"🏆 Clean Script Generator (Gemini) initialized")
        print(f"   Focus: HIGH-QUALITY scripts for voice narration")
        print(f"   NO image prompts in script (generated separately)")

    def generate_clean_script(
        self,
        topic: str,
        story_type: str,
        template: Optional[Dict] = None,
        research_data: Optional[str] = None,
        duration_minutes: int = 10,
    ) -> Dict:
        """
        Generate CLEAN script with NO image descriptions
        Perfect for TTS - no IMAGE: lines that would be read aloud
        """

        if story_type not in STORY_TYPES:
            logger.warning(f"Unknown story type: {story_type}")
            story_type = "scary_horror"

        style = STORY_TYPES[story_type]

        logger.info(f"📝 Generating CLEAN script (no image prompts)")
        logger.info(f"   Topic: {topic}")
        logger.info(f"   Type: {style['name']}")
        logger.info(f"   Duration: {duration_minutes} minutes")

        # Build prompt
        prompt = self._build_clean_script_prompt(
            topic=topic,
            style=style,
            template=template,
            research_data=research_data,
            duration_minutes=duration_minutes
        )

        # Generate with retry
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                logger.info(f"   Attempt {attempt + 1}/{max_attempts}...")

                response = self.model.generate_content(prompt)
                script_text = response.text

                # Clean output
                script_text = self._clean_script(script_text)

                # Validate
                if len(script_text) < 500:
                    logger.warning("   Script too short, retrying...")
                    continue

                logger.success(f"✅ Generated {len(script_text)} characters")
                logger.info(f"   Words: {len(script_text.split())}")

                return {
                    "script": script_text,
                    "story_type": story_type,
                    "word_count": len(script_text.split()),
                    "character_count": len(script_text),
                    "used_template": template is not None,
                    "used_research": research_data is not None,
                }

            except Exception as e:
                logger.error(f"   Attempt {attempt + 1} failed: {e}")
                if attempt == max_attempts - 1:
                    raise

        raise Exception("Failed to generate script after all attempts")

    def _build_clean_script_prompt(
        self,
        topic: str,
        style: Dict,
        template: Optional[Dict],
        research_data: Optional[str],
        duration_minutes: int
    ) -> str:
        """Build prompt for CLEAN script generation (NO image prompts)"""

        target_words = duration_minutes * 150  # 150 words per minute

        style_name = style.get('name', 'story')
        style_desc = style.get('description', 'engaging narrative')
        style_tone = style.get('tone', 'compelling')
        style_pacing = style.get('pacing', 'medium')

        prompt = f"""You are a MASTER storyteller creating a {style_name} for professional YouTube video narration.

🎯 CRITICAL REQUIREMENTS:

TOPIC: {topic}
DURATION: {duration_minutes} minutes
TARGET: EXACTLY {target_words} words (150 words per minute)
TYPE: {style_desc}
TONE: {style_tone}
PACING: {style_pacing}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ CRITICAL: PURE SCRIPT ONLY - NO IMAGE DESCRIPTIONS!

This script will be converted to VOICE NARRATION using Text-to-Speech.
DO NOT include any image descriptions, visual prompts, or camera directions.
DO NOT write "IMAGE:", "SCENE:", or any technical annotations.
ONLY write the narrative text that will be spoken aloud!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎬 NARRATIVE EXCELLENCE:
✅ PRESENT TENSE ONLY ("I walk" not "I walked")
✅ FIRST PERSON for immersion ("I", "my", "me")
✅ SHOW DON'T TELL ("my hands trembled" not "I was scared")
✅ USE ALL 5 SENSES in every paragraph
✅ SPECIFIC DETAILS > VAGUE ("1987 Ford F-150" not "a truck")
✅ ACTIVE VOICE (not passive)
✅ NO LABELS, NO HEADERS, NO IMAGE DESCRIPTIONS
✅ DIALOGUE WITH CONTRACTIONS ("don't", "can't")

🎭 EMOTIONAL DEPTH:
✅ INTERNAL THOUGHTS - Show my mind
✅ VISCERAL REACTIONS - Physical feelings
✅ MICRO-DETAILS - Small observations
✅ EMOTIONAL WAVES - Vary intensity
✅ PACING RHYTHM - Mix sentence lengths:
   - Short. Punchy. Dramatic.
   - Longer flowing sentences that build momentum.
   - Then short. Impact.

💬 DIALOGUE MASTERY:
✅ Use CONTRACTIONS naturally
✅ REALISTIC speech patterns
✅ CHARACTER VOICE (each person talks differently)

🔥 HOOK (First 25-30 words):
✅ IMMEDIATELY grab attention
✅ Create intrigue viewers CAN'T resist
✅ Use CONTRAST or TWIST
✅ Promise a story worth watching

📐 STRUCTURE:
【 HOOK 】(First 25-30 words) - Shocking/compelling opening
【 SETUP 】(~150-200 words) - Introduce character, location, context
【 RISING ACTION 】(Middle 60%) - Build tension in waves
【 CLIMAX 】(Peak 15%) - Everything changes, maximum impact
【 RESOLUTION 】(Final 10-15%) - Show aftermath, emotional landing

"""

        # Add research if available
        if research_data:
            prompt += f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 RESEARCH DATA (Use real facts):
{research_data}

⚠️ Base story on research facts above. Make it authentic.

"""

        # Add template instructions if available
        if template:
            template_hook = template.get('hook_example', '')
            template_tone = template.get('tone', ['engaging'])
            if isinstance(template_tone, list):
                template_tone = ', '.join(template_tone)

            prompt += f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ANALYZE THIS TEMPLATE:

Hook Example: "{template_hook}"
Tone: {template_tone}

LEARN the strategy and style, CREATE new content!
Use SAME quality level and structure, but NEW story.

"""

        prompt += f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 YOUR MISSION:

Write EXACTLY {target_words} words of EXTRAORDINARY quality!

MANDATORY REQUIREMENTS:
✅ Present tense, first person throughout
✅ All 5 senses in EVERY paragraph
✅ Emotional, visceral, deeply engaging
✅ Perfect for VOICE narration (read-aloud friendly)
✅ Hook that IMMEDIATELY grabs attention
✅ Satisfying, memorable ending
✅ Professional story structure

⚠️ CRITICAL REMINDERS:
❌ NO image descriptions (those are generated separately!)
❌ NO "IMAGE:" lines
❌ NO "SCENE:" markers
❌ NO camera directions
❌ NO technical annotations
✅ ONLY the narrative text that will be spoken!

🏆 QUALITY GOAL: Create a script so compelling that:
- Viewers can't stop listening
- They FEEL the emotions
- They SEE the scenes in their mind
- They remember it after watching
- They share it with others
- They subscribe for more

NOW generate the complete {target_words}-word script.
NO preamble, NO commentary - JUST the spoken narrative!
"""

        return prompt

    def _clean_script(self, text: str) -> str:
        """Remove any technical markers or XML tags"""
        # Remove XML/SSML tags
        text = re.sub(r'<[^>]*>', '', text)
        # Remove any IMAGE: lines that might have snuck in
        text = re.sub(r'IMAGE:.*?(?:\n|$)', '', text, flags=re.IGNORECASE)
        # Remove SCENE: markers
        text = re.sub(r'SCENE:.*?(?:\n|$)', '', text, flags=re.IGNORECASE)
        # Remove special characters
        text = re.sub(r'&[a-z]+;', '', text)
        text = re.sub(r'\[\[.*?\]\]', '', text)
        # Clean up extra whitespace
        text = re.sub(r'\n\n\n+', '\n\n', text)
        return text.strip()

    def generate_image_prompts(
        self,
        script: str,
        topic: str,
        story_type: str,
        num_images: int = 10
    ) -> List[str]:
        """
        Generate image prompts SEPARATELY from script
        Takes clean script and creates N visual prompts for SDXL
        """

        logger.info(f"🎨 Generating {num_images} image prompts from script")

        if story_type not in STORY_TYPES:
            story_type = "scary_horror"

        style = STORY_TYPES[story_type]

        prompt = f"""You are an expert visual director creating image prompts for AI image generation.

🎯 TASK: Analyze this script and create {num_images} UNIQUE, CINEMATIC image prompts.

📝 SCRIPT:
{script[:2000]}...

🎬 STORY INFO:
Topic: {topic}
Type: {style.get('name', 'story')}
Tone: {style.get('tone', 'compelling')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ CRITICAL REQUIREMENTS FOR EACH IMAGE PROMPT:

1. TOPIC RELEVANCE: MUST include "{topic}" elements
2. LENGTH: 25-35 words EXACTLY
3. CINEMATIC: Describe like a movie scene
4. SPECIFIC: Exact lighting, mood, objects, actions
5. UNIQUE: All {num_images} images must be DIFFERENT
6. QUALITY: High detail, professional composition

🎨 SHOT VARIETY - Use different types:
- Wide establishing shots
- Medium close-ups
- Dramatic angles
- Intimate close-ups
- Environmental wides
- Character focus shots
- Detail shots
- Tension-building shots
- Climactic moments
- Resolution shots

📐 FORMAT (CRITICAL):
Return EXACTLY {num_images} prompts, one per line, like this:

1. [25-35 word detailed visual description]
2. [25-35 word detailed visual description]
...

EXAMPLE FORMAT (for alien topic):
1. Silver-skinned alien with large dark eyes examining earth technology in dimly lit laboratory, glowing instruments, sci-fi atmosphere, dramatic side lighting, medium close-up, cinematic composition, high detail, photorealistic
2. Crashed spaceship in desert at night, stars visible, alien hieroglyphics glowing blue on hull, wide establishing shot, moody atmosphere, cinematic lighting, professional photography, 8k quality

NOW create {num_images} UNIQUE image prompts based on the script above.
Each prompt MUST:
✅ Relate to script content
✅ Include "{topic}" elements
✅ Be 25-35 words
✅ Be visually distinct from others
✅ Be cinematic and detailed

Return ONLY the numbered list of {num_images} prompts, nothing else!
"""

        try:
            response = self.model.generate_content(prompt)
            prompts_text = response.text

            # Extract numbered prompts
            lines = prompts_text.strip().split('\n')
            prompts = []

            for line in lines:
                # Remove numbering and clean
                clean_line = re.sub(r'^\d+\.\s*', '', line).strip()
                if clean_line and len(clean_line) > 20:
                    prompts.append(clean_line)

            # Ensure we have exactly num_images
            if len(prompts) < num_images:
                logger.warning(f"   ⚠️ Only generated {len(prompts)}/{num_images} prompts")

            prompts = prompts[:num_images]  # Take only what we need

            logger.success(f"✅ Generated {len(prompts)} image prompts")

            return prompts

        except Exception as e:
            logger.error(f"   ❌ Failed to generate image prompts: {e}")
            # Fallback: Generate basic prompts
            return [f"{topic}, cinematic scene {i+1}, professional photography, high detail"
                    for i in range(num_images)]


# Create singleton instance
clean_script_generator = CleanScriptGenerator()
