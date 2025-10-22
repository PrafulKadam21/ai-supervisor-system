# Quick Start Guide - 10 Minutes to Running System

Get from zero to a fully working AI supervisor system in about 10 minutes.

## ⚡ Super Quick Setup (5 minutes)

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Firebase (2 minutes)

1. Go to https://console.firebase.google.com/
2. Click "Add project" → Name it "frontdesk-ai-test"
3. Disable Google Analytics (not needed)
4. Click "Create Firestore Database" → Start in test mode → Choose location
5. Go to Project Settings (⚙️) → Service Accounts
6. Click "Generate new private key"
7. Save as `firebase_config.json` in your project folder

### 3. Get Groq API Key (1 minute)

1. Go to https://console.groq.com/
2. Sign up (free)
3. Click "API Keys" → "Create API Key"
4. Copy the key

### 4. Create .env File (1 minute)

Create `.env` file in project root:

```bash
# Required
GROQ_API_KEY=gsk_your_actual_key_here
FIREBASE_CREDENTIALS_PATH=./firebase_config.json

# Optional (defaults work fine)
FLASK_SECRET_KEY=test-secret-key
SUPERVISOR_PORT=5000
BUSINESS_NAME=Luxe Hair Salon
BUSINESS_HOURS=Mon-Sat 9AM-7PM

# LiveKit (optional - only needed for voice calls)
LIVEKIT_URL=wss://placeholder.livekit.cloud
LIVEKIT_API_KEY=placeholder
LIVEKIT_API_SECRET=placeholder
```

### 5. Seed Data and Test (1 minute)

```bash
# Add initial knowledge
python main.py seed

# Test connections
python main.py test
```

You should see all green checkmarks! ✅

## 🎮 Running the System

### Method 1: Text-Based Agent (Recommended)

**Terminal 1** - Start Supervisor Dashboard:
```bash
python main.py supervisor
```
Visit: http://localhost:5000

**Terminal 2** - Start Test Agent:
```bash
python simple_agent.py
```

This gives you an interactive chat to test with! Try:
- "What are your hours?" (AI will answer)
- "Do you offer wedding packages?" (AI will escalate)
- "new" to start new call
- "quit" to exit

**Terminal 3** - Or Run Automated Tests:
```bash
python simple_agent.py test
```

### Option B: Full LiveKit Integration (Advanced)

Only do this if you want real voice calls:

1. Get LiveKit credentials from https://cloud.livekit.io/
2. Update `.env` with real credentials
3. Run: `python main.py agent`

## 📝 Testing the Full Flow

### Test Scenario 1: AI Answers Question

1. **Start both services** (supervisor + simple_agent)
2. **In simple_agent terminal**, type: "What are your hours?"
3. **AI responds** with business hours immediately
4. ✅ Success - no escalation needed

### Test Scenario 2: AI Escalates to Supervisor

1. **In simple_agent terminal**, type: "Do you offer senior discounts?"
2. **AI escalates** - you'll see notification in console
3. **Open dashboard** at http://localhost:5000
4. **View pending request** in "Pending Requests" tab
5. **Click to expand** the request
6. **Fill in**:
   - Your Name: "Manager"
   - Answer: "Yes, we offer 15% senior discount for ages 65+"
7. **Click "Submit Answer"**
8. **Check console** - you'll see simulated SMS to caller
9. **Check "Learned Knowledge" tab** - new entry added!
10. ✅ Success - complete flow

### Test Scenario 3: AI Uses Learned Knowledge

1. **In simple_agent terminal**, type "new" for new call
2. **Type**: "Do you offer senior discounts?"
3. **AI now answers** using the learned knowledge!
4. ✅ Success - AI learned and improved

## 🎯 What to Demo in Your Video

### Part 1: System Overview (2 min)
- Show project structure
- Explain architecture (Database → Services → Agent/Dashboard)
- Show the three-state lifecycle diagram

### Part 2: Live Demo (3 min)
Screen record:
1. Both terminals running
2. Ask question AI knows → immediate answer
3. Ask question AI doesn't know → escalation
4. Switch to dashboard → pending request appears
5. Submit answer → SMS notification
6. Switch to Knowledge tab → new entry
7. New call with same question → AI answers correctly

