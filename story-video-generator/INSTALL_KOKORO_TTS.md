# 🎤 Install Kokoro TTS - Step by Step

## Why You Need Kokoro

Kokoro TTS provides:
- 48 professional voices
- Better quality than Edge-TTS
- Faster generation (with optimizations)
- More natural speech

---

## ✅ Installation Methods

### Method 1: Install from PyPI (Recommended)

```powershell
# In your venv-activated terminal
pip install kokoro-onnx soundfile torch
```

### Method 2: Install from GitHub (Latest Version)

```powershell
pip install git+https://github.com/thewh1teagle/kokoro-onnx.git
pip install soundfile torch
```

### Method 3: Manual Installation

```powershell
# Install dependencies first
pip install soundfile numpy torch

# Install kokoro
pip install kokoro-onnx
```

---

## 🔍 Verify Installation

After installation, test if it works:

```powershell
python -c "from kokoro import KPipeline; print('✅ Kokoro installed successfully!')"
```

If you see the success message, Kokoro is ready!

---

## 🆘 Common Issues

### Issue 1: "No module named 'kokoro'"

**Solution - Try alternative package name:**
```powershell
pip install kokoro-tts
```

Or:
```powershell
pip install kokoro-onnx
```

### Issue 2: ONNX Runtime Error

**Solution - Install ONNX runtime:**
```powershell
pip install onnxruntime
```

For GPU support (if you have NVIDIA GPU):
```powershell
pip install onnxruntime-gpu
```

### Issue 3: Torch Installation Issues

**Solution - Install CPU-only PyTorch:**
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Issue 4: SoundFile Error

**Solution:**
```powershell
pip install soundfile
```

---

## 📦 All Dependencies for Kokoro

Install all at once:

```powershell
pip install torch soundfile numpy kokoro-onnx onnxruntime
```

---

## 🧪 Test Kokoro After Installation

Create a test file `test_kokoro.py`:

```python
from kokoro import KPipeline

# Initialize
pipeline = KPipeline(lang_code='a')

# Generate test audio
text = "Hello, this is a test of Kokoro TTS."
generator = pipeline(text, voice='af_bella', speed=1.0)

# Collect audio
audio_segments = []
for gs, ps, audio in generator:
    audio_segments.append(audio)

if audio_segments:
    print("✅ Kokoro TTS working!")
else:
    print("❌ Kokoro TTS failed")
```

Run it:
```powershell
python test_kokoro.py
```

---

## 🎯 Restart Backend After Installation

After installing Kokoro:

1. Stop the backend (Ctrl+C in backend terminal)
2. Restart it:
```powershell
python api_server.py
```

You should see:
```
🎤 Voice: Kokoro TTS (48 voices, FREE!)
```

Instead of:
```
⚠️ Kokoro TTS not available
```

---

## 💡 Alternative: Use the Optimized Edge-TTS

If Kokoro installation fails, remember that **Edge-TTS is also optimized** with the same 3-6x speedup and works great!

But if you specifically need Kokoro's voices, follow the installation steps above.

---

## 📞 Package Names to Try

Try these package names in order:

```powershell
# Try 1
pip install kokoro-onnx

# Try 2
pip install kokoro-tts

# Try 3
pip install kokoro

# Try 4 (from GitHub)
pip install git+https://github.com/thewh1teagle/kokoro-onnx.git
```

One of these should work!

---

## ✅ Expected Output After Success

When you restart `python api_server.py`, you should see:

```
============================================================
🚀 API SERVER READY - WITH KOKORO TTS!
============================================================
📍 URL: http://localhost:5000
✨ Features: Templates + Research + Video Generation
🎤 Voice: Kokoro TTS (48 voices, FREE!)
🎤 Backup: Edge-TTS (FREE)
🎨 Images: Pollinations AI (FREE)
📝 Script: Gemini AI with Templates
============================================================
```

No more "⚠️ Kokoro TTS not available" warning!
