# AI Video Generator - Professional Dashboard

A complete, production-ready AI video generation dashboard built with React, TypeScript, and Tailwind CSS. Generate professional story videos in minutes with 20 story types, 14 image styles, 7 image modes, and 8 voice options.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- Your Python backend running at `http://localhost:5000`

### Installation & Setup

```bash
# 1. Install dependencies
npm install

# 2. Configure Supabase (optional, for gallery feature)
cp .env.example .env
# Edit .env and add your Supabase credentials

# 3. Start development server
npm run dev
```

Open http://localhost:5173 in your browser.

## ✅ Connection Status

When you first open the app, check the status badge at the top:
- 🟢 **Green** - API connected, ready to generate videos
- 🔴 **Red** - API offline, ensure backend is running
- 🔵 **Blue** - Checking connection

## 📋 Guides

### Getting Started
- **[QUICK_START.md](./QUICK_START.md)** - Fast setup and troubleshooting
- **[SETUP.md](./SETUP.md)** - Detailed installation guide
- **[BACKEND_SETUP.md](./BACKEND_SETUP.md)** - Backend integration guide

### Reference
- **[FEATURES.md](./FEATURES.md)** - Complete feature list
- **[OPTIONS_REFERENCE.md](./OPTIONS_REFERENCE.md)** - All available options

### Debugging
- **[DEBUG_SCRIPT.js](./DEBUG_SCRIPT.js)** - Paste into browser console to test connection

## 🎯 Core Features

### 1. Video Generation Form
- **Basic Settings**: Topic, duration (1-60 min), character counter
- **20 Story Types**: Horror, Emotional, True Crime, Anime, Documentary, etc.
- **Advanced Settings**: Hook intensity, pacing style, scene count (collapsible)
- **14 Image Styles**: Cinematic, Documentary, Anime, Horror, Comic, Historical, Sci-Fi, Noir, Fantasy, 3D, Sketch, Watercolor, Oil, Retro
- **7 Image Modes**: AI Only, Manual, Stock, AI+Manual, AI+Stock, Manual+Stock, All Three Mix
- **Conditional Sections**: Image upload (for manual modes), stock keywords (for stock modes)
- **8 Voice Options**: Multiple male/female narrators with different accents and tones
- **Character Management**: Define up to 5 characters with descriptions

### 2. Generation Process
Real-time progress tracking with 4 stages:
- 📝 **Script Generation** (0-25%)
- 🎨 **Image Generation** (25-50%)
- 🎤 **Voice Narration** (50-75%)
- 🎬 **Video Compilation** (75-100%)

### 3. Video Result Display
- Full-featured video player with controls
- Video metadata and statistics
- Download, share, and regenerate buttons
- Professional UI with animations

### 4. Gallery System
- View all generated videos
- Metadata display with filtering
- Modal preview
- Delete functionality
- Supabase integration for persistence

## 🔌 API Integration

Your backend must implement these endpoints:

### POST `/api/generate-video`
Starts video generation with parameters from the form.

**Expected Request:**
```json
{
  "topic": "string",
  "story_type": "string",
  "image_style": "string",
  "image_mode": "string",
  "voice_id": "string",
  "duration": number,
  "hook_intensity": "mild|medium|extreme",
  "pacing": "slow|medium|dynamic|fast",
  "num_scenes": number,
  "characters": [{"name": "string", "description": "string"}],
  "manual_image_paths": ["string"],
  "stock_keywords": ["string"]
}
```

### GET `/api/progress`
Returns current generation progress.

**Expected Response:**
```json
{
  "status": "generating|complete|error",
  "progress": 0-100,
  "substatus": "string",
  "details": "string",
  "video_path": "filename.mp4",
  "error": "error message"
}
```

### GET `/api/video/<filename>`
Streams the generated video file.

### GET `/health`
Health check endpoint.

**Response:** `{"status": "ok"}`

## ⚠️ Common Issues

### "API Server Offline"
1. Ensure backend is running: `python app.py`
2. Backend should be at `http://localhost:5000`
3. Check backend console for errors

