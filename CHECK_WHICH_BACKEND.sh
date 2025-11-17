#!/bin/bash

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🔍 DIAGNOSTIC: Which Backend is Running?"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

# Check running processes
echo "📊 Checking running Python processes..."
echo ""

OLD_BACKEND=$(ps aux | grep "api_server.py" | grep -v grep | grep -v "api_server_new.py")
NEW_BACKEND=$(ps aux | grep "api_server_new.py" | grep -v grep)

if [ ! -z "$OLD_BACKEND" ]; then
    echo "❌ OLD BACKEND RUNNING (api_server.py):"
    echo "$OLD_BACKEND"
    echo ""
    echo "⚠️  PROBLEM: This uses Edge-TTS + Flux LOCALLY"
    echo "You need to stop this and start api_server_new.py instead!"
    echo ""
    echo "Run this to fix:"
    echo "  ./FIX_BACKEND_NOW.sh"
    echo ""
fi

if [ ! -z "$NEW_BACKEND" ]; then
    echo "✅ NEW BACKEND RUNNING (api_server_new.py):"
    echo "$NEW_BACKEND"
    echo ""
    echo "Good! This should use Gemini 1 → Gemini 2 → Colab"
    echo ""
fi

if [ -z "$OLD_BACKEND" ] && [ -z "$NEW_BACKEND" ]; then
    echo "⚠️  NO BACKEND RUNNING!"
    echo ""
    echo "Start the NEW backend with:"
    echo "  ./FIX_BACKEND_NOW.sh"
    echo ""
fi

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "🧪 Testing Backend Endpoint..."
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

HEALTH_CHECK=$(curl -s http://localhost:5000/health 2>/dev/null)

if [ $? -eq 0 ]; then
    echo "✅ Backend responding at http://localhost:5000"
    echo ""
    echo "Response:"
    echo "$HEALTH_CHECK" | python -m json.tool 2>/dev/null || echo "$HEALTH_CHECK"
    echo ""

    # Check if it mentions Colab
    if echo "$HEALTH_CHECK" | grep -q "colab"; then
        echo "✅ CORRECT: Backend mentions Colab integration!"
    else
        echo "❌ WRONG: No Colab integration detected!"
        echo "This is the OLD backend!"
    fi
else
    echo "❌ Backend NOT responding at http://localhost:5000"
    echo "Start it with: ./FIX_BACKEND_NOW.sh"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
