# AI Video Generator - Options Reference

Quick reference guide for all available options in the application.

## Story Types (20 Options)

| ID | Name | Icon | Best For |
|----|------|------|----------|
| `scary_horror` | Scary Horror | 👻 | Suspense, fear, supernatural |
| `emotional_heartwarming` | Emotional Heartwarming | ❤️ | Family, friendship, love |
| `true_crime` | True Crime | 🔍 | Documentary, investigation, mystery |
| `anime_style` | Anime Style | 🎌 | Action, adventure, fantasy |
| `historical_documentary` | Historical Documentary | 📚 | History, education, biography |
| `surprising_twist` | Surprising Twist | 🎭 | Mystery, thriller, drama |
| `motivational_inspiring` | Motivational Inspiring | 💪 | Success, self-help, achievement |
| `mystery_thriller` | Mystery Thriller | 🕵️ | Detective, puzzle, suspense |
| `war_military` | War & Military | ⚔️ | Action, history, heroism |
| `nature_wildlife` | Nature & Wildlife | 🦁 | Animals, environment, science |
| `comedy_funny` | Comedy & Funny | 😂 | Entertainment, satire, parody |
| `romantic_love` | Romantic Love | 💑 | Romance, drama, emotions |
| `scifi_future` | Sci-Fi Future | 🚀 | Space, technology, future |
| `fantasy_epic` | Fantasy Epic | ⚔️ | Magic, dragons, mythology |
| `biographical` | Biographical | 📖 | History, inspiration, education |
| `conspiracy` | Conspiracy | 🕵️ | Mystery, investigation, thriller |
| `psychological` | Psychological | 🧠 | Thriller, horror, drama |
| `adventure_survival` | Adventure Survival | 🏔️ | Action, nature, survival |
| `paranormal` | Paranormal | 👻 | Mystery, horror, supernatural |
| `documentary_real` | Documentary Real | 🎬 | Education, news, real events |

## Image Styles (14 Options)

| ID | Name | Icon | Description |
|----|------|------|-------------|
| `cinematic` | Cinematic Film | 🎬 | Movie-quality production |
| `documentary` | Documentary Real | 📹 | National Geographic style |
| `anime` | Anime Style | 🎌 | Professional Japanese animation |
| `horror` | Horror Creepy | 👻 | Dark, terrifying atmosphere |
| `comic` | Comic Book | 📚 | Graphic novel illustration |
| `historical` | Historical Photo | 📸 | Vintage, sepia photography |
| `scifi` | Sci-Fi Future | 🚀 | Cyberpunk, neon, futuristic |
| `noir` | Dark Noir | 🌑 | High contrast, film noir |
| `fantasy` | Fantasy Epic | ⚔️ | Magical, epic fantasy art |
| `3d_render` | 3D Render | 🎮 | Photorealistic 3D graphics |
| `sketch` | Sketch Drawing | ✏️ | Hand-drawn pencil art |
| `watercolor` | Watercolor | 🎨 | Soft watercolor painting |
| `oil_painting` | Oil Painting | 🖼️ | Classical art style |
| `retro` | Retro Vintage | 📻 | 1970s-1980s aesthetic |

## Image Modes (7 Options)

| ID | Name | Processing Time | Best For |
|----|------|----------------|----------|
| `ai_only` | AI Only | ~30-60 seconds | Quick generation, consistent style |
| `manual_only` | Manual Only | Immediate | Custom artwork, specific visuals |
| `stock_only` | Stock Only | ~2-5 minutes | Realistic, professional footage |
| `ai_manual` | AI + Manual Mix | ~1-2 minutes | Partial custom control |
| `ai_stock` | AI + Stock Mix | ~2-4 minutes | Professional + creative |
| `manual_stock` | Manual + Stock Mix | ~2-4 minutes | Personal + professional |
| `all_mix` | All Three Mix | ~3-5 minutes | Maximum quality and variety |

## Voice Options (8 Options)

| ID | Name | Accent | Tone | Best For |
|----|------|--------|------|----------|
| `male_narrator_deep` | Deep Male Narrator | American | Serious, dramatic | Horror, Mystery, True Crime, Documentary |
| `male_professional` | Professional Male | American | Professional, clear | Documentary, Business, Motivational |
| `male_warm` | Warm Male | American | Warm, empathetic | Emotional, Heartwarming, Romance |
| `female_narrator` | Female Narrator | American | Natural, engaging | Emotional, Nature, Educational |
| `female_professional` | Professional Female | American | Professional, confident | Documentary, True Crime, History |
| `male_energetic` | Energetic Male | American | Energetic, intense | Action, Anime, War, Adventure |
| `british_male` | British Male | British (UK) | David Attenborough style | Nature, History, Documentary |
| `female_warm` | Warm Female | American | Soft, caring | Emotional, Romance, Family |