### CORS Error
Backend needs CORS enabled. Add to your Flask app:
```python
from flask_cors import CORS
CORS(app)
```

Or FastAPI:
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

### Using Debug Script
Paste into browser console (F12 → Console tab):
1. Copy all content from `DEBUG_SCRIPT.js`
2. Paste into console
3. Press Enter
4. Follow the diagnostic output

## 🏗️ Project Structure

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
├── store/             # State management
│   └── useVideoStore.ts
├── types/             # TypeScript types
│   └── index.ts
├── constants/         # App constants
│   └── options.ts
├── utils/             # Utilities
│   └── api.ts
├── lib/               # Third-party integrations
│   └── supabase.ts
├── App.tsx            # Main component
├── main.tsx           # Entry point
└── index.css          # Global styles
```

## 🛠️ Scripts

```bash
npm run dev        # Start development server
npm run build      # Build for production
npm run preview    # Preview production build
npm run lint       # Run ESLint
npm run typecheck  # TypeScript type checking
```

## 🎨 Design Features

- **Gradient Header**: Purple to pink gradient
- **Responsive Grid**: 1-4 columns depending on screen size
- **Smooth Animations**: Framer Motion for transitions
- **Professional Colors**: Indigo, pink, green, red, orange, grays
- **Touch-Friendly**: 44px+ buttons for mobile
- **Accessible**: ARIA labels, keyboard navigation, high contrast

## 📦 Technology Stack

- **Frontend**: React 18, TypeScript 5, Vite
- **Styling**: Tailwind CSS 3
- **UI**: Lucide React icons, Framer Motion
- **State**: Zustand
- **Database**: Supabase (PostgreSQL)
- **Upload**: react-dropzone
- **Notifications**: react-hot-toast
- **HTTP**: Fetch API

## 🌐 Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## 📝 File Upload Requirements

- **Formats**: PNG, JPG, JPEG, WEBP
- **Size**: Reasonable file sizes (under 10MB each)
- **Count**: No hard limit, recommended to match scene count

## 🔐 Environment Variables

Create `.env` file:
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## 🚢 Production Deployment

1. **Update API URL** in `src/utils/api.ts`
2. **Update CORS** in backend for production domain
3. **Build**: `npm run build`
4. **Deploy** `dist/` folder to your hosting

## 📚 Additional Resources

- [React Documentation](https://react.dev)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Vite Documentation](https://vitejs.dev)
- [Supabase Documentation](https://supabase.com/docs)

## 🆘 Troubleshooting

**Backend not responding?**
- Check `BACKEND_SETUP.md` for detailed debugging
- Use `DEBUG_SCRIPT.js` to test connection
- Verify CORS is enabled

**Gallery not working?**
- Ensure Supabase credentials are in `.env`
- Check browser console for errors
- Verify `generated_videos` table exists

**Build failing?**
- Run `npm run typecheck` to identify TypeScript errors
- Delete `node_modules` and `package-lock.json`, then reinstall
- Clear Vite cache: `rm -rf node_modules/.vite`

## 📞 Support

For issues:
1. Check the relevant guide (QUICK_START.md, BACKEND_SETUP.md)
2. Run the DEBUG_SCRIPT.js in browser console
3. Check backend logs
4. Review error messages in browser console (F12)

## 🎉 Success Checklist

- ✅ Backend running at http://localhost:5000
- ✅ CORS enabled on backend
- ✅ Frontend running at http://localhost:5173
- ✅ Green "API Server Connected" badge shows
- ✅ Form fills out without errors
- ✅ "Generate Professional Video" button works
- ✅ Progress updates show in real-time
- ✅ Video generates and displays
- ✅ Download button works
- ✅ Gallery shows generated videos

---

**Built with ❤️ using modern web technologies**

For the complete feature list, see [FEATURES.md](./FEATURES.md)
For all available options, see [OPTIONS_REFERENCE.md](./OPTIONS_REFERENCE.md)
