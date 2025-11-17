#!/bin/bash

echo "═══════════════════════════════════════════════════════════════"
echo "🔄 RESTARTING BACKEND WITH LATEST CHANGES"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Stop old backend
echo "⏹️  Stopping old backend..."
pkill -f "python.*api_server"
sleep 2
echo "✅ Old backend stopped"
echo ""

# Pull latest changes
echo "📥 Pulling latest changes..."
cd /home/user/story-video-appp
git pull origin claude/analyze-code-011aGL55wo11Am5xAjH9MumH
echo ""

# Start new backend
echo "🚀 Starting NEW backend..."
echo ""
cd story-video-generator

# Run in foreground so you can see output
python api_server_new.py
