"""
📝 ENHANCED SCRIPT GENERATOR V2 - With Template Analyzer Integration
Uses template analyzer to get structure, then generates matching scripts
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
from src.ai.template_analyzer import template_analyzer


class EnhancedScriptGeneratorV2:
    """Generate scripts using template analysis + main Gemini API"""

    def __init__(self):
        api_key = api_manager.get_key('gemini')
        if not api_key:
            raise ValueError("Gemini API key required!")

        # Configure main Gemini API for script generation
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

        logger.success("🏆 Enhanced Script Generator V2 initialized")
        logger.info("   Using: TWO separate Gemini APIs")
        logger.info("   Step 1: Template Analyzer (dedicated API)")
        logger.info("   Step 2: Script Generator (main API)")

    def generate_with_template(
        self,
        topic: str,
        story_type: str,
        template: Optional[str] = None,
        research_data: Optional[str] = None,
        duration_minutes: int = 5,
        num_scenes: int = 10,
        hook_intensity: str = 'medium',
        pacing: str = 'medium'
    ) -> Dict:
        """
        Generate script with template analysis

        Step 1: Analyze template (if provided) with dedicated API
        Step 2: Generate script using analysis + main API

        Args:
            topic: Video topic/title
            story_type: Type of story (scary_horror, etc)
            template: Optional example script to learn from
            research_data: Optional research/facts
            duration_minutes: Target duration
            num_scenes: Number of scenes
            hook_intensity: Hook intensity level
            pacing: Pacing style

        Returns:
            Dict with 'script' and 'scenes'
        """

        logger.info("📝 Generating script with template analysis (V2)")
        logger.info(f"   Topic: {topic}")
        logger.info(f"   Type: {story_type}")
        logger.info(f"   Template provided: {bool(template)}")
        logger.info(f"   Duration: {duration_minutes} min")
        logger.info(f"   Scenes: {num_scenes}")

        # STEP 1: Analyze template if provided
        template_analysis = None
        style_guide = ""

        if template:
            logger.info("\n🔍 STEP 1: Analyzing template...")
            template_analysis = template_analyzer.analyze_template(
                template_text=template,
                story_type=story_type
            )

            # Create style guide from analysis
            style_guide = template_analyzer.create_style_guide(template_analysis)

            logger.success("✅ Template analyzed!")
            logger.info(f"   Hook style: {template_analysis.get('hook_intensity', 'N/A')}")
            logger.info(f"   Pacing: {template_analysis.get('pacing_speed', 'N/A')}")
            logger.info(f"   Structure: {template_analysis.get('scene_pattern', 'N/A')[:50]}...")

        # STEP 2: Generate script using analysis
        logger.info("\n✍️ STEP 2: Generating script with analyzed style...")

        # Get story type info
        story_info = next((s for s in STORY_TYPES if s['id'] == story_type), None)
        story_name = story_info['name'] if story_info else story_type

        # Build generation prompt
        generation_prompt = self._build_generation_prompt(
            topic=topic,
            story_type=story_name,
            story_type_id=story_type,
            num_scenes=num_scenes,
            duration_minutes=duration_minutes,
            hook_intensity=hook_intensity if not template_analysis else template_analysis.get('hook_intensity', hook_intensity),
            pacing=pacing if not template_analysis else template_analysis.get('pacing_speed', pacing),
            style_guide=style_guide,
            research_data=research_data
        )

        # Generate with retries
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"   Attempt {attempt}/{max_attempts}...")

                response = self.model.generate_content(generation_prompt)
                script_text = response.text.strip()

                # Parse script
                script, scenes = self._parse_script(script_text, num_scenes)

                if script and len(script) > 200:
                    logger.success(f"✅ Script generated!")
                    logger.info(f"   Length: {len(script)} characters")
                    logger.info(f"   Words: ~{len(script.split())}")
                    logger.info(f"   Scenes: {len(scenes)}")

                    return {
                        'script': script,
                        'scenes': scenes,
                        'template_analysis': template_analysis,
                        'style_guide': style_guide
                    }

            except Exception as e:
                logger.warning(f"   Attempt {attempt} failed: {e}")
                if attempt == max_attempts:
                    raise

        raise RuntimeError("Failed to generate script after all attempts")

    def _build_generation_prompt(
        self,
        topic: str,
        story_type: str,
        story_type_id: str,
        num_scenes: int,
        duration_minutes: int,
        hook_intensity: str,
        pacing: str,
        style_guide: str,
        research_data: Optional[str] = None
    ) -> str:
        """Build the script generation prompt"""

        template_section = ""
        if style_guide:
            template_section = f"""
