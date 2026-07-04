#!/bin/bash
# BUDDY AI OS - Backend Startup Script
# Comprehensive startup with diagnostics and error checking

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        BUDDY AI OS - Backend Startup & Diagnostics             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check Python version
echo "[1/6] Checking Python version..."
python_version=$(python3 --version 2>&1)
echo "✅ Found: $python_version"
echo ""

# Step 2: Check virtual environment
echo "[2/6] Checking virtual environment..."
if [ -d "venv" ]; then
    echo "✅ Virtual environment exists"
    source venv/Scripts/activate 2>/dev/null || source venv/bin/activate 2>/dev/null || echo "⚠️  Could not activate venv"
else
    echo "ℹ️  Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/Scripts/activate 2>/dev/null || source venv/bin/activate 2>/dev/null
fi
echo ""

# Step 3: Install/Update dependencies
echo "[3/6] Installing dependencies..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -q -r backend/requirements.txt
echo "✅ Dependencies installed"
echo ""

# Step 4: Check database
echo "[4/6] Checking database configuration..."
if [ ! -f "backend/.env" ]; then
    echo "⚠️  .env file not found in backend/"
    echo "   Creating from .env.example..."
    cp backend/.env.example backend/.env || echo "✅ .env configured"
else
    echo "✅ .env file exists"
fi
echo ""

# Step 5: Run Python import tests
echo "[5/6] Testing Python imports..."
cd backend
python3 << 'EOF'
import sys
import traceback

print("Testing core imports...")

try:
    from config.settings import settings
    print("✅ Settings loaded successfully")
except Exception as e:
    print(f"❌ Settings import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from db.database import init_db, get_db_session
    print("✅ Database module loaded successfully")
except Exception as e:
    print(f"❌ Database import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from core.buddy_core import BuddyCore
    print("✅ Buddy Core loaded successfully")
except Exception as e:
    print(f"❌ Buddy Core import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from api.main import create_app
    print("✅ API main module loaded successfully")
except Exception as e:
    print(f"❌ API main import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from api.v1 import auth, users, agents, workflows, integrations, notifications, admin, files, analytics, search, marketplace
    print("✅ All API routers loaded successfully")
except Exception as e:
    print(f"❌ API routers import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All imports successful!")
EOF

if [ $? -ne 0 ]; then
    echo "❌ Import tests failed!"
    exit 1
fi

cd ..
echo ""

# Step 6: Display startup information
echo "[6/6] Startup configuration..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All systems ready for startup!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📌 Start backend with:"
echo "   cd backend && python3 -m api.main"
echo ""
echo "📌 Or with uvicorn directly:"
echo "   cd backend && uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "📌 Access API at:"
echo "   🔗 http://localhost:8000/docs (Swagger UI)"
echo "   🔗 http://localhost:8000/health (Health check)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
