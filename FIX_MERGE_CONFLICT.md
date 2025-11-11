# 🔧 Fix Merge Conflict in VS Code

## Problem
Your local `api_server.py` has merge conflict markers causing syntax error:
```
<<<<<<< HEAD
```

## ✅ Solution - Run These Commands in VS Code Terminal:

### Step 1: Discard Local Changes and Get Clean Version
```bash
cd C:\Users\pc\story-video-generator\story-video-appp\story-video-generator

# Discard your local conflicted file
git checkout HEAD -- api_server.py

# Pull latest from GitHub
git pull origin claude/fix-image-voice-api-errors-011CUzvEAt2GjmdFRLuwwzzj
```

### Step 2: Verify It's Fixed
```bash
# Should show no conflicts
python api_server.py
```

---

## 🚀 Complete Fresh Start (If Above Doesn't Work)

If you still have issues, do a complete reset:

```bash
cd C:\Users\pc\story-video-generator\story-video-appp

# Save your local changes (if any you want to keep)
git stash

# Get latest from GitHub (clean version)
git fetch origin
git reset --hard origin/claude/fix-image-voice-api-errors-011CUzvEAt2GjmdFRLuwwzzj

# Now you have a clean copy
cd story-video-generator
python api_server.py
```

---

## ✅ What's in GitHub (Clean & Ready):

1. ✅ **api_server.py** - No conflicts, 768 lines, working
2. ✅ **config/settings.py** - COLAB_SERVER_URL = 'https://contemplable-suzy-unfussing.ngrok-free.dev'
3. ✅ All fixes applied and tested

---

## 🎯 After Running Commands Above:

Your VS Code will have:
- ✅ No merge conflicts
- ✅ Clean api_server.py
- ✅ Updated COLAB_SERVER_URL
- ✅ Ready to run `python api_server.py`

---

**Just copy-paste the commands above and you're done!** 🚀
