# 🔧 Fix: White Page in Frontend

## Problem: Frontend Shows Blank White Page

This usually means a JavaScript error is preventing the app from loading.

---

## ✅ Step 1: Check Browser Console

1. **Open your browser** to http://localhost:5173
2. **Press F12** (or right-click → Inspect)
3. **Click "Console" tab**
4. **Look for RED error messages**

**Common errors you might see:**
- `Uncaught ReferenceError`
- `Module not found`
- `Failed to fetch`
- `CORS error`

**📸 Take a screenshot of any errors and share them!**

---

## ✅ Step 2: Check Terminal Output

Look at your frontend terminal - do you see any errors?

**Good output (no errors):**
```
✓ 245 modules transformed.
```

**Bad output (has errors):**
```
✗ [ERROR] Failed to resolve...
```

---

## ✅ Step 3: Quick Fixes to Try

### Fix 1: Clear Cache and Restart

```powershell
# Stop frontend (Ctrl+C)

# Clear Vite cache
rmdir /s node_modules\.vite

# Restart
npm run dev
```

### Fix 2: Reinstall Dependencies

```powershell
# Stop frontend (Ctrl+C)

# Delete node_modules
rmdir /s node_modules

# Reinstall
npm install

# Restart
npm run dev
```

### Fix 3: Check Backend is Running

Make sure your backend is still running in the other terminal!

**Backend should show:**
```
🚀 API SERVER READY
📍 URL: http://localhost:5000
```

If not, restart it:
```powershell
python api_server.py
```

---

## 🔍 Common Causes & Solutions

### Cause 1: Missing Dependencies

**Symptoms:**
- Console shows "Module not found"
- Terminal shows import errors

**Solution:**
```powershell
npm install
```

### Cause 2: TypeScript Errors

**Symptoms:**
- Terminal shows type errors
- Red squiggly lines in code

**Solution:**
```powershell
# Skip type checking for now
npm run dev -- --force
```

### Cause 3: Backend Not Running

**Symptoms:**
- Console shows "Failed to fetch"
- Network errors

**Solution:**
- Make sure backend is running on port 5000

### Cause 4: Port Already in Use

**Symptoms:**
- Terminal says "Port 5173 already in use"

**Solution:**
```powershell
# Kill any process on port 5173
netstat -ano | findstr :5173
# Note the PID and kill it
taskkill /PID <PID_NUMBER> /F

# Then restart
npm run dev
```

---

## 🧪 Test the App Step by Step

### Test 1: Can you see the HTML?

Right-click on the white page → View Page Source

**Good:** You see HTML with `<div id="root"></div>`
**Bad:** You see blank or error page

### Test 2: Is React loading?

In browser console, type:
```javascript
document.getElementById('root')
```

**Good:** Returns `<div id="root"></div>`
**Bad:** Returns `null`

### Test 3: Check network requests

1. Open browser DevTools (F12)
2. Go to "Network" tab
3. Refresh page (F5)
4. Look for failed requests (red)

---

## 🎯 Most Likely Issues

### Issue 1: Environment Variables Missing

**Check if `.env` file exists:**
```powershell
dir .env
```

**If missing, create it:**
```powershell
# Create .env file
echo VITE_API_URL=http://localhost:5000 > .env
```

Then restart:
```powershell
npm run dev
```

### Issue 2: Supabase Configuration Error

The app might crash if Supabase isn't configured.

**Quick fix - check console for Supabase errors**

If you see Supabase errors, the app is trying to connect to a database.

**You can skip this for now** - the gallery feature is optional.

---

## 🆘 Emergency Fix: Use Fallback Build

If nothing works, try the production build:

```powershell
# Build the app
npm run build

# Preview the build
npm run preview
```

This will open on a different port (usually 4173).

---

## 📋 Diagnostic Checklist

Run through this checklist:

- [ ] Backend is running on http://localhost:5000
- [ ] Frontend terminal shows no errors
- [ ] Browser console (F12) shows no red errors
- [ ] `node_modules` folder exists
- [ ] `npm install` completed successfully
- [ ] Can access http://localhost:5173
- [ ] Page shows white (not loading forever)

---

## 🚀 What to Do RIGHT NOW

**1. Open browser to http://localhost:5173**

**2. Press F12 to open DevTools**

**3. Click "Console" tab**

**4. Look for any RED errors**

**5. Copy the error message here:**
```
[Paste error message here]
```

**6. Also check terminal for errors:**
```
[Paste terminal output here]
```

---

## 💡 Quick Troubleshooting Commands

**Copy this block and run it:**

```powershell
# Stop frontend (Ctrl+C)

# Clear cache
Remove-Item -Recurse -Force node_modules\.vite -ErrorAction SilentlyContinue

# Restart
npm run dev
```

---

## 📞 What Information I Need

To help you fix this, please tell me:

1. **What errors show in browser console (F12)?**
2. **What does the frontend terminal show?**
3. **Is the backend still running?**
4. **Does the page say "Loading..." or is it completely blank?**

---

After you check the browser console (F12), share what errors you see and I'll help fix them! 🔍
