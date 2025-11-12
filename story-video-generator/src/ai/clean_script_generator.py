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
import time

from config.settings import GEMINI_SETTINGS
from config.story_types import STORY_TYPES
from src.utils.api_manager import api_manager
from src.utils.logger import logger
from src.utils.gemini_rate_limiter import rate_limiter  # ✅ NEW: Rate limiter


class CleanScriptGenerator:
    """Generate HIGH-QUALITY scripts WITHOUT image prompts for perfect TTS"""

    def __init__(self):
        # ✅ Get all Gemini API keys for rotation
        self.api_keys = api_manager.get_all_gemini_keys()
        if not self.api_keys:
            raise ValueError("Gemini API keys required!")

        # Configure with first key initially
        genai.configure(api_key=self.api_keys[0])
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
        print(f"   API Keys: {len(self.api_keys)} keys with automatic rotation")
        print(f"   Focus: HIGH-QUALITY scripts for voice narration")
        print(f"   NO image prompts in script (generated separately)")

    def generate_script_and_images_batch(
        self,
        topic: str,
        story_type: str,
        num_images: int = 10,
        template: Optional[Dict] = None,
        research_data: Optional[str] = None,
        duration_minutes: int = 10,
    ) -> Dict:
        """
        🚀 BATCHED GENERATION - Script + Image Prompts in ONE API call!
        Uses only 1 request instead of 2, DOUBLING our capacity!

        Returns:
            Dict with 'script', 'image_prompts', 'word_count', etc.
        """

        if story_type not in STORY_TYPES:
            logger.warning(f"Unknown story type: {story_type}")
            story_type = "scary_horror"

        style = STORY_TYPES[story_type]

        logger.info(f"🚀 BATCHED generation (script + {num_images} images in 1 call)")
        logger.info(f"   Topic: {topic}")
        logger.info(f"   Type: {style['name']}")
        logger.info(f"   Duration: {duration_minutes} minutes")

        # Build BATCHED prompt
        prompt = self._build_batched_prompt(
            topic=topic,
            style=style,
            num_images=num_images,
            template=template,
            research_data=research_data,
            duration_minutes=duration_minutes
        )

        # ✅ Generate with retry + SMART API key selection + rate limiting
        max_attempts = len(self.api_keys) * 2
        for attempt in range(max_attempts):
            try:
                # 🎯 SMART KEY SELECTION: Pick key with most capacity available
                best_key_idx, reason = rate_limiter.get_best_available_key(self.api_keys)
                api_key = self.api_keys[best_key_idx]
                logger.info(f"   Attempt {attempt + 1}/{max_attempts} (Key {best_key_idx+1}: ...{api_key[-8:]})...")
                if attempt == 0:  # Show reasoning on first attempt
                    logger.info(f"   📊 Key selection: {reason}")

                # ✅ Rate limiting
                rate_limiter.wait_if_needed(api_key)

                # Reconfigure with new key
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name=GEMINI_SETTINGS['model'],
                    generation_config={
                        "temperature": 0.75,
                        "top_p": 0.92,
                        "top_k": 50,
                        "max_output_tokens": 16384,
                    }
                )

                response = model.generate_content(prompt)
                result_text = response.text

                # Parse the batched response
                parsed = self._parse_batched_response(result_text, num_images)

                if not parsed['script'] or len(parsed['script']) < 500:
                    logger.warning("   Script too short, retrying...")
                    continue

                if not parsed['image_prompts'] or len(parsed['image_prompts']) < num_images // 2:
                    logger.warning("   Not enough image prompts, retrying...")
                    continue

                # ✅ Success - reset failure counter
                rate_limiter.reset_failures()

                logger.success(f"✅ BATCH: {len(parsed['script'])} chars + {len(parsed['image_prompts'])} images in 1 call!")
                logger.info(f"   Used API Key: ...{api_key[-8:]}")

                return parsed

            except Exception as e:
                # ✅ Handle 429 rate limit errors
                if rate_limiter.is_rate_limit_error(e):
                    wait_time = rate_limiter.handle_rate_limit_error(e, attempt, api_key)
                    logger.warning(f"   ⏳ Rate limit hit - waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)

                    if attempt < max_attempts - 1:
                        logger.info(f"   🔄 Retrying with next API key after cooldown...")
                        continue

                logger.error(f"   Attempt {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    logger.info(f"   🔄 Trying next API key...")
                    time.sleep(2)
                else:
                    raise

        raise Exception("Failed to generate batched content after all attempts")

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

        ⚠️ DEPRECATED: Use generate_script_and_images_batch() for 2x speed!
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

        # ✅ Generate with retry + SMART API key selection + rate limiting
        max_attempts = len(self.api_keys) * 2  # Try each key twice (now 8 attempts with 4 keys)
        for attempt in range(max_attempts):
            try:
                # 🎯 SMART KEY SELECTION: Pick key with most capacity available
                best_key_idx, reason = rate_limiter.get_best_available_key(self.api_keys)
                api_key = self.api_keys[best_key_idx]
                logger.info(f"   Attempt {attempt + 1}/{max_attempts} (Key {best_key_idx+1}: ...{api_key[-8:]})...")

                # ✅ Rate limiting: wait if making requests too quickly
                rate_limiter.wait_if_needed(api_key)

                # Reconfigure with new key
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name=GEMINI_SETTINGS['model'],
                    generation_config={
                        "temperature": 0.75,
                        "top_p": 0.92,
                        "top_k": 50,
                        "max_output_tokens": 16384,
                    }
                )

                response = model.generate_content(prompt)
                script_text = response.text

                # Clean output
                script_text = self._clean_script(script_text)

                # Validate
                if len(script_text) < 500:
                    logger.warning("   Script too short, retrying with next key...")
                    continue

                # ✅ Success - reset failure counter
                rate_limiter.reset_failures()

                logger.success(f"✅ Generated {len(script_text)} characters")
                logger.info(f"   Words: {len(script_text.split())}")
                logger.info(f"   Used API Key: ...{api_key[-8:]}")

                return {
                    "script": script_text,
                    "story_type": story_type,
                    "word_count": len(script_text.split()),
                    "character_count": len(script_text),
                    "used_template": template is not None,
                    "used_research": research_data is not None,
                }

            except Exception as e:
                error_str = str(e)

                # ✅ Handle 429 rate limit errors with automatic retry
                if rate_limiter.is_rate_limit_error(e):
                    wait_time = rate_limiter.handle_rate_limit_error(e, attempt, api_key)
                    logger.warning(f"   ⏳ Rate limit hit - waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)

                    # Don't switch keys immediately on rate limit - let cooldown work
                    if attempt < max_attempts - 1:
                        logger.info(f"   🔄 Retrying with next API key after cooldown...")
                        continue

                # Other errors
                logger.error(f"   Attempt {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    logger.info(f"   🔄 Trying next API key...")
                    time.sleep(2)  # Small delay before next key
                else:
                    raise

        raise Exception("Failed to generate script after all attempts with all API keys")

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
        num_images: int = 10,
        start_key_offset: int = 2  # ✅ Start with different key to avoid collision with script gen
    ) -> List[str]:
        """
        Generate image prompts SEPARATELY from script
        Takes clean script and creates N visual prompts for SDXL

        Args:
            start_key_offset: Which key to start with (default 2 to avoid collision with script gen)
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

        # ✅ Try with SMART key selection + rate limiting
        max_attempts = len(self.api_keys) * 2  # Try each key twice (8 attempts with 4 keys)
        for attempt in range(max_attempts):
            try:
                # 🎯 SMART KEY SELECTION: Pick key with most capacity available
                best_key_idx, reason = rate_limiter.get_best_available_key(self.api_keys)
                api_key = self.api_keys[best_key_idx]
                logger.info(f"   Attempt {attempt + 1}/{max_attempts} (Key {best_key_idx+1}: ...{api_key[-8:]})...")

                # ✅ Rate limiting: wait if making requests too quickly
                rate_limiter.wait_if_needed(api_key)

                # Reconfigure with new key
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name=GEMINI_SETTINGS['model'],
                    generation_config={
                        "temperature": 0.75,
                        "top_p": 0.92,
                        "top_k": 50,
                        "max_output_tokens": 8192,
                    }
                )

                response = model.generate_content(prompt)
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

                # ✅ Success - reset failure counter
                rate_limiter.reset_failures()

                logger.success(f"✅ Generated {len(prompts)} image prompts")
                logger.info(f"   Used API Key: ...{api_key[-8:]}")

                return prompts

            except Exception as e:
                # ✅ Handle 429 rate limit errors with automatic retry
                if rate_limiter.is_rate_limit_error(e):
                    wait_time = rate_limiter.handle_rate_limit_error(e, attempt, api_key)
                    logger.warning(f"   ⏳ Rate limit hit - waiting {wait_time:.1f}s...")
                    time.sleep(wait_time)

                    # Retry with next key after cooldown
                    if attempt < max_attempts - 1:
                        logger.info(f"   🔄 Retrying with next API key after cooldown...")
                        continue

                logger.error(f"   ❌ Attempt {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    logger.info(f"   🔄 Trying next API key...")
                    time.sleep(2)
                    continue

        # All keys failed - fallback
        logger.warning(f"   ⚠️ All API keys failed. Using fallback method...")
        return [f"{topic}, cinematic scene {i+1}, professional photography, high detail"
                for i in range(num_images)]

    def _build_batched_prompt(
        self,
        topic: str,
        style: Dict,
        num_images: int,
        template: Optional[Dict],
        research_data: Optional[str],
        duration_minutes: int
    ) -> str:
        """Build BATCHED prompt that requests both script AND image prompts in ONE call"""

        target_words = duration_minutes * 150  # 150 words per minute
        style_name = style.get('name', 'story')
        style_desc = style.get('description', 'engaging narrative')
        style_tone = style.get('tone', 'compelling')
        style_pacing = style.get('pacing', 'medium')

        prompt = f"""You are a MASTER content creator. I need you to complete TWO tasks in this ONE request:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 1: Generate Script
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 REQUIREMENTS:
TOPIC: {topic}
DURATION: {duration_minutes} minutes
TARGET: EXACTLY {target_words} words (150 words per minute)
TYPE: {style_desc}
TONE: {style_tone}
PACING: {style_pacing}

⚠️ CRITICAL: PURE SCRIPT ONLY - NO IMAGE DESCRIPTIONS!
This will be converted to VOICE NARRATION using Text-to-Speech.
ONLY write the narrative text that will be spoken aloud!

🎬 NARRATIVE EXCELLENCE:
✅ PRESENT TENSE ONLY ("I walk" not "I walked")
✅ FIRST PERSON for immersion ("I", "my", "me")
✅ SHOW DON'T TELL ("my hands trembled" not "I was scared")
✅ USE ALL 5 SENSES in every paragraph
✅ SPECIFIC DETAILS > VAGUE ("1987 Ford F-150" not "a truck")
✅ ACTIVE VOICE (not passive)
✅ NO LABELS, NO HEADERS, NO IMAGE DESCRIPTIONS
✅ DIALOGUE WITH CONTRACTIONS ("don't", "can't")

🔥 HOOK (First 25-30 words):
✅ IMMEDIATELY grab attention
✅ Create intrigue viewers CAN'T resist
✅ Use CONTRAST or TWIST

📐 STRUCTURE:
【 HOOK 】(First 25-30 words) - Shocking/compelling opening
【 SETUP 】(~150-200 words) - Introduce character, location, context
【 RISING ACTION 】(Middle 60%) - Build tension in waves
【 CLIMAX 】(Peak 15%) - Everything changes, maximum impact
【 RESOLUTION 】(Final 10-15%) - Show aftermath, emotional landing

"""

        # Add research if available
        if research_data:
            prompt += f"""📚 RESEARCH DATA (Use real facts):
{research_data}

"""

        # Add template if available
        if template:
            template_hook = template.get('hook_example', '')
            template_tone = template.get('tone', ['engaging'])
            if isinstance(template_tone, list):
                template_tone = ', '.join(template_tone)

            prompt += f"""🎯 TEMPLATE TO LEARN FROM:
Hook Example: "{template_hook}"
Tone: {template_tone}

"""

        prompt += f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TASK 2: Generate {num_images} Image Prompts
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Create {num_images} UNIQUE, CINEMATIC image prompts based on the script you wrote above.

⚠️ REQUIREMENTS FOR EACH IMAGE PROMPT:
1. TOPIC RELEVANCE: MUST include "{topic}" elements
2. LENGTH: 25-35 words EXACTLY
3. CINEMATIC: Describe like a movie scene
4. SPECIFIC: Exact lighting, mood, objects, actions
5. UNIQUE: All {num_images} images must be DIFFERENT
6. QUALITY: High detail, professional composition

🎨 SHOT VARIETY - Use different types:
- Wide establishing shots, Medium close-ups, Dramatic angles
- Intimate close-ups, Environmental wides, Character focus shots
- Detail shots, Tension-building shots, Climactic moments

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT (CRITICAL - FOLLOW EXACTLY):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[SCRIPT_START]
[Write the complete {target_words}-word script here]
[SCRIPT_END]

[IMAGES_START]
1. [25-35 word detailed visual description]
2. [25-35 word detailed visual description]
3. [25-35 word detailed visual description]
...
{num_images}. [25-35 word detailed visual description]
[IMAGES_END]

NOW generate BOTH the script AND the {num_images} image prompts using the exact format above!
"""

        return prompt

    def _parse_batched_response(self, text: str, num_images: int) -> Dict:
        """Parse batched response to extract script and image prompts"""

        # Extract script between markers
        script_match = re.search(r'\[SCRIPT_START\](.*?)\[SCRIPT_END\]', text, re.DOTALL)
        if script_match:
            script = script_match.group(1).strip()
        else:
            # Fallback: try to find script before images section
            parts = re.split(r'\[IMAGES_START\]', text, maxsplit=1)
            script = parts[0].strip()

        # Clean script
        script = self._clean_script(script)

        # Extract image prompts between markers
        images_match = re.search(r'\[IMAGES_START\](.*?)\[IMAGES_END\]', text, re.DOTALL)
        if images_match:
            images_text = images_match.group(1).strip()
        else:
            # Fallback: try to find images section
            parts = re.split(r'\[IMAGES_START\]', text, maxsplit=1)
            if len(parts) > 1:
                images_text = parts[1].strip()
            else:
                images_text = ""

        # Parse numbered image prompts
        lines = images_text.split('\n')
        image_prompts = []

        for line in lines:
            # Remove numbering and clean
            clean_line = re.sub(r'^\d+\.\s*', '', line).strip()
            # Remove [IMAGES_END] if it appears
            clean_line = re.sub(r'\[IMAGES_END\]', '', clean_line).strip()
            if clean_line and len(clean_line) > 20:
                image_prompts.append(clean_line)

        # Ensure we have at least num_images//2
        if len(image_prompts) < num_images // 2:
            logger.warning(f"   Only parsed {len(image_prompts)}/{num_images} image prompts from batch")

        # Trim to requested amount
        image_prompts = image_prompts[:num_images]

        return {
            "script": script,
            "image_prompts": image_prompts,
            "story_type": "",  # Will be set by caller
            "word_count": len(script.split()),
            "character_count": len(script),
            "num_images": len(image_prompts),
            "used_template": False,  # Will be set by caller
            "used_research": False,  # Will be set by caller
        }


# Create singleton instance
clean_script_generator = CleanScriptGenerator()
