
"""
📝 PROFESSIONAL SCRIPT GENERATOR - Multi-Niche, Cinema Quality
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    print("⚠️  google-generativeai not installed")
    print("   Run: pip install google-generativeai")
    genai = None
    GENAI_AVAILABLE = False

from typing import Dict, List
import re

from config.settings import GEMINI_SETTINGS
from src.utils.api_manager import api_manager
from src.utils.logger import logger

# Import story types - with error handling
try:
    from config.story_types import STORY_TYPES
except ImportError:
    print("⚠️ story_types.py not found - creating default...")
    STORY_TYPES = {
        "scary_horror": {
            "name": "Scary & Horror",
            "description": "Terrifying stories",
            "tone": "dark, ominous, tense",
            "pacing": "slow burn tension",
            "example": "Something was watching from the darkness"
        }
    }


class ProScriptGenerator:
    """Professional multi-niche story generator"""
    
    def __init__(self):
        if not GENAI_AVAILABLE:
            print("⚠️  ProScriptGenerator: google-generativeai not available")
            self.model = None
            self.character_names = []
            self.api_keys = []
            return

        # ✅ Get all Gemini API keys for rotation
        self.api_keys = api_manager.get_all_gemini_keys()
        if not self.api_keys:
            print("⚠️  ProScriptGenerator: Gemini API keys not found")
            self.model = None
            self.character_names = []
            return

        # Configure with first key initially
        genai.configure(api_key=self.api_keys[0])
        self.model = genai.GenerativeModel(GEMINI_SETTINGS['model'])
        self.character_names = []
        print(f"   API Keys: {len(self.api_keys)} keys with automatic rotation")
    
    def generate_story(
        self,
        topic: str,
        story_type: str,
        duration_minutes: int = 10,
        num_scenes: int = 10
    ) -> Dict:
        """Generate professional story"""
        
        if not self.model:
            raise RuntimeError("Script generator not initialized - check API key and dependencies")
        
        if story_type not in STORY_TYPES:
            logger.warning(f"Unknown story type: {story_type}, using first available")
            story_type = list(STORY_TYPES.keys())[0]
        
        style = STORY_TYPES[story_type]
        
        logger.info(f"📝 Generating {style['name']} story about: {topic}")
        logger.info(f"   Duration: {duration_minutes} minutes")
        logger.info(f"   Scenes: {num_scenes}")
        
        # Build prompt
        prompt = self._build_professional_prompt(
            topic, style, duration_minutes, num_scenes
        )
        
        # Generate
        try:
            response = self.model.generate_content(prompt)
            script_text = response.text
            
            # Extract characters
            self.character_names = self._extract_characters(script_text)
            
            # Parse scenes
            scenes = self._parse_scenes(script_text, num_scenes)
            
            logger.success(f"✅ Generated {len(script_text)} characters")
            logger.info(f"   Characters: {', '.join(self.character_names[:3])}")
            logger.info(f"   Scenes: {len(scenes)}")
            
            return {
                "script": script_text,
                "characters": self.character_names,
                "scenes": scenes,
                "story_type": story_type,
                "style": style,
                "duration": duration_minutes,
                "word_count": len(script_text.split()),
                "character_count": len(script_text)
            }
            
        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            raise
    
    def _build_professional_prompt(self, topic: str, style: Dict, duration: int, num_scenes: int) -> str:
        """Build cinema-quality prompt"""
        
        target_words = duration * 150
        
        prompt = f"""You are an Emmy-award winning screenwriter creating a {duration}-minute {style['name']} story for YouTube.

TOPIC: {topic}

STORY TYPE: {style['description']}
TONE: {style['tone']}
PACING: {style['pacing']}

TARGET LENGTH: {target_words} words (~{duration} minutes narration)

CRITICAL STRUCTURE:
HOOK (First 10-15 seconds): Start with a POWERFUL statement or question
SETUP (Next 1-2 minutes): Introduce main character(s) with NAMES, establish location
RISING ACTION (Middle 60%): Build tension progressively
CLIMAX (Peak moment): The shocking/emotional/surprising event
RESOLUTION (Final 10-15%): Aftermath and consequences

WRITING RULES:
- Use PRESENT TENSE for immediacy
- Character names must be CONSISTENT throughout
- Show emotions through actions, not labels
- Use ALL FIVE SENSES
- Vary sentence length
- Include {num_scenes} distinct visual moments
- NO chapter labels, NO scene markers, NO "Part 1/2/3"
- Just pure, flowing narration from start to finish

EXAMPLE OPENING: "{style['example']}"

Now write the complete {duration}-minute story. Start with the hook immediately:"""
        
        return prompt
    
    def _extract_characters(self, script: str) -> List[str]:
        """Extract character names"""
        words = re.findall(r'\b[A-Z][a-z]+\b', script)
        name_counts = {}
        
        skip_words = {'The', 'He', 'She', 'They', 'It', 'But', 'And', 'When', 'Then', 'That', 'This', 'What', 'Where'}
        
        for word in words:
            if word not in skip_words:
                name_counts[word] = name_counts.get(word, 0) + 1
        
        characters = [name for name, count in name_counts.items() if count >= 3]
        return characters[:5]
    
    def _parse_scenes(self, script: str, target_scenes: int) -> List[Dict]:
        """Parse script into visual scenes"""
        
        paragraphs = [p.strip() for p in script.split('\n\n') if p.strip()]
        if not paragraphs:
            paragraphs = [script]
        
        scenes_per_para = max(1, target_scenes // len(paragraphs))
        scenes = []
        
        for i, para in enumerate(paragraphs):
            if len(scenes) >= target_scenes:
                break
            
            sentences = [s.strip() for s in para.split('.') if len(s.strip()) > 20]
            
            for sentence in sentences[:scenes_per_para]:
                if len(scenes) >= target_scenes:
                    break
                
                scenes.append({
                    "scene_number": len(scenes) + 1,
                    "content": sentence[:300],
                    "image_description": self._create_image_prompt(sentence),
                    "timestamp": f"Scene {len(scenes) + 1}"
                })
        
        while len(scenes) < target_scenes and paragraphs:
            idx = len(scenes) % len(paragraphs)
            scenes.append({
                "scene_number": len(scenes) + 1,
                "content": paragraphs[idx][:200],
                "image_description": "atmospheric scene",
                "timestamp": f"Scene {len(scenes) + 1}"
            })
        
        return scenes[:target_scenes]
    
    def _create_image_prompt(self, sentence: str) -> str:
        """Create visual prompt from sentence"""
        sentence_lower = sentence.lower()
        
        if any(word in sentence_lower for word in ['she', 'he', 'they', 'person', 'man', 'woman']):
            return f"character: {sentence[:150]}"
        
        if any(word in sentence_lower for word in ['room', 'house', 'street', 'forest', 'building']):
            return f"location: {sentence[:150]}"
        
        if any(word in sentence_lower for word in ['door', 'window', 'phone', 'car', 'weapon']):
            return f"detail: {sentence[:150]}"
        
        return f"atmospheric: {sentence[:150]}"


# Global instance
pro_script_generator = ProScriptGenerator()

# Alias for backward compatibility
script_generator = pro_script_generator