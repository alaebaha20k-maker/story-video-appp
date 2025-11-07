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
                "temperature": 0.85,  # Creative but controlled
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
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
        
        # Add writing rules
        prompt += """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✍️ WRITING RULES (MUST FOLLOW)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ PRESENT TENSE ONLY ("She runs" not "She ran")
✅ SHOW DON'T TELL ("hands trembled" not "was scared")
✅ USE ALL 5 SENSES (sight, sound, smell, taste, touch)
✅ CHARACTER NAMES STAY CONSISTENT
✅ SPECIFIC > VAGUE ("rusty Ford truck" not "a car")
✅ ACTIVE VOICE (not passive)
✅ NO LABELS or headers
✅ DIALOGUE WITH CONTRACTIONS
✅ VARIED SENTENCE LENGTH for rhythm
✅ STRONG VOCABULARY without repetition

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WRITE EXACTLY {target_words} WORDS with MAXIMUM quality!
Generate NOW (no preamble):"""
        
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
        """Parse text into scenes"""
        paragraphs = text.split('\n\n')
        scene_length = len(paragraphs) // max(num_scenes, 1)
        
        scenes = []
        for i in range(num_scenes):
            start = i * scene_length
            end = start + scene_length
            scene_text = '\n\n'.join(paragraphs[start:end])
            
            scenes.append({
                'scene_num': i + 1,
                'content': scene_text[:200],
                'char_count': len(scene_text)
            })
        
        return scenes


# Create singleton instance
enhanced_script_generator = EnhancedScriptGenerator()