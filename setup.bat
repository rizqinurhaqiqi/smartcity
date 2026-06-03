@echo off
REM Smart Traffic Bandung - Setup Script for Windows

echo 🚦 Smart Traffic Bandung - Setup Script
echo ======================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.9+
    exit /b 1
)
for /f "tokens=2 in ('python --version 2^>^&1')" do set PYTHON_VERSION=%1
echo ✅ Python %PYTHON_VERSION%

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found. Please install Node.js 18+
    exit /b 1
)
for /f %%I in ('node --version') do set NODE_VERSION=%%I
echo ✅ Node.js %NODE_VERSION%

echo.
echo 🔧 Setting up Backend...
cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Check .env file
if not exist ".env" (
    echo Creating .env from template...
    copy .env.example .env
    echo ⚠️  Please edit .env with your MySQL credentials
)

echo ✅ Backend setup complete!

cd ..

echo.
echo 🎨 Setting up Frontend...
cd frontend

REM Install dependencies
echo Installing Node dependencies...
call npm install

echo ✅ Frontend setup complete!

cd ..

echo.
echo ======================================
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Edit backend\.env with your MySQL credentials
echo 2. Start MySQL service
echo 3. Run backend:
echo    cd backend
echo    venv\Scripts\activate.bat
echo    python -m uvicorn app.main:app --reload
echo.
echo 4. In another terminal, run frontend:
echo    cd frontend
echo    npm run dev
echo.
echo 5. Open http://localhost:5173 in your browser
echo.
echo API docs: http://localhost:8000/docs
echo.
pause
