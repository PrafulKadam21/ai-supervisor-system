# Frontdesk AI Supervisor System

A human-in-the-loop AI system that allows AI receptionists to escalate unknown questions to human supervisors, learn from their responses, and automatically follow up with customers.

## 🎯 Overview

This system enables an AI agent to:
- Handle incoming calls/conversations with customers
- Automatically detect when it doesn't know an answer
- Escalate questions to human supervisors
- Learn from supervisor responses and update its knowledge base
- Follow up with customers automatically when answers are received

## 🏗️ Architecture

### Tech Stack
- **AI/LLM**: Groq (Llama 3.3 70B)
- **Voice Infrastructure**: LiveKit (optional, text agent included for easy testing)
- **Database**: Firebase Firestore
- **Backend**: Python, Flask
- **Frontend**: Vanilla HTML/CSS/JavaScript

### System Components

1. **AI Agent** (`agent/`)
   - Text-based agent for easy testing (`simple_agent.py`)
   - LiveKit voice agent for production calls (`agent_standalone.py`)
   - Uses Groq Llama for conversation and reasoning
   - Maintains knowledge base and checks confidence
   - Escalates when uncertain

2. **Database Layer** (`database/`)
   - Firebase Firestore for persistence
   - Models: HelpRequest, KnowledgeEntry, CallLog
   - Clean abstractions for CRUD operations

3. **Supervisor Dashboard** (`supervisor/`)
   - Flask web application
   - Real-time view of pending requests
   - Simple UI for answering questions
   - Knowledge base viewer

4. **Services** (`services/`)
   - HelpRequestService: Request lifecycle management
   - NotificationService: Simulated SMS/notifications

## 📋 Prerequisites

- Python 3.9+
- Firebase account with Firestore enabled
- Groq API account (free tier available)
- LiveKit account (optional, for voice calls)

## 🚀 Quick Start (5 Minutes)

### 1. Clone and Install

```bash
git clone https://github.com/PrafulKadam21/ai-supervisor-system.git
cd frontdesk-ai-supervisor
pip install -r requirements.txt
```

### 2. Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project
3. Enable Firestore Database (test mode)
4. Download service account key as `firebase_config.json`

### 3. Groq API Setup

