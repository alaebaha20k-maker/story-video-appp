"""
🎨 IMAGE PROMPT EXTRACTOR - Stage 2 Gemini 1.5 Flash
Analyzes finished script and generates DreamShaper XL-optimized image prompts

OPTIMIZED FOR FREE TIER LIMITS:
- Uses Gemini 1.5 Flash (higher free tier limits: 15 RPM, 1M TPM)
- LARGE chunks (8000 chars) = FEWER API calls
- NO retries = immediate fallback on errors
- 5 second delay between chunks
- Fallback prompts always available

SEPARATE FROM SCRIPT GENERATION - Uses dedicated Gemini API for visual prompt extraction
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import os
from typing import List, Dict
import google.generativeai as genai
import time

# ═══════════════════════════════════════════════════════════════
# GEMINI API KEY - STAGE 2 (Image Prompt Extraction)
# ═══════════════════════════════════════════════════════════════

GEMINI_API_KEY_STAGE_2 = "AIzaSyAGbzxD1mg2awU04T1ct2JXZOGy-2IJ95c"

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY_STAGE_2)

# Use Gemini 1.5 Flash - Higher free tier limits than 2.0 Flash
# Free tier: 15 RPM, 1M TPM (vs 2.0 Flash: much lower limits)
model = genai.GenerativeModel('gemini-1.5-flash-latest')


class ImagePromptExtractor:
    """
    STAGE 2: Extracts visual prompts from finished script

    PURPOSE:
    - Receives high-quality script from Stage 1
    - Analyzes important visual scenes
    - Generates SDXL-Turbo optimized prompts
    - Matches exact number of images needed

    CHUNKING STRATEGY:
    - Processes script in chunks to avoid rate limits
    - Each chunk extracts prompts for its portion
    - Combines all prompts at the end
    """

    def __init__(self):
        self.model = model
        # OPTIMIZED: Minimize API calls to avoid rate limits
        self.max_chunk_size = 8000  # LARGER chunks = fewer requests (was 2500)
        self.delay_between_requests = 5  # LONGER delay between chunks (was 3s)
        self.max_retries = 1  # NO retries - use fallback immediately (was 3)
        self.retry_delay = 0  # No retry delay needed

    def extract_prompts(
        self,
        script: str,
        num_images: int,
        story_type: str = 'scary_horror',
        image_style: str = 'cinematic'
    ) -> List[Dict]:
        """
        Extract visual prompts from script

        Args:
            script: The finished script text
            num_images: Exact number of image prompts to generate
            story_type: Type of story (for context)
            image_style: Visual style (cinematic, anime, etc.)

        Returns:
            List of prompt dicts: [{'prompt': '...', 'scene_number': 1}, ...]
        """

        print(f"\n🎨 IMAGE PROMPT EXTRACTOR - Stage 2")
        print(f"   Script length: {len(script)} characters")
        print(f"   Images needed: {num_images}")
        print(f"   Style: {image_style}")
        print(f"   Story type: {story_type}")

        # Split script into chunks if too long
        chunks = self._split_script_into_chunks(script, num_images)

        print(f"   Processing in {len(chunks)} chunks...")

        all_prompts = []

        for i, chunk_data in enumerate(chunks):
            print(f"\n   📝 Chunk {i+1}/{len(chunks)}: Extracting {chunk_data['target_prompts']} prompts...")

            prompts = self._extract_prompts_from_chunk(
                chunk_text=chunk_data['text'],
                target_prompts=chunk_data['target_prompts'],
                story_type=story_type,
                image_style=image_style
            )

            all_prompts.extend(prompts)

            # Rate limit delay
            if i < len(chunks) - 1:
                print(f"      ⏳ Waiting {self.delay_between_requests}s (rate limit protection)...")
                time.sleep(self.delay_between_requests)

        # Ensure we have exactly num_images prompts
        if len(all_prompts) < num_images:
            print(f"   ⚠️  Generated {len(all_prompts)} prompts, need {num_images}. Adding more...")
            all_prompts = self._pad_prompts(all_prompts, num_images, story_type, image_style)
        elif len(all_prompts) > num_images:
            print(f"   ⚠️  Generated {len(all_prompts)} prompts, need {num_images}. Trimming...")
            all_prompts = all_prompts[:num_images]

        print(f"\n   ✅ Extracted {len(all_prompts)} image prompts!")

        return all_prompts

    def _split_script_into_chunks(self, script: str, num_images: int) -> List[Dict]:
        """
        Split script into chunks for processing
        Each chunk gets proportional number of prompts to extract
        """

        script_length = len(script)

        # If short enough, process as one chunk
        if script_length <= self.max_chunk_size:
            return [{
                'text': script,
                'target_prompts': num_images
            }]

        # Split into multiple chunks
        chunks = []
        num_chunks = (script_length // self.max_chunk_size) + 1
        prompts_per_chunk = num_images // num_chunks

        sentences = script.split('. ')
        chunk_text = ""
        chunk_sentences = []

        for sentence in sentences:
            if len(chunk_text) + len(sentence) < self.max_chunk_size:
                chunk_sentences.append(sentence)
                chunk_text += sentence + '. '
            else:
                # Save current chunk
                if chunk_sentences:
                    chunks.append({
                        'text': chunk_text.strip(),
                        'target_prompts': prompts_per_chunk
                    })
                # Start new chunk
                chunk_sentences = [sentence]
                chunk_text = sentence + '. '

        # Add remaining chunk
        if chunk_sentences:
            chunks.append({
                'text': chunk_text.strip(),
                'target_prompts': prompts_per_chunk
            })

        # Adjust last chunk to get exact total
        remaining = num_images - sum(c['target_prompts'] for c in chunks)
        if remaining > 0:
            chunks[-1]['target_prompts'] += remaining

        return chunks

    def _extract_prompts_from_chunk(
        self,
        chunk_text: str,
        target_prompts: int,
        story_type: str,
        image_style: str
    ) -> List[Dict]:
        """Extract prompts from a single chunk using Gemini"""

        # Map style to DreamShaper XL-optimized descriptions
        style_descriptions = {
            'cinematic': 'cinematic movie quality, professional cinematography, dramatic lighting, film photography',
            'anime': 'anime style, manga illustration, Japanese animation art, vibrant colors, detailed anime',
            'realistic': 'photorealistic, highly detailed photography, 8k uhd, sharp focus, professional photo',
            'horror': 'dark horror atmosphere, creepy, terrifying, eerie lighting, ominous mood, disturbing',
            'fantasy': 'fantasy art, magical atmosphere, mystical, ethereal, dreamlike, enchanted',
            'scifi': 'sci-fi futuristic, science fiction, cyberpunk aesthetic, advanced technology, neon lighting',
            'vintage': 'vintage retro style, old photograph, aged, classic 1970s aesthetic, nostalgic',
            'sketch': 'pencil sketch, hand-drawn illustration, artistic sketch, detailed linework, black and white',
            'comic': 'comic book style, graphic novel art, bold lines, pop art illustration, comic panel',
            'watercolor': 'watercolor painting, soft pastel colors, artistic illustration, painted watercolor',
            'oilpainting': 'oil painting, classical fine art, painterly brushstrokes, artistic painting',
            'abstract': 'abstract art, modern artistic, creative composition, abstract expressionism',
            'documentary': 'documentary photography, National Geographic style, photorealistic journalism',
            'noir': 'film noir, high contrast black and white, dramatic shadows, 1940s crime aesthetic'
        }

        style_desc = style_descriptions.get(image_style, 'cinematic film still')

        prompt = f"""You are an expert visual prompt engineer for AI image generation models (SDXL, DreamShaper XL).

