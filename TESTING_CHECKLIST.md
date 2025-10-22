# Testing Checklist

Use this checklist before submitting your project to ensure everything works.

## ✅ Pre-Testing Setup

- [ ] Virtual environment activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with real API keys
- [ ] `firebase_config.json` in project root
- [ ] Firebase Firestore database created and in test mode
- [ ] Initial data seeded (`python main.py seed`)

## ✅ System Tests

### Connection Tests

Run: `python main.py test`

- [ ] Firebase connection successful
- [ ] Groq API connection successful
- [ ] Knowledge base loads successfully
- [ ] All tests pass with green checkmarks

### Database Tests

- [ ] Can create help request
- [ ] Can retrieve help requests
- [ ] Can update help request status
- [ ] Can add knowledge entries
- [ ] Can search knowledge base
- [ ] Can create call logs

Check Firebase Console:
- [ ] `help_requests` collection exists
- [ ] `knowledge_base` collection exists
- [ ] `call_logs` collection exists
- [ ] Seeded data is visible

## ✅ Supervisor Dashboard Tests

Start: `python main.py supervisor`

### UI Loading
- [ ] Dashboard loads at http://localhost:5000
- [ ] No console errors in browser
- [ ] All tabs are visible (Pending, History, Knowledge)
- [ ] Stats cards show initial values

### Pending Requests Tab
- [ ] Shows "All caught up" when no requests
- [ ] Can switch between tabs
- [ ] Auto-refreshes (wait 5 seconds)

### Request History Tab
- [ ] Shows seeded request
- [ ] Displays request details correctly
- [ ] Shows correct status badge
- [ ] Sorted by date (newest first)

### Learned Knowledge Tab
- [ ] Shows seeded knowledge
- [ ] Displays Q&A format
- [ ] Shows usage count
- [ ] Shows creation date

### API Endpoints

Test with curl or browser:

```bash
# Get stats
curl http://localhost:5000/api/stats

# Get pending requests
curl http://localhost:5000/api/requests/pending

# Get all requests
curl http://localhost:5000/api/requests/all

# Get knowledge
curl http://localhost:5000/api/knowledge
```

- [ ] All endpoints return valid JSON
- [ ] No 500 errors
- [ ] Data structure matches expectations

## ✅ AI Agent Tests (Simple Agent)

Start: `python simple_agent.py`

### Interactive Mode Tests

#### Test 1: Known Question
- [ ] Type: "What are your hours?"
- [ ] AI responds with business hours
- [ ] No escalation happens
- [ ] Response is appropriate

#### Test 2: Known Question (Different)
- [ ] Type: "How much is a haircut?"
- [ ] AI responds with pricing
- [ ] No escalation happens

#### Test 3: Unknown Question (Escalation)
- [ ] Type: "Do you offer wedding packages?"
- [ ] AI says it will check with manager
- [ ] Console shows escalation notification
- [ ] Help request created (check dashboard)

#### Test 4: Multiple Questions
- [ ] Start new call (type "new")
- [ ] Ask 2-3 questions in a row
- [ ] AI maintains context
- [ ] Appropriate responses

#### Test 5: Conversation Flow
- [ ] AI greeting is friendly
- [ ] Responses are professional
- [ ] No hallucinations
- [ ] Stays in character

### Automated Tests

Run: `python simple_agent.py test`

- [ ] Scenario 1 completes (known question)
- [ ] Scenario 2 completes (escalation)
- [ ] Scenario 3 completes (multiple questions)
- [ ] No errors in console
- [ ] Help requests created for escalations

## ✅ End-to-End Flow Test

This is the most important test - the complete user journey.

### Setup
1. Terminal 1: `python main.py supervisor`
2. Terminal 2: `python simple_agent.py`
3. Browser: http://localhost:5000

### Flow Steps

#### Step 1: Agent Escalates
- [ ] In agent terminal, type: "Do you have gift certificates?"
- [ ] AI escalates (says will check with manager)
- [ ] Console shows escalation notification
- [ ] Request ID is printed

#### Step 2: Supervisor Sees Request
- [ ] Refresh dashboard (or wait for auto-refresh)
- [ ] New request appears in "Pending Requests" tab
- [ ] Pending count increases in stats
- [ ] Request shows correct question
- [ ] Caller phone number is displayed

#### Step 3: Supervisor Responds
- [ ] Click to expand request
- [ ] Fill in your name: "Manager"
- [ ] Fill in answer: "Yes, we offer gift certificates starting at $25"
- [ ] Click "Submit Answer"
- [ ] Success message appears

#### Step 4: System Updates
- [ ] Console shows SMS notification to caller
- [ ] Request moves from pending to resolved
- [ ] Pending count decreases
- [ ] Resolved count increases

#### Step 5: Knowledge Base Updates
- [ ] Go to "Learned Knowledge" tab
- [ ] New entry appears for gift certificates
- [ ] Entry shows usage count of 0
- [ ] Source is "supervisor"

