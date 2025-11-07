# Quick Start Guide - API Connection

Your frontend is ready and configured to connect to your backend at `http://localhost:5000`. Here's how to get it working immediately.

## Step 1: Ensure Backend Has CORS Enabled

This is the **#1 reason** the frontend won't connect.

### For Flask:
```python
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Add this line
```

### For FastAPI:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Step 2: Start Your Backend
```bash
python app.py
# Should show: Running on http://localhost:5000
```

## Step 3: Start the Frontend
```bash
npm run dev
# Should show: Local: http://localhost:5173
```

## Step 4: Check the Connection Status
1. Open http://localhost:5173 in your browser
2. Look at the top of the page
3. You should see one of these badges:

- 🟢 **Green "API Server Connected"** - Success! Ready to generate videos
- 🔴 **Red "API Server Offline"** - Backend not responding, check steps 1-2
- 🔵 **Blue "Checking API connection..."** - Still checking on first load

## Step 5: Test with Browser Console

Open DevTools (F12) and test:

```javascript
// Test API health
fetch('http://localhost:5000/health')
  .then(r => r.json())
  .then(d => console.log('Status:', d))
  .catch(e => console.log('Error:', e.message))
```

Expected output: `Status: {status: 'ok'}`

If you get a CORS error, your backend needs CORS enabled (see Step 1).

## Step 6: Test Video Generation

1. Fill out the form on the frontend
2. Enter a topic
3. Click "Generate Professional Video"
4. You should see progress updates

## Troubleshooting

### Error: "Cannot connect to API server"

**Check #1:** Backend is running
```bash
curl http://localhost:5000/health
```
Should return: `{"status":"ok"}`

**Check #2:** CORS is enabled
```bash
curl -H "Origin: http://localhost:5173" http://localhost:5000/health -v
```
Should include: `Access-Control-Allow-Origin: *`

**Check #3:** Using correct port
- Frontend: http://localhost:5173
- Backend: http://localhost:5000

### Error: CORS policy error in console

Your backend is not sending CORS headers. Make sure you:
1. Installed `flask-cors` (Flask) or use `CORSMiddleware` (FastAPI)
2. Added the CORS code to your app
3. Restarted the backend after making changes

### Error: 404 not found

The endpoint doesn't exist on your backend. Make sure you have:
- POST `/api/generate-video`
- GET `/api/progress`
- GET `/api/video/<filename>`

## What Happens When You Generate a Video

1. **Frontend sends request** to `/api/generate-video`
2. **Backend starts generation** in background
3. **Frontend polls** `/api/progress` every 1 second
4. **Frontend shows progress** with 4 stages:
   - 0-25%: Script Generation
   - 25-50%: Image Generation
   - 50-75%: Voice Narration
   - 75-100%: Video Compilation
5. **Backend returns video path** when complete
6. **Frontend displays video** and allows download

## API Requests Your Backend Receives

### Request 1: Generate Video
```
POST http://localhost:5000/api/generate-video
Content-Type: application/json

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
  "characters": [...],
  "manual_image_paths": [],
  "stock_keywords": []
}
```

### Request 2: Check Progress (every 1 second)
```
GET http://localhost:5000/api/progress
```

### Request 3: Stream Video
```
GET http://localhost:5000/api/video/video_20251104_123456.mp4
```

## Example Working Backend (Flask)

Here's a minimal working example:

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # CRITICAL: Enable CORS

current_job = {
    'status': 'idle',
    'progress': 0
}

@app.route('/api/generate-video', methods=['POST'])
def generate():
    global current_job
    data = request.json

    # In real implementation, start background task here
    # For now, just start a mock generation
    current_job = {
        'status': 'generating',
        'progress': 0,
        'topic': data.get('topic', '')
    }

    return jsonify({'status': 'generating'})

@app.route('/api/progress', methods=['GET'])
def progress():
    global current_job

    # Simulate progress
    if current_job['status'] == 'generating':
        current_job['progress'] += 5
        if current_job['progress'] >= 100:
            current_job['status'] = 'complete'
            current_job['video_path'] = 'sample_video.mp4'

    return jsonify(current_job)

@app.route('/api/video/<filename>', methods=['GET'])
def video(filename):
    # Return video file
    # For now, return dummy response
    return {'error': 'Video not found'}, 404

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
```

## Next Steps

1. ✅ Add CORS to your backend
2. ✅ Start your backend
3. ✅ Run `npm run dev`
4. ✅ Verify green "API Server Connected" badge
5. ✅ Fill out the form and generate a video
6. ✅ Watch the progress updates
7. ✅ Download your video

If you're still having issues, refer to `BACKEND_SETUP.md` for detailed debugging steps.

---

**Key Point:** The most common issue is missing CORS headers from the backend. If you see a CORS error in the browser console, add the CORS middleware to your Flask/FastAPI app and restart the backend.
