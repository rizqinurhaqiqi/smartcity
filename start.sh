#!/bin/bash

# Quick start script untuk development

echo "🚀 Starting Smart Traffic Bandung..."
echo ""

# Check if MySQL is running
if ! pgrep -x "mysqld" > /dev/null; then
    echo "⚠️  MySQL is not running. Starting MySQL..."
    mysql.server start
    sleep 2
fi

# Start Backend
echo "🔧 Starting Backend Server..."
cd backend
source venv/bin/activate 2>/dev/null || python -m venv venv && source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 2

# Start Frontend
echo "🎨 Starting Frontend Server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "======================================"
echo "✅ All services started!"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo "======================================"

# Handle Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID" INT

wait