#### Step 6: AI Uses New Knowledge
- [ ] In agent terminal, type "new" (new call)
- [ ] Type: "Do you have gift certificates?"
- [ ] AI now answers directly with learned information
- [ ] No escalation this time
- [ ] Response includes "$25" detail

#### Step 7: Knowledge Usage Tracked
- [ ] Refresh "Learned Knowledge" tab
- [ ] Usage count for gift certificates is now 1
- [ ] Knowledge entry shows update time

**Complete E2E Test:** ✅ / ❌

## ✅ Edge Cases & Error Handling

### Empty States
- [ ] Dashboard shows nice message when no pending requests
- [ ] Dashboard shows nice message when no history
- [ ] Dashboard shows nice message when no knowledge

### Invalid Input
- [ ] Try submitting empty answer - should show error
- [ ] Try submitting answer with only spaces - should show error
- [ ] Invalid request ID - should handle gracefully

### Network Issues
- [ ] Stop Firebase (disconnect internet briefly)
- [ ] System shows appropriate error messages
- [ ] Doesn't crash or hang

### Concurrent Requests
- [ ] Create multiple escalations quickly
- [ ] All appear in dashboard
- [ ] Can resolve each independently
- [ ] No race conditions

## ✅ Performance Tests

### Response Time
- [ ] Agent responds in < 3 seconds for known questions
- [ ] Agent escalates in < 5 seconds
- [ ] Dashboard loads in < 2 seconds
- [ ] API calls return in < 1 second

### Load
- [ ] Can handle 10 rapid questions
- [ ] No memory leaks after 20+ interactions
- [ ] Dashboard stays responsive with 10+ requests

## ✅ Code Quality Checks

### Code Organization
- [ ] All files in correct directories
- [ ] `__init__.py` in each module
- [ ] No circular imports
- [ ] Clear separation of concerns

### Documentation
- [ ] README.md is complete
- [ ] Code has comments explaining complex logic
- [ ] Function docstrings present
- [ ] Design decisions documented

### Best Practices
- [ ] No hardcoded credentials
- [ ] Environment variables used correctly
- [ ] Error handling in place
- [ ] Logging is informative

### Clean Repository
- [ ] No `firebase_config.json` in git
- [ ] No `.env` in git
- [ ] `.gitignore` configured correctly
- [ ] No `__pycache__` or `.pyc` files committed

## ✅ Video Demo Preparation

### Content Checklist
- [ ] Show project structure
- [ ] Explain architecture diagram
- [ ] Demo agent answering known question
- [ ] Demo agent escalating unknown question
- [ ] Show supervisor dashboard
- [ ] Resolve a help request
- [ ] Show knowledge base update
- [ ] Demo AI using learned knowledge
- [ ] Explain key design decisions
- [ ] Discuss scaling strategy

### Technical Checklist
- [ ] Screen recording software ready
- [ ] Audio quality tested
- [ ] 1920x1080 resolution
- [ ] 8-12 minutes duration
- [ ] Clear speaking pace
- [ ] No sensitive data visible
- [ ] Video file size < 100MB

## ✅ Submission Checklist

### GitHub Repository
- [ ] README.md complete with setup instructions
- [ ] QUICKSTART.md included
- [ ] requirements.txt present
- [ ] .env.template created (no real keys)
- [ ] .gitignore configured
- [ ] Code is clean and commented
- [ ] No secrets committed
- [ ] Repository is public (or accessible)

### Video
- [ ] Recorded and reviewed
- [ ] Good audio quality
- [ ] Clear visuals
- [ ] Uploaded (YouTube/Loom/Drive)
- [ ] Link is accessible

### Final Checks
- [ ] Run `python main.py test` - all pass
- [ ] Run automated tests - all pass
- [ ] Run E2E flow - works perfectly
- [ ] Dashboard accessible from http://localhost:5000
- [ ] No console errors
- [ ] Everything documented

## 🎉 Ready to Submit!

If all checkboxes are checked, you're ready to submit. Great work!

## 📝 If Something Fails

### Debugging Steps

1. **Check logs**: Look at console output carefully
2. **Check Firebase**: Verify data in Firebase Console
3. **Check API keys**: Ensure they're correct in `.env`
4. **Check dependencies**: Run `pip list` to verify installations
5. **Check Python version**: Must be 3.9+
6. **Restart**: Stop all services and start fresh
7. **Reseed**: Run `python main.py seed` again

### Common Issues

**"Firebase connection failed"**
- Check firebase_config.json path
- Verify Firestore is enabled
- Check Firebase console for errors

**"Groq API failed"**
- Verify API key is correct
- Check you have credits
- Try different model name

**"Module not found"**
- Activate virtual environment
- Reinstall requirements
- Check Python path

**"Port already in use"**
- Change SUPERVISOR_PORT in .env
- Kill process using port 5000
- Use different port

### Getting Help

If stuck:
1. Review error messages carefully
2. Check QUICKSTART.md
3. Review relevant code files
4. Test components individually
5. Check Firebase/Groq console logs