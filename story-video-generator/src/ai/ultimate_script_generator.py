"""
🏆 ULTIMATE SCRIPT GENERATOR - Claude Sonnet 4 + Maximum Quality!
The BEST script generation for YouTube videos
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import Dict, List, Optional
import re
import random

from config.story_types import STORY_TYPES
from src.ai.puter_ai import create_puter_ai
from src.utils.logger import logger
from src.research.fact_searcher import fact_searcher


class UltimateScriptGenerator:
    """Generate ULTIMATE quality scripts using Claude Sonnet 4!"""
    
    # 🏆 EXAMPLE HOOKS - Claude will LEARN from these and create NEW ones!
    # These are just examples to show Claude what GREAT hooks look like
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
        self.puter_ai = create_puter_ai()
        self.character_names = []
        
        print(f"🏆 ULTIMATE Script Generator initialized")
        print(f"   Using: Claude Sonnet 4 (BEST for storytelling!)")
        print(f"   Hook generation: INTELLIGENT (learns from examples!)")
    
    def generate_ultimate_script(
        self,
        topic: str,
        story_type: str,
        template: Optional[Dict] = None,
        research_data: Optional[str] = None,
        duration_minutes: int = 10,
        num_scenes: int = 10,
    ) -> Dict:
        """Generate ULTIMATE quality script using Claude Sonnet 4!
        
        Args:
            topic: Story topic
            story_type: Type of story (horror, romance, etc.)
            template: Optional template from example script
            research_data: Optional research facts
            duration_minutes: Target duration (1-60 minutes)
            num_scenes: Number of scenes/images (will generate this many!)
        
        Returns:
            Dict with script, scenes, characters, etc.
        """
        
        if story_type not in STORY_TYPES:
            logger.warning(f"Unknown story type: {story_type}")
            story_type = "scary_horror"
        
        style = STORY_TYPES[story_type]
        
        logger.info(f"🏆 Generating ULTIMATE script with Claude Sonnet 4")
        logger.info(f"   Topic: {topic}")
        logger.info(f"   Type: {style.get('name', story_type)}")
        logger.info(f"   Duration: {duration_minutes} minutes")
        logger.info(f"   Scenes: {num_scenes}")
        logger.info(f"   Template: {template is not None}")
        logger.info(f"   Research: {research_data is not None}")
        
        # Get research if needed
        if not research_data and story_type in ["historical_documentary", "true_crime", "biographical_life"]:
            logger.info(f"🔍 Fetching research for {topic}...")
            research_result = fact_searcher.search_facts(topic, story_type)
            research_data = research_result.get("research_data", "")
        
        # Build ULTIMATE prompt
        prompt = self._build_ultimate_prompt(
            topic=topic,
            style=style,
            template=template,
            research_data=research_data,
            duration_minutes=duration_minutes,
            num_scenes=num_scenes
        )
        
        # Generate with Claude Sonnet 4 (BEST for storytelling!)
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                logger.info(f"   Attempt {attempt + 1}/{max_attempts} with Claude Sonnet 4...")
                
                # 🏆 Use Claude Sonnet 4 via Puter!
                script_text = self.puter_ai.chat(
                    prompt=prompt,
                    model='claude-sonnet-4',  # BEST model!
                    temperature=0.75,  # Balanced creativity
                    max_tokens=16384  # Support long scripts (60 min)
                )
                
                # Clean output
                script_text = self._clean_script(script_text)
                
                # Validate
                target_words = duration_minutes * 150  # 150 words per minute
                actual_words = len(script_text.split())
                
                if actual_words < target_words * 0.7:  # At least 70% of target
                    logger.warning(f"   Script too short ({actual_words}/{target_words} words), retrying...")
                    continue
                
                # Extract metadata
                self.character_names = self._extract_characters(script_text)
                scenes = self._extract_scenes_from_script(script_text, num_scenes)
                
                logger.success(f"✅ ULTIMATE script generated!")
                logger.info(f"   Characters: {len(script_text)}")
                logger.info(f"   Words: {actual_words} (target: {target_words})")
                logger.info(f"   Scenes extracted: {len(scenes)}")
                logger.info(f"   Characters: {', '.join(self.character_names[:3])}")
                logger.info(f"   🏆 Claude Sonnet 4 quality!")
                
                return {
                    "script": script_text,
                    "characters": self.character_names,
                    "scenes": scenes,
                    "story_type": story_type,
                    "word_count": actual_words,
                    "character_count": len(script_text),
                    "used_template": template is not None,
                    "used_research": research_data is not None,
                    "model_used": "claude-sonnet-4"
                }
                
            except Exception as e:
                logger.error(f"   Attempt {attempt + 1} failed: {e}")
                if attempt == max_attempts - 1:
                    raise
        
        raise Exception("Failed to generate script after all attempts")
    
    def _build_ultimate_prompt(
        self,
        topic: str,
        style: Dict,
        template: Optional[Dict],
        research_data: Optional[str],
        duration_minutes: int,
        num_scenes: int
    ) -> str:
        """Build ULTIMATE quality prompt for Claude Sonnet 4"""
        
        # Calculate exact word count needed
        # Voice reads ~150 words per minute
        target_words = duration_minutes * 150
        
        # Get example hooks for Claude to LEARN from (not copy!)
        example_hooks_text = '\n'.join([f"   • {hook}" for hook in self.EXAMPLE_HOOKS])
        
        # Extract style values BEFORE f-string (avoid bracket issues!)
        style_name = style.get('name', 'story')
        style_desc = style.get('description', 'engaging narrative')
        style_tone = style.get('tone', 'compelling')
        style_pacing = style.get('pacing', 'medium')
        
        # Base prompt for Claude Sonnet 4
        prompt = f"""You are a MASTER storyteller creating a {style_name} for a professional YouTube video.

