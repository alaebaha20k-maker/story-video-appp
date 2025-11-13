"""
📝 ENHANCED SCRIPT GENERATOR - With Example Template + Research
Learns from user examples to generate high-quality scripts
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
from src.research.fact_searcher import fact_searcher
from src.utils.gemini_rate_limiter import rate_limiter  # ✅ Rate limiter
from src.utils.chunk_config import (  # ✅ NEW: Optimal chunking system
    get_optimal_chunk_config,
    estimate_target_length,
    get_chunk_section_goal,
    should_add_ending_requirements
)


def extract_last_sentences(text: str, num_sentences: int = 8) -> str:
    """
    Extract last N sentences from text for seamless continuation.

    This keeps prompts lean by only passing essential context from previous chunk.
    Gemini doesn't need the entire previous chunk - just enough context to continue smoothly.

    Args:
        text: The text to extract from
        num_sentences: Number of sentences to extract (default: 8)

    Returns:
        String containing the last N sentences
    """
    # Split on sentence boundaries
    sentences = re.split(r'[.!?]+', text)

    # Filter out very short sentences and clean them
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    if len(sentences) <= num_sentences:
        # Text is short enough, return as is
        return text

    # Get last N sentences
    last_sentences = sentences[-num_sentences:]

    # Rejoin with periods
    return '. '.join(last_sentences) + '.'


class EnhancedScriptGenerator:
    """Generate ULTIMATE quality scripts using Gemini AI with enhanced prompts!"""
    
    # 🏆 EXAMPLE HOOKS - Gemini will LEARN from these and create NEW ones!
    EXAMPLE_HOOKS = [
        # Horror/Scary
        "I never believed my sister could come back from the dead. Until I answered her call.",
        "The thing wearing my father's face sat down at the dinner table. Nobody else seemed to notice.",
        "I found my daughter's diary. The last entry was dated three years after she disappeared.",
        
        # Romance/Emotional
        "I fell in love with my best friend the moment she smiled at me. Three years too late.",
        "The letter said 'I never stopped loving you.' It arrived ten years after his funeral.",
        "She said yes. I said nothing. Because I couldn't remember proposing.",
        
        # Mystery/Thriller
        "The detective asked about my alibi. I had one. For a murder that hasn't happened yet.",
        "Every morning I wake up, it's the same day. Except one small thing is always different.",
        "The photo showed me at a place I've never been. With people I've never met. Yesterday.",
        
        # Documentary/Real
        "What they don't teach about the pyramids changes everything we thought we knew.",
        "I discovered a secret that's been hiding in plain sight for 4,000 years.",
        "The evidence was always there. We just weren't looking at it correctly.",
    ]
    
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
                "temperature": 0.75,  # ✅ Balanced creativity
                "top_p": 0.92,  # ✅ Tighter control for coherence
                "top_k": 50,  # ✅ Better vocabulary variety
                "max_output_tokens": 8192,  # ✅ Within free tier limits
            }
        )
        self.character_names = []

        print(f"🏆 Enhanced Script Generator (Gemini 2.0 Flash) initialized")
        print(f"   Model: gemini-2.0-flash-exp (FREE tier)")
        print(f"   API Keys: {len(self.api_keys)} keys with automatic rotation")
        print(f"   Max tokens: 8,192 per request")
        print(f"   Features: Character consistency, no-labels, seamless flow")
    
    def generate_with_template(
        self,
        topic: str,
        story_type: str,
        template: Optional[Dict] = None,
        research_data: Optional[str] = None,
        duration_minutes: int = 10,
        num_scenes: int = 10,
    ) -> Dict:
        """
        Generate script using template structure
        Templates make Gemini replicate quality of example scripts
        """
        
        if story_type not in STORY_TYPES:
            logger.warning(f"Unknown story type: {story_type}")
            story_type = "scary_horror"
        
        style = STORY_TYPES[story_type]
        
        logger.info(f"📝 Generating script with template")
        logger.info(f"   Topic: {topic}")
        logger.info(f"   Type: {style['name']}")
        logger.info(f"   Template provided: {template is not None}")
        logger.info(f"   Research data: {research_data is not None}")
        
        # Get research if documentary type
        if not research_data and story_type in ["historical_documentary", "true_crime", "biographical_life"]:
            logger.info(f"🔍 Fetching research for {topic}...")
            research_result = fact_searcher.search_facts(topic, story_type)
            research_data = research_result.get("research_data", "")
        
        # Build prompt with template
        prompt = self._build_template_prompt(
            topic=topic,
            style=style,
            template=template,
            research_data=research_data,
            duration_minutes=duration_minutes,
            num_scenes=num_scenes
        )
        
        # ✅ Generate with retry + automatic API key rotation + rate limiting
        max_attempts = len(self.api_keys) * 2  # Try each key twice (8 attempts with 4 keys)
        for attempt in range(max_attempts):
            try:
                # ✅ Rotate API key for each attempt
                api_key = self.api_keys[attempt % len(self.api_keys)]
                logger.info(f"   Attempt {attempt + 1}/{max_attempts} (Key: ...{api_key[-8:]})...")

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
                        "max_output_tokens": 8192,  # ✅ Free tier limit
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

                # Extract metadata
                self.character_names = self._extract_characters(script_text)
                scenes = self._parse_scenes(script_text, num_scenes)

                # ✅ Success - reset failure counter
                rate_limiter.reset_failures()

                logger.success(f"✅ Generated {len(script_text)} characters")
                logger.info(f"   Words: {len(script_text.split())}")
                logger.info(f"   Characters: {', '.join(self.character_names[:3])}")
                logger.info(f"   Used API Key: ...{api_key[-8:]}")

                return {
                    "script": script_text,
                    "characters": self.character_names,
                    "scenes": scenes,
                    "story_type": story_type,
                    "word_count": len(script_text.split()),
                    "character_count": len(script_text),
                    "used_template": template is not None,
                    "used_research": research_data is not None,
                }

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

                logger.error(f"   Attempt {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    logger.info(f"   🔄 Trying next API key...")
                    time.sleep(2)
                else:
                    raise

        raise Exception("Failed to generate script after all attempts with all API keys")

    def _generate_chunk(
        self,
        chunk_num: int,
        total_chunks: int,
        topic: str,
        style: Dict,
        template: Optional[Dict],
        research_data: Optional[str],
        chars_per_chunk: int,
        num_scenes: int,
        previous_chunk: Optional[str] = None
    ) -> str:
        """
        Generate a single chunk using optimized prompting strategy.

        This method implements the proven strategy from successful Gemini 2.5 Flash implementations:
        - First chunk: Full prompt with all instructions
        - Continuation chunks: Only last 8 sentences + continuation instructions
        - Final chunk: Explicit ending requirements
        """
        style_name = style.get('name', 'story')
        style_desc = style.get('description', 'engaging narrative')
        style_tone = style.get('tone', 'compelling')

        if chunk_num == 1:
            # First chunk: Use full template prompt but with chunk-specific length
            prompt = self._build_template_prompt(
                topic=topic,
                style=style,
                template=template,
                research_data=research_data,
                duration_minutes=chars_per_chunk // 150,  # Rough estimate
                num_scenes=num_scenes // total_chunks  # Scenes for this chunk
            )

            # Modify the prompt to specify this is part of a larger story
            if total_chunks > 1:
                prompt += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ MULTI-CHUNK STORY: This is chunk 1 of {total_chunks}

CRITICAL FOR THIS CHUNK:
🎯 Generate EXACTLY {chars_per_chunk:,} characters
📖 Focus: {get_chunk_section_goal(1, total_chunks)}
✅ Establish ALL character names clearly at start
✅ Set up story world and initial situation
✅ Build momentum towards next section
❌ DO NOT conclude story (more chunks coming!)
❌ DO NOT write "To be continued" or similar
✅ End mid-action or mid-scene naturally

SENSORY IMMERSION (EVERY PARAGRAPH!):
- SIGHT: Visual details, colors, movements
- SOUND: Dialogue, ambient noise, specific sounds
- SMELL: Environment scents, character reactions
- TASTE: When relevant (metallic fear, food, blood)
- TOUCH: Textures, temperature, physical sensations

CRITICAL RULES:
❌ NO labels ("Part", "Chapter", "Scene")
❌ NEVER change character names once established
✅ Show emotions PHYSICALLY (jaw clenching, trembling)
✅ Varied vocabulary - NEVER repeat phrases
✅ Short punchy + long flowing sentences
✅ Natural dialogue with contractions
✅ Build tension CONSTANTLY

Generate NOW (no title, no labels, pure story):"""

        else:
            # Continuation chunk: Use previous context
            previous_context = extract_last_sentences(previous_chunk, 8)
            is_final = (chunk_num == total_chunks)

            prompt = f"""Continue SEAMLESSLY from previous chunk. Chunk {chunk_num} of {total_chunks}.

TOPIC: {topic}
TONE: {style_tone}

PREVIOUS CHUNK ENDED WITH:
"{previous_context}"

🎯 TARGET: EXACTLY {chars_per_chunk:,} characters for this chunk

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔒 CRITICAL CONTINUATION RULES:

SEAMLESS FLOW:
✅ Continue EXACTLY where previous ended
✅ NO recaps, NO reintroductions
✅ NO "Meanwhile...", "Earlier...", "As we saw..."
✅ Continue mid-sentence if previous ended in action
✅ Jump right into narrative

CHARACTER CONSISTENCY (ABSOLUTELY CRITICAL!):
❌ NEVER change character names from previous chunks
❌ NEVER change character personalities or traits
✅ Use EXACT same character names established earlier
✅ Maintain all character relationships
✅ Continue character development naturally

STYLE CONSISTENCY:
✅ Match exact writing style from previous chunk
✅ Same narrative voice and tone
✅ Same sensory detail level
✅ Same pacing rhythm

{f'''
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 FINAL CHUNK - COMPLETE THE STORY!

ENDING REQUIREMENTS:
✅ Resolve ALL story threads and conflicts
✅ Epic climax with detailed execution
✅ Clear aftermath and consequences shown
✅ Character reflection on the journey
✅ Satisfying emotional payoff
✅ Strong, memorable final line
✅ Sense of completion and closure

Build to powerful ending that resonates!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
''' if is_final else f'''
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THIS CHUNK FOCUS:
📖 {get_chunk_section_goal(chunk_num, total_chunks)}

IMPORTANT:
❌ DO NOT end the story (more chunks coming!)
❌ DO NOT write "To be continued"
✅ Build tension and momentum
✅ End naturally mid-scene or mid-action
✅ Keep readers wanting more

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
'''}

WRITING QUALITY (CRITICAL!):
✅ Present tense, first person throughout
✅ ALL 5 SENSES in EVERY paragraph (sight, sound, smell, taste, touch)
✅ Show emotions PHYSICALLY (trembling, sweating, jaw clenching)
✅ Vivid, SPECIFIC details (not generic)
✅ Natural dialogue with contractions ("I'm", "don't", "can't")
✅ Varied sentence rhythm (short punchy + long flowing)
✅ NEVER repeat phrases or vocabulary
✅ Build tension constantly

SENSORY IMMERSION:
- SIGHT: Visual details, colors, movements
- SOUND: Dialogue, ambient noise, specific sounds
- SMELL: Environment scents, reactions
- TASTE: When relevant (fear, blood, food)
- TOUCH: Textures, temperature, sensations

WRITE EXACTLY {chars_per_chunk:,} CHARACTERS with MAXIMUM quality!

Continue NOW (no preamble, no labels, just story):"""

        return prompt

    def _build_template_prompt(
        self,
        topic: str,
        style: Dict,
        template: Optional[Dict],
        research_data: Optional[str],
        duration_minutes: int,
        num_scenes: int
    ) -> str:
        """Build ULTIMATE quality prompt with intelligent hook learning!"""
        
        # ✅ Perfect timing: 150 words per minute (voice narration speed!)
        target_words = duration_minutes * 150
        
        # Get example hooks for Gemini to LEARN from
        example_hooks_text = '\n'.join([f"   • {hook}" for hook in self.EXAMPLE_HOOKS])
        
        # Extract style values safely
        style_name = style.get('name', 'story')
        style_desc = style.get('description', 'engaging narrative')
        style_tone = style.get('tone', 'compelling')
        style_pacing = style.get('pacing', 'medium')
        
        # Base prompt with ULTIMATE quality requirements!
        prompt = f"""You are a MASTER YouTube scriptwriter creating {style_name} content.

TOPIC: {topic}
DURATION: {duration_minutes} minutes
TARGET: EXACTLY {target_words} words (150 words per minute of narration)
SCENES: {num_scenes} distinct visual scenes
TYPE: {style_desc}
TONE: {style_tone}
PACING: {style_pacing}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔒 CRITICAL RULES - NEVER BREAK THESE:

❌ NO labels ("Part", "Chapter", "Scene") - pure narrative only
❌ NO character name changes (establish names early, keep them FOREVER)
❌ NO personality shifts
✅ Start directly with vivid action or hook
✅ EXTREME sensory details (all 5 senses: sight, sound, smell, taste, touch)
✅ Show emotions PHYSICALLY (jaw clenching, trembling hands, cold sweat, etc.)
✅ Varied vocabulary - NEVER repeat phrases
✅ Short sentences (5-10 words) = tension and action
✅ Longer sentences (15-25 words) = atmosphere and description
✅ Natural dialogue with contractions ("I'm", "you're", "can't")
✅ Character thoughts in italics when needed
✅ Build tension CONSTANTLY

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SENSORY IMMERSION (CRITICAL!):
- SIGHT: Visual details, colors, movements, expressions
- SOUND: Dialogue, ambient noise, specific sounds
- SMELL: Scents in the environment, character reactions
- TASTE: When relevant, metallic fear, food, blood
- TOUCH: Textures, temperature, physical sensations

EVERY paragraph must engage multiple senses!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 INTELLIGENT HOOK CREATION (First 20-30 words):

STUDY these example hooks to LEARN the pattern (DON'T COPY!):

{example_hooks_text}

ANALYZE what makes these hooks powerful:
✅ Create immediate intrigue (viewers MUST know more)
✅ Use CONTRAST or TWIST ("I believed X, then Y happened")
✅ Raise questions that NEED answers
✅ Specific and CONCRETE (not vague)
✅ Create emotional connection
✅ Promise a story worth watching

NOW create a COMPLETELY NEW, ORIGINAL hook for "{topic}":

Your hook MUST be:
✅ 100% UNIQUE (NOT from examples - create something NEW!)
✅ PERFECTLY matched to topic: {topic}
✅ {style_name} tone and style
✅ INSTANTLY attention-grabbing
✅ Create curiosity viewers CAN'T resist
✅ Specific, concrete details (not generic)
✅ Emotionally compelling

CRITICAL: Learn the STYLE from examples, create ORIGINAL content!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # Add research if available
        if research_data:
            prompt += f"""📚 RESEARCH DATA (Use real facts):
{research_data}

