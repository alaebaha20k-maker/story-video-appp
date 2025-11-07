#!/bin/bash

echo "🔍 AI Video Generator - Installation Verification"
echo "=================================================="
echo ""

# Check Node.js
echo "1️⃣  Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "   ✅ Node.js $NODE_VERSION installed"
else
    echo "   ❌ Node.js not found"
    exit 1
fi

# Check npm
echo ""
echo "2️⃣  Checking npm..."
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "   ✅ npm $NPM_VERSION installed"
else
    echo "   ❌ npm not found"
    exit 1
fi

# Check project files
echo ""
echo "3️⃣  Checking project structure..."
if [ -d "node_modules" ]; then
    echo "   ✅ node_modules exists"
else
    echo "   ❌ node_modules not found - run 'npm install'"
    exit 1
fi

if [ -f "package.json" ]; then
    echo "   ✅ package.json exists"
else
    echo "   ❌ package.json not found"
    exit 1
fi

# Check source files
echo ""
echo "4️⃣  Checking source files..."
COMPONENTS_COUNT=$(find src/components -name "*.tsx" 2>/dev/null | wc -l)
PAGES_COUNT=$(find src/pages -name "*.tsx" 2>/dev/null | wc -l)
echo "   ✅ Found $COMPONENTS_COUNT components"
echo "   ✅ Found $PAGES_COUNT pages"

# Check documentation
echo ""
echo "5️⃣  Checking documentation..."
DOCS=$(ls -1 *.md 2>/dev/null | wc -l)
echo "   ✅ Found $DOCS documentation files"

# Check if Supabase is configured
echo ""
echo "6️⃣  Checking Supabase configuration..."
if [ -f ".env" ]; then
    if grep -q "VITE_SUPABASE_URL" .env; then
        echo "   ✅ Supabase configured in .env"
    else
        echo "   ⚠️  .env exists but missing Supabase URL"
    fi
else
    echo "   ℹ️  .env not found (optional - gallery won't work without it)"
fi

echo ""
echo "=================================================="
echo "✅ Installation verification complete!"
echo ""
echo "Next steps:"
echo "1. npm run dev           # Start frontend at http://localhost:5173"
echo "2. Start your backend at http://localhost:5000"
echo "3. Check for green 'API Server Connected' badge"
echo ""
echo "For troubleshooting, see QUICK_START.md"
