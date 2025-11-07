# AI Video Generator - Setup Guide

## Overview

This is an ultra-professional AI Video Generator Dashboard that connects to your Python backend API at `http://localhost:5000`. The application features a complete video generation pipeline with 20 story types, 14 image styles, 7 image modes, 8 voice options, and a full-featured gallery powered by Supabase.

## Prerequisites

1. **Backend API Server** running at `http://localhost:5000`
2. **Supabase Account** (optional, for gallery feature)

## Environment Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Supabase (Optional - for Gallery feature)

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Supabase credentials:

```env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

If you don't configure Supabase, the app will still work but the Gallery page won't save videos.

### 3. Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Features

### Main Generator Page

#### 1. Basic Settings
- **Topic Input**: Large text area for story description
- **Duration Slider**: 1-60 minutes with visual labels
- **Character Counter**: Shows input length
- **Word Estimate**: Calculates approximate word count

#### 2. Story Types (20 Options)
- Scary Horror
- Emotional Heartwarming
- True Crime
- Anime Style
- Historical Documentary
- Surprising Twist
- Motivational Inspiring
- Mystery Thriller
- War & Military
- Nature & Wildlife
- Comedy & Funny
- Romantic Love
- Sci-Fi Future
- Fantasy Epic
- Biographical
- Conspiracy
- Psychological
- Adventure Survival
- Paranormal
- Documentary Real

#### 3. Advanced Script Settings (Collapsible)
- **Hook Intensity**: Mild, Medium, Extreme
- **Pacing Style**: Slow, Medium, Dynamic, Fast
- **Number of Scenes**: 5-20 (affects image generation)

#### 4. Image Generation Styles (14 Options)
- Cinematic Film
- Documentary Real
- Anime Style
- Horror Creepy
- Comic Book
- Historical Photo
- Sci-Fi Future
- Dark Noir
- Fantasy Epic
- 3D Render
- Sketch Drawing
- Watercolor
- Oil Painting
- Retro Vintage

#### 5. Image Modes (7 Options)
- **AI Only**: Fully automated generation
- **Manual Only**: Upload your own images
- **Stock Only**: Professional Pexels media
- **AI + Manual Mix**: Combine both
- **AI + Stock Mix**: AI + professional footage
- **Manual + Stock Mix**: Custom + professional
- **All Three Mix**: Maximum variety

##### Conditional Sections
- **Image Upload**: Appears for Manual/Hybrid modes
  - Drag & drop support
  - Multi-file selection
  - Preview thumbnails
  - PNG, JPG, WEBP support

- **Stock Keywords**: Appears for Stock/Hybrid modes
  - Comma-separated tags
  - Quick add buttons
  - Auto-detection option

#### 6. Voice Selection (8 Options)
- Deep Male Narrator (Horror, Mystery)
- Professional Male (Documentary, Business)
- Warm Male (Emotional, Heartwarming)
- Female Narrator (Emotional, Nature)
- Professional Female (True Crime, History)
- Energetic Male (Action, Anime)
- British Male (Nature, History)
- Warm Female (Romance, Family)

#### 7. Character Management (Advanced)
- Define up to 5 main characters
- Name + detailed description
- Ensures consistent appearance
- Collapsible section

### Generation Process

Real-time progress tracking with 4 stages:

1. **Script Generation (0-25%)**
   - Analyzes topic and style
   - Creates professional narrative
   - Applies hook intensity and pacing

2. **Image Generation (25-50%)**
   - Creates/downloads images
   - Maintains character consistency
   - Shows scene-by-scene progress

3. **Voice Narration (50-75%)**
   - Records professional voiceover
   - Selected voice applied
   - Audio waveform animation

4. **Video Compilation (75-100%)**
   - Combines all elements
   - Adds transitions and effects
   - Final encoding

### Video Result

Once complete, displays:
- **Video Player**: Full controls, autoplay option
- **Video Details**: Duration, generation date, scene count
- **Metadata Badges**: Story type, image style, voice
- **Statistics**: Word count, characters detected
- **Action Buttons**:
  - Download Video (saves to local)
  - Share (native share API or copy link)
  - Generate Another (resets form)

### Gallery Page

View all generated videos:
- Grid layout with thumbnails
- Video metadata display
- Click to preview in modal
- Delete videos
- Automatic save on generation
- Sorted by creation date

## API Integration

### Expected Backend Endpoints

#### POST `/api/generate-video`
```json
{
  "topic": "string",
  "story_type": "string",
  "image_style": "string",
  "image_mode": "string",
  "voice_id": "string",
  "duration": 5,
  "hook_intensity": "medium",
  "pacing": "medium",
  "num_scenes": 10,
  "characters": [
    {
      "name": "Sarah",
      "description": "25 years old, brown hair, terrified expression"
    }
  ],
  "manual_image_paths": [],
  "stock_keywords": []
}
```

#### GET `/api/progress`
Returns:
```json
{
  "status": "generating" | "complete" | "error",
  "progress": 45,
  "substatus": "Creating scene 5 of 10",
  "details": "Additional info",
  "video_path": "filename.mp4",
  "error": "error message if failed"
}
```

#### GET `/api/video/<filename>`
Streams the generated video file

#### GET `/health`
Health check endpoint (returns 200 if API is online)

## Development

### Scripts

```bash
npm run dev        # Start development server
npm run build      # Build for production
npm run preview    # Preview production build
npm run lint       # Lint code
npm run typecheck  # TypeScript type checking
```

### Technology Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: Custom components with Lucide React icons
- **State Management**: Zustand
- **Form Handling**: React hooks
- **File Upload**: react-dropzone
- **Notifications**: react-hot-toast
- **Animations**: Framer Motion
- **Database**: Supabase (PostgreSQL)
- **HTTP Client**: Fetch API

### Project Structure

```
src/
├── components/          # React components
│   ├── Header.tsx
│   ├── BasicSettings.tsx
│   ├── StoryTypeSelector.tsx
│   ├── AdvancedSettings.tsx
│   ├── ImageStyleSelector.tsx
│   ├── ImageModeSelector.tsx
│   ├── ImageUpload.tsx
│   ├── StockKeywords.tsx
│   ├── VoiceSelector.tsx
│   ├── CharacterManager.tsx
│   ├── GenerateButton.tsx
│   ├── GenerationProgress.tsx
│   └── VideoResult.tsx
├── pages/              # Page components
│   ├── GeneratorPage.tsx
│   └── GalleryPage.tsx
├── store/             # Zustand state management
│   └── useVideoStore.ts
├── types/             # TypeScript types
│   └── index.ts
├── constants/         # App constants
│   └── options.ts
├── utils/             # Utility functions
│   └── api.ts
├── lib/               # Third-party integrations
│   └── supabase.ts
├── App.tsx            # Main app component
├── main.tsx           # Entry point
└── index.css          # Global styles
```

## Troubleshooting

### API Connection Issues

If you see "API Server Offline":
1. Ensure your backend is running at `http://localhost:5000`
2. Check the `/health` endpoint is accessible
3. Verify CORS is enabled on the backend
4. Check browser console for errors

