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
    "model": "gemini-1.5-flash-latest",  # ← FREE MODEL! (Gemini 1.5 Flash - Stable)
    "temperature": 0.7,
    "max_output_tokens": 8192  # Free tier: 15 RPM, 1M TPM, 1500 RPD
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

# FLUX.1 Schnell image generation settings (via Pollinations AI)
FLUX_SETTINGS = {
    "model": "flux",  # FLUX.1 Schnell via Pollinations
    "width": 1024,
    "height": 1024,
    "nologo": True,
    "enhance": True,
    "description": "FLUX.1 Schnell - Fastest high-quality model from Black Forest Labs"
}

# Image settings
IMAGE_SETTINGS = {
    "resolution": (1920, 1080),
    "quality": 95,
    "format": "PNG"
}

# ═══════════════════════════════════════════════════════════════
# 🎤 VOICE ENGINE SETTINGS - EDGE-TTS ONLY
# ═══════════════════════════════════════════════════════════════

# Voice engine priority (Edge is the only supported option)
VOICE_ENGINE = "edge"
VOICE_PRIORITY = ["edge"]

# 🎤 EDGE-TTS SETTINGS (Primary)
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
        "female_narrator_warm": "en-US-SaraNeural",
        "male_narrator_dramatic": "en-US-DavisNeural",
        "female_storyteller": "en-GB-LibbyNeural",
        "narrator_british_female": "en-GB-SoniaNeural",
        "narrator_british_male": "en-GB-RyanNeural",
    }
}


# Human-friendly aliases for Edge voices used by API routes.
EDGE_VOICE_MAP = {
    "male_narrator_deep": "en-US-GuyNeural",
    "male_narrator_calm": "en-US-ChristopherNeural",
    "male_narrator_dramatic": "en-US-DavisNeural",
    "female_narrator": "en-US-AriaNeural",
    "female_narrator_warm": "en-US-SaraNeural",
    "female_storyteller": "en-GB-LibbyNeural",
    "female_young": "en-US-JennyNeural",
    "narrator_british_female": "en-GB-SoniaNeural",
    "narrator_british_male": "en-GB-RyanNeural",
}


def resolve_edge_voice(voice_id=None):
    """Return the configured Edge voice identifier."""
    if voice_id:
        return EDGE_VOICE_MAP.get(voice_id, voice_id)
    return EDGE_TTS_SETTINGS.get("default_voice", "en-US-AriaNeural")


def get_voice_engine_and_id(requested_engine=None, requested_voice=None):
    """Resolve the voice engine and identifier expected by downstream code."""
    engine = "edge"
    if requested_engine and requested_engine.lower() != "edge":
        print(f"⚠️ Voice engine '{requested_engine}' requested but Edge-TTS is enforced.")

    voice_id = resolve_edge_voice(requested_voice)
    return engine, voice_id

# Voice settings consumed by the Edge-only TTSEngine helper
VOICE_SETTINGS = EDGE_TTS_SETTINGS.copy()

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