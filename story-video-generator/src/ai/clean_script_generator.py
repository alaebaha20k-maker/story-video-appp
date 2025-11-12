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
                "max_output_tokens": 8192,  # Within gemini-2.0-flash-exp limit
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

        ⚡ SMART CHUNKING for long scripts:
        - Checks SCRIPT_LENGTHS config to determine # of chunks needed
        - Splits long scripts into multiple API calls
        - Each chunk generates part of the script
        - Combines all chunks at the end

        Returns:
            Dict with 'script', 'image_prompts', 'word_count', etc.
        """

        if story_type not in STORY_TYPES:
            logger.warning(f"Unknown story type: {story_type}")
            story_type = "scary_horror"

        style = STORY_TYPES[story_type]

        # Calculate target characters and determine chunking strategy
        target_chars = duration_minutes * 150 * 5  # 150 words/min × 5 chars/word

        # 🚨 AGGRESSIVE CHUNKING to avoid rate limits
        # Even short videos need chunking to stay under API limits
        from config.settings import SCRIPT_LENGTHS
        num_chunks = 1

        if target_chars > 50000:  # 60+ min videos
            num_chunks = 4
        elif target_chars > 30000:  # 40+ min videos
            num_chunks = 3
        elif target_chars > 15000:  # 20+ min videos (INCLUDING 24-min!)
            num_chunks = 2
        else:  # 10-15 min videos only
            num_chunks = 1

        logger.info(f"📊 Target: {target_chars} chars ({duration_minutes} min) → {num_chunks} chunk{'s' if num_chunks > 1 else ''}")

        if num_chunks > 1:
            logger.info(f"📊 CHUNKED generation: {target_chars} chars = {num_chunks} chunks")
            return self._generate_script_chunked(
                topic=topic,
                style=style,
                num_images=num_images,
                template=template,
                research_data=research_data,
                duration_minutes=duration_minutes,
                num_chunks=num_chunks
            )

        # Single chunk generation (original batched method)
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
                        "max_output_tokens": 8192,  # Within gemini-2.0-flash-exp limit
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
                        "max_output_tokens": 8192,  # Within gemini-2.0-flash-exp limit
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

    def _generate_script_chunked(
        self,
        topic: str,
        style: Dict,
        num_images: int,
        template: Optional[Dict],
        research_data: Optional[str],
        duration_minutes: int,
        num_chunks: int
    ) -> Dict:
        """
        Generate LONG scripts in CHUNKS to respect API limits and quality
        Each chunk generates part of the story
        """

        logger.info(f"📝 Generating {duration_minutes}-min script in {num_chunks} chunks...")

        chunks_data = []
        chunk_duration = duration_minutes / num_chunks
        chunk_images = max(num_images // num_chunks, 3)  # At least 3 images per chunk

        for chunk_num in range(num_chunks):
            logger.info(f"\n🔄 Chunk {chunk_num + 1}/{num_chunks} ({chunk_duration:.1f} minutes)...")

            # Build chunk-specific prompt
            if chunk_num == 0:
                # First chunk: Opening + setup
                chunk_prompt = f"""CONTEXT: You're writing the BEGINNING of a {duration_minutes}-minute story.
Total story length: {num_chunks} chunks ({duration_minutes} minutes total)
This chunk: ~{chunk_duration:.0f} minutes (~{chunk_duration * 150:.0f} words)

YOUR TASK:
- Start with a POWERFUL HOOK (first 25-30 words) that grabs attention
- Establish the setting, character, and situation
- Build initial tension and intrigue
- End at a natural transition point (complete thought, not mid-sentence)

