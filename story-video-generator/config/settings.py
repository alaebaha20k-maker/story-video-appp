"""
⚙️ SETTINGS - Configuration for the video generator
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output"
CACHE_DIR = BASE_DIR / "cache"
TEMP_DIR = OUTPUT_DIR / "temp"

# Video settings
VIDEO_SETTINGS = {
    "resolution": (1920, 1080),  # 1080p
    "fps": 30,
    "codec": "libx264",
    "audio_codec": "aac",
    "preset": "medium",
    "bitrate": "8000k"
}

GEMINI_SETTINGS = {
    "model": "gemini-2.5-pro",  # ← MOST POWERFUL!
    "temperature": 0.7,
    "max_output_tokens": 8192
}

# Script length configurations
SCRIPT_LENGTHS = {
    "10k": {
        "characters": 10000,
        "words": 2000,
        "audio_minutes": "10-12 minutes",
        "images_needed": 5,
        "api_calls": 1
    },
    "30k": {
        "characters": 30000,
        "words": 6000,
        "audio_minutes": "30-35 minutes",
        "images_needed": 10,
        "api_calls": 1
    },
    "70k": {
        "characters": 70000,
        "words": 14000,
        "audio_minutes": "70-80 minutes",
        "images_needed": 25,
        "api_calls": 2
    },
    "100k": {
        "characters": 100000,
        "words": 20000,
        "audio_minutes": "100-120 minutes",
        "images_needed": 30,
        "api_calls": 3
    }
}

# FLUX image generation settings
FLUX_SETTINGS = {
    "model": "black-forest-labs/FLUX.1-schnell",
    "width": 1024,
    "height": 1024,
    "steps": 4,
    "guidance_scale": 0
}

# Image settings
IMAGE_SETTINGS = {
    "resolution": (1920, 1080),
    "quality": 95,
    "format": "PNG"
}

# ═══════════════════════════════════════════════════════════════
# 🎤 VOICE ENGINE SETTINGS - KOKORO TTS (PRIMARY) + EDGE-TTS (BACKUP)
# ═══════════════════════════════════════════════════════════════

# Voice engine priority (will try in this order)
VOICE_ENGINE = "edge"  # Options: "kokoro", "edge"
VOICE_PRIORITY = ["edge"]  # Fallback order

# 🎤 KOKORO TTS SETTINGS (disabled)
KOKORO_SETTINGS = {
    "enabled": False,
    "device": "cpu",  # Change to "cuda" for GPU acceleration (210× faster!)
    "sample_rate": 24000,
    "default_voice": "af_bella",  # Warm female voice
    "default_speed": 1.0,
    
    # Voice categories for easy selection
    "voice_categories": {
        # Narrators
        "narrator_male_deep": "am_adam",           # Deep, authoritative
        "narrator_male_professional": "am_michael", # Clear, professional
        "narrator_female_warm": "af_bella",        # Warm, engaging
        "narrator_female_professional": "af_sarah", # Professional, clear
        "narrator_female_energetic": "af_nova",    # Energetic, dynamic
        
        # British voices
        "narrator_british_female": "bf_emma",      # British female
        "narrator_british_male": "bm_george",      # British male
        
        # Story-specific
        "horror_narrator": "am_adam",              # Deep, ominous
        "documentary_narrator": "af_sarah",        # Professional, clear
        "mystery_narrator": "bf_emma",             # British, mysterious
        "fantasy_narrator": "af_nova",             # Energetic, epic
    }
}

# 🎤 EDGE-TTS SETTINGS (Backup, also FREE)
EDGE_TTS_SETTINGS = {
    "enabled": True,
    "default_voice": "en-US-GuyNeural",
    "rate": "+0%",
    "volume": "+0%",
    "output_format": "mp3",
    
    # Voice mapping
    "voice_categories": {
        "male_narrator_deep": "en-US-GuyNeural",
        "female_narrator": "en-US-AriaNeural",
        "female_young": "en-US-JennyNeural",
        "male_narrator_calm": "en-US-ChristopherNeural",
        "female_narrator_warm": "en-US-SaraNeural"
    }
}

# Voice settings (legacy support - maps to Kokoro)
VOICE_SETTINGS = KOKORO_SETTINGS.copy()

# Pexels API settings
PEXELS_SETTINGS = {
    "orientation": "landscape",
    "size": "large",
    "per_page": 15
}

# Niche styles
NICHE_STYLES = {
    "horror_paranormal": {
        "base_style": "dark cinematic horror, eerie atmosphere",
        "art_direction": "professional photography, dramatic lighting",
        "color_palette": "dark muted colors, deep shadows",
        "mood": "ominous and unsettling",
        "seed_base": 42
    },
    "mystery_thriller": {
        "base_style": "noir mystery, suspenseful atmosphere",
        "art_direction": "film noir style, dramatic composition",
        "color_palette": "high contrast, noir tones",
        "mood": "tense and mysterious",
        "seed_base": 100
    },
    "sci_fi": {
        "base_style": "futuristic sci-fi, cyberpunk aesthetic",
        "art_direction": "cinematic sci-fi, dramatic angles",
        "color_palette": "neon colors, blue and purple tones",
        "mood": "futuristic and otherworldly",
        "seed_base": 200
    },
    "documentary": {
        "base_style": "realistic documentary style",
        "art_direction": "natural photography, authentic",
        "color_palette": "natural colors, realistic tones",
        "mood": "informative and authentic",
        "seed_base": 300
    },
    "fantasy": {
        "base_style": "epic fantasy, magical atmosphere",
        "art_direction": "fantasy art, dramatic composition",
        "color_palette": "vibrant colors, magical glow",
        "mood": "enchanting and epic",
        "seed_base": 400
    }
}

# Effect types
EFFECT_TYPES = [
    "simple_zoom",
    "zoom_in",
    "zoom_out",
    "pan_right",
    "pan_left",
    "zoom_pan",
    "static"
]

# Transition types
TRANSITION_TYPES = [
    "crossfade",
    "fade",
    "none"
]