"""
📊 GEMINI SERVER 0 - Template Analysis ONLY
Dedicated to analyzing example scripts and extracting structure
Separate API key = Separate quota pool!
"""

import google.generativeai as genai
from typing import Dict
import re
import json

from src.utils.logger import logger


class GeminiServer0:
    """
    Gemini Server 0 - Dedicated to template analysis ONLY
    This runs BEFORE Server 1 to learn from example scripts
    Uses separate API key to avoid quota conflicts
    """

    def __init__(self):
        # Dedicated API key for template analysis
        api_key = "AIzaSyDqDOGfR0J0BQVMJ0E5fF8bhntpuZcV3gM"

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config={
                "temperature": 0.3,  # Lower temp for consistent analysis
                "top_p": 0.85,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )

        logger.info(f"✅ Gemini Server 0 initialized")
        logger.info(f"   Model: gemini-2.0-flash-exp")
        logger.info(f"   Purpose: Template analysis (ONLY)")
        logger.info(f"   API Key: ...{api_key[-8:]}")

    def analyze_template_script(
        self,
        example_script: str,
        script_type: str
    ) -> Dict:
        """
        Analyze example script to extract structure, style, and patterns
        This is the ONLY job of Server 0

        Args:
            example_script: User's example script to learn from
            script_type: Type of script (story, documentary, etc.)

        Returns:
            Template structure dict with:
            - hookExample: First 2-3 sentences
            - hookStyle: dramatic/mysterious/emotional/etc
            - setupLength: % of script for setup
            - riseLength: % for rising action
            - climaxLength: % for climax
            - endLength: % for conclusion
            - tone: List of tone keywords
            - keyPatterns: Sentence patterns and techniques
            - sentenceVariation: How sentences are mixed
            - chunkSize: Preferred paragraph/chunk size
        """

        logger.info(f"\n📊 SERVER 0: Analyzing template script...")
        logger.info(f"   Length: {len(example_script)} characters")
        logger.info(f"   Type: {script_type}")

        prompt = f"""You are a script analysis expert. Analyze this example script and extract its EXACT structure, style, and patterns.

EXAMPLE SCRIPT TO ANALYZE:
{example_script}

SCRIPT TYPE: {script_type}

Your job is to extract EVERY detail so another AI can replicate this style perfectly.

Analyze and return:

1. **HOOK ANALYSIS:**
   - Extract the first 2-3 sentences (the hook)
   - Identify the hook style (dramatic, mysterious, emotional, suspenseful, etc.)
   - Note what makes it effective

2. **STRUCTURE BREAKDOWN:**
   - What % of the script is SETUP (introduction/context)?
   - What % is RISING ACTION (building tension)?
   - What % is CLIMAX (peak moment)?
   - What % is CONCLUSION (resolution)?

3. **TONE & VOICE:**
   - List 3-5 tone keywords (e.g., suspenseful, heartfelt, creepy, mysterious)
   - Is it first-person, second-person, or third-person?
   - What emotions does it evoke?

4. **SENTENCE PATTERNS:**
   - How are short and long sentences mixed?
   - Are there repeated sentence structures?
   - Any rhetorical devices? (questions, repetition, etc.)

5. **PACING & RHYTHM:**
   - Fast-paced or slow-burn?
   - Where are the pauses/breaks?
   - How long are typical paragraphs/chunks?

6. **KEY WRITING TECHNIQUES:**
   - Descriptive techniques used
   - Dialogue style (if any)
   - Sensory details (sight, sound, touch, etc.)
   - Any unique patterns?

FORMAT YOUR RESPONSE AS PURE JSON (no markdown, no ```):
{{
  "hookExample": "first 2-3 sentences exactly as written",
  "hookStyle": "dramatic/mysterious/emotional/etc",
  "setupLength": 20,
  "riseLength": 40,
  "climaxLength": 30,
  "endLength": 10,
  "tone": ["keyword1", "keyword2", "keyword3"],
  "perspective": "first-person/second-person/third-person",
  "keyPatterns": ["pattern1", "pattern2", "pattern3"],
  "sentenceVariation": "description of how sentences vary",
  "pacing": "fast/medium/slow",
  "chunkSize": "short/medium/long paragraphs",
  "writingTechniques": ["technique1", "technique2"],
  "uniqueFeatures": ["feature1", "feature2"]
}}

Analyze thoroughly and return ONLY the JSON:"""

        try:
            logger.info("   🔄 Calling Gemini Server 0...")
            response = self.model.generate_content(prompt)

            if not response or not response.text:
                raise Exception("Empty response from Gemini Server 0")

            # Extract JSON from response
            text = response.text.strip()

            # Remove markdown code blocks if present
            if text.startswith('```'):
                text = re.sub(r'^```json?\s*', '', text)
                text = re.sub(r'\s*```$', '', text)

            # Find JSON object
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                template = json.loads(json_match.group())
            else:
                # Try parsing entire text as JSON
                template = json.loads(text)

            logger.success(f"✅ SERVER 0: Template analysis complete!")
            logger.info(f"   Hook Style: {template.get('hookStyle', 'unknown')}")
            logger.info(f"   Tone: {', '.join(template.get('tone', []))}")
            logger.info(f"   Perspective: {template.get('perspective', 'unknown')}")

            return template

        except json.JSONDecodeError as e:
            logger.error(f"❌ SERVER 0: JSON parsing error: {e}")
            logger.error(f"   Response text: {response.text[:500]}...")

            # Return basic default template
            return self._create_default_template(example_script)

        except Exception as e:
            logger.error(f"❌ SERVER 0: Analysis error: {e}")

            # Check if quota error
            error_str = str(e)
            if '429' in error_str or 'quota' in error_str.lower():
                logger.warning("   Server 0 quota exceeded - returning default template")
                return self._create_default_template(example_script, quota_exceeded=True)

            raise

    def _create_default_template(self, example_script: str, quota_exceeded: bool = False) -> Dict:
        """
        Create a basic default template when analysis fails
        """
        return {
            "hookExample": example_script[:200] + "..." if len(example_script) > 200 else example_script,
            "hookStyle": "engaging",
            "setupLength": 20,
            "riseLength": 40,
            "climaxLength": 30,
            "endLength": 10,
            "tone": ["engaging", "narrative", "descriptive"],
            "perspective": "first-person",
            "keyPatterns": ["Descriptive storytelling", "Sensory details"],
            "sentenceVariation": "Mix of short and long sentences",
            "pacing": "medium",
            "chunkSize": "medium",
            "writingTechniques": ["Vivid descriptions", "Emotional depth"],
            "uniqueFeatures": ["Engaging narrative"],
            "quotaExceeded": quota_exceeded,
            "message": "Default template used" + (" - Server 0 quota exceeded" if quota_exceeded else "")
        }


# Global instance
gemini_server_0 = GeminiServer0()
