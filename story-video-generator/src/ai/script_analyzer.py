"""
📊 SCRIPT ANALYZER - Extract template from example scripts
Analyzes structure to make Gemini replicate quality
"""

import re
from typing import Dict, List
from src.utils.logger import logger


class ScriptAnalyzer:
    """Analyze example scripts and extract their structure"""
    
    def analyze_script(self, script_content: str, script_type: str = "story") -> Dict:
        """
        Analyze script structure and extract template
        Returns pattern that Gemini can replicate
        """
        
        logger.info(f"🔍 Analyzing script structure ({len(script_content)} chars)...")
        
        # Extract sections
        hook = self._extract_hook(script_content)
        setup = self._extract_setup(script_content)
        rising_action = self._extract_rising_action(script_content)
        climax = self._extract_climax(script_content)
        ending = self._extract_ending(script_content)
        
        # Analyze writing style
        tone = self._analyze_tone(script_content)
        key_patterns = self._extract_key_patterns(script_content)
        sentence_variation = self._analyze_sentence_variation(script_content)
        
        # Calculate lengths
        setup_length = len(setup.split()) if setup else 0
        rise_length = len(rising_action.split()) if rising_action else 0
        climax_length = len(climax.split()) if climax else 0
        end_length = len(ending.split()) if ending else 0
        
        logger.info(f"✅ Template extracted:")
        logger.info(f"   Hook: {len(hook.split())} words")
        logger.info(f"   Setup: {setup_length} words")
        logger.info(f"   Rising: {rise_length} words")
        logger.info(f"   Climax: {climax_length} words")
        logger.info(f"   Ending: {end_length} words")
        logger.info(f"   Tone: {', '.join(tone)}")
        
        return {
            "hook_example": hook,
            "hook_style": self._classify_hook_style(hook),
            "setup_example": setup,
            "setup_length": setup_length,
            "rising_action_example": rising_action[:200] + "...",  # First 200 chars
            "rise_length": rise_length,
            "climax_example": climax[:200] + "...",
            "climax_length": climax_length,
            "ending_example": ending,
            "end_length": end_length,
            "tone": tone,
            "key_patterns": key_patterns,
            "sentence_variation": sentence_variation,
            "total_words": len(script_content.split()),
            "total_chars": len(script_content),
            "script_type": script_type,
        }
    
    def _extract_hook(self, text: str) -> str:
        """Extract the hook (first compelling sentence)"""
        
        # Try to find first paragraph
        paragraphs = text.split('\n\n')
        
        if not paragraphs:
            return ""
        
        first_para = paragraphs[0].strip()
        
        # Take first 1-2 sentences as hook
        sentences = re.split(r'[.!?]+', first_para)
        hook = sentences[0].strip()
        
        # If first sentence is too short, add second
        if len(hook.split()) < 5 and len(sentences) > 1:
            hook = sentences[0] + ". " + sentences[1]
        
        return hook[:150]  # Max 150 chars
    
    def _extract_setup(self, text: str) -> str:
        """Extract setup section (character intro + context)"""
        
        paragraphs = text.split('\n\n')
        
        if len(paragraphs) < 2:
            return paragraphs[0] if paragraphs else ""
        
        # Setup is usually first 2-3 paragraphs
        setup = '\n\n'.join(paragraphs[:2])
        
        # Return first 300 words of setup
        words = setup.split()
        return ' '.join(words[:300])
    
    def _extract_rising_action(self, text: str) -> str:
        """Extract rising action (building tension)"""
        
        paragraphs = text.split('\n\n')
        
        # Rising action is middle 50% of text
        start_idx = len(paragraphs) // 4
        end_idx = (len(paragraphs) * 3) // 4
        
        middle_paras = paragraphs[start_idx:end_idx]
        rising = '\n\n'.join(middle_paras)
        
        return rising[:500]  # First 500 chars
    
    def _extract_climax(self, text: str) -> str:
        """Extract climax (peak moment)"""
        
        paragraphs = text.split('\n\n')
        
        if not paragraphs:
            return ""
        
        # Climax is usually 75% through
        climax_idx = int(len(paragraphs) * 0.75)
        
        if climax_idx >= len(paragraphs):
            climax_idx = len(paragraphs) - 1
        
        # Take 2-3 paragraphs around climax
        start = max(0, climax_idx - 1)
        end = min(len(paragraphs), climax_idx + 2)
        
        climax = '\n\n'.join(paragraphs[start:end])
        
        return climax[:400]
    
    def _extract_ending(self, text: str) -> str:
        """Extract ending (resolution)"""
        
        paragraphs = text.split('\n\n')
        
        if not paragraphs:
            return ""
        
        # Ending is last 2-3 paragraphs
        ending = '\n\n'.join(paragraphs[-2:])
        
        return ending[:300]
    
    def _analyze_tone(self, text: str) -> List[str]:
        """Analyze emotional tone of script"""
        
        tone_indicators = {
            "ominous": ["dark", "shadowy", "creeping", "dread", "fear"],
            "suspenseful": ["wait", "suddenly", "shocking", "reveal", "twist"],
            "emotional": ["tears", "heart", "felt", "loved", "loss", "forever"],
            "intense": ["blood", "fight", "battle", "explosion", "chaos"],
            "mysterious": ["unknown", "secret", "hidden", "mystery", "clue"],
            "hopeful": ["hope", "dream", "believe", "triumph", "success"],
            "melancholic": ["sad", "alone", "lost", "gone", "memory", "grief"],
            "humorous": ["laugh", "funny", "absurd", "ridiculous", "hilarious"],
        }
        
        text_lower = text.lower()
        detected_tones = []
        
        for tone, keywords in tone_indicators.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected_tones.append(tone)
                    break
        
        return list(set(detected_tones))[:3]  # Top 3 tones
    
    def _classify_hook_style(self, hook: str) -> str:
        """Classify the style of hook"""
        
        hook_lower = hook.lower()
        
        if any(word in hook_lower for word in ["died", "dead", "killed", "murder", "blood"]):
            return "shocking"
        elif any(word in hook_lower for word in ["didn't", "never", "wasn't", "didn't know"]):
            return "discovery"
        elif any(word in hook_lower for word in ["secret", "hidden", "truth", "reveal", "mystery"]):
            return "mysterious"
        elif any(word in hook_lower for word in ["suddenly", "then", "next", "happened"]):
            return "dramatic"
        elif any(word in hook_lower for word in ["what", "how", "why", "when"]):
            return "question"
        else:
            return "statement"
    
    def _extract_key_patterns(self, text: str) -> List[str]:
        """Extract writing patterns and techniques used"""
        
        patterns = []
        
        # Check for dialogue
        if re.search(r'"[^"]*"', text):
            patterns.append("dialogue-driven")
        
        # Check for sensory details
        if any(word in text.lower() for word in ["smell", "taste", "heard", "felt", "saw"]):
            patterns.append("sensory-rich")
        
        # Check for direct address
        if "you" in text.lower() or "we" in text.lower():
            patterns.append("first-person-connection")
        
        # Check for time references
        if any(word in text.lower() for word in ["seconds", "minutes", "hours", "days"]):
            patterns.append("time-aware")
        
        # Check for character emotion description
        if re.search(r'(trembled|shook|gasped|whispered|shouted)', text, re.IGNORECASE):
            patterns.append("emotion-driven")
        
        # Check for detailed descriptions
        if len(text.split()) > 3000:
            patterns.append("detailed-narrative")
        
        # Check for short sentences
        short_sentences = len([s for s in text.split('.') if len(s.split()) < 5])
        if short_sentences > len(text.split('.')) * 0.3:
            patterns.append("short-sentence-rhythm")
        
        return patterns
    
    def _analyze_sentence_variation(self, text: str) -> str:
        """Analyze how much sentence structure varies"""
        
        sentences = re.split(r'[.!?]+', text)
        
        if len(sentences) < 3:
            return "unknown"
        
        sentence_lengths = [len(s.strip().split()) for s in sentences if s.strip()]
        
        if not sentence_lengths:
            return "uniform"
        
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum((x - avg_length) ** 2 for x in sentence_lengths) / len(sentence_lengths)
        std_dev = variance ** 0.5
        
        # Classify based on variation
        if std_dev < 3:
            return "uniform"
        elif std_dev < 6:
            return "medium"
        else:
            return "varied"


# Create singleton instance
script_analyzer = ScriptAnalyzer()