"""
🔍 TEMPLATE ANALYZER - Dedicated Gemini API for Template Analysis
Analyzes user templates to extract structure, hooks, and style patterns
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import google.generativeai as genai
from typing import Dict, Optional
import json

from src.utils.logger import logger


class TemplateAnalyzer:
    """Dedicated template analyzer with separate Gemini API"""

    def __init__(self):
        # Dedicated API key for template analysis
        self.api_key = 'AIzaSyCLAEQSW3P1E499fxvw7i9k1ZELGdZIdrw'

        # Configure Gemini
        genai.configure(api_key=self.api_key)

        # Use Gemini 2.0 Flash for fast analysis
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

        logger.info("🔍 Template Analyzer initialized")
        logger.info("   Using: Dedicated Gemini API for template analysis")
        logger.info("   Model: gemini-2.0-flash-exp")

    def analyze_template(self, template_text: str, story_type: str = None) -> Dict:
        """
        Analyze a template to extract structure and patterns

        Args:
            template_text: The example script/template to analyze
            story_type: Optional story type context

        Returns:
            Dict with analyzed structure:
            {
                'hook_style': str,
                'structure': str,
                'pacing': str,
                'tone': str,
                'writing_style': str,
                'scene_transitions': str,
                'key_patterns': list,
                'recommendations': dict
            }
        """

        logger.info("🔍 Analyzing template...")
        logger.info(f"   Template length: {len(template_text)} characters")
        if story_type:
            logger.info(f"   Story type: {story_type}")

        analysis_prompt = f"""
You are an expert script analyst. Analyze this example script/template and extract DETAILED structural information.

TEMPLATE TO ANALYZE:
```
{template_text}
```

STORY TYPE CONTEXT: {story_type or 'Unknown'}

ANALYZE AND EXTRACT:

1. **HOOK STYLE**:
   - How does it open? (question, statement, action, mystery)
   - Hook intensity level (mild, medium, extreme)
   - First sentence pattern
   - Attention-grabbing technique

2. **STRUCTURE**:
   - Scene breakdown pattern
   - How scenes are connected
   - Build-up pattern (linear, flashback, mystery reveal)
   - Climax placement
   - Resolution style

3. **PACING**:
   - Sentence length patterns (short/punchy vs long/descriptive)
   - Paragraph structure
   - Scene duration balance
   - Speed of reveals

4. **TONE & VOICE**:
   - Narrative perspective (1st person, 3rd person, omniscient)
   - Emotional tone (scary, emotional, factual, dramatic)
   - Vocabulary level
   - Descriptive vs action-focused

5. **WRITING STYLE**:
   - Sentence structure patterns
   - Use of dialogue vs narration
   - Descriptive techniques
   - Metaphor/imagery usage

6. **SCENE TRANSITIONS**:
   - How scenes connect
   - Time jumps
   - Location changes
   - Mood shifts

7. **KEY PATTERNS** (List specific recurring elements):
   - Repeated phrases or structures
   - Signature techniques
   - Unique stylistic choices

8. **RECOMMENDATIONS FOR SCRIPT GENERATOR**:
   - Specific instructions to replicate this style
   - Key dos and don'ts
   - Critical elements to maintain

Return your analysis as a JSON object with these exact keys:
{{
  "hook_style": "detailed description",
  "hook_intensity": "mild|medium|extreme",
  "hook_opening": "specific pattern/technique",
  "structure": "detailed structure breakdown",
  "scene_pattern": "how scenes are structured",
  "pacing": "detailed pacing analysis",
  "pacing_speed": "slow|medium|fast|dynamic",
  "tone": "detailed tone analysis",
  "narrative_voice": "1st person|3rd person|omniscient",
  "writing_style": "detailed style analysis",
  "sentence_style": "short and punchy|long and descriptive|mixed",
  "scene_transitions": "transition techniques",
  "key_patterns": ["pattern 1", "pattern 2", "pattern 3"],
  "vocabulary_level": "simple|moderate|advanced",
  "descriptive_vs_action": "more descriptive|balanced|more action",
  "recommendations": {{
    "critical_elements": ["element 1", "element 2"],
    "style_instructions": "specific instructions for replicating style",
    "avoid": ["thing to avoid 1", "thing to avoid 2"],
    "emphasis": "what to emphasize most"
  }}
}}

