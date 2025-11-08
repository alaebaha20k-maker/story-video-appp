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

from config.settings import GEMINI_SETTINGS
from config.story_types import STORY_TYPES
from src.utils.api_manager import api_manager
from src.utils.logger import logger
from src.research.fact_searcher import fact_searcher


class EnhancedScriptGenerator:
    """Generate high-quality scripts using example templates + research"""
    
    def __init__(self):
        api_key = api_manager.get_key('gemini')
        if not api_key:
            raise ValueError("Gemini API key required!")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=GEMINI_SETTINGS['model'],
            generation_config={
                "temperature": 0.75,  # ✅ Reduced for more consistent quality (was 0.85)
                "top_p": 0.92,  # ✅ Tighter control for better coherence
                "top_k": 50,  # ✅ Increased for better vocabulary variety
                "max_output_tokens": 16384,  # ✅ Doubled for longer, detailed scripts
            }
        )
        self.character_names = []
    
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
                
                # Extract metadata
                self.character_names = self._extract_characters(script_text)
                scenes = self._parse_scenes(script_text, num_scenes)
                
                logger.success(f"✅ Generated {len(script_text)} characters")
                logger.info(f"   Words: {len(script_text.split())}")
                logger.info(f"   Characters: {', '.join(self.character_names[:3])}")
                
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
                logger.error(f"   Attempt {attempt + 1} failed: {e}")
                if attempt == max_attempts - 1:
                    raise
        
        raise Exception("Failed to generate script after all attempts")
    
    def _build_template_prompt(
        self,
        topic: str,
        style: Dict,
        template: Optional[Dict],
        research_data: Optional[str],
        duration_minutes: int,
        num_scenes: int
    ) -> str:
        """Build prompt that uses template structure"""
        
        target_words = duration_minutes * 200  # ~200 words per minute
        
        # Base prompt
        prompt = f"""You are a world-class scriptwriter creating a {style['name']} story.

🎯 MISSION: Generate a compelling {duration_minutes}-minute script about: {topic}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 STORY REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Target: {target_words} words EXACTLY
Type: {style['description']}
Tone: {style['tone']}
Pacing: {style['pacing']}
Scenes: {num_scenes}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
        
        # Add enhanced writing rules for 10/10 quality
        prompt += f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✍️ PROFESSIONAL SCRIPTWRITING RULES (10/10 QUALITY!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎬 NARRATIVE REQUIREMENTS:
✅ PRESENT TENSE ONLY ("She runs" not "She ran")
✅ FIRST PERSON for emotional connection (use "I", "my", "me")
✅ SHOW DON'T TELL ("my hands trembled" not "I was scared")
✅ USE ALL 5 SENSES (what I see, hear, smell, taste, feel)
✅ SPECIFIC DETAILS > VAGUE ("my father's rusty 1987 Ford F-150" not "a truck")
✅ ACTIVE VOICE (not passive voice)
✅ NO LABELS, NO HEADERS, NO METADATA
✅ DIALOGUE WITH CONTRACTIONS ("don't", "can't", "I'm")

🎭 EMOTIONAL DEPTH (CRITICAL!):
✅ INTERNAL THOUGHTS - Show character's mind
✅ VISCERAL REACTIONS - Physical sensations of emotion
✅ SUBTEXT - What's unsaid is as important as what's said
✅ MICRO-DETAILS - Small observations that reveal character
✅ EMOTIONAL BEATS - Vary intensity (high → low → higher)
✅ PACING - Mix short punchy sentences with longer flowing ones

🎨 SCENE DESCRIPTIONS FOR IMAGES ({num_scenes} scenes):
✅ After each major story beat, add: IMAGE: [detailed visual description]
✅ Image descriptions must be:
   - VIVID and SPECIFIC
   - Include LIGHTING, MOOD, COMPOSITION
   - Describe CHARACTERS, SETTING, ACTION
   - Use CINEMATIC language
   - 15-30 words per image description

EXAMPLE FORMAT:
[Story text]... She opens the door slowly, heart pounding.

IMAGE: Woman's trembling hand on old brass doorknob, dim hallway behind, shadows stretching, eerie silence, cinematic lighting, close-up shot, suspenseful atmosphere.

[Continue story]...

🎯 QUALITY TARGETS:
✅ Emotional impact: 10/10
✅ Character depth: 10/10  
✅ Visual imagery: 10/10
✅ Pacing & rhythm: 10/10
✅ Dialogue authenticity: 10/10
✅ Sensory details: 10/10
✅ Plot coherence: 10/10
✅ Satisfying ending: 10/10

⚡ VOICE OPTIMIZATION:
✅ Write for spoken delivery (read-aloud test)
✅ Use RHYTHM - vary sentence length
✅ Add PAUSES with periods or commas
✅ Build to CRESCENDOS for impact
✅ Use REPETITION strategically for emphasis
✅ Include MOMENTS OF SILENCE (short sentences)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 YOUR MISSION: Write EXACTLY {target_words} words of EXTRAORDINARY quality!

REQUIREMENTS:
- {num_scenes} IMAGE: descriptions embedded throughout
- Present tense, first person
- Emotional, visceral, engaging
- Perfect for voice narration
- Vivid visual scenes for video

Generate the complete script NOW (no preamble, no commentary):"""
        
        return prompt
    
    def _format_template_instructions(self, template: Dict, target_words: int) -> str:
        """Format template as instructions for Gemini"""
        
        setup_pct = int((template.get("setup_length", 150) / target_words) * 100)
        rise_pct = int((template.get("rise_length", 200) / target_words) * 100)
        
        instructions = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📐 FOLLOW THIS TEMPLATE STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This template is from a high-quality example script.
