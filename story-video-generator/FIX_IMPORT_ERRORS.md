# 🔧 Fix: Import Errors in Backend

## Problem

You were getting this error:
```
ImportError: cannot import name 'script_generator' from 'src.ai.script_generator'
```

## Root Cause

The module had `pro_script_generator` but your code was trying to import `script_generator`.

---

## ✅ Fixes Applied

### 1. Fixed `script_generator` Import

**File:** `src/ai/script_generator.py`

**Added:**
```python
# Alias for backward compatibility
script_generator = pro_script_generator
```

### 2. Fixed `image_generator` Import

**File:** `src/ai/image_generator.py`

**Added:**
```python
# Default global instance for backward compatibility
image_generator = UltraImageGenerator()
```

### 3. Made Dependencies More Graceful

**File:** `src/ai/script_generator.py`

**Changed:** No longer exits if `google-generativeai` is not installed. Instead, it warns and continues, allowing other parts of the app to work.

---

## 🚀 How to Run Backend Now

### Option 1: Run API Server (Recommended)

```bash
cd story-video-generator
python api_server.py
```

This starts the Flask API server on http://localhost:5000

### Option 2: Run Main Script

```bash
cd story-video-generator  
python main.py --interactive
```

This runs the interactive CLI mode.

---

## 📋 Check Your Setup

### 1. Verify Python Environment

Make sure you're in your virtual environment:

```bash
# On Windows (VS Code terminal)
venv\Scripts\activate

# Verify activation (should show (venv) prefix)
```

### 2. Install Missing Dependencies

If you get import errors for packages, install them:

```bash
# For script generation
pip install google-generativeai

# For TTS (if using Kokoro)
pip install kokoro soundfile

# Core dependencies
pip install -r requirements.txt
```

### 3. Set API Keys

Create a `.env` file in the `story-video-generator` folder:

```env
# Google Gemini API Key (for script generation)
GEMINI_API_KEY=your_key_here

# Optional: Other API keys
OPENAI_API_KEY=your_key_here
```

---

## 🧪 Test Imports

I created a test script for you. Run it to check all imports:

```bash
python test_imports.py
```

This will show you exactly which imports work and which need fixing.

---

## Common Issues & Solutions

### Issue 1: "python: command not found"

**Solution:** Use `python3` instead:
```bash
python3 api_server.py
```

Or add alias in your terminal:
```bash
# Windows (PowerShell)
Set-Alias python python3

# Linux/Mac
alias python=python3
```

### Issue 2: "No module named 'google.generativeai'"

**Solution:** Install the package:
```bash
pip install google-generativeai
```

### Issue 3: "ModuleNotFoundError: No module named 'src'"

**Solution:** Make sure you're running from the correct directory:
```bash
cd story-video-generator
# Then run your command
```

### Issue 4: Virtual environment not activated

**Solution (Windows):**
```bash
# Navigate to project
cd C:\Users\pc\story-video-generator\story-video-appp\story-video-generator

# Activate venv
venv\Scripts\activate

# You should see (venv) in your prompt

# Now run
python api_server.py
```

---

## ✅ Verification Steps

1. **Activate virtual environment**
   ```bash
   venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test imports**
   ```bash
   python test_imports.py
   ```

4. **Run backend**
   ```bash
   python api_server.py
   ```

5. **Check output** - Should see:
   ```
   🚀 API SERVER READY - WITH KOKORO TTS!
   📍 URL: http://localhost:5000
   ```

---

## 🎯 Quick Start (Copy-Paste This)

```bash
# Windows PowerShell - Copy all these commands

# 1. Navigate to project
cd C:\Users\pc\story-video-generator\story-video-appp\story-video-generator

# 2. Activate venv (if not already active)
venv\Scripts\activate

# 3. Install/update dependencies
pip install -r requirements.txt

# 4. Run API server
python api_server.py
```

If you see the server startup message, you're good to go! 🚀

---

## 📞 Still Having Issues?

### Check these:

1. **Python version:**
   ```bash
   python --version
   # Should be Python 3.8+
   ```

2. **Current directory:**
   ```bash
   pwd  # or cd (Windows)
   # Should be in: .../story-video-generator
   ```

3. **Virtual environment:**
   ```bash
   # Should see (venv) in prompt
   # If not, activate it
   ```

4. **Dependencies:**
   ```bash
   pip list
   # Should show: flask, edge-tts, pydub, etc.
   ```

---

## Summary

✅ **Fixed:** Import errors for `script_generator` and `image_generator`  
✅ **Fixed:** Graceful handling of missing dependencies  
✅ **Added:** Test script to verify all imports  
✅ **Added:** This comprehensive troubleshooting guide  

**Next step:** Run `python api_server.py` and it should work! 🎉
