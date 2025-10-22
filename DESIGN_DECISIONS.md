# Design Decisions & Architecture

This document explains the key design decisions made in building the Frontdesk AI Supervisor system.

## 🏗️ Overall Architecture

### Layered Architecture Pattern

```
┌─────────────────────────────────────┐
│     Interfaces Layer                │
│  (Agent / Dashboard / API)          │
├─────────────────────────────────────┤
│     Services Layer                  │
│  (Business Logic)                   │
├─────────────────────────────────────┤
│     Database Layer                  │
│  (Data Access / Models)             │
└─────────────────────────────────────┘
```

**Why this architecture?**
- **Separation of Concerns**: Each layer has a single responsibility
- **Testability**: Can test each layer independently
- **Flexibility**: Easy to swap Firebase for PostgreSQL
- **Maintainability**: Changes in one layer don't affect others
- **Scalability**: Can scale layers independently

### Directory Structure

```
frontdesk-ai-supervisor/
├── agent/           # AI conversation logic
├── database/        # Data persistence
├── services/        # Business logic
├── supervisor/      # Web interface
└── main.py          # Orchestration
```

**Why this structure?**
- Each directory is a self-contained module
- Clear imports: `from database.firebase_client import FirebaseClient`
- Easy to understand for new developers
- Follows Python best practices

## 📊 Data Model Design

### 1. Help Request Model

```python
HelpRequest:
  - id: string
  - caller_id: string
  - caller_phone: string
  - question: string
  - context: string (optional)
  - status: enum (pending/resolved/timeout)
  - created_at: timestamp
  - resolved_at: timestamp (optional)
  - supervisor_answer: string (optional)
  - supervisor_name: string (optional)
```

**Design Decisions:**

**✅ Three-state lifecycle** (pending → resolved/timeout)
- **Why**: Simple, covers all cases, extensible
- **Alternative considered**: More states (in_progress, escalated, cancelled)
- **Rationale**: YAGNI - three states cover current needs, can add more later

**✅ Embedded supervisor info** (not separate collection)
- **Why**: Simplifies queries, denormalized for read performance
- **Alternative considered**: Separate supervisors table
- **Rationale**: For 1000/day, denormalization is faster. At 100k/day, would normalize

**✅ Optional context field**
- **Why**: Helps supervisor understand situation, but not always needed
- **Alternative considered**: Always require context
- **Rationale**: Flexible - sometimes question is self-explanatory

**✅ Timestamps in UTC**
- **Why**: Avoids timezone confusion, standard practice
- **Alternative considered**: Local time
- **Rationale**: Always store UTC, convert on display

### 2. Knowledge Entry Model

```python
KnowledgeEntry:
  - id: string
  - question: string
  - answer: string
  - source: string
  - help_request_id: string (optional)
  - created_at: timestamp
  - updated_at: timestamp
  - usage_count: int
```

**Design Decisions:**

**✅ Usage tracking** (usage_count field)
- **Why**: Identifies valuable knowledge, informs prioritization
- **Alternative considered**: Separate analytics table
- **Rationale**: Simple counter works for MVP, shows what AI uses most

**✅ Link to help_request_id**
- **Why**: Traceability - know where knowledge came from
- **Alternative considered**: No linkage
- **Rationale**: Helps audit quality, understand learning sources

**✅ Q&A format** (not embeddings yet)
- **Why**: Simple, human-readable, works for small scale
- **Alternative considered**: Vector embeddings from start
- **Rationale**: Start simple. Add embeddings when > 100 entries or accuracy drops

**✅ Updated timestamp**
- **Why**: Track when knowledge was last modified
- **Alternative considered**: Only created_at
- **Rationale**: Useful for cache invalidation, auditing

### 3. Call Log Model

```python
CallLog:
  - id: string
  - caller_id: string
  - caller_phone: string
  - started_at: timestamp
  - ended_at: timestamp (optional)
  - transcript: string (optional)
  - help_requests: list[string]
  - resolved_by_ai: boolean
```

**Design Decisions:**

