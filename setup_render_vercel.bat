@echo off
echo 🚀 Buddy AI - Render + Vercel Setup
echo.

echo 📋 Step 1: Checking deployment readiness...
python render_vercel_check.py

echo.
echo 📦 Step 2: Installing dependencies...
pip install -r requirements.txt

echo.
echo ⚛️  Step 3: Setting up frontend...
cd my-app
call npm install
echo Frontend dependencies installed!

cd ..
echo.
echo ✅ Setup complete!
echo.
echo 🚀 Next steps:
echo 1. Make sure your .env file has your real GEMINI_API_KEY
echo 2. Push your code to GitHub
echo 3. Follow RENDER_VERCEL_DEPLOYMENT.md for deployment steps
echo.
echo 📖 Deployment guide: RENDER_VERCEL_DEPLOYMENT.md
echo.
pause
