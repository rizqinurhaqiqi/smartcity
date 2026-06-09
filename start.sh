#!/bin/bash

# Quick start script untuk development
# Jalankan dari folder root project: bash start.sh

DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Starting Smart Traffic Bandung..."
echo ""

# Kill existing processes on ports
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null
sleep 1

# Start Backend
echo "[1/2] Starting Backend (port 8000)..."
cd "$DIR/backend"
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
sleep 3

# Start Frontend
echo "[2/2] Starting Frontend (port 5173)..."
cd "$DIR/frontend"
npm run dev &
FRONTEND_PID=$!
sleep 3

echo ""
echo "======================================"
echo "  All services started!"
echo ""
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to stop all services"
echo "======================================"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" INT TERM
wait
