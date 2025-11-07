"""
🎨 ULTRA-PRO IMAGE PROMPTS - Cinema Quality, All Niches, All Styles
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ImageStyle:
    """Image generation style definition"""
    name: str
    base_style: str
    camera: str
    lighting: str
    quality: str
    negative: str


# ALL IMAGE STYLES YOU CAN CHOOSE FROM
IMAGE_STYLES = {
    # PHOTOREALISTIC STYLES
    "cinematic_film": ImageStyle(
        name="Cinematic Film",
        base_style="cinematic film still, professional movie screenshot",
        camera="shot on ARRI Alexa 65, anamorphic lens, 35mm, shallow depth of field",
        lighting="dramatic cinematic lighting, volumetric fog, professional color grading",
        quality="8k uhd, raw photo, film grain, masterpiece, award winning cinematography",
        negative="cartoon, anime, drawing, painting, amateur, low quality"
    ),
    
    "documentary_real": ImageStyle(
        name="Documentary Realistic",
        base_style="documentary photography, photojournalism style, real life",
        camera="shot on Canon EOS R5, 50mm lens, natural perspective",
        lighting="natural lighting, authentic atmosphere, real world",
        quality="high resolution, professional photography, national geographic style",
        negative="staged, artificial, cartoon, fake, rendered"
    ),
    
    "dark_noir": ImageStyle(
        name="Dark Noir",
        base_style="film noir style, dark moody atmosphere, high contrast",
        camera="vintage camera aesthetic, 50mm prime lens, dramatic angles",
        lighting="low key lighting, deep shadows, single light source, chiaroscuro",
        quality="black and white photography, grain, classic film stock",
        negative="bright, colorful, cheerful, cartoon"
    ),
    
    "horror_creepy": ImageStyle(
        name="Horror Creepy",
        base_style="horror movie still, terrifying atmosphere, unsettling",
        camera="handheld camera, found footage style, Dutch angle",
        lighting="eerie lighting, shadows, dim light, ominous atmosphere",
        quality="grainy, desaturated colors, disturbing, professional horror cinematography",
        negative="bright, happy, cartoon, cute"
    ),
    
    # STYLIZED REALISTIC
    "anime_style": ImageStyle(
        name="Anime Style",
        base_style="anime style, manga illustration, detailed anime art",
        camera="dynamic anime composition, dramatic perspective",
        lighting="anime lighting, cel shaded, vibrant colors",
        quality="highly detailed, professional anime art, studio quality",
        negative="3d, realistic, photograph, western cartoon"
    ),
    
    "comic_book": ImageStyle(
        name="Comic Book",
        base_style="comic book art style, graphic novel illustration",
        camera="dramatic comic panel composition, dynamic angles",
        lighting="bold shadows, high contrast, comic book lighting",
        quality="professional comic art, detailed linework, vibrant colors",
        negative="photograph, realistic, 3d render, blurry"
    ),
    
    "oil_painting": ImageStyle(
        name="Oil Painting",
        base_style="oil painting, classical art style, painted",
        camera="portrait composition, artistic framing",
        lighting="rembrandt lighting, painted light, artistic",
        quality="masterpiece painting, museum quality, detailed brushwork",
        negative="photograph, digital art, cartoon, modern"
    ),
    
    # SPECIALIZED STYLES
    "historical_photo": ImageStyle(
        name="Historical Photography",
        base_style="historical photograph, vintage photo, period accurate",
        camera="vintage camera, old photography equipment, sepia or black and white",
        lighting="natural period lighting, authentic atmosphere",
        quality="archival photo, historical accuracy, aged photograph",
        negative="modern, digital, colorful, cartoon"
    ),
    
    "sci_fi_future": ImageStyle(
        name="Sci-Fi Futuristic",
        base_style="sci-fi concept art, futuristic setting, cyberpunk aesthetic",
        camera="wide angle lens, establishing shot, sci-fi cinematography",
        lighting="neon lighting, holographic glow, futuristic atmosphere",
        quality="highly detailed, concept art quality, trending on artstation",
        negative="medieval, historical, low tech, cartoon"
    ),
    
    "fantasy_epic": ImageStyle(
        name="Fantasy Epic",
        base_style="epic fantasy art, magical world, fantasy illustration",
        camera="heroic composition, wide cinematic shot",
        lighting="magical lighting, ethereal glow, dramatic sky",
        quality="concept art, highly detailed, fantasy masterpiece",
        negative="modern, realistic, boring, plain"
    ),
    
    "sketch_drawing": ImageStyle(
        name="Sketch Drawing",
        base_style="detailed pencil sketch, charcoal drawing, hand drawn",
        camera="sketch composition, artistic perspective",
        lighting="sketch shading, crosshatching, tonal values",
        quality="professional illustration, detailed linework, artist quality",
        negative="photograph, color, digital, messy"
    ),
    
    "watercolor": ImageStyle(
        name="Watercolor Painting",
        base_style="watercolor painting, soft artistic style",
        camera="artistic composition, painterly framing",
        lighting="soft diffused light, watercolor technique",
        quality="professional watercolor art, delicate details, artistic",
        negative="photograph, digital, harsh, cartoon"
    ),
    
    # MODERN DIGITAL
    "3d_render": ImageStyle(
        name="3D Render",
        base_style="3d render, cgi, digital art, unreal engine",
        camera="3d camera, perfect composition, professional rendering",
        lighting="ray tracing, global illumination, volumetric lighting",
        quality="octane render, 8k, photorealistic 3d, highly detailed",
        negative="2d, flat, sketch, amateur"
    ),
    
    "retro_vintage": ImageStyle(
        name="Retro Vintage",
        base_style="retro aesthetic, vintage style, 1970s 1980s look",
        camera="vintage camera look, film photography",
        lighting="nostalgic lighting, warm tones, vintage atmosphere",
        quality="authentic vintage, retro colors, period accurate",
        negative="modern, digital, sharp, clean"
    ),
}


# NICHE-SPECIFIC ENHANCEMENTS
NICHE_PROMPTS = {
    "scary_horror": {
        "mood": "terrifying, ominous, unsettling, dread",
        "atmosphere": "dark fog, eerie shadows, abandoned",
        "color": "desaturated, muted colors, dark palette",
        "details": "disturbing details, creepy atmosphere"
    },
    
    "emotional_heartwarming": {
        "mood": "warm, touching, emotional, tender",
        "atmosphere": "soft light, cozy, intimate",
        "color": "warm tones, golden hour, soft colors",
        "details": "emotional expressions, human connection"
    },
    
    "true_crime": {
        "mood": "serious, gritty, realistic, documentary",
        "atmosphere": "authentic, real world, investigative",
        "color": "realistic colors, muted professional tones",
        "details": "forensic details, evidence, real locations"
    },
    
    "anime_style": {
        "mood": "dramatic, emotional, dynamic",
        "atmosphere": "anime world, stylized environment",
        "color": "vibrant anime colors, cel shaded",
        "details": "anime character design, expressive"
    },
    
    "historical_documentary": {
        "mood": "authoritative, educational, authentic",
        "atmosphere": "period accurate, historical setting",
        "color": "period appropriate colors, aged look",
        "details": "historically accurate details, period costumes"
    },
    
    "sci_fi_future": {
        "mood": "futuristic, high tech, advanced",
        "atmosphere": "neon lights, holographic, cyberpunk",
        "color": "neon blues, purples, cyan, electric colors",
        "details": "technology, circuits, holograms, future tech"
    },
    
    "fantasy_magical": {
        "mood": "magical, enchanting, wondrous, epic",
        "atmosphere": "mystical fog, magical glow, fantasy world",
        "color": "vibrant fantasy colors, magical light",
        "details": "magic effects, fantasy creatures, enchanted"
    },
    
    "war_military": {
        "mood": "intense, gritty, heroic, brutal",
        "atmosphere": "battlefield, combat zone, military",
        "color": "desaturated, war tones, dust and smoke",
        "details": "military equipment, weapons, uniforms"
    },
    
    "nature_wildlife": {
        "mood": "majestic, natural, awe-inspiring",
        "atmosphere": "natural habitat, wilderness, pristine",
        "color": "natural colors, earth tones, vibrant nature",
        "details": "wildlife, animals, natural environment"
    },
}


class UltraImagePromptBuilder:
    """Build ultra-professional image prompts"""
    
    def __init__(self, image_style: str = "cinematic_film", story_type: str = "scary_horror"):
        """
        Initialize with chosen styles
        
        Args:
            image_style: Key from IMAGE_STYLES
            story_type: Key from NICHE_PROMPTS
        """
        
        if image_style not in IMAGE_STYLES:
            print(f"⚠️ Unknown style: {image_style}, using cinematic_film")
            image_style = "cinematic_film"
        
        if story_type not in NICHE_PROMPTS:
            print(f"⚠️ Unknown niche: {story_type}, using defaults")
            story_type = "scary_horror"
        
        self.style = IMAGE_STYLES[image_style]
        self.niche = NICHE_PROMPTS.get(story_type, NICHE_PROMPTS["scary_horror"])
        self.character_descriptions = {}
    
    def register_character(self, name: str, description: str):
        """Register character for consistent appearance"""
        self.character_descriptions[name] = description
    
    def build_scene_prompt(
        self,
        scene_description: str,
        scene_type: str = "establishing",
        characters: List[str] = None
    ) -> Dict:
        """
        Build complete professional prompt
        
        Args:
            scene_description: What's happening in the scene
            scene_type: establishing, character_closeup, action, atmospheric, detail
            characters: List of character names in scene
        """
        
        # Build character part
        character_part = ""
        if characters:
            char_descs = []
            for char in characters:
                if char in self.character_descriptions:
                    char_descs.append(self.character_descriptions[char])
                else:
                    char_descs.append(f"{char} (character)")
            character_part = ", ".join(char_descs) + ", "
        
        # Scene type specific
        scene_prefix = {
            "establishing": "wide establishing shot, ",
            "character_closeup": "close-up portrait, face detail, emotional expression, ",
            "action": "dynamic action shot, motion, dramatic moment, ",
            "atmospheric": "atmospheric shot, mood and environment, ",
            "detail": "extreme close-up, important detail, symbolic, ",
            "location": "location shot, environment, setting, "
        }.get(scene_type, "")
        
        # Build complete prompt
        full_prompt = (
            f"{self.style.base_style}, "
            f"{scene_prefix}"
            f"{character_part}"
            f"{scene_description}, "
            f"{self.niche['atmosphere']}, "
            f"{self.niche['mood']}, "
            f"{self.style.camera}, "
            f"{self.style.lighting}, "
            f"{self.niche['color']}, "
            f"{self.niche['details']}, "
            f"{self.style.quality}"
        )
        
        # Clean up
        full_prompt = " ".join(full_prompt.split())  # Remove extra spaces
        full_prompt = full_prompt.replace(" ,", ",")  # Fix spacing
        
        return {
            "prompt": full_prompt,
            "negative_prompt": self.style.negative,
            "scene_type": scene_type,
            "style_name": self.style.name
        }
    
    def build_character_reference(self, name: str, description: str) -> str:
        """Build consistent character description"""
        
        base = f"{name}: {description}"
        
        # Add style-specific character traits
        if "anime" in self.style.name.lower():
            base += ", anime character design, detailed anime style"
        elif "realistic" in self.style.name.lower() or "cinematic" in self.style.name.lower():
            base += ", photorealistic human, detailed features, realistic"
        elif "comic" in self.style.name.lower():
            base += ", comic book character design, dynamic art style"
        
        return base


# Quick access functions
def create_prompt_builder(image_style: str, story_type: str) -> UltraImagePromptBuilder:
    """Create a prompt builder with chosen styles"""
    return UltraImagePromptBuilder(image_style, story_type)


def list_available_styles() -> Dict[str, List[str]]:
    """List all available styles"""
    return {
        "image_styles": list(IMAGE_STYLES.keys()),
        "story_niches": list(NICHE_PROMPTS.keys())
    }


if __name__ == "__main__":
    print("\n🎨 ULTRA IMAGE PROMPT SYSTEM\n")
    
    # Show available styles
    styles = list_available_styles()
    
    print("📷 IMAGE STYLES:")
    for style in styles["image_styles"][:5]:
        print(f"   - {style}")
    print(f"   ... and {len(styles['image_styles']) - 5} more\n")
    
    print("🎬 STORY NICHES:")
    for niche in styles["story_niches"][:5]:
        print(f"   - {niche}")
    print(f"   ... and {len(styles['story_niches']) - 5} more\n")
    
    # Test prompt
    builder = create_prompt_builder("cinematic_film", "scary_horror")
    builder.register_character("Sarah", "young woman, 25 years old, brown hair, terrified expression")
    
    prompt = builder.build_scene_prompt(
        "Sarah stands in a dark abandoned hospital corridor",
        scene_type="character_closeup",
        characters=["Sarah"]
    )
    
    print("✅ EXAMPLE PROMPT:")
    print(f"   {prompt['prompt'][:200]}...\n")
    
    print("✅ System ready!\n")