REMEMBER: Write seamless narrative. NO mention of "Part 1" or "first section"!
The listener won't know this is chunked - it should flow like one story."""

            elif chunk_num == num_chunks - 1:
                # Last chunk: Climax + resolution
                chunk_prompt = f"""CONTEXT: You're writing the ENDING of a {duration_minutes}-minute story.
Total story length: {num_chunks} chunks ({duration_minutes} minutes total)
This chunk: ~{chunk_duration:.0f} minutes (~{chunk_duration * 150:.0f} words)

YOUR TASK:
- Continue SEAMLESSLY from previous section (NO "finally" or "in conclusion")
- Build to the CLIMAX - the most intense, emotional peak
- Resolve the story with a satisfying, memorable ending
- Leave the listener feeling complete and satisfied

REMEMBER: Write seamless narrative. NO mention of "final part" or technical markers!
The listener won't know this is chunked - it should flow naturally."""

            else:
                # Middle chunks: Rising action
                chunk_prompt = f"""CONTEXT: You're writing the MIDDLE of a {duration_minutes}-minute story.
Total story length: {num_chunks} chunks ({duration_minutes} minutes total)
This chunk: ~{chunk_duration:.0f} minutes (~{chunk_duration * 150:.0f} words)

YOUR TASK:
- Continue SEAMLESSLY from previous section (NO "meanwhile" or "next")
- Build tension and develop the plot
- Deepen character emotions and stakes
- End at a natural transition point (complete thought, not mid-sentence)

REMEMBER: Write seamless narrative. NO mention of "middle section" or "continuation"!
The listener won't know this is chunked - it should flow like one story."""

            # Generate this chunk
            prompt = self._build_batched_prompt(
                topic=topic,
                style=style,
                num_images=chunk_images,
                template=template if chunk_num == 0 else None,  # Only use template for first chunk
                research_data=research_data if chunk_num == 0 else None,  # Only use research for first chunk
                duration_minutes=chunk_duration,
                chunk_instructions=chunk_prompt
            )

            # Generate with smart key selection
            max_attempts = len(self.api_keys) * 2
            chunk_generated = False

            for attempt in range(max_attempts):
                try:
                    best_key_idx, reason = rate_limiter.get_best_available_key(self.api_keys)
                    api_key = self.api_keys[best_key_idx]
                    logger.info(f"   Attempt {attempt + 1}/{max_attempts} (Key {best_key_idx+1}: ...{api_key[-8:]})...")

                    rate_limiter.wait_if_needed(api_key)

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

                    parsed = self._parse_batched_response(result_text, chunk_images)

                    if parsed['script'] and len(parsed['script']) > 200:
                        rate_limiter.reset_failures()
                        chunks_data.append(parsed)
                        logger.success(f"✅ Chunk {chunk_num + 1}: {len(parsed['script'])} chars, {len(parsed['image_prompts'])} images")
                        chunk_generated = True
                        break

                except Exception as e:
                    if rate_limiter.is_rate_limit_error(e):
                        wait_time = rate_limiter.handle_rate_limit_error(e, attempt, api_key)
                        logger.warning(f"   ⏳ Rate limit - waiting {wait_time:.1f}s...")
                        time.sleep(wait_time)
                        continue

                    logger.error(f"   Chunk {chunk_num + 1} attempt {attempt + 1} failed: {e}")
                    if attempt < max_attempts - 1:
                        time.sleep(2)
                        continue
                    else:
                        raise

            if not chunk_generated:
                raise Exception(f"Failed to generate chunk {chunk_num + 1} after all attempts")

        # Combine all chunks
        logger.info(f"\n🔗 Combining {num_chunks} chunks...")

        full_script = "\n\n".join([chunk['script'] for chunk in chunks_data])
        all_images = []
        for chunk in chunks_data:
            all_images.extend(chunk['image_prompts'])

        logger.success(f"✅ CHUNKED COMPLETE: {len(full_script)} chars total, {len(all_images)} images")

        return {
            "script": full_script,
            "image_prompts": all_images[:num_images],  # Trim to requested amount
            "story_type": style.get('name', 'story'),
            "word_count": len(full_script.split()),
            "character_count": len(full_script),
            "num_images": min(len(all_images), num_images),
            "used_template": template is not None,
            "used_research": research_data is not None,
        }

    def _build_batched_prompt(
        self,
        topic: str,
        style: Dict,
        num_images: int,
        template: Optional[Dict],
        research_data: Optional[str],
        duration_minutes: int,
        chunk_instructions: Optional[str] = None
    ) -> str:
        """Build BATCHED prompt that requests both script AND image prompts in ONE call"""

        target_words = duration_minutes * 150  # 150 words per minute
        style_name = style.get('name', 'story')
        style_desc = style.get('description', 'engaging narrative')
        style_tone = style.get('tone', 'compelling')
        style_pacing = style.get('pacing', 'medium')

        # Add chunk instructions if this is part of a chunked generation
        chunk_section = ""
        if chunk_instructions:
            chunk_section = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ CHUNKED GENERATION - CONTEXT ONLY (DO NOT INCLUDE IN SCRIPT):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 IMPORTANT CONTEXT (for AI only - NOT for output):

{chunk_instructions}

⚠️ CRITICAL: The above is CONTEXT ONLY!
- DO NOT write "Part 1", "Part 2", or any technical markers in the script
- DO NOT mention "first chunk", "this section", or "this part"
- The viewer will NEVER know this is chunked
- Write as if this is ONE CONTINUOUS story
- Start naturally, end naturally
- NO meta-commentary about story structure

The script you generate will be spoken aloud by Text-to-Speech.
Write ONLY pure narrative that flows naturally!

"""

        prompt = f"""You are a MASTER content creator. I need you to complete TWO tasks in this ONE request:

{chunk_section}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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

Create {num_images} UNIQUE, CINEMATIC image prompts that MATCH the script you wrote above.

🎯 CRITICAL: Images must FOLLOW the script's narrative flow!
- Image 1 = Opening scene (hook moment)
- Middle images = Follow story progression
- Final image = Climax or resolution moment
- Each image should represent a KEY MOMENT from the script

⚠️ REQUIREMENTS FOR EACH IMAGE PROMPT:
1. SCRIPT ACCURACY: Image must match the corresponding part of your script
2. TOPIC RELEVANCE: MUST include "{topic}" elements
3. LENGTH: 25-35 words EXACTLY
4. CINEMATIC: Describe like a movie scene
5. SPECIFIC: Exact lighting, mood, objects, actions
6. UNIQUE: All {num_images} images must be DIFFERENT
7. QUALITY: High detail, professional composition

🎨 SHOT VARIETY - Distribute these across {num_images} images:
- Opening: Wide establishing shot (sets the scene)
- Early: Medium shots (introduce character/situation)
- Middle: Dramatic angles, close-ups (build tension)
- Climax: Dynamic action shot or intense moment
- End: Emotional resolution shot

📐 EXAMPLE (for horror story):
1. "Abandoned Victorian mansion at twilight, broken windows, overgrown ivy, ominous dark clouds, eerie atmosphere, cinematic wide shot"
2. "Young woman's face illuminated by flickering candlelight in dark hallway, fear in eyes, shadows dancing, medium close-up"
3. "Ghostly figure standing at end of corridor, translucent form, cold blue lighting, dramatic perspective, horror atmosphere"

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