1. Go to [Groq Console](https://console.groq.com/)
2. Sign up (free!)
3. Generate API key

### 4. Configure Environment

Create `.env` file:

```bash
# Required
GROQ_API_KEY=gsk_your_actual_key_here
FIREBASE_CREDENTIALS_PATH=./firebase_config.json

# Optional (for LiveKit voice - not required for demo)
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# Flask Configuration
FLASK_SECRET_KEY=your-random-secret-key
SUPERVISOR_PORT=5000

# Business Information
BUSINESS_NAME=Luxe Hair Salon
BUSINESS_HOURS=Mon-Sat 9AM-7PM
BUSINESS_PHONE=+1-555-123-4567
```

### 5. Initialize and Test

```bash
# Seed initial knowledge
python main.py seed

# Verify setup
python main.py test
```

## 🎮 Running the System

### Recommended: Text-Based Agent (Easy Testing)

**Terminal 1** - Start Supervisor Dashboard:
```bash
python main.py supervisor
```
Visit: `http://localhost:5000`

**Terminal 2** - Start Text Agent:
```bash
python simple_agent.py
```

This gives you full functionality without voice setup!

### Optional: LiveKit Voice Agent

If you want voice calls:

1. Set up LiveKit credentials in `.env`
2. Run: `python main.py agent`
3. Connect through LiveKit playground

**Note**: Text agent demonstrates identical functionality and is recommended for testing and demos.

## 📊 How It Works

### Request Lifecycle

```
1. Customer asks question
   ↓
2. AI checks knowledge base
   ↓
3a. If confident → Answer immediately
3b. If uncertain → Escalate
   ↓
4. Create HelpRequest (status: PENDING)
   ↓
5. Notify supervisor (console + dashboard)
   ↓
6. Tell customer: "Let me check and get back to you"
   ↓
7. Supervisor views in dashboard
   ↓
8. Supervisor submits answer
   ↓
9. Update HelpRequest (status: RESOLVED)
   ↓
10. Add to knowledge base
   ↓
11. Send follow-up to customer (simulated SMS)
   ↓
12. AI uses new knowledge for future calls
```

## 🧪 Testing the System

### Interactive Testing

1. Start both services (supervisor + simple_agent)
2. In simple_agent terminal, try:
   - "What are your hours?" → AI answers directly
   - "Do you offer wedding packages?" → AI escalates
3. Open dashboard at http://localhost:5000
4. View pending request and submit answer
5. Start new call (type "new")
6. Ask same question → AI now knows the answer!

### Automated Testing

```bash
python simple_agent.py test
```

This runs 3 test scenarios automatically.

## 📁 Project Structure

```
frontdesk-ai-supervisor/
├── agent/
│   ├── ai_agent.py              # LiveKit voice agent (optional)
│   ├── knowledge_base.py        # Learning system
│   └── prompts.py               # System prompts
├── database/
│   ├── firebase_client.py       # Database operations
│   └── models.py                # Pydantic data models
├── services/
│   ├── help_request_service.py  # Request lifecycle
│   └── notification_service.py  # Notifications
├── supervisor/
│   ├── app.py                   # Flask application
│   ├── routes.py                # API endpoints
│   └── templates/
│       └── dashboard.html       # Supervisor UI
├── main.py                      # Entry point
├── simple_agent.py              # Text-based agent (recommended for testing)
├── agent_standalone.py          # LiveKit voice agent (optional)
├── groq_llm_adapter.py          # Custom Groq adapter for LiveKit
├── requirements.txt
├── .env.template
└── README.md
```

## 🎨 Key Design Decisions

### 1. Two Agent Options

**Text Agent** (`simple_agent.py`):
- ✅ Works immediately
- ✅ Easy to test and demo
- ✅ No external dependencies
- ✅ Perfect for development
- **Recommended for demos and testing**

**Voice Agent** (`agent_standalone.py`):
- Uses LiveKit for real voice calls
- Groq LLM integration
- Production-ready voice interface
- Optional for advanced use

### 2. Database: Firebase Firestore

**Why:**
- Free tier handles 1,000+ requests/day
- Zero ops, no server management
- Real-time updates
- Fast setup (5 minutes)

**Scaling Path:**
- 0-1k/day: Firestore (current)
- 1k-10k/day: Firestore + Redis cache
- 10k+/day: PostgreSQL + Redis + Queue system

### 3. Request Lifecycle

Three-state lifecycle: `PENDING → RESOLVED / TIMEOUT`

**Why:**
- Simple but complete
- Clear state transitions
- Easy to extend (can add more states)
- Handles timeout gracefully

### 4. Knowledge Base

Simple Q&A pairs with usage tracking

**Why:**
- Fast, works for <100 entries
- Human-readable
- No dependencies
- Tracks what's valuable

**When to upgrade:**
- At 100+ entries: Add vector embeddings
- At 1000+ entries: Use semantic search

### 5. Escalation Logic

AI self-assesses confidence before answering

**Why:**
- Prevents hallucinations
- Better than keyword matching
- Learns what it doesn't know
- Transparent decision making

## 📊 Data Models

### HelpRequest
```python
{
  id: string,
  caller_id: string,
  caller_phone: string,
  question: string,
  context: string (optional),
  status: "pending" | "resolved" | "timeout",
  created_at: timestamp,
  resolved_at: timestamp (optional),
  supervisor_answer: string (optional),
  supervisor_name: string (optional)
}
```

### KnowledgeEntry
```python
{
  id: string,
  question: string,
  answer: string,
  source: "supervisor" | "initial_seed",
  help_request_id: string (optional),
  created_at: timestamp,
  updated_at: timestamp,
  usage_count: number
}
```

### CallLog
```python
{
  id: string,
  caller_id: string,
  caller_phone: string,
  started_at: timestamp,
  ended_at: timestamp (optional),
  transcript: string (optional),
  help_requests: [string],
  resolved_by_ai: boolean
}
```

## 🔧 Configuration

### Business Information

Update in `.env`:
```bash
BUSINESS_NAME=Your Business Name
BUSINESS_HOURS=Your Hours
BUSINESS_PHONE=Your Phone
```

Or modify `agent/prompts.py` directly.

### Timeout Settings

In `services/help_request_service.py`:
```python
def timeout_old_requests(self, hours: int = 24):
    # Adjust timeout period here
```

### Knowledge Base Search

In `agent/knowledge_base.py`:
```python
def _is_similar(self, q1: str, q2: str, threshold: float = 0.6):
    # Adjust similarity threshold
```

## 📈 Scaling Considerations

### Current Capacity: ~1,000 requests/day

**Bottlenecks:**
- Single Flask instance
- Firebase free tier
- No caching layer

### Scaling to 10,000/day

**Required changes:**

1. **Caching**: Add Redis for knowledge base
2. **Multiple instances**: Load balance Flask
3. **Queue**: RabbitMQ for async processing
4. **Monitoring**: DataDog/NewRelic

### Scaling to 100,000/day

**Additional requirements:**

1. **Database**: Migrate to PostgreSQL with replicas
2. **Microservices**: Split into separate services
3. **Event-driven**: Use Kafka/SQS
4. **CDN**: CloudFront for dashboard
5. **Vector DB**: Pinecone for knowledge base

## 🧪 Available Commands

```bash
# Setup
python main.py seed          # Add initial knowledge
python main.py test          # Verify connections
python verify_setup.py       # Check full setup

# Running
python main.py supervisor    # Start dashboard
python simple_agent.py       # Start text agent
python main.py agent         # Start voice agent (optional)

# Testing
python simple_agent.py test  # Run automated tests
```

## 🚧 Known Limitations

1. **Voice Integration**: LiveKit requires additional API setup
2. **Notifications**: Console-only (no real SMS/Slack yet)
3. **Knowledge Search**: Simple text matching (no semantic search)
4. **Authentication**: No auth on supervisor dashboard
5. **Single-tenant**: Supports one business only

## 🔮 Future Improvements

### Phase 2 Features
- Live call transfer to supervisor
- Supervisor availability detection
- Hold music during transfer
- Call recording and transcription

### Production Features
- OAuth authentication
- Multi-tenant support
- Advanced analytics
- A/B testing framework
- CRM integrations
- Voice cloning for consistency

## 🎥 Demo Video Tips

**Show:**
1. Project structure overview
2. Start both services
3. AI answering known question
4. AI escalating unknown question
5. Supervisor dashboard interaction
6. Resolve request flow
7. Knowledge base update
8. AI using learned knowledge

**Explain:**
- Why Firebase (fast setup, scales well)
- Request lifecycle design
- Scaling strategy (1k → 10k → 100k/day)
- Text vs voice agent approach

## 💡 Why Two Agent Options?

**Text Agent** (`simple_agent.py`):
- Demonstrates all core functionality
- Zero external dependencies (beyond Groq)
- Perfect for development and testing
- Easy to understand and debug
- Recommended for initial setup and demos

**Voice Agent** (`agent_standalone.py` + `groq_llm_adapter.py`):
- Production voice interface
- LiveKit integration
- Real-time audio processing
- Optional advanced feature
- Can be added after core system works

Both agents use the **same services layer**, so the business logic is identical!

## 🆘 Troubleshooting

### "Firebase connection failed"
- Check `firebase_config.json` exists
- Verify path in `.env`
- Ensure Firestore is enabled

### "Groq API failed"
- Check API key in `.env`
- Verify key is active in Groq console
- Check for API credits

### "Module not found"
- Run `pip install -r requirements.txt`
- Activate virtual environment
- Check Python version (3.9+)

### Dashboard won't load
- Check port 5000 isn't in use
- Try: `SUPERVISOR_PORT=5001 python main.py supervisor`

### Agent not escalating
- Check Groq API is working
- Verify knowledge base has data
- Try asking more unusual questions

## 📝 Documentation

- **README.md** (this file) - Complete overview
- **QUICKSTART.md** - 15-minute setup guide
- **DESIGN_DECISIONS.md** - Architecture explanations
- **TESTING_CHECKLIST.md** - Comprehensive testing guide
- **STEP_BY_STEP_EXECUTION.md** - Detailed build guide

## 📄 License

MIT License

## 🤝 Support

For setup help:
1. Check QUICKSTART.md
2. Run `python verify_setup.py`
3. Review error messages carefully
4. Check Firebase/Groq console logs

---

**Built for Frontdesk Engineering Assessment**

**Quick Start**: `python main.py seed` → `python main.py supervisor` → `python simple_agent.py`

### System Components

1. **AI Agent** (`agent/`)
   - Handles voice calls via LiveKit
   - Uses Groq Llama for conversation and reasoning
   - Maintains knowledge base and checks confidence
   - Escalates when uncertain

2. **Database Layer** (`database/`)
   - Firebase Firestore for persistence
   - Models: HelpRequest, KnowledgeEntry, CallLog
   - Clean abstractions for CRUD operations

3. **Supervisor Dashboard** (`supervisor/`)
   - Flask web application
   - Real-time view of pending requests
   - Simple UI for answering questions
   - Knowledge base viewer

4. **Services** (`services/`)
   - HelpRequestService: Request lifecycle management
   - NotificationService: Simulated SMS/notifications

## 📋 Prerequisites

- Python 3.9+
- Firebase account with Firestore enabled
- Groq API account (free tier available)
- LiveKit account (free tier available)

## 🚀 Setup Instructions

### 1. Clone and Install Dependencies

```bash
git clone <your-repo-url>
cd frontdesk-ai-supervisor
pip install -r requirements.txt
```

### 2. Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project
3. Enable Firestore Database
4. Go to Project Settings → Service Accounts
5. Click "Generate New Private Key"
6. Save the JSON file as `firebase_config.json` in the project root

### 3. Groq API Setup

1. Go to [Groq Console](https://console.groq.com/)
2. Sign up for free account
3. Generate API key
4. Copy the API key for `.env` file

### 4. LiveKit Setup

1. Go to [LiveKit Cloud](https://cloud.livekit.io/)
2. Sign up for free account
3. Create a new project
4. Copy the WebSocket URL, API Key, and API Secret

### 5. Environment Configuration

Create a `.env` file in the project root:

```bash
# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

# Groq Configuration
GROQ_API_KEY=gsk_your_groq_api_key

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=./firebase_config.json

# Flask Configuration
FLASK_SECRET_KEY=your-random-secret-key-here
SUPERVISOR_PORT=5000

# Business Information (customize as needed)
BUSINESS_NAME=Luxe Hair Salon
BUSINESS_HOURS=Mon-Sat 9AM-7PM
BUSINESS_PHONE=+1-555-123-4567
```

### 6. Initialize Data

Seed the database with initial knowledge:

```bash
python main.py seed
```

### 7. Run Tests

Verify all connections are working:

```bash
python main.py test
```

## 🎮 Running the System

### Start Supervisor Dashboard

In terminal 1:
```bash
python main.py supervisor
```

Visit: `http://localhost:5000/dashboard`

### Start AI Agent

In terminal 2:
```bash
python main.py agent
```

## 📊 How It Works

### Request Lifecycle

```
1. Caller asks question
   ↓
2. AI checks knowledge base
   ↓
3a. If confident → Answer immediately
3b. If uncertain → Escalate
   ↓
4. Create HelpRequest (status: PENDING)
   ↓
5. Notify supervisor (console + dashboard)
   ↓
6. Tell caller: "Let me check and text you back"
   ↓
7. Supervisor views in dashboard
   ↓
8. Supervisor submits answer
   ↓
9. Update HelpRequest (status: RESOLVED)
   ↓
10. Add to knowledge base
   ↓
11. Send follow-up to caller (simulated SMS)
   ↓
12. AI uses new knowledge for future calls
```

### Database Schema

**help_requests**
```javascript
{
  id: string,
  caller_id: string,
  caller_phone: string,
  question: string,
  context: string?,
  status: "pending" | "resolved" | "timeout",
  created_at: timestamp,
  resolved_at: timestamp?,
  supervisor_answer: string?,
  supervisor_name: string?
}
```

**knowledge_base**
```javascript
{
  id: string,
  question: string,
  answer: string,
  source: "supervisor" | "initial_seed",
  help_request_id: string?,
  created_at: timestamp,
  updated_at: timestamp,
  usage_count: number
}
```

**call_logs**
```javascript
{
  id: string,
  caller_id: string,
  caller_phone: string,
  started_at: timestamp,
  ended_at: timestamp?,
  transcript: string?,
  help_requests: [string],
  resolved_by_ai: boolean
}
```

## 🎨 Design Decisions

### 1. Request Lifecycle Management
- **Choice**: Three-state lifecycle (pending → resolved/timeout)
- **Rationale**: Simple but extensible. Timeout state allows graceful handling of abandoned requests
- **Scaling**: Add SLA tracking, priority levels, routing to specific supervisors

### 2. Knowledge Base Structure
- **Choice**: Simple Q&A pairs with usage tracking
- **Rationale**: Fast to implement, easy to search, tracks what's useful
- **Scaling**: Implement vector embeddings for semantic search, add categories, version control

### 3. Notification Strategy
- **Choice**: Console logging (simulated notifications)
- **Rationale**: Makes testing easy, no external dependencies
- **Production**: Integrate Twilio for SMS, Slack for supervisor alerts, webhooks for flexibility

### 4. Escalation Logic
- **Choice**: Groq LLM confidence check before answering
- **Rationale**: Prevents hallucinations by having AI self-assess
- **Improvements**: Add confidence thresholds, context-aware escalation, learn from false escalations

### 5. Database Choice (Firebase)
- **Choice**: Firestore with Pydantic models
- **Rationale**: Free tier, real-time updates, easy to start
- **Scaling**: 
  - 10/day: Current setup is fine
  - 1,000/day: Add caching layer (Redis), optimize queries
  - 10,000/day: Move to PostgreSQL + Redis, implement queue system

### 6. Modular Architecture
```
Database Layer ← Services ← Agent/Dashboard
```
- Clean separation of concerns
- Easy to test individual components
- Can swap Firebase for PostgreSQL with minimal changes

## 🔧 Configuration

### Business Information
Update in `.env` or modify `agent/prompts.py`:
- Business hours
- Services offered
- Pricing
- Location details

### Timeout Settings
In `services/help_request_service.py`:
```python
def timeout_old_requests(self, hours: int = 24):
    # Adjust timeout period here
```

### Knowledge Base Search
In `agent/knowledge_base.py`:
```python
def _is_similar(self, q1: str, q2: str, threshold: float = 0.6):
    # Adjust similarity threshold
```

## 📈 Scaling Considerations

### From 10/day to 1,000/day

**Current system handles this well with:**
- Firebase free tier (50k reads, 20k writes/day)
- Connection pooling
- Simple caching in KnowledgeBase

**Optimizations:**
- Add Redis for knowledge base caching
- Batch notification sending
- Database query optimization

### From 1,000/day to 10,000/day

**Requires:**
1. **Database**: Move to PostgreSQL with read replicas
2. **Queue**: Add message queue (RabbitMQ/SQS) for request processing
3. **Caching**: Redis cluster for knowledge base and session data
4. **Load Balancing**: Multiple supervisor dashboard instances
5. **Monitoring**: Add DataDog/NewRelic for observability
6. **Rate Limiting**: Implement rate limits per caller

## 🧪 Testing

### Manual Testing

1. **Start both services** (supervisor + agent)
2. **Simulate a call** via LiveKit dashboard
3. **Ask a question** the AI doesn't know
4. **Check console** for escalation notification
5. **Open dashboard**, verify request appears
6. **Submit answer** through UI
7. **Verify** knowledge base updates
8. **Check console** for simulated SMS to caller

### Automated Testing (Future)

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# End-to-end tests
pytest tests/e2e/
```

## 🚧 Known Limitations

1. **Voice Integration**: LiveKit integration is basic - needs proper STT/TTS setup
2. **Notifications**: Console-only (no real SMS/Slack)
3. **Knowledge Search**: Simple text matching (no semantic search)
4. **Authentication**: No auth on supervisor dashboard
5. **Multi-tenancy**: Single business only
6. **Analytics**: Basic stats only

## 🔮 Future Improvements

### Phase 2 Features
- **Live Call Transfer**: Transfer to supervisor during active call
- **Call Recording**: Store and transcribe full calls
- **Supervisor Availability**: Check if supervisor is online before escalating
- **Hold Music**: Put caller on hold during transfer

### Production Features
- **Authentication**: OAuth for supervisor dashboard
- **Multi-tenant**: Support multiple businesses
- **Analytics Dashboard**: Advanced metrics and insights
- **A/B Testing**: Test different prompts and strategies
- **Voice Cloning**: Consistent AI voice across conversations
- **CRM Integration**: Connect to Salesforce, HubSpot, etc.

## 📝 Project Structure

```
frontdesk-ai-supervisor/
├── agent/
│   ├── ai_agent.py           # LiveKit AI agent
│   ├── knowledge_base.py     # Knowledge management
│   └── prompts.py            # System prompts
├── database/
│   ├── firebase_client.py    # Firebase operations
│   └── models.py             # Data models
├── services/
│   ├── help_request_service.py  # Request lifecycle
│   └── notification_service.py  # Notifications
├── supervisor/
│   ├── app.py                # Flask application
│   ├── routes.py             # API endpoints
│   └── templates/
│       └── dashboard.html    # Supervisor UI
├── .env                       # Environment variables
├── requirements.txt           # Python dependencies
├── firebase_config.json       # Firebase credentials
├── main.py                    # Entry point
└── README.md                  # This file
```

## 🤝 Contributing

This is a technical assessment project. For production use, consider:
- Adding comprehensive tests
- Implementing proper error handling
- Adding monitoring and alerting
- Setting up CI/CD pipeline
- Implementing security best practices


## 🆘 Support

For issues or questions:
1. Check Firebase/Groq/LiveKit console logs
2. Run `python main.py test` to verify connections
3. Review environment variables in `.env`
4. Check Firestore database rules

---

**Built with ❤️ for Frontdesk Engineering Assessment**