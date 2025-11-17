"""
📝 GEMINI SERVER 1 - Script Generation ONLY
Dedicated to generating high-quality scripts
Does NOT analyze templates (Server 0 handles that)
Does NOT generate image prompts (Server 2 handles that)
"""

import google.generativeai as genai
from typing import Dict, Optional
import re

from config.settings import GEMINI_SETTINGS
from config.story_types import STORY_TYPES
from src.utils.api_manager import api_manager
from src.utils.logger import logger


class GeminiServer1:
    """
    Gemini Server 1 - Dedicated to script generation ONLY
    Does NOT generate image prompts - that's Server 2's job
    """

    def __init__(self):
        api_key = api_manager.get_key('gemini')
        if not api_key:
            raise ValueError("Gemini Server 1 requires API key!")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config={
                "temperature": 0.75,
                "top_p": 0.92,
                "top_k": 50,
                "max_output_tokens": 16384,
            }
        )

        print(f"✅ Gemini Server 1 initialized")
        print(f"   Model: gemini-2.0-flash-exp")
        print(f"   Purpose: Script generation (NO image prompts)")

    def generate_script_from_template(
        self,
        topic: str,
        story_type: str,
        template: Optional[Dict],
        duration_minutes: int,
        num_scenes: int
    ) -> str:
        """
        Generate ONLY the script (no image prompts)
        Server 2 will handle image prompts separately

        CHUNKING: If script is too long (>10 min), splits into chunks
        and generates each separately, then merges seamlessly

        Args:
            topic: Story topic
            story_type: Type of story
            template: Optional template structure learned from example
            duration_minutes: Video duration
            num_scenes: Number of scenes (for pacing)

        Returns:
            High-quality script text ONLY
        """

        logger.info(f"\n📝 Gemini Server 1: Generating script...")
        logger.info(f"   Topic: {topic}")
        logger.info(f"   Type: {story_type}")
        logger.info(f"   Duration: {duration_minutes} min")
        logger.info(f"   Scenes: {num_scenes}")
        logger.info(f"   Template: {'Yes' if template else 'No'}")

        # Calculate target word count (150 words/min for narration)
        target_words = duration_minutes * 150

        # Check if chunking needed for long scripts (>10 min = 1500 words)
        CHUNK_THRESHOLD = 1500  # words (10 minutes)

        if target_words > CHUNK_THRESHOLD:
            logger.info(f"   🔪 Long script detected - using chunked generation")
            return self._generate_in_chunks(
                topic, story_type, template, target_words, num_scenes, duration_minutes
            )
        else:
            logger.info(f"   ✅ Standard generation (within limits)")
            return self._generate_single(
                topic, story_type, template, target_words, num_scenes, duration_minutes
            )

    def _generate_single(
        self,
        topic: str,
        story_type: str,
        template: Optional[Dict],
        target_words: int,
        num_scenes: int,
        duration_minutes: int
    ) -> str:
        """
        Generate script in a single call (for scripts under 1500 words / 10 min)
        """
        # Build prompt
        prompt = self._build_script_prompt(
            topic, story_type, template, target_words, num_scenes, duration_minutes
        )

        try:
            response = self.model.generate_content(prompt)

            if not response or not response.text:
                raise Exception("Empty response from Gemini Server 1")

            script = response.text.strip()

            logger.success(f"✅ Script generated: {len(script)} characters, ~{len(script.split())} words")

            return script

        except Exception as e:
            logger.error(f"❌ Gemini Server 1 error: {e}")
            raise

    def _generate_in_chunks(
        self,
        topic: str,
        story_type: str,
        template: Optional[Dict],
        target_words: int,
        num_scenes: int,
        duration_minutes: int
    ) -> str:
        """
        Generate a long script in chunks to avoid API token limits

        Strategy:
        1. Split into 3 parts: Beginning (25%), Middle (50%), End (25%)
        2. Generate each chunk with clear instructions for seamless flow
        3. Merge chunks intelligently with smooth transitions
        """
        logger.info(f"   📊 Target: {target_words} words")
        logger.info(f"   📊 Chunking into 3 parts...")

        # Calculate word targets for each chunk
        beginning_words = int(target_words * 0.25)
        middle_words = int(target_words * 0.50)
        end_words = int(target_words * 0.25)

        # Calculate scenes per chunk
        beginning_scenes = int(num_scenes * 0.25)
        middle_scenes = int(num_scenes * 0.50)
        end_scenes = int(num_scenes * 0.25)

        logger.info(f"   📊 Chunk 1 (Beginning): {beginning_words} words, {beginning_scenes} scenes")
        logger.info(f"   📊 Chunk 2 (Middle): {middle_words} words, {middle_scenes} scenes")
        logger.info(f"   📊 Chunk 3 (End): {end_words} words, {end_scenes} scenes")

        try:
            # Generate beginning chunk (hook + setup)
            logger.info(f"   🔄 Generating BEGINNING chunk...")
            chunk_beginning = self._generate_chunk(
                topic,
                story_type,
                template,
                beginning_words,
                beginning_scenes,
                duration_minutes,
                "beginning",
                "Start with a powerful hook and establish the setup. End at a point where tension is building.",
                None  # No previous chunk
            )

            # Generate middle chunk (rising action + climax build)
            logger.info(f"   🔄 Generating MIDDLE chunk...")
            chunk_middle = self._generate_chunk(
                topic,
                story_type,
                template,
                middle_words,
                middle_scenes,
                duration_minutes,
                "middle",
                "Continue from the setup, build rising action and tension. Move toward the climax.",
                chunk_beginning[-300:]  # Last 300 chars for context
            )

            # Generate end chunk (climax + resolution)
            logger.info(f"   🔄 Generating END chunk...")
            chunk_end = self._generate_chunk(
                topic,
                story_type,
                template,
                end_words,
                end_scenes,
                duration_minutes,
                "end",
                "Deliver the climax and provide a satisfying resolution. End the story powerfully.",
                chunk_middle[-300:]  # Last 300 chars for context
            )

            # Merge chunks seamlessly
            logger.info(f"   🔀 Merging chunks...")
            merged_script = self._merge_script_chunks(
                chunk_beginning,
                chunk_middle,
                chunk_end
            )

            logger.success(f"✅ Chunked script generated!")
            logger.info(f"   Total: {len(merged_script)} chars, ~{len(merged_script.split())} words")
            logger.info(f"   Chunks merged: 3")

            return merged_script

        except Exception as e:
            logger.error(f"❌ Gemini Server 1: Chunked generation error: {e}")
            raise

    def _generate_chunk(
        self,
        topic: str,
        story_type: str,
        template: Optional[Dict],
        target_words: int,
        num_scenes: int,
        duration_minutes: int,
        chunk_position: str,
        special_instruction: str,
        previous_chunk_context: Optional[str]
    ) -> str:
        """
        Generate a single chunk of a long script
        """
        # Calculate duration for this chunk proportionally
        chunk_duration = int(duration_minutes * (target_words / (duration_minutes * 150)))

        prompt = self._build_script_prompt(
            topic, story_type, template, target_words, num_scenes, chunk_duration
        )

        # Add chunk-specific instructions
        chunk_instruction = f"""

CHUNK POSITION: {chunk_position.upper()}
{special_instruction}

"""
        # Add context from previous chunk for smooth transition
        if previous_chunk_context:
            chunk_instruction += f"""PREVIOUS CHUNK ENDING (for context):
...{previous_chunk_context}

Continue naturally from this point. DO NOT repeat this text.
"""

        prompt += chunk_instruction

        response = self.model.generate_content(prompt)
        if not response or not response.text:
            raise Exception(f"Empty response for {chunk_position} chunk")

        return response.text.strip()

    def _merge_script_chunks(
        self,
        beginning: str,
        middle: str,
        end: str
    ) -> str:
        """
        Merge script chunks seamlessly
        Simply concatenate with paragraph breaks
        """
        # Add paragraph breaks between chunks for natural flow
        merged = beginning + "\n\n" + middle + "\n\n" + end
        return merged

    def _build_script_prompt(
        self,
        topic: str,
        story_type: str,
        template: Optional[Dict],
        target_words: int,
        num_scenes: int,
        duration_minutes: int
    ) -> str:
        """Build the prompt for script generation"""

        if story_type not in STORY_TYPES:
            story_type = "scary_horror"

        style = STORY_TYPES[story_type]

        # Base prompt
        prompt = f"""You are a professional script writer for viral YouTube videos.

TASK: Write a {target_words}-word script for a {duration_minutes}-minute video.

TOPIC: {topic}

STORY TYPE: {style['name']}
- Tone: {style['tone']}
- Pacing: {style['pacing']}
- Atmosphere: {', '.join(style.get('atmosphere', ['engaging']))}

"""

        # Add template structure if provided
        if template:
            prompt += f"""
STRUCTURE TEMPLATE (Learn from this example):
- Hook Style: {template.get('hookStyle', 'dramatic')}
- Hook Example: "{template.get('hookExample', '')}"
- Opening: {template.get('setupLength', 20)}% of story
- Rising Action: {template.get('riseLength', 40)}% of story
- Climax: {template.get('climaxLength', 30)}% of story
- Conclusion: {template.get('endLength', 10)}% of story
- Tone: {', '.join(template.get('tone', ['engaging']))}
- Key Patterns: {', '.join(template.get('keyPatterns', []))}

CREATE A NEW UNIQUE HOOK in the same style (don't copy the example!).
"""

        prompt += f"""
REQUIREMENTS:

1. **LENGTH: EXACTLY {target_words} words** ({duration_minutes} minutes at 150 words/min)

2. **STRUCTURE:**
   - Powerful hook (first 2-3 sentences)
   - {num_scenes} distinct story beats/scenes
   - Clear beginning, middle, climax, end
   - Satisfying conclusion

3. **WRITING STYLE:**
   - First-person narrative ("I saw...", "I felt...")
   - ALL 5 senses in every paragraph (sight, sound, smell, taste, touch)
   - Internal thoughts and emotions
   - Varied sentence lengths (mix short and long)
   - Read-aloud friendly (natural pauses, rhythm)

4. **QUALITY MARKERS:**
   - Emotional depth (make readers FEEL)
   - Vivid sensory details (show, don't tell)
   - Authentic dialogue (if any)
   - Unexpected twists or revelations
   - Strong visual imagery

5. **PACING:**
   - Build tension gradually
   - Peak at climax
   - Satisfying resolution

6. **VOICE OPTIMIZATION:**
   - Natural speaking rhythm
   - Strategic pauses (commas, periods)
   - Emphasis through repetition
   - Avoid tongue-twisters

7. **DO NOT:**
   - Include image prompts (Server 2 will generate those)
   - Add stage directions or camera notes
   - Use markdown formatting
   - Include word count in output

OUTPUT FORMAT:
[Start directly with the hook - no title, no labels, just the story]

Write the {target_words}-word script now:"""

        return prompt

    # ═══════════════════════════════════════════════════════════════
    # NOTE: Template analysis removed from Server 1
    # ═══════════════════════════════════════════════════════════════
    # Server 0 (gemini_server_0.py) handles ALL template analysis
    # Server 1 is dedicated to script generation ONLY
    # This separation prevents quota conflicts and improves clarity
    # ═══════════════════════════════════════════════════════════════


# Global instance
gemini_server_1 = GeminiServer1()
