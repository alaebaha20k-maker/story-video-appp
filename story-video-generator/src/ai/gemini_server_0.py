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

        CHUNKING: If script is too long (>8000 chars), splits into chunks
        and analyzes each separately, then merges results

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

        # Check if chunking is needed (API safe limit)
        CHUNK_THRESHOLD = 8000  # Safe limit to avoid API token limits

        if len(example_script) > CHUNK_THRESHOLD:
            logger.info(f"   🔪 Script too long - using chunked analysis")
            return self._analyze_in_chunks(example_script, script_type)
        else:
            logger.info(f"   ✅ Script within limits - single analysis")
            return self._analyze_single(example_script, script_type)

    def _analyze_single(
        self,
        example_script: str,
        script_type: str
    ) -> Dict:
        """
        Analyze a single script (not chunked) - for scripts under 8000 chars
        """
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

    def _analyze_in_chunks(
        self,
        example_script: str,
        script_type: str
    ) -> Dict:
        """
        Analyze a long script in chunks to avoid API token limits

        Strategy:
        1. Split script into beginning (25%), middle (50%), end (25%)
        2. Analyze each chunk separately
        3. Merge results intelligently
        """
        script_length = len(example_script)

        # Calculate chunk boundaries (by character count)
        beginning_end = int(script_length * 0.25)
        middle_start = beginning_end
        middle_end = int(script_length * 0.75)

        # Split into chunks
        chunk_beginning = example_script[:beginning_end]
        chunk_middle = example_script[middle_start:middle_end]
        chunk_end = example_script[middle_end:]

        logger.info(f"   📊 Chunk 1 (Beginning): {len(chunk_beginning)} chars")
        logger.info(f"   📊 Chunk 2 (Middle): {len(chunk_middle)} chars")
        logger.info(f"   📊 Chunk 3 (End): {len(chunk_end)} chars")

        try:
            # Analyze beginning chunk (for hook and setup)
            logger.info(f"   🔄 Analyzing BEGINNING chunk...")
            template_beginning = self._analyze_chunk(
                chunk_beginning,
                script_type,
                "beginning",
                "Focus on hook style, opening structure, and setup patterns"
            )

            # Analyze middle chunk (for pacing and techniques)
            logger.info(f"   🔄 Analyzing MIDDLE chunk...")
            template_middle = self._analyze_chunk(
                chunk_middle,
                script_type,
                "middle",
                "Focus on pacing, tension building, and writing techniques"
            )

            # Analyze end chunk (for conclusion and resolution)
            logger.info(f"   🔄 Analyzing END chunk...")
            template_end = self._analyze_chunk(
                chunk_end,
                script_type,
                "end",
                "Focus on climax, resolution, and conclusion structure"
            )

            # Merge results
            logger.info(f"   🔀 Merging chunk analyses...")
            merged_template = self._merge_chunk_analyses(
                template_beginning,
                template_middle,
                template_end
            )

            logger.success(f"✅ SERVER 0: Chunked analysis complete!")
            logger.info(f"   Chunks analyzed: 3")
            logger.info(f"   Hook Style: {merged_template.get('hookStyle', 'unknown')}")
            logger.info(f"   Tone: {', '.join(merged_template.get('tone', []))}")

            return merged_template

        except Exception as e:
            logger.error(f"❌ SERVER 0: Chunked analysis error: {e}")
            error_str = str(e)
            if '429' in error_str or 'quota' in error_str.lower():
                return self._create_default_template(example_script, quota_exceeded=True)
            raise

    def _analyze_chunk(
        self,
        chunk_text: str,
        script_type: str,
        chunk_position: str,
        focus_instruction: str
    ) -> Dict:
        """
        Analyze a single chunk of a long script
        """
        prompt = f"""You are a script analysis expert. Analyze this {chunk_position} section of a script.

SCRIPT SECTION ({chunk_position.upper()}):
{chunk_text}

SCRIPT TYPE: {script_type}

FOCUS: {focus_instruction}

Extract patterns from this section and return as JSON (no markdown):
{{
  "hookExample": "first 2-3 sentences if this is beginning, otherwise key sentences",
  "hookStyle": "dramatic/mysterious/emotional/etc",
  "tone": ["keyword1", "keyword2"],
  "perspective": "first-person/second-person/third-person",
  "keyPatterns": ["pattern1", "pattern2"],
  "sentenceVariation": "description",
  "pacing": "fast/medium/slow",
  "chunkSize": "short/medium/long paragraphs",
  "writingTechniques": ["technique1", "technique2"],
  "uniqueFeatures": ["feature1", "feature2"]
}}

Return ONLY the JSON:"""

        response = self.model.generate_content(prompt)
        if not response or not response.text:
            raise Exception(f"Empty response for {chunk_position} chunk")

        # Extract JSON
        text = response.text.strip()
        if text.startswith('```'):
            text = re.sub(r'^```json?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)

        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            return json.loads(json_match.group())
        else:
            return json.loads(text)

    def _merge_chunk_analyses(
        self,
        beginning: Dict,
        middle: Dict,
        end: Dict
    ) -> Dict:
        """
        Merge analyses from multiple chunks into one comprehensive template
        """
        # Hook comes from beginning
        merged = {
            "hookExample": beginning.get("hookExample", ""),
            "hookStyle": beginning.get("hookStyle", "engaging"),

            # Structure: estimate from all chunks
            "setupLength": 20,  # Beginning heavy
            "riseLength": 40,   # Middle focus
            "climaxLength": 30,  # End focus
            "endLength": 10,

            # Tone: combine unique tones from all chunks
            "tone": list(set(
                beginning.get("tone", []) +
                middle.get("tone", []) +
                end.get("tone", [])
            ))[:5],  # Top 5 unique tones

            # Perspective: use most common
            "perspective": beginning.get("perspective", "first-person"),

            # Key patterns: merge all unique patterns
            "keyPatterns": list(set(
                beginning.get("keyPatterns", []) +
                middle.get("keyPatterns", []) +
                end.get("keyPatterns", [])
            ))[:5],  # Top 5

            # Sentence variation: average assessment
            "sentenceVariation": middle.get("sentenceVariation", "Mix of short and long sentences"),

            # Pacing: middle chunk is most representative
            "pacing": middle.get("pacing", "medium"),

            # Chunk size: from any chunk
            "chunkSize": beginning.get("chunkSize", "medium"),

            # Writing techniques: combine all
            "writingTechniques": list(set(
                beginning.get("writingTechniques", []) +
                middle.get("writingTechniques", []) +
                end.get("writingTechniques", [])
            ))[:5],

            # Unique features: combine all
            "uniqueFeatures": list(set(
                beginning.get("uniqueFeatures", []) +
                middle.get("uniqueFeatures", []) +
                end.get("uniqueFeatures", [])
            ))[:5],

            # Add flag to indicate this was chunked
            "chunked": True,
            "chunksAnalyzed": 3
        }

        return merged

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
