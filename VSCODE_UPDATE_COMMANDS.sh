#!/bin/bash
# 🔄 COPY AND PASTE THIS IN YOUR VS CODE TERMINAL
# This will update your local repo with all the new changes

echo "🔄 Updating your local repository with merged changes..."
echo ""

# Navigate to project root (adjust path if needed)
cd ~/story-video-appp || cd ./story-video-appp || cd /path/to/story-video-appp

echo "📍 Current directory: $(pwd)"
echo ""

# Fetch all changes from GitHub
echo "⏳ Fetching latest changes from GitHub..."
git fetch --all

# Switch to the feature branch with all changes
echo "⏳ Switching to feature branch..."
git checkout claude/analyze-code-011aGL55wo11Am5xAjH9MumH

# Pull latest
echo "⏳ Pulling latest changes..."
git pull origin claude/analyze-code-011aGL55wo11Am5xAjH9MumH

echo ""
echo "================================================================================================"
echo "✅ UPDATE COMPLETE!"
echo "================================================================================================"
echo ""
echo "📦 You now have:"
echo "   • Gemini Server 1 (script generation)"
echo "   • Gemini Server 2 (image prompts)"
echo "   • Colab integration (SDXL + Coqui TTS)"
echo "   • Auto-start script"
echo "   • Complete documentation"
echo ""
echo "🚀 NEXT STEPS:"
echo ""
echo "1. Make start script executable:"
echo "   chmod +x START_SYSTEM.sh"
echo ""
echo "2. Start the complete system:"
echo "   ./START_SYSTEM.sh"
echo ""
echo "3. Or manually:"
echo "   # Terminal 1:"
echo "   cd story-video-generator && python api_server_new.py"
echo ""
echo "   # Terminal 2:"
echo "   curl -X POST http://localhost:5000/api/set-colab-url \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"url\": \"https://contemplable-suzy-unfussing.ngrok-free.dev\"}'"
echo ""
echo "   # Terminal 3:"
echo "   cd project-bolt-sb1-nqwbmccj/project && npm run dev"
echo ""
echo "4. Open http://localhost:5173 and generate videos!"
echo ""
echo "================================================================================================"
echo "📖 READ THESE FILES:"
echo "   • COMPLETE_SETUP_GUIDE.md - Full documentation"
echo "   • START_SYSTEM.sh - Auto-start script"
echo "   • COLAB_NGROK_URL.txt - Ngrok configuration"
echo "================================================================================================"
echo ""
