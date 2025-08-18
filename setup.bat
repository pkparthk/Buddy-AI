@echo off
REM Buddy AI Deployment Setup Script for Windows

echo 🚀 Setting up Buddy AI for deployment...

REM Check if .env exists
if not exist .env (
    echo 📋 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env file and add your API keys!
    echo    - Get Gemini API key from: https://makersuite.google.com/app/apikey
)

REM Install backend dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

REM Setup frontend
echo ⚛️  Setting up React frontend...
cd my-app
call npm install

REM Build frontend for production
echo 🏗️  Building frontend for production...
call npm run build

cd ..

echo ✅ Setup complete!
echo.
echo 🔑 Next steps:
echo 1. Edit .env file with your API keys
echo 2. Update CORS origins in api.py with your frontend URL
echo 3. Update VITE_BACKEND_URL in my-app/.env.production
echo 4. Deploy to your chosen platform (Railway, Render, etc.)
echo.
echo 📖 See DEPLOYMENT_GUIDE.md for detailed instructions

pause
