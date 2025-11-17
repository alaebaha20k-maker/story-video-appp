#!/bin/bash

# 🚀 START COMPLETE VIDEO GENERATION SYSTEM
# This script starts the entire system in the correct order

echo "================================================================================================"
echo "🎬 STARTING COMPLETE VIDEO GENERATION SYSTEM"
echo "================================================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

COLAB_URL="https://contemplable-suzy-unfussing.ngrok-free.dev"

echo -e "${BLUE}📋 System Components:${NC}"
echo "   1. Google Colab (SDXL + Coqui TTS + FFmpeg)"
echo "   2. Backend Server (Gemini Server 1 + 2 + Orchestration)"
echo "   3. Frontend (React + Vite)"
echo ""

# Step 1: Verify Colab is running
echo -e "${YELLOW}⏳ Step 1: Checking if Colab is running...${NC}"
if curl -s -f "${COLAB_URL}/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Colab is running at ${COLAB_URL}${NC}"
else
    echo -e "${YELLOW}⚠️  Colab is not responding. Please:${NC}"
    echo "   1. Open your Colab notebook"
    echo "   2. Run all cells (1-7)"
    echo "   3. Copy the ngrok URL if it changed"
    echo "   4. Update COLAB_URL in this script if needed"
    echo ""
    read -p "Press Enter when Colab is running, or Ctrl+C to exit..."
fi

echo ""

# Step 2: Start Backend
echo -e "${YELLOW}⏳ Step 2: Starting Backend Server...${NC}"
cd /home/user/story-video-appp/story-video-generator

# Kill any existing backend process
pkill -f "api_server_new.py" 2>/dev/null

# Start backend in background
nohup python api_server_new.py > backend.log 2>&1 &
BACKEND_PID=$!

echo "   Waiting for backend to start..."
sleep 5

# Check if backend is running
if curl -s -f http://localhost:5000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend started (PID: ${BACKEND_PID})${NC}"
else
    echo -e "${YELLOW}⚠️  Backend failed to start. Check backend.log${NC}"
    exit 1
fi

echo ""

# Step 3: Set Colab URL
echo -e "${YELLOW}⏳ Step 3: Connecting Backend to Colab...${NC}"
curl -s -X POST http://localhost:5000/api/set-colab-url \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"${COLAB_URL}\"}" | python -m json.tool

echo -e "${GREEN}✅ Colab URL configured${NC}"
echo ""

# Step 4: Start Frontend
echo -e "${YELLOW}⏳ Step 4: Starting Frontend...${NC}"
cd /home/user/story-video-appp/project-bolt-sb1-nqwbmccj/project

# Kill any existing frontend process
pkill -f "vite" 2>/dev/null

# Start frontend in background
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!

echo "   Waiting for frontend to start..."
sleep 8

if curl -s -f http://localhost:5173 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend started (PID: ${FRONTEND_PID})${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend failed to start. Check frontend.log${NC}"
fi

echo ""
echo "================================================================================================"
echo -e "${GREEN}🎉 SYSTEM READY!${NC}"
echo "================================================================================================"
echo ""
echo -e "${BLUE}📍 URLs:${NC}"
echo "   🌐 Frontend:  http://localhost:5173"
echo "   🔌 Backend:   http://localhost:5000"
echo "   ☁️  Colab:     ${COLAB_URL}"
echo ""
echo -e "${BLUE}📊 System Status:${NC}"
curl -s http://localhost:5000/health | python -m json.tool
echo ""
echo -e "${BLUE}📝 Logs:${NC}"
echo "   Backend:  tail -f /home/user/story-video-appp/story-video-generator/backend.log"
echo "   Frontend: tail -f /home/user/story-video-appp/project-bolt-sb1-nqwbmccj/project/frontend.log"
echo ""
echo -e "${BLUE}🛑 To Stop:${NC}"
echo "   kill ${BACKEND_PID} ${FRONTEND_PID}"
echo "   Or: pkill -f 'api_server_new.py|vite'"
echo ""
echo "================================================================================================"
echo -e "${GREEN}✅ Ready to generate videos! Open http://localhost:5173 in your browser${NC}"
echo "================================================================================================"