**✅ Array of help_request IDs**
- **Why**: One call can have multiple escalations
- **Alternative considered**: One-to-one relationship
- **Rationale**: More flexible, handles complex calls

**✅ resolved_by_ai flag**
- **Why**: Quick metric - how often AI needs help
- **Alternative considered**: Compute from help_requests
- **Rationale**: Denormalized for faster analytics queries

**✅ Optional transcript**
- **Why**: Not all calls need full transcription, saves storage
- **Alternative considered**: Always transcribe
- **Rationale**: Storage cost, privacy concerns

## 🎯 Key Architectural Decisions

### 1. Database Choice: Firebase Firestore

**✅ Chosen: Firebase Firestore**

**Pros:**
- Free tier: 50k reads, 20k writes/day (handles 1000 requests/day)
- Zero ops: No server management
- Real-time updates: Dashboard auto-refreshes
- Fast setup: 5 minutes to production
- Python SDK: Well-documented
- NoSQL flexibility: Easy schema evolution

**Cons:**
- Vendor lock-in
- Query limitations (no complex joins)
- Costs scale with usage
- Not ideal for analytics

**Alternatives Considered:**

**PostgreSQL:**
- Pros: Mature, powerful queries, open source
- Cons: Requires server, more setup, more maintenance
- Verdict: Better for 10k+/day, overkill for MVP

**MongoDB:**
- Pros: Flexible schema, good Python support
- Cons: Similar to Firestore but requires hosting
- Verdict: Firestore is simpler for this scale

**SQLite:**
- Pros: Zero setup, perfect for development
- Cons: Not for production, no concurrent writes
- Verdict: Good for testing, not for deployed system

**Scaling Path:**
- 0-1k/day: **Firestore** (current)
- 1k-10k/day: **Firestore + Redis cache**
- 10k-100k/day: **PostgreSQL + Redis + Queue**
- 100k+/day: **PostgreSQL cluster + Redis cluster + Kafka**

### 2. LLM Choice: Groq (Llama)

**✅ Chosen: Groq with Llama 3.1**

**Why Groq:**
- **Speed**: 300+ tokens/second (vs OpenAI 40-60)
- **Cost**: Very affordable, generous free tier
- **Quality**: Llama 3.1 70B is excellent
- **Latency**: Critical for voice calls

**Alternatives Considered:**

**OpenAI:**
- Pros: Industry standard, very reliable
- Cons: Slower, more expensive, rate limits
- Verdict: Good choice, but Groq is faster/cheaper

**Anthropic Claude:**
- Pros: High quality, good at reasoning
- Cons: More expensive, rate limited
- Verdict: Would use for complex reasoning tasks

**Open source (Ollama):**
- Pros: Free, private, full control
- Cons: Requires GPU, maintenance, slower
- Verdict: Not practical for this project

**Why two models:**
```python
# Fast, cheap for confidence checks
llama-3.1-8b-instant

# Smarter for actual responses
llama-3.1-70b-versatile
```

### 3. Voice Infrastructure: LiveKit

**✅ Chosen: LiveKit**

**Why:**
- Open source, production-ready
- Excellent Python SDK
- WebRTC-based (low latency)
- Free tier available
- Real-time capabilities

**Alternatives Considered:**

**Twilio:**
- Pros: Battle-tested, comprehensive
- Cons: More expensive, less flexible
- Verdict: Good for production, but pricier

**Vonage:**
- Pros: Good API, reliable
- Cons: Similar to Twilio
- Verdict: Comparable alternative

**Custom WebRTC:**
- Pros: Full control
- Cons: Too much complexity
- Verdict: Not worth building from scratch

**Note**: Simple text agent (`simple_agent.py`) included for testing without LiveKit setup.

### 4. Web Framework: Flask

**✅ Chosen: Flask**

**Why:**
- Lightweight, perfect for simple API
- Easy to understand
- Minimal boilerplate
- Great for MVPs

**Alternatives Considered:**

**FastAPI:**
- Pros: Modern, async, auto docs
- Cons: More complex for simple needs
- Verdict: Would use for larger API