🎯 CRITICAL REQUIREMENTS:

TOPIC: {topic}
DURATION: {duration_minutes} minutes
TARGET: EXACTLY {target_words} words (150 words per minute of narration)
SCENES: {num_scenes} distinct visual scenes
TYPE: {style_desc}
TONE: {style_tone}
PACING: {style_pacing}

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
✅ Make viewers NEED to keep watching

CRITICAL: Learn the STYLE from examples, create ORIGINAL content!
Never repeat patterns - each hook must be COMPLETELY UNIQUE!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📐 PERFECT STRUCTURE (Based on {duration_minutes}-minute duration):

【 HOOK 】(20-30 words - {int(target_words * 0.02)} words)
- Start with shocking statement
- Grab attention IMMEDIATELY
- Make them NEED to know what happens

【 SETUP 】({int(target_words * 0.15)} words)
- First-person perspective ("I", "my", "me")
- Introduce yourself with FULL NAME
- Establish SPECIFIC location with details
- Create sympathy/connection
- Use ALL 5 SENSES (see, hear, smell, taste, touch)

【 RISING ACTION 】({int(target_words * 0.55)} words)
- Build tension in waves (low → high → higher)
- Add complications and obstacles
- Use foreshadowing
- Include internal thoughts ("I think...", "I realize...")
- Show visceral reactions ("my hands shake", "heart pounds")
- Vary sentence length for rhythm

【 CLIMAX 】({int(target_words * 0.20)} words)
- Peak emotional moment
- Everything changes
- Maximum impact
- Short, punchy sentences for drama

【 RESOLUTION 】({int(target_words * 0.08)} words)
- Show aftermath
- Emotional landing
- Satisfying conclusion
- Leave impact

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎨 VISUAL SCENES ({num_scenes} UNIQUE scenes):

After each major story beat, add:
IMAGE: [detailed 20-30 word visual description]

Requirements for each IMAGE:
✅ UNIQUE - Every scene visually DIFFERENT!
✅ SPECIFIC - Exact details (lighting, mood, action)
✅ CINEMATIC - Include shot type and composition
✅ STORY-MATCHED - Perfectly fits that moment
✅ VIVID - Use strong visual language

Vary shot types across {num_scenes} scenes:
1. Wide establishing shot (set the scene)
2. Medium close-up (introduce character)
3. Dramatic angle (build interest)
4. Intimate close-up (emotional moment)
5. Environmental wide (world detail)
6. Character focus (development)
7. Detail shot (important object)
8. Tension shot (increasing stakes)
9. Climactic shot (peak moment)
10. Resolution shot (ending)

