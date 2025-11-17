#!/bin/bash

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🔧 FIXING BACKEND - Switching to NEW Architecture"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

# Step 1: Stop OLD backend
echo "⏹️  STEP 1: Stopping OLD backend (api_server.py)..."
pkill -f "api_server.py" 2>/dev/null
pkill -f "python.*api_server.py" 2>/dev/null
sleep 2
echo "✅ Old backend stopped"
echo ""

# Step 2: Verify NEW backend exists
echo "🔍 STEP 2: Checking NEW backend exists..."
if [ -f "story-video-generator/api_server_new.py" ]; then
    echo "✅ Found api_server_new.py"
else
    echo "❌ ERROR: api_server_new.py NOT FOUND!"
    echo "You need to pull the latest changes first!"
    exit 1
fi
echo ""

# Step 3: Start NEW backend
echo "🚀 STEP 3: Starting NEW backend (api_server_new.py)..."
echo ""
echo "This will start the backend with:"
echo "  ✅ Gemini Server 1 (script generation)"
echo "  ✅ Gemini Server 2 (image prompts)"
echo "  ✅ Colab integration (SDXL + Coqui TTS)"
echo ""
echo "Opening backend in new terminal..."
echo ""

# Check if we're in the right directory
if [ -d "story-video-generator" ]; then
    cd story-video-generator
    echo "📍 Starting from: $(pwd)"
    echo ""
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo "⚠️  IMPORTANT: Look for these lines when backend starts:"
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo ""
    echo "You should see:"
    echo "  🔥 NEW VIDEO GENERATOR - Gemini 1 → Gemini 2 → Colab Flow!"
    echo "  1️⃣  Gemini Server 1: Script generation"
    echo "  2️⃣  Gemini Server 2: Image prompts"
    echo "  3️⃣  Google Colab: Video generation"
    echo ""
    echo "If you see 'Voice Engine: EDGE-TTS' → WRONG BACKEND!"
    echo "If you see 'FLUX' → WRONG BACKEND!"
    echo ""
    echo "════════════════════════════════════════════════════════════════════════════════"
    echo ""

    python api_server_new.py
else
    echo "❌ ERROR: story-video-generator directory not found!"
    echo "Run this script from the project root directory"
    exit 1
fi