TASK: Analyze this script and create EXACTLY {target_prompts} detailed image prompts for the most visually important scenes.

SCRIPT:
{chunk_text}

VISUAL STYLE: {style_desc}
STORY TYPE: {story_type}
IMAGE FORMAT: 16:9 landscape (1536x864)

PROMPT REQUIREMENTS:
✅ Generate EXACTLY {target_prompts} prompts (no more, no less)
✅ Each prompt must be 50-100 words of pure visual description
✅ Focus on concrete, photographable/renderable scenes
✅ Include: setting, lighting, atmosphere, composition, colors, mood
✅ Specify camera angle when relevant (wide shot, close-up, aerial view, etc.)
✅ Use vivid, specific details (not generic descriptions)

AVOID:
❌ Abstract concepts or emotions without visual elements
❌ Text, logos, signs with readable text
❌ Copyrighted characters or trademarked content
❌ Human faces with specific features (keep descriptions general)

OUTPUT FORMAT - Return ONLY numbered prompts:
1. [Complete detailed visual prompt for first key scene]
2. [Complete detailed visual prompt for second key scene]
...
{target_prompts}. [Complete detailed visual prompt for final scene]

IMPORTANT: Each prompt should paint a complete visual picture that an AI can render. Be specific about lighting, colors, composition, and atmosphere.

