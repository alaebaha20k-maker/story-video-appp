"""
🎨 IMAGE PROMPT EXTRACTOR - Stage 2 Gemini AI
Analyzes finished script and generates SDXL-optimized image prompts

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

# Use Gemini Flash for speed (Stage 2 is fast analysis)
# FIXED: Use correct model name for v1beta API
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
        self.max_chunk_size = 3000  # Characters per chunk
        self.delay_between_requests = 2  # Seconds between API calls

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

        # Map style to SDXL-optimized descriptions
        style_descriptions = {
            'cinematic': 'cinematic film still, movie quality, professional cinematography, dramatic lighting',
            'documentary': 'documentary photography, National Geographic style, photorealistic',
            'anime': 'anime art style, vibrant colors, Japanese animation, detailed illustration',
            'horror': 'dark horror atmosphere, terrifying, creepy, unsettling, dramatic shadows',
            'comic': 'comic book style, bold lines, graphic novel art, illustrated',
            'historical': 'historical photograph, vintage sepia, old photo aesthetic',
            'scifi': 'sci-fi futuristic, cyberpunk, neon lighting, high-tech',
            'noir': 'film noir, high contrast black and white, dramatic shadows',
            'fantasy': 'fantasy art, magical atmosphere, epic fantasy illustration',
            '3d_render': 'photorealistic 3D render, CGI, highly detailed',
            'sketch': 'pencil sketch, hand-drawn, artistic sketch style',
            'watercolor': 'watercolor painting, soft colors, artistic watercolor',
            'oil_painting': 'oil painting, classical art style, painterly',
            'retro': 'retro 1970s-1980s aesthetic, vintage colors'
        }

        style_desc = style_descriptions.get(image_style, 'cinematic film still')

        prompt = f"""You are a visual prompt expert for SDXL-Turbo AI image generation.

TASK: Analyze this script excerpt and generate EXACTLY {target_prompts} SDXL-optimized image prompts for the most important visual scenes.

SCRIPT EXCERPT:
{chunk_text}

REQUIREMENTS:
1. Generate EXACTLY {target_prompts} prompts
2. Each prompt must be detailed and visual (not abstract)
3. Focus on KEY MOMENTS that need illustration
4. Style: {style_desc}
5. Story type: {story_type}
6. Format: 16:9 landscape (1920x1080)
7. Include specific details: setting, characters, mood, lighting, atmosphere

SDXL-TURBO OPTIMIZATION:
- Use concrete visual descriptions (not emotions)
- Specify lighting, colors, composition
- Mention camera angle if relevant
- Keep prompts focused (50-100 words each)
- Avoid: text, logos, faces with text, copyrighted characters

OUTPUT FORMAT (EXACTLY {target_prompts} prompts):
1. [Detailed SDXL prompt for scene 1]
2. [Detailed SDXL prompt for scene 2]
...
{target_prompts}. [Detailed SDXL prompt for scene {target_prompts}]

Generate the prompts now:"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text

            # Parse numbered prompts
            prompts = self._parse_prompts_from_response(response_text, target_prompts)

            return prompts

        except Exception as e:
            print(f"      ❌ Error: {e}")
            # Return fallback prompts
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
