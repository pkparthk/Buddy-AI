#!/usr/bin/env python3
"""
Simple deployment readiness verification
"""

import os

def check_deployment_ready():
    print("🚀 Buddy AI - Deployment Readiness Check")
    print("=" * 45)
    
    checks_passed = 0
    total_checks = 5
    
    # Check 1: .env file exists
    if os.path.exists('.env'):
        print("✅ .env file exists")
        checks_passed += 1
    else:
        print("❌ .env file missing")
    
    # Check 2: API key configured
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            content = f.read()
            if 'GEMINI_API_KEY=' in content and not 'your_actual' in content:
                print("✅ GEMINI_API_KEY configured")
                checks_passed += 1
            else:
                print("❌ GEMINI_API_KEY not set")
    
    # Check 3: Backend files exist
    if os.path.exists('api.py') and os.path.exists('requirements.txt'):
        print("✅ Backend files ready")
        checks_passed += 1
    else:
        print("❌ Backend files missing")
    
    # Check 4: Frontend files exist
    if os.path.exists('my-app/package.json') and os.path.exists('my-app/vercel.json'):
        print("✅ Frontend files ready")
        checks_passed += 1
    else:
        print("❌ Frontend files missing")
    
    # Check 5: Deployment configs exist
    if os.path.exists('render.yaml') and os.path.exists('COMPLETE_DEPLOYMENT_GUIDE.md'):
        print("✅ Deployment configs ready")
        checks_passed += 1
    else:
        print("❌ Deployment configs missing")
    
    print(f"\n📊 {checks_passed}/{total_checks} checks passed")
    
    if checks_passed == total_checks:
        print("🎉 READY TO DEPLOY!")
        print("📖 Follow COMPLETE_DEPLOYMENT_GUIDE.md")
    else:
        print("⚠️  Fix issues above before deploying")
    
    return checks_passed == total_checks

if __name__ == "__main__":
    check_deployment_ready()