🎨 TEMPLATE STYLE GUIDE (FOLLOW EXACTLY):
{style_guide}

IMPORTANT: Your script MUST match the template's style, structure, and patterns exactly!
"""

        research_section = ""
        if research_data:
            research_section = f"""
📚 RESEARCH DATA TO INCORPORATE:
{research_data}

Use this information to make the story more authentic and detailed.
"""

        prompt = f"""
You are a professional YouTube script writer. Generate a {story_type} story script.

📝 REQUIREMENTS:
- Topic: {topic}
- Story Type: {story_type}
- Target Duration: {duration_minutes} minutes
- Number of Scenes: {num_scenes}
- Hook Intensity: {hook_intensity}
- Pacing: {pacing}

{template_section}

{research_section}

🎯 SCRIPT STRUCTURE:

1. **HOOK** (First 3-5 seconds):
   - Must grab attention IMMEDIATELY
   - Use {hook_intensity} intensity
   - Example techniques: shocking question, bold statement, mysterious reveal

2. **SCENES** ({num_scenes} scenes):
   - Each scene should be {duration_minutes * 60 / num_scenes:.0f} seconds
   - Build tension progressively
   - Use {pacing} pacing
   - Include vivid descriptions
   - Natural transitions

3. **CLIMAX** (Peak moment):
   - Highest tension point
   - Satisfying reveal or twist

4. **RESOLUTION** (Final scene):
   - Wrap up the story
   - Leave impact/emotion

📋 FORMATTING:
- Write in natural, spoken language (for narration)
- No markdown, asterisks, or special formatting
- No scene labels (just continuous narrative)
- No "IMAGE:" prompts
- ⚠️ ABSOLUTELY NO EMOJIS in the script text
- Total length: approximately {duration_minutes * 60 * 2.5:.0f} words

✍️ WRITING STYLE:
- Conversational and engaging
- Varied sentence lengths for rhythm
- Strong imagery and emotion
- Build suspense naturally
- Perfect for YouTube narration

🎬 GENERATE THE COMPLETE SCRIPT NOW:
"""

        return prompt

    def _parse_script(self, script_text: str, num_scenes: int) -> tuple:
        """Parse script and create scene markers"""

        # Clean script
        script = script_text.strip()

        # Remove any markdown
        script = re.sub(r'\*\*', '', script)
        script = re.sub(r'__', '', script)

        # ⚠️ REMOVE ALL EMOJIS (comprehensive pattern)
        # This removes all Unicode emoji characters
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            u"\U0001FA00-\U0001FA6F"  # Chess Symbols
            u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            u"\U00002600-\U000026FF"  # Miscellaneous Symbols
            u"\U00002700-\U000027BF"  # Dingbats
            "]+", flags=re.UNICODE)
        script = emoji_pattern.sub('', script)

        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', script)

        # Create scene markers
        sentences_per_scene = max(1, len(sentences) // num_scenes)

        scenes = []
        for i in range(num_scenes):
            start_idx = i * sentences_per_scene
            end_idx = start_idx + sentences_per_scene if i < num_scenes - 1 else len(sentences)

            scene_text = ' '.join(sentences[start_idx:end_idx])

            if scene_text:
                scenes.append({
                    'scene_number': i + 1,
                    'content': scene_text,
                    'prompt': '',  # Image prompts generated separately
                    'image_description': ''
                })

        return script, scenes


# Singleton instance
enhanced_script_generator_v2 = EnhancedScriptGeneratorV2()


# Test function
if __name__ == '__main__':
    print("\n🧪 Testing Enhanced Script Generator V2...\n")

    example_template = """
I never believed in ghosts. Until the night I saw my reflection blink.

It started three weeks ago. I moved into an old Victorian house on Maple Street.
    """

    try:
        result = enhanced_script_generator_v2.generate_with_template(
            topic="A haunted mirror that steals souls",
            story_type="scary_horror",
            template=example_template,
            research_data=None,
            duration_minutes=2,
            num_scenes=5,
            hook_intensity="extreme",
            pacing="fast"
        )

        print("\n✅ GENERATION SUCCESS!")
        print(f"\nScript length: {len(result['script'])} characters")
        print(f"Scenes: {len(result['scenes'])}")
        print(f"\nFirst 200 characters:\n{result['script'][:200]}...")

        if result.get('template_analysis'):
            print(f"\nTemplate analyzed: ✅")
            print(f"Hook style: {result['template_analysis'].get('hook_intensity')}")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
