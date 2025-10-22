# Step-by-Step Execution Guide

Follow these exact steps to build and run the Frontdesk AI Supervisor system.

## 🎯 Phase 1: Initial Setup (10 minutes)

### Step 1: Create Project Directory

```bash
mkdir frontdesk-ai-supervisor
cd frontdesk-ai-supervisor
```

### Step 2: Create All Directories

```bash
mkdir -p agent
mkdir -p database
mkdir -p services
mkdir -p supervisor/templates
```

### Step 3: Create __init__.py Files

```bash
touch agent/__init__.py
touch database/__init__.py
touch services/__init__.py
touch supervisor/__init__.py
```

### Step 4: Create requirements.txt

Copy the requirements.txt artifact content into a file named `requirements.txt`

### Step 5: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 6: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

✅ **Checkpoint**: Run `pip list` - you should see all packages installed

## 🔥 Phase 2: Firebase Setup (5 minutes)

### Step 7: Create Firebase Project

1. Go to https://console.firebase.google.com/
2. Click "Add project"
3. Enter name: `frontdesk-ai-test`
4. Disable Google Analytics (not needed)
5. Click "Create project"

### Step 8: Enable Firestore

1. In Firebase Console, click "Firestore Database"
2. Click "Create database"
3. Choose "Start in test mode"
4. Select your region (closest to you)
5. Click "Enable"

### Step 9: Get Service Account Key

1. Click the ⚙️ gear icon → "Project settings"
2. Go to "Service accounts" tab
3. Click "Generate new private key"
4. Click "Generate key"
5. Save the JSON file as `firebase_config.json` in your project root

✅ **Checkpoint**: You should have `firebase_config.json` in your project folder

## 🤖 Phase 3: Groq API Setup (2 minutes)

### Step 10: Create Groq Account

