#!/bin/bash

# Buddy AI OS - Development Setup Script
# This script sets up the complete development environment

set -e

echo "🚀 Buddy AI OS - Development Setup"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "📦 Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
else
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

# Check Node.js
echo "📦 Checking Node.js installation..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js $NODE_VERSION found${NC}"
else
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

# Check Docker
echo "📦 Checking Docker installation..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✅ $DOCKER_VERSION found${NC}"
else
    echo -e "${YELLOW}⚠️  Docker not found. Some features will be unavailable${NC}"
fi

# Setup Backend
echo ""
echo "🔧 Setting up Backend..."

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate || . venv/Scripts/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements-dev.txt

# Create logs directory
mkdir -p logs

echo -e "${GREEN}✅ Backend setup complete${NC}"

cd ..

# Setup Frontend
echo ""
echo "🔧 Setting up Frontend..."

cd frontend-web

# Install Node dependencies
echo "Installing Node dependencies..."
npm install --legacy-peer-deps

echo -e "${GREEN}✅ Frontend setup complete${NC}"

cd ..

# Setup Environment
echo ""
echo "📝 Setting up environment variables..."

if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please update .env with your configuration${NC}"
else
    echo -e "${GREEN}✅ .env file exists${NC}"
fi

# Summary
echo ""
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo ""
echo "📚 Next Steps:"
echo "1. Review and update .env file with your configuration"
echo "2. Start Docker services: docker-compose up -d"
echo "3. Run development server: bash scripts/dev.sh"
echo ""
echo "📖 Documentation: https://github.com/tecno-spark/buddy-ai-os"
