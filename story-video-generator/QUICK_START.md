# 🚀 Quick Start - Backend Setup (Windows)

## Problem: Flask Not Installed

You have venv activated but dependencies aren't installed yet.

---

## ✅ Solution 1: Run Installation Script (EASIEST)

**Step 1:** In VS Code, open terminal in your project folder  
**Step 2:** Make sure venv is activated (you should see `(venv)`)  
**Step 3:** Run this command:

```powershell
pip install flask flask-cors edge-tts pydub moviepy pillow numpy requests python-dotenv google-generativeai
```

**Step 4:** Wait for installation (2-5 minutes)

**Step 5:** Run the server:

```powershell
python api_server.py
```

---

## ✅ Solution 2: Step-by-Step Commands

Copy and paste **ONE LINE AT A TIME** into PowerShell:

```powershell
# 1. Check Python works
python --version

# 2. Check pip works
pip --version

# 3. Install Flask first
pip install flask

# 4. Test Flask installed
python -c "import flask; print('Flask OK')"

# 5. Install remaining packages
pip install flask-cors edge-tts pydub moviepy pillow numpy requests python-dotenv

# 6. Run server
python api_server.py
```

---

## 🔍 Verify Your Setup

### Check 1: Is venv activated?

```powershell
# You should see (venv) at the start of your line
# Example: (venv) PS C:\Users\pc\story-video-generator\...
```

**If you DON'T see (venv), activate it:**

```powershell
venv\Scripts\activate
```

### Check 2: Is Python in venv?

```powershell
where python
```

**Should show:**
```
C:\Users\pc\story-video-generator\story-video-appp\story-video-generator\venv\Scripts\python.exe
```

**If it shows system Python (C:\Python\...), you need to activate venv first!**

### Check 3: Is pip working?

```powershell
pip --version
```

**Should show something like:**
```
pip 24.0 from C:\Users\pc\...\venv\Lib\site-packages\pip (python 3.x)
```

---

## 🆘 Common Issues

### Issue 1: "venv\Scripts\activate : cannot be loaded"

**Solution (run this ONCE):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again:
```powershell
venv\Scripts\activate
```

### Issue 2: "pip is not recognized"

**Solution:**
```powershell
python -m pip install flask
```

### Issue 3: Installation fails with errors

**Solution - Use these flags:**
```powershell
pip install --no-cache-dir flask flask-cors edge-tts
```

### Issue 4: Still can't import flask after installing

**Check where it installed:**
```powershell
pip show flask
```

Look at "Location:" - it should be in your venv folder.

**If it's in the wrong location, reinstall:**
```powershell
pip uninstall flask
pip install flask
```

---

## 💡 Alternative: Install from requirements.txt

```powershell
# Make sure you're in the right folder
cd C:\Users\pc\story-video-generator\story-video-appp\story-video-generator

# Activate venv
venv\Scripts\activate

# Install from file
pip install -r requirements.txt
```

---

## 🎯 Complete Fresh Start (If Nothing Works)

```powershell
# 1. Navigate to project
cd C:\Users\pc\story-video-generator\story-video-appp\story-video-generator

# 2. Delete old venv
Remove-Item -Recurse -Force venv

# 3. Create new venv
python -m venv venv

# 4. Activate new venv
venv\Scripts\activate

# 5. Upgrade pip
python -m pip install --upgrade pip

# 6. Install dependencies
pip install flask flask-cors edge-tts pydub moviepy pillow numpy requests python-dotenv

# 7. Run server
python api_server.py
```

---

## ✅ Success Checklist

After installing, verify:

- [ ] `(venv)` appears in your prompt
- [ ] `python --version` shows Python 3.8+
- [ ] `pip --version` shows pip version
- [ ] `pip show flask` shows Flask is installed
- [ ] `python -c "import flask"` runs without error
- [ ] `python api_server.py` starts the server

---

## 🚀 What to Run RIGHT NOW

**Copy this entire block into PowerShell:**

```powershell
# Make sure venv is activated
venv\Scripts\activate

# Install Flask and core dependencies
pip install flask flask-cors edge-tts pydub requests python-dotenv

# Test Flask
python -c "import flask; print('✅ Flask installed successfully!')"

# Run server
python api_server.py
```

---

## 📞 Expected Output After Success

When `python api_server.py` works, you'll see:

```
============================================================
🚀 API SERVER READY - WITH KOKORO TTS!
============================================================
📍 URL: http://localhost:5000
✨ Features: Templates + Research + Video Generation
🎤 Voice: Edge-TTS (FREE)
🎨 Images: Pollinations AI (FREE)
📝 Script: Gemini AI with Templates
============================================================
```

---

## 🎉 You're Done!

Once the server is running:
1. Keep this terminal open
2. Open a NEW terminal for the frontend
3. Navigate to the frontend folder
4. Run `npm run dev`

Both backend and frontend should now work together! 🚀