⚠️ CRITICAL: Base story on research facts above. Make it authentic and credible.

"""
        
        # Add template structure if available
        if template:
            prompt += self._format_template_instructions(template, target_words)
        else:
            # Default structure
            prompt += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📐 STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【 HOOK 】(First 25-30 words)
- Start with shocking/compelling statement
- Grab attention immediately
- Make them want to know what happens next

【 SETUP 】(Next 150-200 words)  
- Introduce character with FULL NAME
- Establish SPECIFIC location
- Give context

【 RISING ACTION 】(Middle 60% of story)
- Build tension in waves
- Add complications
- Use foreshadowing

【 CLIMAX 】(Peak moment - 15% of story)
- Everything changes
- Maximum impact

【 RESOLUTION 】(Final 10-15%)
- Show aftermath
- Emotional landing
- Satisfying ending

"""
        
        # Add ULTIMATE writing rules for 10/10 quality
        prompt += f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✍️ PROFESSIONAL SCRIPTWRITING RULES (10/10 QUALITY!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎬 NARRATIVE EXCELLENCE:
✅ PRESENT TENSE ONLY ("I walk" not "I walked")
✅ FIRST PERSON for immersion ("I", "my", "me", "I'm")
✅ SHOW DON'T TELL ("my hands trembled" not "I was scared")
✅ USE ALL 5 SENSES in EVERY paragraph!
   - What I SEE (visual details)
   - What I HEAR (sounds, voices)
   - What I SMELL (scents, odors)
   - What I TASTE (if relevant)
   - What I FEEL/TOUCH (textures, sensations)
✅ SPECIFIC DETAILS > VAGUE ("my father's rusty 1987 Ford F-150" not "a truck")
✅ ACTIVE VOICE (not passive)
✅ NO LABELS, NO HEADERS, NO METADATA
✅ DIALOGUE WITH CONTRACTIONS ("don't", "can't", "I'm")

🎭 EMOTIONAL DEPTH (CRITICAL for YouTube!):
✅ INTERNAL THOUGHTS - Show my mind ("I think...", "I realize...")
✅ VISCERAL REACTIONS - Physical feelings ("heart races", "stomach churns")
✅ SUBTEXT - What's unsaid matters ("she smiles, but her eyes are cold")
✅ MICRO-DETAILS - Small observations reveal character
✅ EMOTIONAL WAVES - Vary intensity (calm → tense → terrified → calm)
✅ PACING RHYTHM - Mix sentence lengths:
   - Short. Punchy. Dramatic.
   - Longer flowing sentences that build momentum and carry emotion forward.
   - Then back to short. Impact.

💬 DIALOGUE MASTERY:
✅ Use CONTRACTIONS ("don't", "can't", "I'm", "won't")
✅ REALISTIC speech patterns (people don't talk in perfect sentences)
✅ SUBTEXT (dialogue says one thing, means another)
✅ CHARACTER VOICE (each person talks differently)

🎨 CRITICAL: VISUAL STORYTELLING - {num_scenes} UNIQUE IMAGE DESCRIPTIONS!

⚠️ MANDATORY: You MUST include EXACTLY {num_scenes} IMAGE: descriptions in your story!

FORMAT FOR EACH IMAGE:
IMAGE: [20-30 word detailed visual description]

REQUIREMENTS FOR EACH IMAGE:
✅ Include TOPIC elements: "{topic}" (MUST mention aliens if topic is aliens, etc!)
✅ 20-30 words EXACTLY
✅ UNIQUE visuals (never repeat!)
✅ SPECIFIC details (exact lighting, mood, objects, actions)
✅ CINEMATIC language (like a movie scene!)
✅ VARIED compositions across all {num_scenes} images

SHOT VARIETY - Use these {num_scenes} different types:
1. Wide establishing shot - show the full scene
2. Medium close-up - focus on character
3. Dramatic angle - unique perspective
4. Intimate close-up - emotional detail
5. Environmental wide - setting/world
6. Character focus - personality moment
7. Detail shot - important object
8. Tension shot - building stakes
9. Climactic shot - peak moment
10. Resolution shot - ending peace

EXAMPLE FORMATS:

For ALIEN topic:
IMAGE: Silver-skinned alien with large dark eyes lying on kitchen floor, glowing blue blood pooling, spaceship wreckage visible through window, sci-fi atmosphere, wide establishing shot, dramatic lighting, high detail.

For HORROR topic:
IMAGE: Woman's trembling hand on old brass doorknob, dim hallway behind with shadows stretching, eerie silence, single flickering bulb overhead, horror atmosphere, close-up shot, cinematic lighting, suspenseful mood, high detail.

For ROMANCE topic:
IMAGE: Two people's hands almost touching across coffee shop table, warm golden hour lighting streaming through window, steam rising from cups, intimate medium shot, romantic atmosphere, soft focus background, heartwarming mood.

⚠️ CRITICAL: Each IMAGE must MATCH the story moment AND the topic "{topic}"!

🎯 QUALITY TARGETS (10/10!):
✅ Emotional impact: 10/10 (MAXIMUM engagement!)
✅ Character depth: 10/10 (Complex, relatable)
✅ Visual imagery: 10/10 (All 5 senses constantly!)
✅ Pacing & rhythm: 10/10 (Professional variation)
✅ Dialogue authenticity: 10/10 (Sounds real)
✅ Sensory immersion: 10/10 (Reader feels they're there)
✅ Plot coherence: 10/10 (No holes, perfect flow)
✅ Satisfying ending: 10/10 (Emotional payoff)

⚡ VOICE OPTIMIZATION (CRITICAL!):
✅ RHYTHM - Vary sentence length for natural speech
✅ PAUSES - Use periods and commas strategically
✅ CRESCENDOS - Build intensity to peaks
✅ SILENCE - Short sentences for dramatic pauses
✅ REPETITION - Use for emphasis ("I trusted them. I trusted them completely.")
✅ READ-ALOUD TEST - Every sentence must sound natural when spoken

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 YOUR MISSION:

Write EXACTLY {target_words} words of EXTRAORDINARY quality!

MANDATORY REQUIREMENTS:
✅ EXACTLY {num_scenes} IMAGE: descriptions (COUNT THEM! Must have {num_scenes}!)
✅ Present tense, first person throughout
✅ All 5 senses in EVERY paragraph
✅ Each IMAGE includes topic "{topic}" elements!
✅ Emotional, visceral, deeply engaging
✅ Perfect for voice narration (read-aloud friendly)
✅ Vivid, unique visual scenes for EACH image (all different!)
✅ Hook that IMMEDIATELY grabs attention
✅ Satisfying, memorable ending
✅ Professional story structure

🏆 QUALITY GOAL: Create a script so good that:
- Viewers can't stop watching
- They FEEL the emotions
- They SEE the scenes in their mind
- They remember it after watching
- They share it with others
- They subscribe for more

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ BEFORE YOU START WRITING:
1. Plan {num_scenes} DIFFERENT image scenes
2. Each image MUST include "{topic}" elements
3. Each image MUST be visually DIFFERENT from others
4. Distribute images evenly throughout story

NOW Generate the complete {target_words}-word script with {num_scenes} IMAGE: descriptions.
NO preamble, NO commentary, NO explanations - JUST the story with IMAGES!

REMEMBER: {num_scenes} IMAGES REQUIRED - COUNT THEM!"""
        
        return prompt
    
    def _format_template_instructions(self, template: Dict, target_words: int) -> str:
        """Format template as CRYSTAL CLEAR instructions for Gemini"""
        
        # Extract template values safely
        template_hook = template.get('hook_example', 'Create compelling hook')
        template_tone_list = template.get('tone', ['engaging'])
        template_tone = ', '.join(template_tone_list) if isinstance(template_tone_list, list) else str(template_tone_list)
        
        instructions = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 CRITICAL: ANALYZE THIS EXAMPLE SCRIPT TEMPLATE!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This template is from a HIGH-QUALITY example script that worked PERFECTLY.

YOUR TASK:
1. STUDY the template carefully
2. ANALYZE what makes it effective  
3. LEARN the writing strategy and structure
4. CREATE a COMPLETELY NEW story using the SAME strategy
5. Keep the QUALITY and STYLE, change the CONTENT!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【 TEMPLATE HOOK EXAMPLE 】
"{template_hook}"

ANALYZE THIS HOOK:
- What makes it compelling?
- How does it grab attention?
- What's the pattern/structure?

NOW CREATE YOUR NEW HOOK:
- Use SAME strategy (contrast, twist, question, etc.)
- Make it JUST AS compelling
- But about YOUR new topic (not the template topic!)
- Create UNIQUE hook, not copy!

【 TEMPLATE TONE 】
{template_tone}

MATCH THIS TONE:
- Same emotional level
- Same intensity
- Same style
- But NEW story!

【 TEMPLATE STRUCTURE 】
Setup: ~{template.get('setup_length', 150)} words
Rising: ~{template.get('rise_length', 200)} words
Climax: ~{template.get('climax_length', 100)} words
Ending: ~{template.get('end_length', 80)} words

USE SAME PROPORTIONS:
- Same pacing rhythm
- Same emotional progression
- Same story arc shape
- But NEW content for your topic!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 CRITICAL INSTRUCTIONS:

1. DON'T copy the template story!
2. DO copy the template STRATEGY!
3. If template hook uses "contrast" → Your hook uses "contrast"
4. If template builds tension slowly → Your story builds tension slowly
5. If template has emotional ending → Your story has emotional ending
6. CREATE entirely NEW story, SAME quality level!

THINK OF IT LIKE:
- Template is the BLUEPRINT
- You're building a NEW HOUSE with same blueprint
- Different materials (new topic), same structure (proven strategy)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        return instructions
    
    def _clean_script(self, text: str) -> str:
        """Remove XML/SSML tags"""
        text = re.sub(r'<[^>]*>', '', text)
        text = re.sub(r'&[a-z]+;', '', text)
        text = re.sub(r'\[\[.*?\]\]', '', text)
        return text.strip()
    
    def _extract_characters(self, text: str) -> List[str]:
        """Extract character names"""
        pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b'
        names = set(re.findall(pattern, text))
        return sorted(list(names))[:10]
    
    def _parse_scenes(self, text: str, num_scenes: int) -> List[Dict]:
        """Parse text into scenes with proper IMAGE descriptions"""
        
        # First, try to extract IMAGE: descriptions from script
        image_descriptions = re.findall(r'IMAGE:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        
        if image_descriptions and len(image_descriptions) >= num_scenes:
            # Use explicit IMAGE: descriptions from script
            logger.info(f"   ✅ Found {len(image_descriptions)} IMAGE descriptions in script")
            
            scenes = []
            for i in range(min(num_scenes, len(image_descriptions))):
                # Find the text around this image description
                img_desc = image_descriptions[i]
                
                scenes.append({
                    'scene_number': i + 1,
                    'image_description': img_desc.strip(),
                    'content': img_desc.strip(),  # For character detection
                    'has_explicit_image': True
                })
            
            return scenes
        
        # Fallback: FORCE creation of exactly num_scenes images!
        logger.warning(f"   ⚠️  Only found {len(image_descriptions)} IMAGE descriptions!")
        logger.info(f"   🔧 FORCING creation of {num_scenes} topic-specific images...")
        
        # Split text into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if not paragraphs:
            paragraphs = [text[:500]]  # Use first part of text
        
        scenes = []
        scene_length = max(1, len(paragraphs) // num_scenes)
        
        # FORCE generation of EXACTLY num_scenes images!
        for i in range(num_scenes):
            start_idx = i * scene_length
            end_idx = min(start_idx + scene_length, len(paragraphs))
            
            # Get scene text
            scene_paragraphs = paragraphs[start_idx:end_idx] if start_idx < len(paragraphs) else paragraphs[-1:]
            scene_text = ' '.join(scene_paragraphs)[:200] if scene_paragraphs else text[i*100:(i+1)*100]
            
            # Create SPECIFIC image description
            # FORCE topic inclusion and variety!
            description = self._create_topic_specific_image(
                scene_text,
                scene_num=i + 1,
                num_scenes=num_scenes
            )
            
            scenes.append({
                'scene_number': i + 1,
                'image_description': description,
                'content': scene_text[:200],
                'has_explicit_image': False
            })
        
        logger.info(f"   ✅ Created {len(scenes)} topic-specific image descriptions")
        return scenes
    
    def _create_topic_specific_image(self, text: str, scene_num: int, num_scenes: int) -> str:
        """Create TOPIC-SPECIFIC image description - FORCES correct content!"""
        
        # Shot types for variety (cycle through these)
        shot_types = [
            "wide establishing shot, cinematic",
            "medium close-up, character focus",
            "dramatic low angle, tension",
            "intimate close-up, emotional",
            "atmospheric wide, environmental",
            "over-shoulder, interaction",
            "extreme close-up, detail",
            "dutch angle, dramatic",
            "climactic wide, peak moment",
            "resolution shot, peaceful"
        ]
        
        shot_type = shot_types[(scene_num - 1) % len(shot_types)]
        
        # Extract key snippet from text (first significant words)
        text_clean = text.replace('\n', ' ').strip()
        key_words = ' '.join(text_clean.split()[:15])  # First 15 words
        
        # Build SPECIFIC description with text content
        description = f"{key_words}, {shot_type}, cinematic lighting, high detail, professional composition, photorealistic"
        
        return description
    
    def _create_image_description_from_text(self, text: str, scene_num: int, story_type: str) -> str:
        """Create detailed image description from story text"""
        
        # Extract key elements (characters, objects, actions, emotions)
        words = text.lower().split()[:50]  # First 50 words of scene
        
        # Detect scene elements
        has_character = any(name.lower() in ' '.join(words) for name in self.character_names[:3])
        has_action = any(word in ' '.join(words) for word in ['run', 'walk', 'look', 'turn', 'move', 'open', 'close'])
        has_emotion = any(word in ' '.join(words) for word in ['fear', 'joy', 'sad', 'angry', 'love', 'terror', 'happy'])
        
        # Build rich description
        description_parts = []
        
        # Add main subject
        if has_character and self.character_names:
            description_parts.append(f"{self.character_names[0]}")
        else:
            description_parts.append("Main character")
        
        # Add key text snippet (cleaned)
        clean_snippet = text[:80].replace('\n', ' ').strip()
        if clean_snippet:
            description_parts.append(clean_snippet)
        
        # Add cinematic elements
        description_parts.append(f"{story_type} atmosphere")
        description_parts.append("cinematic lighting")
        description_parts.append("high detail")
        
        # Add composition based on scene number
        compositions = [
            "establishing wide shot",
            "medium close-up",
            "dramatic angle",
            "intimate close-up",
            "atmospheric wide",
            "character focus",
            "environmental detail",
            "tension building shot",
            "climactic moment",
            "emotional resolution"
        ]
        if scene_num <= len(compositions):
            description_parts.append(compositions[scene_num - 1])
        
        return ', '.join(description_parts)


# Create singleton instance
enhanced_script_generator = EnhancedScriptGenerator()