Example IMAGE format:
IMAGE: Woman's trembling hand reaching for old brass doorknob, dim hallway stretching behind with shadows dancing on cracked walls, eerie silence, single flickering bulb overhead, horror atmosphere, close-up shot, cinematic lighting, suspenseful mood, high detail.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        # Add research if available
        if research_data:
            prompt += f"""
📚 RESEARCH DATA (CRITICAL - Use these REAL FACTS):
{research_data}

⚠️  MANDATORY: Base your story on the research above.
- Use REAL names, dates, locations from research
- Make it AUTHENTIC and CREDIBLE
- Don't make up facts - use what's provided!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        # Add template structure if available
        if template:
            # Extract tone safely (avoid f-string bracket issues)
            default_tone = [style.get('tone', 'engaging')]
            template_tone = template.get('tone', default_tone)
            tone_str = ', '.join(template_tone) if isinstance(template_tone, list) else str(template_tone)
            
            prompt += f"""
📋 TEMPLATE STRUCTURE (Learn from this example):

This template is from a HIGH-QUALITY example script.
MATCH this structure but create COMPLETELY NEW content for: {topic}

Hook Style: {template.get('hook_style', 'compelling')}
Tone: {tone_str}
Pacing: {template.get('sentence_variation', 'varied')}

✅ Use SAME structural approach
✅ Match SAME emotional beats
✅ Keep SAME pacing rhythm
✅ But create 100% ORIGINAL content!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        # Add ULTIMATE writing rules
        prompt += f"""
✍️ PROFESSIONAL SCRIPTWRITING RULES (MAXIMUM QUALITY!):

🎬 NARRATIVE EXCELLENCE:
✅ PRESENT TENSE ONLY ("I walk" not "I walked")
✅ FIRST PERSON for immersion ("I", "my", "me", "I'm")
✅ SHOW DON'T TELL ("my hands trembled" not "I was scared")
✅ USE ALL 5 SENSES every paragraph!
   - What I SEE (visual details)
   - What I HEAR (sounds, voices)
   - What I SMELL (scents, odors)
   - What I TASTE (if relevant)
   - What I FEEL/TOUCH (textures, sensations)

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

🎨 VISUAL STORYTELLING ({num_scenes} scenes):
✅ EMBED {num_scenes} IMAGE: descriptions throughout story
✅ Place IMAGE after each major story beat
✅ Each IMAGE must be:
   - 20-30 words
   - UNIQUE visuals (never repeat!)
   - SPECIFIC details (exact lighting, objects, actions)
   - CINEMATIC language
   - VARIED compositions (wide, close-up, dramatic, etc.)

🎯 QUALITY TARGETS (11/10!):
✅ Emotional impact: 11/10 (MAXIMUM engagement!)
✅ Character depth: 11/10 (Complex, relatable)
✅ Visual imagery: 11/10 (All 5 senses constantly!)
✅ Pacing & rhythm: 11/10 (Professional variation)
✅ Dialogue authenticity: 11/10 (Sounds real)
✅ Sensory immersion: 11/10 (Reader feels they're there)
✅ Plot coherence: 11/10 (No holes, perfect flow)
✅ Satisfying ending: 11/10 (Emotional payoff)

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
✅ {num_scenes} IMAGE: descriptions embedded (one after each major beat)
✅ Present tense, first person throughout
✅ All 5 senses in EVERY paragraph
✅ Emotional, visceral, deeply engaging
✅ Perfect for voice narration (read-aloud friendly)
✅ Vivid, unique visual scenes for each IMAGE
✅ Hook that IMMEDIATELY grabs attention
✅ Satisfying, memorable ending
✅ Professional story structure (Hook → Setup → Rise → Climax → Resolution)

🏆 QUALITY GOAL: Create a script so good that:
- Viewers can't stop watching
- They FEEL the emotions
- They SEE the scenes in their mind
- They remember it after watching
- They share it with others
- They subscribe for more

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generate the complete {target_words}-word script NOW.
NO preamble, NO commentary, NO explanations - JUST the story!"""

        return prompt
    
    def _clean_script(self, text: str) -> str:
        """Clean script output"""
        # Remove any XML/SSML tags
        text = re.sub(r'<[^>]*>', '', text)
        text = re.sub(r'&[a-z]+;', '', text)
        text = re.sub(r'\[\[.*?\]\]', '', text)
        # Remove markdown headers
        text = re.sub(r'^#+\s.*$', '', text, flags=re.MULTILINE)
        return text.strip()
    
    def _extract_characters(self, text: str) -> List[str]:
        """Extract character names from script"""
        # Look for capitalized names (First Last or just First)
        pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b'
        names = set(re.findall(pattern, text))
        
        # Filter out common words
        common_words = {'I', 'The', 'A', 'An', 'My', 'This', 'That', 'There', 'Here', 'When', 'Where', 'Why', 'How', 'What', 'Who', 'But', 'And', 'Or', 'Not', 'No', 'Yes', 'It', 'He', 'She', 'They', 'We', 'You', 'Me', 'Him', 'Her', 'Us', 'Them'}
        names = [n for n in names if n not in common_words]
        
        return sorted(list(set(names)))[:10]
    
    def _extract_scenes_from_script(self, text: str, num_scenes: int) -> List[Dict]:
        """Extract IMAGE descriptions from script"""
        
        # Find all IMAGE: descriptions
        image_pattern = r'IMAGE:\s*(.+?)(?:\n\n|\n(?=[A-Z])|$)'
        image_descriptions = re.findall(image_pattern, text, re.IGNORECASE | re.DOTALL)
        
        scenes = []
        
        if image_descriptions and len(image_descriptions) >= num_scenes:
            logger.info(f"   ✅ Found {len(image_descriptions)} IMAGE descriptions in script")
            
            # Use the image descriptions from script
            for i in range(min(num_scenes, len(image_descriptions))):
                img_desc = image_descriptions[i].strip()
                
                # Clean up description
                img_desc = img_desc.replace('\n', ' ').strip()
                
                scenes.append({
                    'scene_number': i + 1,
                    'image_description': img_desc,
                    'content': img_desc[:200],
                    'has_explicit_image': True
                })
        else:
            logger.warning(f"   ⚠️  Only found {len(image_descriptions)} IMAGE descriptions, expected {num_scenes}")
            logger.info(f"   Creating fallback descriptions...")
            
            # Fallback: Create descriptions from story chunks
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip() and not p.strip().startswith('IMAGE:')]
            
            if not paragraphs:
                paragraphs = [text]
            
            scene_length = max(1, len(paragraphs) // num_scenes)
            
            for i in range(num_scenes):
                start_idx = i * scene_length
                end_idx = min(start_idx + scene_length, len(paragraphs))
                
                scene_text = ' '.join(paragraphs[start_idx:end_idx])[:300]
                
                # Create rich description
                description = self._create_image_description(scene_text, i + 1, 'story')
                
                scenes.append({
                    'scene_number': i + 1,
                    'image_description': description,
                    'content': scene_text[:200],
                    'has_explicit_image': False
                })
        
        return scenes
    
    def _create_image_description(self, text: str, scene_num: int, story_type: str) -> str:
        """Create detailed image description from story text"""
        
        # Shot types for variety
        shot_types = [
            "wide establishing shot, cinematic",
            "medium close-up, character focus",
            "dramatic low angle, tension building",
            "intimate close-up, emotional moment",
            "atmospheric wide shot, environmental detail",
            "over-shoulder shot, character interaction",
            "extreme close-up, detail emphasis",
            "dutch angle, disorientation",
            "climactic moment, peak intensity",
            "resolution shot, emotional conclusion"
        ]
        
        shot_type = shot_types[min(scene_num - 1, len(shot_types) - 1)]
        
        # Extract key words from text
        key_snippet = text[:100].replace('\n', ' ').strip()
        
        # Build rich description
        description = f"{key_snippet}, {story_type} atmosphere, {shot_type}, cinematic lighting, high detail, professional composition"
        
        return description


# Create singleton
ultimate_script_generator = UltimateScriptGenerator()
