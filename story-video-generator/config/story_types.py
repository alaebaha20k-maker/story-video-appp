"""
🎭 COMPLETE STORY TYPE SYSTEM - All Niches
"""

STORY_TYPES = {
    # EMOTIONS
    "emotional_heartwarming": {
        "name": "Emotional & Heartwarming",
        "description": "Stories that touch the heart and inspire",
        "tone": "warm, uplifting, inspiring, hopeful",
        "pacing": "medium, building to emotional climax",
        "example": "A stranger's small act of kindness changes everything",
        "voice_style": "gentle, warm, sincere delivery with emotional peaks",
        "visual_style": "soft lighting, warm colors, intimate moments, heartfelt expressions",
        "key_elements": ["personal growth", "human connection", "hope", "redemption", "kindness"]
    },
    
    "scary_horror": {
        "name": "Scary & Horror",
        "description": "Terrifying stories that keep you up at night",
        "tone": "dark, ominous, tense, unsettling",
        "pacing": "slow burn tension, sudden shocks",
        "example": "They thought they were alone in the house. They were wrong.",
        "voice_style": "suspenseful whispers, sudden intensity, building dread",
        "visual_style": "dark shadows, eerie lighting, unsettling angles, horror atmosphere",
        "key_elements": ["creeping dread", "jump scares", "supernatural terror", "isolation", "the unknown"]
    },
    
    "surprising_twist": {
        "name": "Surprising Twist",
        "description": "Mind-bending stories with unexpected endings",
        "tone": "mysterious, clever, unpredictable",
        "pacing": "steady buildup, shocking reveal",
        "example": "Everything you think you know is about to change"
    },
    
    "tragic_sad": {
        "name": "Tragic & Sad",
        "description": "Heart-breaking stories of loss and struggle",
        "tone": "melancholic, poignant, heavy, reflective",
        "pacing": "gradual descent, powerful emotional weight",
        "example": "Some goodbyes hurt more than others"
    },
    
    "motivational_inspiring": {
        "name": "Motivational & Inspiring",
        "description": "Stories of triumph against all odds",
        "tone": "powerful, determined, victorious, uplifting",
        "pacing": "rising action, triumphant climax",
        "example": "When the world said no, they said watch me"
    },
    
    # GENRES
    "true_crime": {
        "name": "True Crime",
        "description": "Real criminal cases and investigations",
        "tone": "investigative, serious, factual, gripping",
        "pacing": "methodical buildup, shocking revelations",
        "example": "The detective thought it was routine. The evidence proved otherwise.",
        "voice_style": "investigative tone, suspenseful delivery, factual but gripping",
        "visual_style": "crime scene aesthetic, noir lighting, investigation atmosphere, evidence close-ups",
        "key_elements": ["investigation", "clues", "suspects", "justice", "shocking truths"]
    },
    
    "mystery_thriller": {
        "name": "Mystery & Thriller",
        "description": "Suspenseful whodunnit stories",
        "tone": "suspenseful, noir, tense, clever",
        "pacing": "constant tension, clues revealed strategically",
        "example": "Every clue pointed to the wrong person"
    },
    
    "historical_documentary": {
        "name": "Historical Documentary",
        "description": "Real events from history told dramatically",
        "tone": "authoritative, educational, dramatic, factual",
        "pacing": "narrative documentary style",
        "example": "What history books left out changes everything",
        "voice_style": "authoritative narrator, clear enunciation, dramatic pauses for impact",
        "visual_style": "period-appropriate imagery, archival aesthetic, dramatic historical recreation",
        "key_elements": ["historical accuracy", "compelling facts", "human drama", "context", "revelations"]
    },
    
    "supernatural_paranormal": {
        "name": "Supernatural & Paranormal",
        "description": "Unexplained phenomena and ghost stories",
        "tone": "eerie, mysterious, otherworldly, chilling",
        "pacing": "building dread, supernatural escalation",
        "example": "Science couldn't explain what happened next"
    },
    
    "adventure_survival": {
        "name": "Adventure & Survival",
        "description": "Against-the-odds survival stories",
        "tone": "intense, dramatic, visceral, raw",
        "pacing": "escalating danger, desperate solutions",
        "example": "127 hours. One decision. No second chances."
    },
    
    "sci_fi_future": {
        "name": "Sci-Fi & Future",
        "description": "Futuristic and technological stories",
        "tone": "innovative, speculative, cerebral, visionary",
        "pacing": "concept-driven, mind-expanding",
        "example": "The AI made a choice that should have been impossible"
    },
    
    "fantasy_magical": {
        "name": "Fantasy & Magical",
        "description": "Magical worlds and epic quests",
        "tone": "enchanting, epic, wondrous, mythical",
        "pacing": "hero's journey structure",
        "example": "The forgotten prophecy was about to come true"
    },
    
    "comedy_funny": {
        "name": "Comedy & Funny",
        "description": "Hilarious and absurd stories",
        "tone": "lighthearted, witty, absurd, entertaining",
        "pacing": "quick, punchy, comedic timing",
        "example": "What could possibly go wrong? Everything. Hilariously."
    },
    
    "romantic_love": {
        "name": "Romantic & Love",
        "description": "Love stories that captivate",
        "tone": "passionate, tender, emotional, intimate",
        "pacing": "emotional buildup, romantic climax",
        "example": "Two strangers. One moment. Changed everything forever.",
        "voice_style": "intimate, tender, heartfelt with romantic crescendos",
        "visual_style": "soft focus, golden hour lighting, intimate close-ups, romantic atmosphere",
        "key_elements": ["first meetings", "chemistry", "vulnerability", "passion", "connection"]
    },
    
    "war_military": {
        "name": "War & Military",
        "description": "Combat and military operations",
        "tone": "intense, gritty, heroic, brutal",
        "pacing": "tactical, explosive, strategic",
        "example": "Behind enemy lines. No backup. Mission critical."
    },
    
    "biographical_life": {
        "name": "Biographical Life Story",
        "description": "Real people's extraordinary lives",
        "tone": "personal, intimate, authentic, reflective",
        "pacing": "life journey structure",
        "example": "From nobody to legend. This is how it happened."
    },
    
    "conspiracy_mystery": {
        "name": "Conspiracy & Cover-up",
        "description": "Hidden truths and conspiracies",
        "tone": "suspicious, investigative, revelatory",
        "pacing": "uncovering layers, shocking truths",
        "example": "What they don't want you to know"
    },
    
    "anime_style": {
        "name": "Anime-Style Story",
        "description": "Dramatic anime-inspired narratives",
        "tone": "dramatic, emotional, action-packed, stylized",
        "pacing": "episodic structure, dramatic reveals",
        "example": "The power awakened at the worst possible moment"
    },
    
    "psychological_mind": {
        "name": "Psychological Mind-Bender",
        "description": "Mind games and psychological thrillers",
        "tone": "cerebral, unsettling, thought-provoking",
        "pacing": "mental spiral, reality-questioning",
        "example": "Sanity is more fragile than you think"
    },
    
    "nature_wildlife": {
        "name": "Nature & Wildlife",
        "description": "Animal kingdom and natural world",
        "tone": "majestic, educational, awe-inspiring",
        "pacing": "observational, dramatic natural events",
        "example": "In nature, survival is the only rule"
    },
}