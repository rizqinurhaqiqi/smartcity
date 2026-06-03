#!/bin/bash

# Smart Traffic Bandung - Setup Script

echo "🚦 Smart Traffic Bandung - Setup Script"
echo "======================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi
echo "✅ Python $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi
echo "✅ Node.js $(node --version)"

# Check MySQL
if ! command -v mysql &> /dev/null; then
    echo "⚠️  MySQL not found. Make sure MySQL server is installed and running"
else
    echo "✅ MySQL found"
fi

echo ""
echo "🔧 Setting up Backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check .env file
if [ ! -f ".env" ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your MySQL credentials"
fi

echo "✅ Backend setup complete!"

cd ..

echo ""
echo "🎨 Setting up Frontend..."
cd frontend

# Install dependencies
echo "Installing Node dependencies..."
npm install

echo "✅ Frontend setup complete!"

cd ..

echo ""
echo "======================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your MySQL credentials"
echo "2. Start MySQL: mysql.server start (or brew services start mysql)"
echo "3. Run backend:"
echo "   cd backend && source venv/bin/activate"
echo "   python -m uvicorn app.main:app --reload"
echo ""
echo "4. In another terminal, run frontend:"
echo "   cd frontend && npm run dev"
echo ""
echo "5. Open http://localhost:5173 in your browser"
echo ""
echo "API docs: http://localhost:8000/docs"
