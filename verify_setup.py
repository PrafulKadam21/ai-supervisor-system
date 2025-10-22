#!/usr/bin/env python3
"""
Setup Verification Script
Run this to verify your environment is correctly configured
"""
import os
import sys
from pathlib import Path


def check_mark(passed):
    return "✅" if passed else "❌"


def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def check_files():
    """Check if all required files exist"""
    print_header("Checking File Structure")
    
    required_files = {
        "Core Files": [
            "main.py",
            "simple_agent.py",
            "requirements.txt",
            ".env",
            "firebase_config.json",
            ".gitignore"
        ],
        "Agent Files": [
            "agent/__init__.py",
            "agent/ai_agent.py",
            "agent/knowledge_base.py",
            "agent/prompts.py"
        ],
        "Database Files": [
            "database/__init__.py",
            "database/models.py",
            "database/firebase_client.py"
        ],
        "Service Files": [
            "services/__init__.py",
            "services/help_request_service.py",
            "services/notification_service.py"
        ],
        "Supervisor Files": [
            "supervisor/__init__.py",
            "supervisor/app.py",
            "supervisor/routes.py",
            "supervisor/templates/dashboard.html"
        ],
        "Documentation": [
            "README.md",
            "QUICKSTART.md"
        ]
    }
    
    all_passed = True
    for category, files in required_files.items():
        print(f"\n{category}:")
        for file_path in files:
            exists = Path(file_path).exists()
            all_passed = all_passed and exists
            print(f"  {check_mark(exists)} {file_path}")
    
    return all_passed


def check_env_vars():
    """Check if environment variables are set"""
    print_header("Checking Environment Variables")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        "GROQ_API_KEY": "Should start with 'gsk_'",
        "FIREBASE_CREDENTIALS_PATH": "Path to firebase_config.json",
        "FLASK_SECRET_KEY": "Random secret key",
        "BUSINESS_NAME": "Your business name"
    }
    
    all_passed = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        exists = value is not None and value != "" and "placeholder" not in value.lower() and "your_" not in value.lower()
        
        if var == "GROQ_API_KEY" and exists:
            exists = value.startswith("gsk_")
        
        all_passed = all_passed and exists
        status = check_mark(exists)
        print(f"  {status} {var}")
        if not exists:
            print(f"      ⚠️  {description}")
    
    return all_passed


def check_dependencies():
    """Check if required packages are installed"""
    print_header("Checking Python Dependencies")
    
    required_packages = [
        "firebase_admin",
        "groq",
        "flask",
        "pydantic",
        "python-dotenv",
        "livekit"
    ]
    
    all_passed = True
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            all_passed = False
    
    return all_passed


def check_firebase():
    """Check Firebase connection"""
    print_header("Checking Firebase Connection")
    
    try:
        from database.firebase_client import FirebaseClient
        fb = FirebaseClient()
        print("  ✅ Firebase client initialized")
        print("  ✅ Connection successful")
        return True
    except Exception as e:
        print(f"  ❌ Firebase connection failed: {str(e)}")
        return False


def check_groq():
    """Check Groq API connection"""
    print_header("Checking Groq API Connection")
    
    try:
        from groq import Groq
        from dotenv import load_dotenv
        load_dotenv()
        
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Test with a simple request
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5
        )
        
        print("  ✅ Groq API key is valid")
        print("  ✅ API connection successful")
        return True
    except Exception as e:
        print(f"  ❌ Groq API connection failed: {str(e)}")
        return False


def check_python_version():
    """Check Python version"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    is_valid = version.major == 3 and version.minor >= 9
    print(f"  {check_mark(is_valid)} Python {version_str}")
    
    if not is_valid:
        print("  ⚠️  Python 3.9+ required")
    
    return is_valid


def main():
    """Run all checks"""
    print("\n" + "🔍 " + "="*58)
    print("    FRONTDESK AI SUPERVISOR - SETUP VERIFICATION")
    print("="*60)
    
    results = {}
    
    # Run all checks
    results["Python Version"] = check_python_version()
    results["File Structure"] = check_files()
    results["Environment Variables"] = check_env_vars()
    results["Dependencies"] = check_dependencies()
    results["Firebase Connection"] = check_firebase()
    results["Groq API Connection"] = check_groq()
    
    # Summary
    print_header("Summary")
    
    all_passed = all(results.values())
    
    for check, passed in results.items():
        print(f"  {check_mark(passed)} {check}")
    
    print("\n" + "="*60)
    
    if all_passed:
        print("  ✅ ALL CHECKS PASSED!")
        print("  🚀 You're ready to run the system!")
        print("\n  Next steps:")
        print("    1. python main.py seed       # Add initial data")
        print("    2. python main.py supervisor # Terminal 1")
        print("    3. python simple_agent.py    # Terminal 2")
        print("    4. Open http://localhost:5000")
    else:
        print("  ❌ SOME CHECKS FAILED")
        print("\n  Please fix the issues above before proceeding.")
        print("  Check QUICKSTART.md for detailed setup instructions.")
    
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())