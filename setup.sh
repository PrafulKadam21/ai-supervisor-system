#!/bin/bash

# Frontdesk AI Supervisor - Setup Script
# This script helps automate the initial setup

set -e

echo "=================================="
echo "🚀 Frontdesk AI Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create directory structure
echo "Creating directory structure..."
mkdir -p agent database services supervisor/templates
echo "✅ Directories created"
echo ""

# Create __init__.py files
echo "Creating __init__.py files..."
touch agent/__init__.py
touch database/__init__.py
touch services/__init__.py
touch supervisor/__init__.py
echo "✅ __init__.py files created"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found"
    echo ""
    echo "Creating .env from template..."
    cat > .env << 'EOF'
# Groq Configuration
GROQ_API_KEY=your_groq_api_key_here

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=./firebase_config.json

# LiveKit Configuration (optional for now)
LIVEKIT_URL=wss://placeholder.livekit.cloud
LIVEKIT_API_KEY=placeholder
LIVEKIT_API_SECRET=placeholder

# Flask Configuration
FLASK_SECRET_KEY=dev-secret-key-change-me
SUPERVISOR_PORT=5000

# Business Information
BUSINESS_NAME=Luxe Hair Salon
BUSINESS_HOURS=Mon-Sat 9AM-7PM
BUSINESS_PHONE=+1-555-123-4567
EOF
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: You need to:"
    echo "   1. Add your Groq API key to .env"
    echo "   2. Download firebase_config.json from Firebase Console"
    echo "   3. Place firebase_config.json in project root"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

# Check for Firebase config
if [ ! -f "firebase_config.json" ]; then
    echo "⚠️  firebase_config.json not found"
    echo ""
    echo "📝 To get firebase_config.json:"
    echo "   1. Go to https://console.firebase.google.com/"
    echo "   2. Create or select your project"
    echo "   3. Go to Project Settings → Service Accounts"
    echo "   4. Click 'Generate New Private Key'"
    echo "   5. Save the file as firebase_config.json here"
    echo ""
else
    echo "✅ firebase_config.json found"
    echo ""
fi

# Check if Groq API key is set
if grep -q "your_groq_api_key_here" .env 2>/dev/null; then
    echo "⚠️  Groq API key not set in .env"
    echo ""
    echo "📝 To get Groq API key:"
    echo "   1. Go to https://console.groq.com/"
    echo "   2. Sign up (free)"
    echo "   3. Create API key"
    echo "   4. Update GROQ_API_KEY in .env"
    echo ""
fi

echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Make sure you've set up:"
echo "   - Groq API key in .env"
echo "   - firebase_config.json file"
echo ""
echo "2. Seed initial data:"
echo "   python main.py seed"
echo ""
echo "3. Test the system:"
echo "   python main.py test"
echo ""
echo "4. Run the system:"
echo "   Terminal 1: python main.py supervisor"
echo "   Terminal 2: python simple_agent.py"
echo ""
echo "5. Open dashboard:"
echo "   http://localhost:5000"
echo ""
echo "📚 For detailed instructions, see QUICKSTART.md"
echo ""