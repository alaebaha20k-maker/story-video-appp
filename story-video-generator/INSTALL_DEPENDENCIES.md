# 🔧 Install All Dependencies - Quick Fix

## Problem

You're getting: `ModuleNotFoundError: No module named 'flask'`

This means your virtual environment is missing dependencies.

---

## ✅ Quick Fix (Copy-Paste These Commands)

Open **PowerShell** or **Command Prompt** in VS Code and run:

```bash
# 1. Make sure you're in the project folder
cd C:\Users\pc\story-video-generator\story-video-appp\story-video-generator

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Install ALL dependencies
pip install flask flask-cors edge-tts pydub moviepy pillow numpy requests python-dotenv google-generativeai soundfile

# 4. Run the server
python api_server.py
```

---

## 📋 Or Use requirements.txt (Recommended)

```bash
# In your project folder with venv activated
pip install -r requirements.txt
```

This will install:
- ✅ Flask (web server)
- ✅ Flask-CORS (for frontend connection)
- ✅ Edge-TTS (text-to-speech)
- ✅ PyDub (audio processing)
- ✅ MoviePy (video editing)
- ✅ Pillow (image processing)
- ✅ NumPy (numerical operations)
- ✅ Requests (HTTP requests)
- ✅ Google Generative AI (script generation)
- ✅ SoundFile (audio I/O)
- ✅ Python-dotenv (environment variables)

---

## 🚀 Complete Setup Steps

### Step 1: Check Virtual Environment

```bash
# You should see (venv) at the start of your prompt
# Example: (venv) PS C:\Users\pc\story-video-generator\...

# If you don't see it, activate:
venv\Scripts\activate
```

### Step 2: Update pip (Important!)

```bash
python -m pip install --upgrade pip
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
# Check Flask is installed
pip show flask

# Should show:
# Name: Flask
# Version: 3.0.0 (or higher)
```

### Step 5: Run Server

```bash
python api_server.py
```

**Expected output:**
```
🚀 API SERVER READY - WITH KOKORO TTS!
📍 URL: http://localhost:5000
```

---

## 🆘 Troubleshooting

### Issue 1: "pip: command not found"

**Solution:**
```bash
python -m pip install -r requirements.txt
```

### Issue 2: Installation fails with SSL error

**Solution:**
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Issue 3: "Permission denied"

**Solution:** Run as administrator or add `--user`:
```bash
pip install --user -r requirements.txt
```

### Issue 4: Old packages cause conflicts

**Solution:** Upgrade everything:
```bash
pip install --upgrade -r requirements.txt
```

### Issue 5: Virtual environment issues

**Solution:** Recreate venv:
```bash
# Deactivate current venv
deactivate

# Remove old venv folder
rmdir /s venv

# Create new venv
python -m venv venv

# Activate new venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 📦 Individual Package Installation

If you prefer to install one by one:

```bash
# Core web server
pip install flask flask-cors

# AI & Script Generation
pip install google-generativeai openai

# Text-to-Speech
pip install edge-tts

# Audio processing
pip install pydub soundfile

# Video editing
pip install moviepy pillow

# Utilities
pip install numpy requests python-dotenv
```

---

## ✅ Verify Everything is Installed

Run this test:

```bash
python -c "import flask, flask_cors, edge_tts, pydub, moviepy, PIL, numpy, requests; print('✅ All dependencies installed!')"
```

If you see "✅ All dependencies installed!" you're ready to go!

---

## 🎯 Quick Checklist

- [ ] Virtual environment activated (see `(venv)` in prompt)
- [ ] pip updated: `python -m pip install --upgrade pip`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] No error messages during installation
- [ ] Test import works: `python -c "import flask"`
- [ ] Server runs: `python api_server.py`

---

## 🚀 Final Command Sequence

Copy all of this into PowerShell:

```powershell
# Navigate to project
cd C:\Users\pc\story-video-generator\story-video-appp\story-video-generator

# Activate venv
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify installation
python -c "import flask, edge_tts, pydub; print('Dependencies OK')"

# Start server
python api_server.py
```

---

## 📞 Still Not Working?

Check these:

1. **Python version:**
   ```bash
   python --version
   # Should be 3.8 or higher
   ```

2. **Virtual environment path:**
   ```bash
   where python
   # Should point to: ...\venv\Scripts\python.exe
   ```

3. **pip version:**
   ```bash
   pip --version
   # Should be 23.0 or higher
   ```

If all else fails, try the individual package installation method above.

---

After running these commands, your backend should start successfully! 🎉
