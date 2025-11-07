# Backend Integration - Critical Setup

Your frontend is ready to connect to your backend at `http://localhost:5000`. This guide covers what your backend needs to implement.

## Backend Requirements

### 1. CORS Configuration (CRITICAL)

Your Python backend **MUST** enable CORS to allow requests from the frontend at `http://localhost:5173`.

#### Flask Example:
```python
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

#### FastAPI Example:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Required Endpoints

Your backend must implement these three endpoints:

#### Endpoint 1: POST /api/generate-video
Starts the video generation process.

**Request Body:**
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
  "stock_keywords": ["lighthouse", "ocean", "storm"]
}
```

**Response:**
```json
{
  "status": "generating",
  "job_id": "some-unique-id"
}
```

**What it should do:**
1. Accept the request immediately
2. Start video generation in background
3. Return immediately (don't block on generation)
4. Store generation state to return on /api/progress

---

#### Endpoint 2: GET /api/progress
Returns current generation progress.

**Response (during generation):**
```json
{
  "status": "generating",
  "progress": 45,
  "substatus": "Creating scene 5 of 10",
  "details": "Processing images...\nApplying filters..."
}
```

**Response (when complete):**
```json
{
  "status": "complete",
  "progress": 100,
  "video_path": "video_20251104_123456.mp4",
  "substatus": "Video ready for download"
}
```

**Response (on error):**
```json
{
  "status": "error",
  "progress": 50,
  "error": "Failed to generate images"
}
```

**Progress Ranges (Frontend Expectations):**
- 0-25%: Script Generation
- 25-50%: Image Generation
- 50-75%: Voice Narration
- 75-100%: Video Compilation

---

#### Endpoint 3: GET /api/video/<filename>
Streams the generated video file.

**Response:**
- Content-Type: `video/mp4`
- Binary video file stream
- Allow range requests for seeking

**Example:**
```
GET /api/video/video_20251104_123456.mp4
```

---

#### Endpoint 4 (Optional): GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

**HTTP Status:** 200

---

### 3. Backend Workflow Example

Here's a typical backend implementation pattern:

```python
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import uuid
import threading
import time

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Store generation jobs
jobs = {}

def generate_video_background(job_id, params):
    """Runs in background thread"""
    try:
        jobs[job_id]['status'] = 'generating'
        jobs[job_id]['progress'] = 0

        # Step 1: Generate script (0-25%)
        jobs[job_id]['progress'] = 10
        jobs[job_id]['substatus'] = 'Generating script...'
        script = generate_script(params)
        jobs[job_id]['progress'] = 25

        # Step 2: Generate images (25-50%)
        jobs[job_id]['progress'] = 30
        jobs[job_id]['substatus'] = 'Generating images...'
        images = generate_images(script, params)
        jobs[job_id]['progress'] = 50

        # Step 3: Generate voice (50-75%)
        jobs[job_id]['progress'] = 55
        jobs[job_id]['substatus'] = 'Recording narration...'
        audio = generate_audio(script, params['voice_id'])
        jobs[job_id]['progress'] = 75

        # Step 4: Compile video (75-100%)
        jobs[job_id]['progress'] = 80
        jobs[job_id]['substatus'] = 'Compiling video...'
        video_path = compile_video(images, audio, params)
        jobs[job_id]['progress'] = 100

        jobs[job_id]['status'] = 'complete'
        jobs[job_id]['video_path'] = video_path

    except Exception as e:
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)

@app.route('/api/generate-video', methods=['POST'])
def generate_video():
    params = request.json
    job_id = str(uuid.uuid4())

    # Store job state
    jobs[job_id] = {
        'status': 'queued',
        'progress': 0,
        'params': params
    }

    # Start background generation
    thread = threading.Thread(
        target=generate_video_background,
        args=(job_id, params)
    )
    thread.daemon = True
    thread.start()

    return jsonify({'status': 'generating', 'job_id': job_id})

@app.route('/api/progress')
def get_progress():
    # Return progress of most recent job
    if jobs:
        latest_job = list(jobs.values())[-1]
        return jsonify(latest_job)

    return jsonify({'status': 'idle', 'progress': 0})

@app.route('/api/video/<filename>')
def get_video(filename):
    # Serve the video file
    return send_file(f'videos/{filename}', mimetype='video/mp4')

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
```

---

## Debugging Connection Issues

### Issue: "Cannot connect to API server"

**Troubleshooting Steps:**

1. **Check Backend is Running**
   ```bash
   curl http://localhost:5000/health
   ```
   Should return: `{"status":"ok"}`

2. **Check CORS Headers**
   ```bash
   curl -H "Origin: http://localhost:5173" \
        -H "Access-Control-Request-Method: POST" \
        -H "Access-Control-Request-Headers: Content-Type" \
        http://localhost:5000/api/generate-video -v
   ```
   Should include:
   ```
   Access-Control-Allow-Origin: *
   Access-Control-Allow-Methods: POST, GET, OPTIONS
   ```

3. **Check Browser Console**
   - Open DevTools (F12)
   - Check Network tab
   - Look for failed requests to `http://localhost:5000`
   - Check Console for error messages

4. **Verify Ports**
   - Frontend should be at: `http://localhost:5173` (Vite dev server)
   - Backend should be at: `http://localhost:5000` (your API)
   - Both must be running simultaneously

5. **Check Backend Logs**
   - Look for CORS errors
   - Check for request handling issues
   - Verify endpoints are being called

### Issue: "CORS error - No 'Access-Control-Allow-Origin' header"

**Solution:**
Add CORS middleware to your Flask/FastAPI app (see examples above).

### Issue: "HTTP 404 - Endpoint not found"

**Check:**
- POST `/api/generate-video` exists
- GET `/api/progress` exists
- GET `/api/video/<filename>` exists

### Issue: "Timeout waiting for generation"

**Check:**
- Generation is actually starting in background
- Progress endpoint is returning updates
- Try increasing timeout or checking backend logs

---

## Frontend Status Indicators

The frontend displays connection status at the top:

- 🟢 **Green** - API Server Connected (health check passed)
- 🔴 **Red** - API Server Offline (cannot reach backend)
- 🔵 **Blue** - Checking API connection (first load)

---

## Testing the Connection

### Step 1: Verify Backend Responds
```bash
# In terminal, test the health endpoint
curl http://localhost:5000/health
# Should return: {"status":"ok"}
```

### Step 2: Check CORS
```bash
# Test POST endpoint with CORS headers
curl -X POST http://localhost:5000/api/generate-video \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:5173" \
  -d '{"topic":"test","story_type":"scary_horror"}'
# Should not return CORS error
```

### Step 3: Try Frontend
1. Run: `npm run dev`
2. Open: `http://localhost:5173`
3. You should see "API Server Connected" (green badge)
4. Try filling out form and clicking "Generate Professional Video"

---

## Production Deployment

When deploying to production:

1. **Update API URL** in `src/utils/api.ts`:
   ```typescript
   const API_BASE_URL = 'https://your-production-api.com';
   ```

2. **Update CORS Origins** in backend:
   ```python
   allow_origins=[
       "https://your-frontend-domain.com",
       "https://www.your-frontend-domain.com"
   ]
   ```

3. **Use HTTPS** for both frontend and backend

4. **Update Supabase URL** in `.env` for production

---

## Common Implementation Mistakes

1. ❌ **Blocking on video generation** → Use background threads/tasks
2. ❌ **Not setting CORS headers** → Add CORS middleware
3. ❌ **Returning only final result** → Return progress updates
4. ❌ **Using different port numbers** → Backend on 5000, frontend on 5173
5. ❌ **Not storing job state** → Need to persist progress between requests
6. ❌ **Synchronous video generation** → Must be asynchronous/background

---

## Next Steps

1. ✅ Ensure CORS is enabled on your backend
2. ✅ Implement the three required endpoints
3. ✅ Start your backend at `http://localhost:5000`
4. ✅ Run `npm run dev` on the frontend
5. ✅ Test connection - you should see green "API Server Connected" badge
6. ✅ Try generating a video

If you're still having issues, check your backend logs and ensure all three endpoints are responding correctly.