REPLICATE this exact structure but with NEW content for: {template.get('topic', 'unknown')}

【 HOOK 】- REPLICATE THIS STYLE:
"{template.get('hook_example', 'Hook goes here')}"

Hook Style: {template.get('hook_style', 'unknown')}
✅ Use SAME hook style
✅ Start with SAME intensity
✅ Make audience lean in immediately

【 SETUP 】- ~{template.get('setup_length', 150)} words
Use SAME approach:
- Introduce character with personality
- Set SPECIFIC location with details
- Create sympathy/interest
- Match this pacing: {template.get('sentence_variation', 'medium')}

【 RISING ACTION 】- ~{template.get('rise_length', 200)} words  
Build tension LIKE THIS EXAMPLE:
{template.get('rising_action_example', '[Example would go here]')[:200]}...

✅ Same escalation pattern
✅ Same number of complications
✅ Same tone shift

【 CLIMAX 】- ~{template.get('climax_length', 100)} words
Peak moment SIMILAR TO:
{template.get('climax_example', '[Example would go here]')[:150]}...

【 RESOLUTION 】- ~{template.get('end_length', 80)} words
End LIKE THIS:
{template.get('ending_example', '[Example would go here]')[:150]}...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 KEY PATTERNS TO REPLICATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tone: {', '.join(template.get('tone', []))}
Patterns: {', '.join(template.get('key_patterns', []))}
Sentence Variation: {template.get('sentence_variation', 'medium')}

✅ Match all these patterns
✅ Use same emotional beats
✅ Keep same rhythm and pacing

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
        
        # Fallback: Create scenes from text chunks with generated descriptions
        logger.info(f"   ⚠️  No IMAGE descriptions found, creating from story content")
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if not paragraphs:
            paragraphs = [text]
        
        scene_length = max(1, len(paragraphs) // num_scenes)
        
        scenes = []
        for i in range(num_scenes):
            start_idx = i * scene_length
            end_idx = min(start_idx + scene_length, len(paragraphs))
            
            scene_paragraphs = paragraphs[start_idx:end_idx]
            scene_text = ' '.join(scene_paragraphs)[:300]  # First 300 chars of scene
            
            # Create rich image description from scene content
            # Extract key visual elements
            description = self._create_image_description_from_text(
                scene_text,
                scene_num=i + 1,
                story_type=style.get('name', 'story') if 'style' in locals() else 'story'
            )
            
            scenes.append({
                'scene_number': i + 1,
                'image_description': description,
                'content': scene_text,
                'has_explicit_image': False
            })
        
        return scenes
    
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