## Hook Intensity Options

| Value | Label | Description |
|-------|-------|-------------|
| `mild` | Gentle Opening | Slow build-up, atmospheric start |
| `medium` | Strong Opening | Clear intrigue, engaging start |
| `extreme` | EXPLOSIVE Opening | Immediate action, grabs attention instantly |

## Pacing Style Options

| Value | Label | Description |
|-------|-------|-------------|
| `slow` | Atmospheric | Long, detailed sentences, immersive |
| `medium` | Balanced | Steady progression, well-paced |
| `dynamic` | Varied | Mix of fast and slow, dynamic rhythm |
| `fast` | Rapid Fire | Short, punchy sentences, intense |

## Duration Guidelines

| Range | Label | Estimated Words | Recommended For |
|-------|-------|----------------|-----------------|
| 1-5 min | Quick | 150-750 words | Short stories, quick content |
| 6-15 min | Medium | 900-2,250 words | Standard videos, most content |
| 16-30 min | Long | 2,400-4,500 words | Detailed documentaries |
| 31-60 min | Epic | 4,650-9,000 words | Feature-length content |

## Scene Count Guidelines

| Scenes | Recommended For | Image Generation |
|--------|----------------|------------------|
| 5-7 | Quick videos | Minimal images, fast generation |
| 8-12 | Standard videos | Balanced, good variety |
| 13-16 | Detailed videos | Rich visual storytelling |
| 17-20 | Epic videos | Maximum visual detail |

## Character Management

- **Maximum Characters**: 5 per video
- **Required Fields**: Name, Description
- **Description Tips**:
  - Include age, gender, appearance
  - Mention clothing and distinctive features
  - Add emotional state if relevant
  - Example: "Sarah, 25, brown hair, terrified expression, wearing hospital scrubs"

## File Upload Requirements (Manual Mode)

| Property | Details |
|----------|---------|
| **Formats** | PNG, JPG, JPEG, WEBP |
| **Max Files** | No hard limit |
| **Recommended** | Match scene count for best results |
| **Size** | Reasonable file sizes (under 10MB each) |
| **Order** | Files used in upload order |

## Stock Keywords (Stock Mode)

- **Format**: Comma-separated tags
- **Examples**: nature, city, ocean, mountain, space, people
- **Auto-detection**: Leave empty to auto-generate from story
- **Multiple Keywords**: More keywords = better variety
- **Recommended**: 3-5 relevant keywords

## Progress Stages

| Stage | Progress | Duration | What Happens |
|-------|----------|----------|--------------|
| Script Generation | 0-25% | 10-30s | AI creates narrative, applies settings |
| Image Generation | 25-50% | 30s-3min | Creates/downloads visuals |
| Voice Narration | 50-75% | 20-60s | Records voiceover |
| Video Compilation | 75-100% | 30-90s | Combines elements, adds effects |

## API Request Format

```json
{
  "topic": "The Vanishing Lighthouse",
  "story_type": "scary_horror",
  "image_style": "cinematic",
  "image_mode": "ai_only",
  "voice_id": "male_narrator_deep",
  "duration": 5,
  "hook_intensity": "extreme",
  "pacing": "dynamic",
  "num_scenes": 10,
  "characters": [
    {
      "name": "Sarah",
      "description": "25 years old, brown hair, terrified expression"
    }
  ],
  "manual_image_paths": [],
  "stock_keywords": ["lighthouse", "ocean", "storm", "horror"]
}
```

## Recommended Combinations

### Horror Story
- **Story Type**: Scary Horror
- **Image Style**: Horror Creepy or Dark Noir
- **Voice**: Deep Male Narrator
- **Hook**: Extreme
- **Pacing**: Dynamic or Fast

### Nature Documentary
- **Story Type**: Nature & Wildlife
- **Image Style**: Documentary Real
- **Voice**: British Male
- **Hook**: Mild or Medium
- **Pacing**: Slow or Medium

### Motivational Video
- **Story Type**: Motivational Inspiring
- **Image Style**: Cinematic Film
- **Voice**: Professional Male or Energetic Male
- **Hook**: Medium or Extreme
- **Pacing**: Medium or Dynamic

### Emotional Story
- **Story Type**: Emotional Heartwarming
- **Image Style**: Cinematic Film or Watercolor
- **Voice**: Warm Male or Warm Female
- **Hook**: Mild or Medium
- **Pacing**: Slow or Medium

### Anime Adventure
- **Story Type**: Anime Style
- **Image Style**: Anime Style
- **Voice**: Energetic Male
- **Hook**: Extreme
- **Pacing**: Fast or Dynamic

---

Use this reference to quickly select the best options for your video generation needs.
