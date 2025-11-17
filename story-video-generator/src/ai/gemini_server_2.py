"""
🎨 GEMINI SERVER 2 - Image Prompt Generation
Separate server using different API key for generating image prompts from script
"""

import google.generativeai as genai
from typing import List, Dict
import re

class GeminiServer2:
    """
    Gemini Server 2 - Dedicated to generating image prompts from scripts
    Uses separate API key from Server 1
    """

    def __init__(self, api_key: str):
        """
        Initialize Gemini Server 2 with dedicated API key

        Args:
            api_key: Separate API key for image prompt generation
        """
        if not api_key:
            raise ValueError("Gemini Server 2 requires API key!")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config={
                "temperature": 0.8,  # More creative for visual descriptions
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )

        print(f"✅ Gemini Server 2 initialized")
        print(f"   Model: gemini-2.0-flash-exp")
        print(f"   Purpose: Image prompt generation")

    def generate_image_prompts(
        self,
        script: str,
        num_images: int,
        story_type: str,
        image_style: str
    ) -> List[str]:
        """
        Generate detailed image prompts from script

        Args:
            script: The complete script from Server 1
            num_images: Number of image prompts to generate
            story_type: Type of story (scary_horror, romance, etc.)
            image_style: Style of images (cinematic_film, anime, etc.)

        Returns:
            List of detailed SDXL prompts
        """

        print(f"\n🎨 Gemini Server 2: Generating {num_images} image prompts...")
        print(f"   Script length: {len(script)} characters")
        print(f"   Story type: {story_type}")
        print(f"   Image style: {image_style}")

        # Build prompt for Gemini Server 2
        prompt = self._build_image_prompt_generation_prompt(
            script, num_images, story_type, image_style
        )

        try:
            response = self.model.generate_content(prompt)

            if not response or not response.text:
                raise Exception("Empty response from Gemini Server 2")

            # Parse image prompts from response
            image_prompts = self._parse_image_prompts(response.text, num_images)

            print(f"✅ Generated {len(image_prompts)} image prompts")
            for i, prompt in enumerate(image_prompts, 1):
                print(f"   {i}. {prompt[:60]}...")

            return image_prompts

        except Exception as e:
            print(f"❌ Gemini Server 2 error: {e}")
            # Fallback: Generate basic prompts from script
            return self._generate_fallback_prompts(script, num_images, story_type)

    def _build_image_prompt_generation_prompt(
        self,
        script: str,
        num_images: int,
        story_type: str,
        image_style: str
    ) -> str:
        """Build the prompt for Gemini to generate image prompts"""

        style_descriptions = {
            "cinematic_film": "cinematic film photography, dramatic lighting, professional cinematography",
            "anime": "anime style, manga aesthetic, vibrant colors, detailed anime art",
            "realistic": "photorealistic, ultra detailed, 8k resolution, professional photography",
            "horror_dark": "dark horror atmosphere, eerie lighting, unsettling composition",
            "fantasy_art": "epic fantasy art, magical atmosphere, dramatic fantasy illustration"
        }

        style_desc = style_descriptions.get(image_style, "cinematic film photography")

        prompt = f"""You are an expert at creating detailed SDXL image generation prompts.

Your task: Analyze the following script and generate {num_images} detailed image prompts that capture the key scenes from start to end.

SCRIPT:
{script}

REQUIREMENTS:

1. **Generate EXACTLY {num_images} image prompts**
2. **Each prompt must be 25-40 words**
3. **Follow this structure for each prompt:**
   - Main subject/action (what's happening)
   - Setting/environment (where)
   - Lighting and mood (how it looks)
   - Camera angle/composition
   - Style: {style_desc}

4. **Story type: {story_type}**
   - Ensure prompts match this genre's atmosphere

5. **Coverage:**
   - Prompt 1: Opening scene (sets the tone)
   - Middle prompts: Key story moments (evenly distributed)
   - Final prompt: Climax or conclusion

6. **SDXL-optimized:**
   - Use descriptive adjectives
   - Include lighting details (golden hour, dramatic shadows, etc.)
   - Specify composition (close-up, wide shot, etc.)
   - Add artistic style keywords

7. **Progression:**
   - Prompts should follow the story chronologically
   - Show clear visual variety between scenes
   - Match the emotional arc of the script

FORMAT YOUR RESPONSE AS:

PROMPT_1: [detailed 25-40 word SDXL prompt]
PROMPT_2: [detailed 25-40 word SDXL prompt]
...
PROMPT_{num_images}: [detailed 25-40 word SDXL prompt]

Generate the prompts now:"""

        return prompt

    def _parse_image_prompts(self, response_text: str, num_images: int) -> List[str]:
        """Parse image prompts from Gemini's response"""

        prompts = []

        # Try to extract prompts in format "PROMPT_X: ..."
        pattern = r'PROMPT_\d+:\s*(.+?)(?=\n(?:PROMPT_\d+:|$))'
        matches = re.findall(pattern, response_text, re.DOTALL | re.IGNORECASE)

        if matches:
            prompts = [match.strip() for match in matches]
        else:
            # Fallback: split by lines
            lines = [line.strip() for line in response_text.split('\n') if line.strip()]
            prompts = [line for line in lines if len(line) > 20][:num_images]

        # Ensure we have exactly num_images prompts
        while len(prompts) < num_images:
            prompts.append(prompts[-1] if prompts else "cinematic scene, dramatic lighting")

        return prompts[:num_images]

    def _generate_fallback_prompts(
        self,
        script: str,
        num_images: int,
        story_type: str
    ) -> List[str]:
        """Generate basic prompts if Gemini fails"""

        print("⚠️  Using fallback prompt generation")

        # Split script into chunks
        words = script.split()
        chunk_size = len(words) // num_images

        prompts = []
        for i in range(num_images):
            start = i * chunk_size
            end = start + chunk_size if i < num_images - 1 else len(words)
            chunk = ' '.join(words[start:end])[:100]

            prompt = f"{chunk}, {story_type} style, cinematic lighting, professional photography"
            prompts.append(prompt)

        return prompts

    def generate_image_prompts_chunked(
        self,
        script: str,
        num_images: int,
        story_type: str,
        image_style: str,
        chunk_size: int = 5
    ) -> List[str]:
        """
        Generate image prompts in chunks for very long scripts
        Useful for 60+ minute videos with many images

        Args:
            chunk_size: Generate this many prompts per API call
        """

        if num_images <= chunk_size:
            return self.generate_image_prompts(script, num_images, story_type, image_style)

        print(f"\n🎨 Using chunked generation: {num_images} prompts in chunks of {chunk_size}")

        all_prompts = []
        chunks_needed = (num_images + chunk_size - 1) // chunk_size

        # Split script into sections
        words = script.split()
        section_size = len(words) // chunks_needed

        for chunk_idx in range(chunks_needed):
            # Calculate how many prompts for this chunk
            remaining = num_images - len(all_prompts)
            prompts_this_chunk = min(chunk_size, remaining)

            # Get script section for this chunk
            start = chunk_idx * section_size
            end = start + section_size if chunk_idx < chunks_needed - 1 else len(words)
            section = ' '.join(words[start:end])

            print(f"   Chunk {chunk_idx + 1}/{chunks_needed}: {prompts_this_chunk} prompts")

            # Generate prompts for this section
            chunk_prompts = self.generate_image_prompts(
                section, prompts_this_chunk, story_type, image_style
            )

            all_prompts.extend(chunk_prompts)

        print(f"✅ Total prompts generated: {len(all_prompts)}")
        return all_prompts[:num_images]


# Global instance with Server 2 API key
GEMINI_SERVER_2_API_KEY = "AIzaSyC3lCI117uyVbJkFOXI6BffwlUCLSdYIH0"

gemini_server_2 = GeminiServer2(GEMINI_SERVER_2_API_KEY)