### Gallery Not Working

If videos don't appear in gallery:
1. Verify Supabase credentials in `.env`
2. Check browser console for errors
3. Ensure the `generated_videos` table exists
4. Verify RLS policies are correct

### Upload Issues

If image uploads fail:
1. Check file types (PNG, JPG, WEBP only)
2. Verify file size is reasonable
3. Check browser console for errors

### Build Issues

If build fails:
1. Run `npm run typecheck` to identify TypeScript errors
2. Delete `node_modules` and `package-lock.json`, then run `npm install`
3. Clear Vite cache: `rm -rf node_modules/.vite`

## Production Deployment

### Build

```bash
npm run build
```

The production files will be in the `dist/` directory.

### Environment Variables

Ensure these are set in your production environment:
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`

### API Configuration

If your API is not at `http://localhost:5000`, update:
```typescript
// src/utils/api.ts
const API_BASE_URL = 'your-production-api-url';
```

## Features Summary

- **20 Story Types** with detailed descriptions
- **14 Image Styles** with visual previews
- **7 Image Modes** including AI, Manual, Stock, and Hybrids
- **8 Voice Options** with characteristics
- **Character Consistency** system for up to 5 characters
- **Real-time Progress** tracking with 4-stage visualization
- **Video Gallery** with Supabase persistence
- **Responsive Design** works on mobile, tablet, desktop
- **Error Handling** with user-friendly messages
- **API Health Monitoring** with status indicators
- **Professional UI** with animations and polish

## Support

For issues related to:
- **Frontend**: Check this codebase and documentation
- **Backend API**: Refer to your Python backend documentation
- **Supabase**: Visit https://supabase.com/docs

---

Built with modern web technologies for professional video generation.
