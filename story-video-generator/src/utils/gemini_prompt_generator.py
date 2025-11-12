"""
✨ GEMINI IMAGE PROMPT GENERATOR - High-quality SDXL prompts from scripts

Uses Google Gemini API to generate detailed, creative image prompts
from story scripts. Much better than extracting prompts from script.

Features:
- Multiple API keys with automatic fallback
- Generates N detailed prompts matching script content
- Optimized for SDXL-Turbo (cinematic, high-quality)
- Handles API errors gracefully
"""

import requests
import json
import time
from typing import List, Dict, Optional

class GeminiPromptGenerator:
    """Generate detailed image prompts using Google Gemini API"""

    # 🔍 SINGLE API KEY - For dashboard monitoring
    API_KEYS = [
        "AIzaSyAyI5VYus18_vStkISQ-ioVw3zzaQFE0qo"   # Single key for clear monitoring
    ]

    def __init__(self):
        """Initialize Gemini prompt generator"""
        self.current_key_index = 0
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"  # ✅ Gemini 2.0 Flash (FREE)

    def _get_next_api_key(self) -> str:
        """Get next API key in rotation"""
        key = self.API_KEYS[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.API_KEYS)
        return key

    def generate_image_prompts(
        self,
        script: str,
        num_images: int,
        style: str = "cinematic"
    ) -> List[str]:
        """
        Generate detailed image prompts from script using Gemini API

        Args:
            script: Full story script/narration
            num_images: Number of image prompts to generate
            style: Visual style (cinematic, anime, horror, etc.)

        Returns:
            List of detailed SDXL-compatible image prompts
        """

        # Build Gemini prompt
        gemini_prompt = f"""You are an expert visual storytelling AI. Analyze this story script and generate exactly {num_images} detailed image prompts for AI image generation (SDXL).

SCRIPT:
{script}

REQUIREMENTS:
1. Generate exactly {num_images} unique, detailed image prompts
2. Each prompt should capture a KEY MOMENT from the script
3. Prompts should be HIGHLY DETAILED with:
   - Visual description (what's in the scene)
   - Mood/atmosphere
   - Lighting (golden hour, dramatic, soft, etc.)
   - Camera angle (wide shot, close-up, aerial, etc.)
   - Art style: {style} style, professional, high quality
4. Each prompt should be 40-80 words
5. Prompts should work well with SDXL-Turbo (no people faces if possible, focus on scenes/environments/abstract concepts)
6. Spread prompts evenly across the story (beginning, middle, end)

OUTPUT FORMAT:
Return ONLY a JSON array of strings, nothing else. Example:
["prompt 1 here", "prompt 2 here", "prompt 3 here", ...]

Generate the {num_images} image prompts now:"""

        # Try each API key until one works
        for attempt in range(len(self.API_KEYS)):
            api_key = self._get_next_api_key()

            try:
                print(f"\n🤖 Generating {num_images} image prompts with Gemini AI...")
                print(f"   API Key: ...{api_key[-8:]}")

                # Make API request
                url = f"{self.base_url}?key={api_key}"
                headers = {'Content-Type': 'application/json'}
                data = {
                    "contents": [{
                        "parts": [{
                            "text": gemini_prompt
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.9,  # Creative but not too random
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": 2048,
                    }
                }

                response = requests.post(url, headers=headers, json=data, timeout=30)
                response.raise_for_status()

                # Parse response
                result = response.json()

                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']
                    text = content['parts'][0]['text']

                    # Extract JSON array from response
                    # Gemini might wrap it in markdown code blocks
                    text = text.strip()
                    if text.startswith('```json'):
                        text = text.replace('```json', '').replace('```', '').strip()
                    elif text.startswith('```'):
                        text = text.replace('```', '').strip()

                    # Parse JSON
                    prompts = json.loads(text)

                    if isinstance(prompts, list) and len(prompts) == num_images:
                        print(f"   ✅ Generated {len(prompts)} detailed image prompts!")

                        # Preview first prompt
                        if prompts:
                            print(f"   📝 Example prompt: {prompts[0][:80]}...")

                        return prompts
                    else:
                        print(f"   ⚠️  Unexpected format: got {len(prompts) if isinstance(prompts, list) else 'non-list'} prompts")
                        # If we got close to the right number, pad or trim
                        if isinstance(prompts, list):
                            if len(prompts) < num_images:
                                # Pad with duplicates
                                while len(prompts) < num_images:
                                    prompts.append(prompts[-1])
                            else:
                                # Trim excess
                                prompts = prompts[:num_images]
                            return prompts

            except requests.exceptions.RequestException as e:
                print(f"   ❌ API Error (key ...{api_key[-8:]}): {e}")
                if attempt < len(self.API_KEYS) - 1:
                    print(f"   🔄 Trying next API key...")
                    time.sleep(1)
                continue

            except json.JSONDecodeError as e:
                print(f"   ❌ JSON Parse Error: {e}")
                print(f"   📄 Response text: {text[:200]}...")
                if attempt < len(self.API_KEYS) - 1:
                    print(f"   🔄 Trying next API key...")
                    time.sleep(1)
                continue

            except Exception as e:
                print(f"   ❌ Unexpected error: {e}")
                if attempt < len(self.API_KEYS) - 1:
                    print(f"   🔄 Trying next API key...")
                    time.sleep(1)
                continue

        # All API keys failed - fallback to basic extraction
        print(f"\n   ⚠️  All Gemini API keys failed. Using fallback method...")
        return self._fallback_extract_prompts(script, num_images, style)

    def _fallback_extract_prompts(
        self,
        script: str,
        num_images: int,
        style: str
    ) -> List[str]:
        """
        Fallback method: Extract simple prompts from script
        Used when all Gemini API keys fail
        """
        # Split script into sentences
        sentences = [s.strip() for s in script.replace('\n', ' ').split('.') if s.strip()]

        # Select evenly spaced sentences
        if len(sentences) >= num_images:
            step = len(sentences) // num_images
            selected = [sentences[i * step] for i in range(num_images)]
        else:
            # Not enough sentences, repeat
            selected = sentences * (num_images // len(sentences) + 1)
            selected = selected[:num_images]

        # Convert to basic prompts
        prompts = []
        for sentence in selected:
            # Take first 50 words, add style
            words = sentence.split()[:50]
            prompt = ' '.join(words) + f", {style} style, high quality, detailed, professional photography"
            prompts.append(prompt)

        print(f"   ✅ Generated {len(prompts)} fallback prompts")
        return prompts


# Global instance
gemini_generator = GeminiPromptGenerator()
