"""
🎨 PROMPT BUILDER - Optimizes prompts for AI image generation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.settings import NICHE_STYLES


class PromptBuilder:
    """Builds optimized prompts for consistent AI image generation"""
    
    def __init__(self, niche: str = "horror_paranormal"):
        self.niche = niche
        self.style = NICHE_STYLES.get(niche, NICHE_STYLES["horror_paranormal"])
        self.seed_base = self.style.get("seed_base", 42)
    
    def build_image_prompt(
        self,
        scene_description: str,
        scene_number: int = 0,
        custom_style: str = None
    ) -> dict:
        """Build complete prompt with style consistency"""
        
        # Base style elements
        base_style = custom_style or self.style["base_style"]
        art_direction = self.style["art_direction"]
        color_palette = self.style["color_palette"]
        mood = self.style["mood"]
        
        # Combine into full prompt
        full_prompt = f"{scene_description}, {base_style}, {art_direction}, {color_palette}, {mood}"
        
        # Clean up the prompt
        full_prompt = self._clean_prompt(full_prompt)
        
        # Generate consistent seed
        seed = self.seed_base + scene_number
        
        return {
            "prompt": full_prompt,
            "seed": seed,
            "scene_number": scene_number,
            "style": self.niche
        }
    
    def build_batch_prompts(
        self,
        scene_descriptions: list,
        custom_style: str = None
    ) -> list:
        """Build prompts for multiple scenes"""
        prompts = []
        
        for i, description in enumerate(scene_descriptions):
            prompt_data = self.build_image_prompt(
                description,
                scene_number=i,
                custom_style=custom_style
            )
            prompts.append(prompt_data)
        
        return prompts
    
    def _clean_prompt(self, prompt: str) -> str:
        """Clean and optimize prompt"""
        # Remove multiple spaces
        prompt = " ".join(prompt.split())
        
        # Remove duplicate phrases
        words = prompt.split(", ")
        seen = set()
        cleaned = []
        for word in words:
            if word.lower() not in seen:
                seen.add(word.lower())
                cleaned.append(word)
        
        return ", ".join(cleaned)
    
    def add_quality_tags(self, prompt: str) -> str:
        """Add quality enhancement tags"""
        quality_tags = [
            "highly detailed",
            "professional quality",
            "8k resolution",
            "sharp focus"
        ]
        return f"{prompt}, {', '.join(quality_tags)}"
    
    def set_niche(self, niche: str):
        """Change the niche style"""
        if niche in NICHE_STYLES:
            self.niche = niche
            self.style = NICHE_STYLES[niche]
            self.seed_base = self.style.get("seed_base", 42)
        else:
            raise ValueError(f"Unknown niche: {niche}")
    
    def get_available_niches(self) -> list:
        """Get list of available niche styles"""
        return list(NICHE_STYLES.keys())
    
    def get_style_info(self) -> dict:
        """Get current style information"""
        return {
            "niche": self.niche,
            "base_style": self.style["base_style"],
            "art_direction": self.style["art_direction"],
            "color_palette": self.style["color_palette"],
            "mood": self.style["mood"],
            "seed_base": self.seed_base
        }


def build_prompt(scene_description: str, niche: str = "horror_paranormal") -> dict:
    """Quick function to build a single prompt"""
    builder = PromptBuilder(niche)
    return builder.build_image_prompt(scene_description)


if __name__ == "__main__":
    print("\n🧪 Testing PromptBuilder...\n")
    
    builder = PromptBuilder("horror_paranormal")
    
    # Test single prompt
    scene = "A dark abandoned lighthouse on a stormy cliff"
    prompt_data = builder.build_image_prompt(scene, scene_number=0)
    
    print("✅ Generated Prompt:")
    print(f"   Scene: {scene}")
    print(f"   Full Prompt: {prompt_data['prompt'][:100]}...")
    print(f"   Seed: {prompt_data['seed']}")
    
    # Test batch prompts
    scenes = [
        "Dark lighthouse exterior at night",
        "Inside the lighthouse keeper's quarters",
        "Spiral staircase going up"
    ]
    
    batch = builder.build_batch_prompts(scenes)
    print(f"\n✅ Generated {len(batch)} prompts with consistent style")
    
    # Test available niches
    niches = builder.get_available_niches()
    print(f"\n✅ Available niches: {', '.join(niches)}")
    
    # Test style info
    info = builder.get_style_info()
    print(f"\n✅ Current style: {info['niche']}")
    print(f"   Base: {info['base_style']}")
    print(f"   Mood: {info['mood']}")
    
    print("\n✅ PromptBuilder working perfectly!\n")