**Django:**
- Pros: Batteries included, admin panel
- Cons: Too heavy for this project
- Verdict: Overkill for simple dashboard

### 5. Frontend: Vanilla HTML/CSS/JS

**✅ Chosen: No framework**

**Why:**
- **Requirement**: "Keep UI extremely simple"
- No build step needed
- Fast to develop
- Easy to understand
- 100% browser compatible

**Alternatives Considered:**

**React:**
- Pros: Component-based, rich ecosystem
- Cons: Build step, complexity, learning curve
- Verdict: Unnecessary for admin panel

**Vue:**
- Pros: Simple framework, good docs
- Cons: Still adds complexity
- Verdict: Would use for customer-facing UI

**Trade-off**: Chose simplicity over features. For production customer UI, would use React/Vue.

## 🔄 Request Lifecycle Design

### State Machine

```
┌─────────┐
│ PENDING │
└────┬────┘
     │
     ├──→ [Supervisor answers] ──→ RESOLVED
     │
     └──→ [24h passes] ──→ TIMEOUT
```

**Why this design:**
- **Simple**: Only 3 states, easy to reason about
- **Clear**: No ambiguous transitions
- **Extensible**: Can add states later (in_progress, escalated, cancelled)

**Improvements for production:**
```
PENDING
  ↓
ASSIGNED (to specific supervisor)
  ↓
IN_PROGRESS (supervisor opened it)
  ↓
RESOLVED / CANCELLED / TIMEOUT
```

### Timeout Strategy

**Current**: 24 hours hard timeout

**Why:**
- Prevents zombie requests
- Forces supervisor action
- Reasonable SLA

