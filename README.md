# Frontdesk AI Supervisor System

A human-in-the-loop AI system that allows AI receptionists to escalate unknown questions to human supervisors, learn from their responses, and automatically follow up with customers.

## 🎯 Overview

This system enables an AI agent to:
- Handle incoming calls using LiveKit and Groq's Llama model
- Automatically detect when it doesn't know an answer
- Escalate questions to human supervisors
- Learn from supervisor responses and update its knowledge base
- Follow up with customers automatically when answers are received

## 🏗️ Architecture

### Tech Stack
- **AI/LLM**: Groq (Llama 3.1)
- **Voice Infrastructure**: LiveKit
- **Database**: Firebase Firestore
- **Backend**: Python, Flask
- **Frontend**: Vanilla HTML/CSS/JavaScript

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

## 💡 Tips for Demo Video

1. **Start with overview**: Show architecture diagram
2. **Demo happy path**: Call → Question → Answer → No escalation
3. **Demo escalation**: Call → Unknown question → Escalation
4. **Show dashboard**: Pending requests, answer submission
5. **Show follow-up**: Console logs showing SMS to caller
6. **Show learning**: Knowledge base update, next call uses new knowledge
7. **Discuss decisions**: Why Firebase, scaling strategy, etc.

## 🤝 Contributing

This is a technical assessment project. For production use, consider:
- Adding comprehensive tests
- Implementing proper error handling
- Adding monitoring and alerting
- Setting up CI/CD pipeline
- Implementing security best practices

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

For issues or questions:
1. Check Firebase/Groq/LiveKit console logs
2. Run `python main.py test` to verify connections
3. Review environment variables in `.env`
4. Check Firestore database rules

---

**Built with ❤️ for Frontdesk Engineering Assessment**