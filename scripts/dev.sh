#!/bin/bash

# Buddy AI OS - Development Server Script
# Starts the complete development environment

set -e

echo "🚀 Starting Buddy AI OS Development Environment"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if Docker is running
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker not found. Skipping Docker services.${NC}"
    echo "Install Docker to run database services automatically"
else
    echo "🐳 Starting Docker services..."
    docker-compose up -d postgres redis chromadb ollama

    # Wait for services to be healthy
    echo "⏳ Waiting for services to be healthy..."
    sleep 5
    echo -e "${GREEN}✅ Docker services started${NC}"
fi

echo ""
echo "🔧 Starting Backend..."

# Activate Python virtual environment
cd backend
source venv/bin/activate || . venv/Scripts/activate

# Start FastAPI server
echo -e "${BLUE}Backend running on: http://localhost:8000${NC}"
echo "API Docs: http://localhost:8000/docs"
echo ""

# Run in background
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

cd ..

echo ""
echo "🎨 Starting Frontend..."

cd frontend-web

# Start React development server
echo -e "${BLUE}Frontend running on: http://localhost:3000${NC}"
echo ""

# Run in background
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo -e "${GREEN}✅ Development environment is ready!${NC}"
echo ""
echo "📍 Services Running:"
echo "   • Frontend: http://localhost:3000"
echo "   • Backend: http://localhost:8000"
echo "   • API Docs: http://localhost:8000/docs"
echo "   • PostgreSQL: localhost:5432"
echo "   • Redis: localhost:6379"
echo "   • ChromaDB: http://localhost:8001"
echo "   • Ollama: http://localhost:11434"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