1. Go to https://console.groq.com/
2. Sign up (it's free!)
3. Verify your email

### Step 11: Generate API Key

1. In Groq Console, click "API Keys"
2. Click "Create API Key"
3. Give it a name: "frontdesk-ai"
4. Copy the key (starts with `gsk_...`)

✅ **Checkpoint**: You should have your Groq API key copied

## 📝 Phase 4: Configuration (2 minutes)

### Step 12: Create .env File

Create a file named `.env` in your project root:

```bash
# Groq Configuration
GROQ_API_KEY=gsk_YOUR_ACTUAL_KEY_HERE

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=./firebase_config.json

# LiveKit Configuration (optional for now)
LIVEKIT_URL=wss://placeholder.livekit.cloud
LIVEKIT_API_KEY=placeholder
LIVEKIT_API_SECRET=placeholder

# Flask Configuration
FLASK_SECRET_KEY=your-random-secret-key-12345
SUPERVISOR_PORT=5000

# Business Information
BUSINESS_NAME=Luxe Hair Salon
BUSINESS_HOURS=Mon-Sat 9AM-7PM
BUSINESS_PHONE=+1-555-123-4567
```

**Important**: Replace `gsk_YOUR_ACTUAL_KEY_HERE` with your actual Groq API key!

### Step 13: Create .gitignore

Copy the .gitignore artifact content into `.gitignore`

✅ **Checkpoint**: Your `.env` file has your real Groq API key

## 💾 Phase 5: Create Database Models (5 minutes)

### Step 14: Create database/models.py

Copy the entire `database/models.py` artifact content

### Step 15: Create database/firebase_client.py

Copy the entire `database/firebase_client.py` artifact content

✅ **Checkpoint**: You have 2 files in the `database/` folder

## 🧠 Phase 6: Create Agent Components (10 minutes)

### Step 16: Create agent/prompts.py

Copy the entire `agent/prompts.py` artifact content

### Step 17: Create agent/knowledge_base.py

Copy the entire `agent/knowledge_base.py` artifact content

### Step 18: Create agent/ai_agent.py

Copy the entire `agent/ai_agent.py` artifact content

✅ **Checkpoint**: You have 3 files in the `agent/` folder

## 🛠️ Phase 7: Create Services (5 minutes)

### Step 19: Create services/notification_service.py

Copy the entire `services/notification_service.py` artifact content

### Step 20: Create services/help_request_service.py

Copy the entire `services/help_request_service.py` artifact content

✅ **Checkpoint**: You have 2 files in the `services/` folder

## 🎛️ Phase 8: Create Supervisor Dashboard (10 minutes)

### Step 21: Create supervisor/routes.py

Copy the entire `supervisor/routes.py` artifact content

### Step 22: Create supervisor/app.py

Copy the entire `supervisor/app.py` artifact content

### Step 23: Create supervisor/templates/dashboard.html

Copy the entire `supervisor/templates/dashboard.html` artifact content

✅ **Checkpoint**: You have 2 Python files and 1 HTML file in `supervisor/`

## 🚀 Phase 9: Create Entry Points (5 minutes)

### Step 24: Create main.py

Copy the entire `main.py` artifact content

### Step 25: Create simple_agent.py

Copy the entire `simple_agent.py` artifact content

✅ **Checkpoint**: You have `main.py` and `simple_agent.py` in project root

## 📚 Phase 10: Create Documentation (5 minutes)

### Step 26: Create README.md

Copy the entire `README.md` artifact content

### Step 27: Create QUICKSTART.md

Copy the entire `QUICKSTART.md` artifact content

### Step 28: Create Other Documentation

Optional but recommended:
- Copy `DESIGN_DECISIONS.md` artifact
- Copy `TESTING_CHECKLIST.md` artifact
- Copy `PROJECT_SUMMARY.md` artifact

✅ **Checkpoint**: Your project is fully documented

## ✅ Phase 11: Test the System (5 minutes)

### Step 29: Seed Initial Data

```bash
python main.py seed
```

You should see:
```
🌱 SEEDING INITIAL DATA
✅ Added knowledge: What are your hours?
✅ Added knowledge: How much is a haircut?
✅ Added knowledge: Do you take walk-ins?
✅ Added knowledge: Where are you located?
✅ Added sample help request: <request_id>
✅ DATA SEEDING COMPLETE
```

### Step 30: Run System Tests

```bash
python main.py test
```

You should see all green checkmarks:
```
🧪 RUNNING SYSTEM TESTS
✅ Firebase connection successful
✅ Groq API connection successful
✅ Knowledge base loaded (4 entries)
✅ ALL TESTS PASSED
```

✅ **Checkpoint**: All tests pass!

## 🎮 Phase 12: Run the System (2 minutes)

### Step 31: Start Supervisor Dashboard

Open Terminal 1:
```bash
python main.py supervisor
```

You should see:
```
🎛️  SUPERVISOR DASHBOARD STARTING
   URL: http://localhost:5000/dashboard
```

### Step 32: Start Test Agent

Open Terminal 2:
```bash
python simple_agent.py
```

You should see:
```
🤖 FRONTDESK AI - INTERACTIVE TEST MODE
📞 INCOMING CALL from +1-555-TEST-001
🤖 AI: Hello! Thank you for calling. How can I help you today?
```

### Step 33: Open Dashboard in Browser

Open your browser and go to:
```
http://localhost:5000
```

You should see the Supervisor Dashboard with stats and tabs.

✅ **Checkpoint**: Both services running, dashboard loads

## 🧪 Phase 13: Test End-to-End Flow (5 minutes)

### Step 34: Test Known Question

In Terminal 2 (agent), type:
```
What are your hours?
```

Expected result:
- AI responds with business hours
- No escalation
- Response is appropriate

### Step 35: Test Escalation

In Terminal 2, type:
```
Do you offer wedding packages?
```

Expected result:
- AI says it will check with manager
- Console shows escalation notification
- Tells you to check dashboard

### Step 36: Resolve Request in Dashboard

1. Switch to your browser (dashboard)
2. You should see a new pending request
3. Click to expand it
4. Fill in:
   - Your Name: "Manager"
   - Answer: "Yes, we offer customized wedding packages starting at $500"
5. Click "Submit Answer"

Expected result:
- Success message appears
- Console in Terminal 2 shows SMS notification
- Request disappears from Pending tab

### Step 37: Check Knowledge Base

1. In dashboard, click "Learned Knowledge" tab
2. You should see the new entry about wedding packages

### Step 38: Test AI Learned

In Terminal 2, type:
```
new
```
(This starts a new call)

Then type:
```
Do you offer wedding packages?
```

Expected result:
- AI now answers directly using the learned knowledge!
- No escalation this time

✅ **Checkpoint**: Complete end-to-end flow works!

## 🎥 Phase 14: Record Demo Video (30 minutes)

### Step 39: Prepare Demo Environment

1. Close unnecessary browser tabs
2. Clean up terminal windows
3. Have both terminals + browser visible
4. Test screen recording software

### Step 40: Record Video

Follow this script:

**Part 1: Overview (2 min)**
- Show project structure in file explorer
- Explain the three layers (Database, Services, Interfaces)
- Show the data models briefly

**Part 2: Live Demo (4 min)**
- Show both terminals running
- Ask question AI knows → immediate answer
- Ask question AI doesn't know → escalation
- Switch to dashboard → pending request
- Submit answer → SMS notification
- Switch to Knowledge tab → new entry
- New call with same question → AI answers correctly

**Part 3: Code Walkthrough (2 min)**
- Show `database/models.py` - explain data structure
- Show `services/help_request_service.py` - explain lifecycle
- Show `agent/knowledge_base.py` - explain learning

**Part 4: Design Discussion (2 min)**
- Explain why Firebase (fast, free, scales to 1k/day)
- Explain scaling to 10k/day (PostgreSQL, Redis, queues)
- Show request lifecycle diagram
- Discuss modularity benefits

**Conclusion (1 min)**
- Summary of what was built
- Thank reviewers for their time

### Step 41: Review and Upload

1. Watch the video
2. Check audio quality
3. Verify no sensitive data visible
4. Upload to YouTube (unlisted) or Loom
5. Copy the link

✅ **Checkpoint**: Video is recorded and uploaded

## 📤 Phase 15: Prepare for Submission (10 minutes)

### Step 42: Clean Repository

```bash
# Make sure virtual environment is in .gitignore
echo "venv/" >> .gitignore

# Make sure secrets are not tracked
git status
# Should NOT see .env or firebase_config.json
```

### Step 43: Initialize Git (if not done)

```bash
git init
git add .
git commit -m "Initial commit: Frontdesk AI Supervisor System"
```

### Step 44: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `frontdesk-ai-supervisor`
3. Make it **public** (or provide access)
4. Don't initialize with README (you have one)
5. Click "Create repository"

### Step 45: Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/frontdesk-ai-supervisor.git
git branch -M main
git push -u origin main
```

### Step 46: Verify Repository

1. Go to your GitHub repository URL
2. Check that all files are there
3. **Verify** no secrets (.env, firebase_config.json)
4. Check README.md displays properly

✅ **Checkpoint**: Code is on GitHub, no secrets committed

## 📧 Phase 16: Submit (5 minutes)

### Step 47: Create Submission Email/Form

Include:
- GitHub repository URL
- Video demo link
- Brief summary (optional)

### Step 48: Double-Check Submission

- [ ] GitHub repository is accessible
- [ ] README.md has setup instructions
- [ ] No secrets in repository
- [ ] Video link works
- [ ] Video shows complete flow

### Step 49: Submit!

Send your submission and celebrate! 🎉

## 🎉 You're Done!

### What You Built

✅ Complete AI supervisor system
✅ Database layer with Firebase
✅ AI agent with Groq
✅ Knowledge base with learning
✅ Supervisor dashboard
✅ Full request lifecycle
✅ Comprehensive documentation
✅ Working demo
✅ Clean, professional code

### Total Time

- Setup: ~30 minutes
- Coding: ~8-10 hours
- Testing: ~1-2 hours
- Documentation: ~2 hours
- Video: ~30 minutes
- **Total: 12-15 hours** ✅

## 🆘 Troubleshooting Quick Reference

### "Firebase connection failed"
```bash
# Check file exists
ls firebase_config.json

# Check .env path
cat .env | grep FIREBASE
```

### "Groq API failed"
```bash
# Check API key in .env
cat .env | grep GROQ

# Test key directly
python -c "from groq import Groq; import os; from dotenv import load_dotenv; load_dotenv(); print(Groq(api_key=os.getenv('GROQ_API_KEY')).models.list())"
```

### "Module not found"
```bash
# Activate venv
source venv/bin/activate

# Reinstall
pip install -r requirements.txt
```

### "Port already in use"
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Or use different port
SUPERVISOR_PORT=5001 python main.py supervisor
```

## 📞 Support

If you get stuck:
1. Check error messages carefully
2. Review QUICKSTART.md
3. Check TESTING_CHECKLIST.md
4. Verify all steps above were followed

Good luck! 🚀