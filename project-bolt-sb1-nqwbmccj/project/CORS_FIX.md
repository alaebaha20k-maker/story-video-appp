# 🔴 CRITICAL: CORS Configuration

**If you see "Cannot connect to API server" - READ THIS FIRST**

---

## The Problem

Your frontend (at `http://localhost:5173`) is trying to communicate with your backend (at `http://localhost:5000`), but the backend is not allowing cross-origin requests. This is a **CORS (Cross-Origin Resource Sharing)** issue.

## The Solution

### Option 1: Flask (RECOMMENDED)

Add these two lines to your Flask app:

```python
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# ADD THESE TWO LINES
CORS(app)
# or with more control:
# CORS(app, resources={r"/api/*": {"origins": "*"}})

# Rest of your app...
```

**Install flask-cors if you don't have it:**
```bash
pip install flask-cors
```

### Option 2: FastAPI

Add this to your FastAPI app:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ADD THIS BLOCK
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rest of your app...
```

### Option 3: Django

Add to your `settings.py`:

```python
INSTALLED_APPS = [
    # ... other apps
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ... other middleware
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

Install django-cors-headers:
```bash
pip install django-cors-headers
```

### Option 4: Other Frameworks

Search for "[Your Framework] CORS" and enable CORS headers:
- Node.js/Express: `npm install cors` and use `app.use(cors())`
- Go/Gin: Use `github.com/gin-contrib/cors`
- etc.

---

## Verification

After adding CORS to your backend:

1. **Restart your backend**
```bash
# Kill the old process
# Ctrl+C in the terminal running your backend

# Restart it
python app.py
```

2. **Test the connection** in your browser console (F12):
```javascript
fetch('http://localhost:5000/health')
  .then(r => r.json())
  .then(d => console.log('Success:', d))
  .catch(e => console.log('Failed:', e.message))
```

Should see: `Success: {status: 'ok'}`

3. **Refresh the frontend** at http://localhost:5173

You should now see a **green "API Server Connected" badge** at the top.

---

## What is CORS?

CORS is a browser security feature that prevents websites from making requests to different servers without permission. Since your frontend and backend are on different ports, the backend must explicitly allow the frontend to communicate with it.

## Why Frontend Port is 5173

- **Frontend**: Vite development server runs on port **5173**
- **Backend**: Your Python API runs on port **5000**
- **Different ports** = different origin = needs CORS

## Testing CORS with curl

```bash
# Test if CORS headers are present
curl -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     http://localhost:5000/api/generate-video -v

# Look for these headers in response:
# Access-Control-Allow-Origin: *
# Access-Control-Allow-Methods: POST, GET, OPTIONS, DELETE, PUT
# Access-Control-Allow-Headers: Content-Type, ...
```

---

## Still Not Working?

1. **Double-check you restarted the backend** after adding CORS
2. **Check the backend logs** for any errors
3. **Verify CORS syntax** matches your framework exactly
4. **Run DEBUG_SCRIPT.js** in browser console for detailed diagnostics
5. **Check backend is actually running**:
   ```bash
   curl http://localhost:5000/health
   ```

---

## Production Deployment

For production, instead of `"*"`, specify your exact domain:

### Flask
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com", "https://www.yourdomain.com"]
    }
})
```

### FastAPI
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Summary

| Step | Action | Verify With |
|------|--------|-------------|
| 1 | Add CORS to backend | Check backend logs |
| 2 | Restart backend | `curl http://localhost:5000/health` |
| 3 | Refresh frontend | Green badge at top of page |
| 4 | Try generating | Form should work |

**Most common mistake:** Forgetting to restart the backend after adding CORS. Make sure you restart it!

---

If you still see errors after adding CORS and restarting, run `DEBUG_SCRIPT.js` in the browser console for detailed diagnostics.