IMPORTANT: Return ONLY the JSON object, no other text.
"""

        try:
            # Call Gemini for analysis
            response = self.model.generate_content(analysis_prompt)
            analysis_text = response.text.strip()

            # Extract JSON from response
            if '```json' in analysis_text:
                analysis_text = analysis_text.split('```json')[1].split('```')[0].strip()
            elif '```' in analysis_text:
                analysis_text = analysis_text.split('```')[1].split('```')[0].strip()

            # Parse JSON
            analysis = json.loads(analysis_text)

            logger.success("✅ Template analyzed successfully!")
            logger.info(f"   Hook style: {analysis.get('hook_style', 'N/A')[:50]}...")
            logger.info(f"   Structure: {analysis.get('structure', 'N/A')[:50]}...")
            logger.info(f"   Pacing: {analysis.get('pacing_speed', 'N/A')}")

            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse analysis JSON: {e}")
            logger.error(f"   Response: {analysis_text[:200]}...")

            # Return a basic structure
            return {
                'hook_style': 'Could not analyze',
                'structure': 'Could not analyze',
                'pacing': 'medium',
                'tone': 'neutral',
                'writing_style': 'standard',
                'scene_transitions': 'standard',
                'key_patterns': [],
                'recommendations': {
                    'critical_elements': [],
                    'style_instructions': 'Generate naturally',
                    'avoid': [],
                    'emphasis': 'Story quality'
                }
            }

        except Exception as e:
            logger.error(f"❌ Template analysis failed: {e}")
            import traceback
            traceback.print_exc()

            # Return basic structure
            return {
                'hook_style': 'standard opening',
                'structure': 'linear progression',
                'pacing': 'medium',
                'tone': 'neutral',
                'writing_style': 'standard narration',
                'scene_transitions': 'chronological',
                'key_patterns': [],
                'recommendations': {
                    'critical_elements': ['Clear narrative', 'Good pacing'],
                    'style_instructions': 'Generate engaging story',
                    'avoid': ['Rushed endings', 'Unclear transitions'],
                    'emphasis': 'Story quality and engagement'
                }
            }

    def create_style_guide(self, analysis: Dict) -> str:
        """
        Convert analysis into a style guide for the script generator

        Args:
            analysis: Template analysis dictionary

        Returns:
            Formatted style guide string
        """

        style_guide = f"""
TEMPLATE STYLE GUIDE:

🎯 HOOK STYLE:
{analysis.get('hook_style', 'Standard opening')}
- Intensity: {analysis.get('hook_intensity', 'medium')}
- Opening pattern: {analysis.get('hook_opening', 'engaging question or statement')}

📝 STRUCTURE:
{analysis.get('structure', 'Linear progression with clear acts')}
- Scene pattern: {analysis.get('scene_pattern', 'Sequential scenes building to climax')}

⚡ PACING:
{analysis.get('pacing', 'Balanced pacing with varied scene lengths')}
- Speed: {analysis.get('pacing_speed', 'medium')}
- Sentence style: {analysis.get('sentence_style', 'mixed')}

🎭 TONE & VOICE:
{analysis.get('tone', 'Engaging narrative tone')}
- Narrative voice: {analysis.get('narrative_voice', '3rd person')}
- Descriptive vs Action: {analysis.get('descriptive_vs_action', 'balanced')}

✍️ WRITING STYLE:
{analysis.get('writing_style', 'Clear, engaging narration')}
- Vocabulary: {analysis.get('vocabulary_level', 'moderate')}

🔄 SCENE TRANSITIONS:
{analysis.get('scene_transitions', 'Smooth chronological transitions')}

🔑 KEY PATTERNS:
{chr(10).join([f"- {pattern}" for pattern in analysis.get('key_patterns', ['Engaging narrative', 'Clear structure'])])}

⭐ CRITICAL ELEMENTS TO MAINTAIN:
{chr(10).join([f"- {elem}" for elem in analysis.get('recommendations', {}).get('critical_elements', ['Story quality'])])}

📋 STYLE INSTRUCTIONS:
{analysis.get('recommendations', {}).get('style_instructions', 'Generate engaging story matching template style')}

🚫 AVOID:
{chr(10).join([f"- {avoid}" for avoid in analysis.get('recommendations', {}).get('avoid', ['Rushed pacing'])])}

🎯 EMPHASIS:
{analysis.get('recommendations', {}).get('emphasis', 'Story engagement and quality')}
"""

        return style_guide


# Singleton instance
template_analyzer = TemplateAnalyzer()


# Test function
if __name__ == '__main__':
    print("\n🧪 Testing Template Analyzer...\n")

    example_template = """
I never believed in ghosts. Until the night I saw my reflection blink.

It started three weeks ago. I moved into an old Victorian house on Maple Street. The realtor said it was a "fixer-upper." She didn't mention the mirror.

Every morning, I'd brush my teeth in front of the bathroom mirror. Normal. Until one Tuesday, my reflection moved... differently. Just a fraction of a second delay. Like watching a video with bad sync.

I told myself it was the lighting. Old houses, weird shadows. But then it got worse.

My reflection started doing things I didn't do. Small things at first. A smile when I wasn't smiling. A wave when my hands were at my sides.

Last night, I woke up at 3 AM. Something drew me to the mirror. My reflection was already standing there. Waiting. Watching.

And then it spoke.

"I've been trapped here for 40 years," it said. "Now it's your turn."

The mirror rippled like water. I felt hands—cold, dead hands—pulling me toward the glass.

I'm writing this from inside the mirror now. If you're reading this, you bought the house. I'm sorry.

Don't look in the bathroom mirror.

Whatever you do... don't look.
"""

    try:
        # Analyze template
        analysis = template_analyzer.analyze_template(
            template_text=example_template,
            story_type='scary_horror'
        )

        print("\n📊 ANALYSIS RESULT:")
        print(json.dumps(analysis, indent=2))

        # Create style guide
        style_guide = template_analyzer.create_style_guide(analysis)

        print("\n📋 STYLE GUIDE:")
        print(style_guide)

        print("\n✅ Template analyzer test passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