### Part 3: Code Walkthrough (3 min)
Show and explain:
- `database/models.py` - clean data models
- `services/help_request_service.py` - lifecycle management
- `agent/knowledge_base.py` - learning mechanism
- `supervisor/routes.py` - API design

### Part 4: Design Decisions (2 min)
Discuss:
- Why Firebase (fast to start, scales to 1000/day)
- How to scale to 10k/day (PostgreSQL, Redis, queues)
- Request lifecycle design
- Knowledge base search strategy
- Modular architecture benefits

## 🐛 Troubleshooting

### "Firebase connection failed"
- Check `firebase_config.json` exists
- Check Firebase credentials path in `.env`
- Verify Firestore is enabled in Firebase console

### "Groq API connection failed"
- Check API key in `.env`
- Verify key is active in Groq console
- Check you have API credits (free tier available)

### "Module not found"
- Run `pip install -r requirements.txt`
- Make sure you're in project directory
- Check Python version (3.9+)

### Dashboard won't load
- Check port 5000 isn't in use
- Try different port: `SUPERVISOR_PORT=5001 python main.py supervisor`
- Check Flask is installed

### Agent not escalating
- Check Groq API is working (`python main.py test`)
- Verify knowledge base has initial data (`python main.py seed`)
- Try asking more specific/unusual questions

## 📊 Checking Your Data

### View Firebase Data
1. Go to Firebase Console
2. Click "Firestore Database"
3. You should see collections:
   - `help_requests`
   - `knowledge_base`
   - `call_logs`

### Check Stats
Visit dashboard: http://localhost:5001
- Pending Requests count
- Resolved count
- Learned Answers count
- Average response time

## 🚀 Next Steps

Once basic system works:

1. **Customize business info** in `.env`
2. **Add more initial knowledge** in `main.py` seed function
3. **Test edge cases** - what breaks the system?
4. **Set up LiveKit** for real voice calls
5. **Add authentication** to supervisor dashboard
6. **Deploy to cloud** (Heroku, AWS, GCP)

## 💡 Pro Tips

### Faster Testing
Create alias in terminal:
```bash
alias fdsup="python main.py supervisor"
alias fdagent="python simple_agent.py"
alias fdtest="python simple_agent.py test"
```

### Reset Database
If you want to start fresh:
1. Go to Firebase Console
2. Delete all collections
3. Run `python main.py seed` again

### Quick Knowledge Addition
Directly add to Firebase console for testing:
1. Go to `knowledge_base` collection
2. Click "Add Document"
3. Fill in question/answer fields

### Monitor in Real-Time
Keep dashboard open while testing - it auto-refreshes every 5 seconds!

## 📹 Recording Your Demo

### Recommended Setup
1. Screen size: 1920x1080
2. Use OBS Studio or QuickTime (free)
3. Show terminal + browser side by side
4. Speak clearly, explain as you demo
5. 8-10 minutes total is perfect

### Demo Script Template
```
"Hi, I'm showing the Frontdesk AI Supervisor system.

[Show architecture]
The system has three main parts: database, services, and interfaces.

[Show code structure]
I organized it for modularity and scalability.

[Start demo]
Let me show it working...
[Run through scenarios]

[Explain decisions]
I chose Firebase because... 
For scaling to 10k/day I would...

[Discuss improvements]
Next I would add...

Thanks for watching!"
```

## ✅ Pre-Submission Checklist

- [ ] All tests pass (`python main.py test`)
- [ ] Supervisor dashboard loads
- [ ] Can create help request
- [ ] Can resolve help request
- [ ] Knowledge base updates
- [ ] Console shows notifications
- [ ] README.md is complete
- [ ] Code is commented
- [ ] `.env.template` exists
- [ ] Video is recorded
- [ ] GitHub repo is clean (no secrets!)

## 🎉 You're Ready!

If you got through this guide, you have:
- ✅ Working database layer
- ✅ Functional AI agent
- ✅ Supervisor dashboard
- ✅ Complete request lifecycle
- ✅ Learning knowledge base
- ✅ Clean, modular code

Now record your demo and submit! Good luck! 🚀