Generate the {target_prompts} prompts now:"""

        # Single attempt - NO retries (to avoid rate limits)
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text

            # Parse numbered prompts
            prompts = self._parse_prompts_from_response(response_text, target_prompts)

            if prompts and len(prompts) > 0:
                print(f"      ✅ Successfully extracted {len(prompts)} prompts")
                return prompts
            else:
                print(f"      ⚠️  No valid prompts in response. Using fallback...")
                return self._generate_fallback_prompts(target_prompts, story_type, image_style)

        except Exception as e:
            error_msg = str(e)
            print(f"      ❌ Error: {error_msg[:100]}")
            print(f"      ⚠️  Using fallback prompts (no retries to avoid rate limits)...")
            return self._generate_fallback_prompts(target_prompts, story_type, image_style)

    def _parse_prompts_from_response(self, response_text: str, target_count: int) -> List[Dict]:
        """Parse numbered prompts from Gemini response"""

        prompts = []
        lines = response_text.split('\n')

        for line in lines:
            line = line.strip()
            # Match numbered prompts: "1. prompt text" or "1) prompt text"
            if line and (line[0].isdigit() or line.startswith('*')):
                # Remove numbering
                prompt_text = line.split('.', 1)[-1].split(')', 1)[-1].strip()
                if len(prompt_text) > 20:  # Valid prompt
                    prompts.append({
                        'prompt': prompt_text,
                        'scene_number': len(prompts) + 1
                    })

        # If not enough prompts, try alternate parsing
        if len(prompts) < target_count:
            # Split by double newlines (paragraphs)
            paragraphs = [p.strip() for p in response_text.split('\n\n') if len(p.strip()) > 20]
            prompts = [{'prompt': p, 'scene_number': i+1} for i, p in enumerate(paragraphs)]

        return prompts[:target_count]

    def _generate_fallback_prompts(
        self,
        count: int,
        story_type: str,
        image_style: str
    ) -> List[Dict]:
        """Generate fallback prompts if API fails"""

        base_prompts = {
            'scary_horror': [
                'Dark abandoned mansion at night, eerie fog, moonlight through broken windows, cinematic horror atmosphere',
                'Shadowy figure in dark forest, creepy atmosphere, dramatic lighting, horror scene',
                'Old cemetery at midnight, mist rolling over gravestones, ominous mood'
            ],
            'documentary': [
                'Nature landscape, golden hour lighting, professional documentary photography',
                'Urban cityscape, dramatic sky, photorealistic documentary style',
                'Wildlife scene, natural habitat, National Geographic quality'
            ]
        }

        prompts_list = base_prompts.get(story_type, base_prompts['documentary'])

        # Cycle through base prompts to reach target count
        prompts = []
        for i in range(count):
            base_prompt = prompts_list[i % len(prompts_list)]
            prompts.append({
                'prompt': f"{base_prompt}, {image_style} style, 16:9 format",
                'scene_number': i + 1
            })

        return prompts

    def _pad_prompts(
        self,
        prompts: List[Dict],
        target_count: int,
        story_type: str,
        image_style: str
    ) -> List[Dict]:
        """Add more prompts to reach target count"""

        while len(prompts) < target_count:
            # Duplicate and modify existing prompts
            base_prompt = prompts[len(prompts) % len(prompts)]['prompt']
            new_prompt = f"{base_prompt}, alternate angle, different composition"
            prompts.append({
                'prompt': new_prompt,
                'scene_number': len(prompts) + 1
            })

        return prompts


# Singleton instance
image_prompt_extractor = ImagePromptExtractor()


def extract_image_prompts(script: str, num_images: int, story_type: str = 'scary_horror', image_style: str = 'cinematic') -> List[Dict]:
    """Convenience function"""
    return image_prompt_extractor.extract_prompts(script, num_images, story_type, image_style)


if __name__ == "__main__":
    print("\n🧪 Testing Image Prompt Extractor...\n")

    test_script = """
    The old lighthouse stood alone on the rocky cliff, its light long extinguished.
    Sarah approached cautiously, the wind howling around her. Inside, darkness consumed everything.
    Strange whispers echoed from below. She descended the spiral staircase, each step creaking ominously.
    At the bottom, she found a hidden chamber. Ancient symbols covered the walls.
    """

    prompts = extract_image_prompts(
        script=test_script,
        num_images=5,
        story_type='scary_horror',
        image_style='cinematic'
    )

    print(f"\nExtracted {len(prompts)} prompts:")
    for p in prompts:
        print(f"  {p['scene_number']}. {p['prompt'][:80]}...")

    print("\n✅ Image Prompt Extractor ready!")