**Production considerations:**
- Priority levels (urgent = 1h, normal = 24h)
- Escalation chain (notify manager after 4h)
- Business hours aware (don't timeout overnight)

## 🧠 Knowledge Base Strategy

### Search Algorithm

**Current**: Simple text matching with word overlap

```python
def _is_similar(self, q1: str, q2: str, threshold: float = 0.6):
    words1 = set(q1.split())
    words2 = set(q2.split())
    similarity = len(intersection) / len(union)
    return similarity >= threshold
```

**Why:**
- Fast (O(n) where n = word count)
- Good enough for < 100 entries
- No dependencies
- Interpretable

**Limitations:**
- No semantic understanding ("cost" vs "price")
- No synonym handling
- Word order ignored
- Doesn't scale beyond 1000 entries

**Scaling path:**

**100-1,000 entries: Full-text search**
```python
# Use Firebase text search or Elasticsearch
```

**1,000+ entries: Vector embeddings**
```python
# OpenAI embeddings + Pinecone/Weaviate
question_embedding = openai.embed(question)
results = vector_db.search(question_embedding, top_k=5)
```

### Cache Strategy

**Current**: In-memory cache on startup

```python
def _load_cache(self):
    self._cache = self.db.get_all_knowledge()
```

**Why:**
- Fast reads (no DB call)
- Simple implementation
- Works for small KB

**When to change:**
- > 1000 entries (memory concern)
- Multiple servers (cache inconsistency)
- Frequent updates (stale cache)

**Next level: Redis**
```python
# Cached with 1h TTL
knowledge = redis.get(f"kb:{question_hash}")
if not knowledge:
    knowledge = db.get_knowledge(question)
    redis.setex(f"kb:{question_hash}", 3600, knowledge)
```

## 🚀 Scaling Strategy

### Current Capacity: ~1,000 requests/day

**Bottlenecks:**
- Single Flask instance (10-20 req/sec)
- Firebase free tier (50k reads/day)
- No caching layer
- No queue system

### Scaling to 10,000/day

**Required changes:**

**1. Database**
```
Firebase → PostgreSQL + Connection pooling
- Handles complex queries
- Better for analytics
- More cost-effective at scale
```

**2. Caching**
```
Add Redis:
- Knowledge base cache (1h TTL)
- Session data
- Rate limiting
- Request deduplication
```

**3. Multiple instances**
```
Load Balancer
   ├── Flask Instance 1
   ├── Flask Instance 2
   └── Flask Instance 3
```

**4. Async processing**
```
API → Queue (RabbitMQ) → Workers
- Non-blocking escalations
- Batch notifications
- Background knowledge updates
```

**5. Monitoring**
```
- DataDog / New Relic
- Error tracking (Sentry)
- Performance monitoring
- Alert on SLA breaches
```

### Scaling to 100,000/day

**Additional requirements:**

**1. Microservices**
```
- Agent service (handles calls)
- Knowledge service (manages KB)
- Notification service (sends messages)
- Analytics service (reports)
```

**2. Event-driven architecture**
```
Events: request_created, request_resolved, knowledge_added
Kafka/SQS for reliable event delivery
```

**3. Database sharding**
```
Shard by: caller_phone or region
Read replicas for analytics
```

**4. CDN for dashboard**
```
CloudFront / Cloudflare
Static asset caching
```

**5. Advanced knowledge base**
```
- Vector database (Pinecone)
- Semantic search
- Auto-categorization
- Knowledge graph
```

## 🔐 Security Considerations

### Current State (MVP)

**What's implemented:**
- Environment variables for secrets
- Firebase auth (service account)
- No hardcoded credentials

**What's missing:**
- No authentication on dashboard
- No authorization/roles
- No rate limiting
- No input validation
- No CSRF protection

### Production Requirements

**1. Authentication**
```python
# OAuth 2.0 with Google/Okta
@app.route('/dashboard')
@require_auth
def dashboard():
    ...
```

**2. Authorization**
```python
roles = {
    'supervisor': ['view_requests', 'resolve_requests'],
    'manager': ['view_requests', 'resolve_requests', 'view_analytics'],
    'admin': ['*']
}
```

**3. Rate Limiting**
```python
# Per IP, per user
@limiter.limit("100 per hour")
def api_endpoint():
    ...
```

**4. Input Sanitization**
```python
# Prevent SQL injection, XSS
answer = bleach.clean(request.form['answer'])
```

**5. Audit Logging**
```python
# Track who did what when
audit_log.info(f"User {user_id} resolved request {req_id}")
```

## 📊 Observability

### What to Monitor

**1. System Health**
- API response times
- Error rates
- Database connection pool
- Memory usage

**2. Business Metrics**
- Escalation rate (target: < 20%)
- Resolution time (target: < 15 minutes)
- Knowledge base growth
- Caller satisfaction

**3. AI Performance**
- Confidence accuracy
- False escalation rate
- Knowledge base hit rate
- Response quality

### Logging Strategy

**Current**: Console logging

**Production**: Structured logging
```python
import structlog

log = structlog.get_logger()
log.info("request_created", 
    request_id=req_id, 
    caller=phone, 
    question_length=len(question))
```

## 🎯 Design Principles Used

### 1. YAGNI (You Aren't Gonna Need It)
- Started simple, didn't over-engineer
- No premature optimization
- Can add complexity when needed

### 2. Separation of Concerns
- Database layer doesn't know about Flask
- Services don't know about UI
- Clean abstractions

### 3. Fail Fast
- Validate inputs early
- Raise exceptions for bad data
- Don't hide errors

### 4. Explicit Over Implicit
- Clear function names
- Typed models (Pydantic)
- Obvious code flow

### 5. Optimize for Readability
- Code is read 10x more than written
- Comments explain "why" not "what"
- Consistent naming

## 🔮 Future Enhancements

### Phase 2 (Mentioned in requirements)
- Live call transfer to supervisor
- Hold music during transfer
- Supervisor availability check
- Real-time call monitoring

### Phase 3 (Natural evolution)
- Multi-tenant (support multiple businesses)
- Mobile app for supervisors
- Voice analytics
- Sentiment analysis
- Automated knowledge curation

### Phase 4 (Advanced)
- AI learns from resolutions without human input
- Predictive escalation (escalate before failing)
- Multi-language support
- Integration marketplace (Salesforce, Shopify, etc.)

---

**Key Takeaway**: Started simple with clear abstractions, making it easy to scale and enhance as needs grow.