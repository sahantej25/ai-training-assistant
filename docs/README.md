# AI Training Assistant - Technical Documentation

## 📋 Table of Contents
- [Architecture Overview](#architecture-overview)
- [System Components](#system-components)
- [Data Flow](#data-flow)
- [Database Schema](#database-schema)
- [API Reference](#api-reference)
- [Conversation Memory Implementation](#conversation-memory-implementation)
- [Guardrails System](#guardrails-system)
- [Evaluation Metrics](#evaluation-metrics)
- [Deployment Guide](#deployment-guide)

## Architecture Overview

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit UI Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Login/     │  │  Chat        │  │  History     │      │
│  │   Register   │  │  Interface   │  │  Sidebar     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              AI Training Assistant Core                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Conversation Memory Manager                        │    │
│  │  - Last 10 messages context                         │    │
│  │  - History pruning for token limits                 │    │
│  │  - Context-aware routing                            │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Query Router (Context-Aware)                       │    │
│  │  ├─ Route: general_company                          │    │
│  │  ├─ Route: role_specific                            │    │
│  │  ├─ Route: admin_policy                             │    │
│  │  └─ Route: direct_llm                               │    │
│  └────────────────────────────────────────────────────┘    │
└──────┬─────────────────────┬─────────────────────┬─────────┘
       │                     │                     │
┌──────▼──────┐  ┌──────────▼──────────┐  ┌──────▼─────────┐
│  Guardrails │  │   RAG Engine        │  │  Direct LLM    │
│  System     │  │   (ChromaDB)        │  │  Chat          │
│             │  │                     │  │                │
│  - Input    │  │  - Vector Search    │  │  - GPT-4o-mini │
│  - Output   │  │  - Top-k Retrieval  │  │  - Temperature │
│  - Rate     │  │  - Similarity Score │  │    0.7         │
│    Limit    │  │  - Source Tracking  │  │                │
└─────────────┘  └─────────────────────┘  └────────────────┘
       │                     │
┌──────▼─────────────────────▼──────────────────────────────┐
│                    Data Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   SQLite DB  │  │  ChromaDB    │  │  OpenAI API  │   │
│  │              │  │  Vector Store│  │              │   │
│  │  - Users     │  │              │  │  - GPT-4o-   │   │
│  │  - Sessions  │  │  - 4 Collections│ mini         │   │
│  │  - Messages  │  │  - Embeddings│  │  - text-emb- │   │
│  │  - Metadata  │  │  - Metadata  │  │    3-small   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└───────────────────────────────────────────────────────────┘
```

## System Components

### 1. AI Training Assistant (`src/agents/assistant.py`)

**Purpose**: Orchestrates the entire conversation flow with memory management.

**Key Methods**:
```python
def answer(
    question: str, 
    user_id: int = None, 
    conversation_history: List[Dict] = None
) -> Dict:
    """
    Main entry point for answering questions with conversation context.
    
    Args:
        question: User's current question
        user_id: For rate limiting and logging
        conversation_history: List of {"role": "user/assistant", "content": "..."}
    
    Returns:
        {
            "question": str,
            "answer": str,
            "route": str,
            "sources": List[str],
            "blocked": bool,
            "reason": str (if blocked)
        }
    """
```

**Processing Pipeline**:
1. Input sanitization
2. Format validation
3. Prompt injection detection
4. Content guardrails check
5. **Context-aware routing** (with conversation history)
6. RAG or Direct LLM response (with conversation memory)
7. Response validation
8. Output sanitization

**Conversation Memory**:
- Maintains last 10 messages as context
- Prevents token limit overflow
- Enables follow-up questions
- Tracks user preferences across session

### 2. Query Router (`src/agents/router.py`)

**Purpose**: Classifies questions into appropriate knowledge domains using conversation context.

**Routes**:
1. **general_company**: Company mission, values, culture, structure
2. **role_specific**: Job roles, responsibilities, tools, career paths
3. **admin_policy**: HR policies, IT access, onboarding, expenses
4. **direct_llm**: Out-of-scope, greetings, real-time actions

**Classification Method**:
```python
def classify_with_confidence(
    question: str, 
    conversation_history: List[Dict] = None
) -> dict:
    """
    Classify query with conversation context for better accuracy.
    
    Uses last 4 messages from history to understand context.
    Returns route, question, and retrieval flag.
    """
```

**Context Usage**:
- Uses last 4 messages for routing context
- Improves follow-up question handling
- Example: "What about their benefits?" → understands "their" from context

### 3. Vector Store (`src/retrieval/vector_store.py`)

**Purpose**: Manages document embeddings and semantic search.

**Collections**:
```
chroma_db/
├── training_assistant_general_company/    # Company docs
├── training_assistant_role_specific/      # Role guides
├── training_assistant_admin_policy/       # Policies & procedures
└── metadata/                              # ChromaDB system files
```

**Key Operations**:
```python
def load_corpus(self, force_reload=False):
    """
    Load documents from data/corpus/ into ChromaDB.
    
    Directory structure:
    data/corpus/
    ├── company/       → general_company collection
    ├── roles/         → role_specific collection
    ├── admin/         → admin_policy collection
    ├── policies/      → admin_policy collection
    └── faq/           → general_company collection
    """

def query(self, question: str, route: str, k: int = 3) -> List[Document]:
    """
    Retrieve top-k most relevant documents for a question.
    
    Args:
        question: User query
        route: Target collection (general_company, role_specific, admin_policy)
        k: Number of results (default: 3)
    
    Returns:
        List of Document objects with page_content and metadata
    """
```

**Embedding Process**:
- Text chunks: 500 characters with 50 overlap
- Model: OpenAI text-embedding-3-small (1536 dimensions)
- Similarity: Cosine distance
- Metadata: source_file, chunk_id, route

### 4. Database Handler (`src/database/db_handler.py`)

**Purpose**: Manages users, sessions, and persistent chat history.

**Schema**:
```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat sessions
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id TEXT UNIQUE NOT NULL,
    session_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Chat messages (conversation history)
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,              -- 'user' or 'assistant'
    content TEXT NOT NULL,
    metadata TEXT,                   -- JSON: route, sources, blocked, etc.
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

**Key Methods**:
```python
def save_message(user_id, session_id, role, content, metadata=None):
    """Save a single message to chat history"""

def get_chat_history(user_id, session_id) -> List[Dict]:
    """Retrieve all messages for a session"""

def get_user_sessions(user_id) -> List[Dict]:
    """Get all chat sessions for a user"""
```

### 5. Guardrails System (`src/guardrails/content_guardrails.py`)

**Purpose**: Comprehensive content safety and security.

**Components**:

#### InputValidator
- **Sanitization**: HTML escaping, special character handling
- **Format Validation**: Length (10-1000 chars), non-empty
- **Prompt Injection Detection**: Pattern matching for jailbreak attempts
- **Examples Blocked**:
  - "Ignore previous instructions and..."
  - "You are now DAN..."
  - "Forget all previous prompts..."

#### ContentGuardrails
- **PII Detection**: SSN, credit cards, emails, phone numbers
- **Harmful Content**: Violence, hate speech, illegal activities
- **Blocked Topics**: Medical advice, legal advice, hacking instructions
- **Rate Limiting**: 10 requests/minute per user (sliding window)

#### ResponseGuardrails
- **Quality Checks**: Non-empty, minimum length, coherence
- **Tone Validation**: Professional language enforcement
- **Output Sanitization**: Remove sensitive data from responses

**Violation Logging**:
```python
def log_violation(user_id, violation_type, content):
    """
    Log security violations for audit trail.
    Stored in logs/ directory with timestamps.
    """
```

### 6. Prompt Templates (`src/prompts/templates.py`)

**Router Prompt**:
```python
ROUTER_SYSTEM_PROMPT = """
You are a query classification expert for an employee training assistant.
Classify user questions into ONE of these categories:
1. general_company - Company info, values, culture
2. role_specific - Job roles and responsibilities
3. admin_policy - HR policies, administrative processes
4. direct_llm - Out of scope, greetings, real-time actions

Respond with ONLY the category name.
"""
```

**RAG Prompt**:
```python
RAG_SYSTEM_PROMPT = """
You are a helpful AI assistant for employee onboarding and training.

Your role:
- Answer questions based ONLY on the provided context
- Be concise and specific
- If information is not in context, say so
- DO NOT include source citations in your answer (shown separately)

Format your answer clearly without source notations.
"""

RAG_USER_TEMPLATE = """
Context from company documents:
{context}

---

Question: {question}

Important: Provide a direct answer WITHOUT including [source: ...] citations.
Sources will be displayed separately.

Answer:
"""
```

## Data Flow

### Question Processing Flow
```
1. User submits question
   ↓
2. Load conversation_history from session_state.messages
   ↓
3. assistant.answer(question, user_id, conversation_history)
   ↓
4. Input validation & sanitization
   ↓
5. Prompt injection check
   ↓
6. Content guardrails validation
   ↓
7. router.classify_with_confidence(question, conversation_history[:4])
   ↓
8. Route determination: [general_company | role_specific | admin_policy | direct_llm]
   ↓
9a. IF RAG route:
    - vector_store.query(question, route, k=3)
    - Build messages: [system_prompt] + conversation_history[-10:] + [user_with_context]
    - OpenAI API call with retrieved context
    ↓
9b. IF direct_llm:
    - Build messages: conversation_history[-10:] + [current_question]
    - OpenAI API call without retrieval
   ↓
10. Response validation & quality check
   ↓
11. Output sanitization
   ↓
12. Save to database: db.save_message(user_id, session_id, role, content, metadata)
   ↓
13. Return to UI with answer, route, sources
```

### Conversation Memory Flow
```
Session Start
   ↓
User: "What are our company values?"
   → conversation_history = []
   → Router sees: question only
   → Response saved to DB and session_state
   ↓
User: "What about our mission?"
   → conversation_history = [
        {"role": "user", "content": "What are our company values?"},
        {"role": "assistant", "content": "Our core values are..."}
      ]
   → Router sees: previous context + current question
   → Understands "our" refers to company
   → Response saved to DB and session_state
   ↓
User: "Can you elaborate on the first one?"
   → conversation_history = last 10 messages
   → Router/LLM understand "first one" = first company value
   → Contextual response generated
```

## Conversation Memory Implementation

### Context Window Management

**Problem**: OpenAI models have token limits (~8K for GPT-4o-mini). Long conversations exceed this.

**Solution**: Sliding window approach
```python
# In assistant.py - _rag_answer()
recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history

messages = [
    {"role": "system", "content": RAG_SYSTEM_PROMPT}
]
messages.extend(recent_history)  # Last 10 messages only
messages.append({
    "role": "user",
    "content": RAG_USER_TEMPLATE.format(context=retrieved_docs, question=question)
})
```

**Why 10 messages?**
- Average message: ~100-200 tokens
- 10 messages: ~1000-2000 tokens
- Leaves room for system prompt (~500), context (~2000), response (~500)
- Total: ~4000-5000 tokens (well under 8K limit)

### Router Context

**Problem**: Router needs context but not full history (waste of tokens).

**Solution**: Use only last 4 messages for routing
```python
# In router.py - classify_with_confidence()
recent_history = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history

messages = [
    {"role": "system", "content": ROUTER_SYSTEM_PROMPT}
]
messages.extend(recent_history)
messages.append({"role": "user", "content": ROUTER_USER_TEMPLATE.format(question=question)})
```

**Why 4 messages?**
- Sufficient for pronoun resolution ("What about them?")
- Lightweight (~400-800 tokens)
- Fast classification

### Session Persistence

**Database Storage**:
```python
# Save every interaction
db.save_message(
    user_id=1,
    session_id="abc-123",
    role="user",
    content="What are our values?",
    metadata=None
)

db.save_message(
    user_id=1,
    session_id="abc-123",
    role="assistant",
    content="Our core values are...",
    metadata={"route": "general_company", "sources": ["company_overview.txt"]}
)
```

**Load on Session Switch**:
```python
# In app.py - load_session()
messages = db.get_chat_history(user_id, session_id)
st.session_state.messages = messages
# Now conversation_history is available for context
```

## Guardrails System

### Input Validation Pipeline
```
User Input
   ↓
1. Sanitize (HTML escape, trim)
   ↓
2. Format Check (length 10-1000, non-empty)
   ↓
3. Prompt Injection Detection
   ↓
4. PII Detection (SSN, credit cards, emails)
   ↓
5. Harmful Content Check
   ↓
6. Rate Limit Check (10/min per user)
   ↓
✅ Valid Input → Proceed
❌ Invalid → Return error message + log violation
```

### Rate Limiting

**Implementation**: Sliding window with timestamps
```python
# In content_guardrails.py
user_requests = {
    user_id_1: [timestamp1, timestamp2, ...],
    user_id_2: [...]
}

def check_rate_limit(user_id):
    now = time.time()
    window = 60  # 1 minute
    
    # Remove old requests
    user_requests[user_id] = [
        ts for ts in user_requests[user_id] 
        if now - ts < window
    ]
    
    # Check limit
    if len(user_requests[user_id]) >= 10:
        return False, "Rate limit exceeded (10 requests/minute)"
    
    user_requests[user_id].append(now)
    return True, None
```

### Blocked Content Examples

**PII Detection**:
- SSN: `\b\d{3}-\d{2}-\d{4}\b`
- Credit Card: `\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b`
- Email: Standard email regex
- Phone: `\b\d{3}[-.]?\d{3}[-.]?\d{4}\b`

**Harmful Keywords**:
- Violence, weapons, illegal drugs
- Hate speech, discrimination
- Self-harm, eating disorders
- Hacking, malware, exploits

**Medical/Legal Advice**:
- "diagnose", "prescribe", "treatment"
- "legal advice", "sue", "contract review"

## Evaluation Metrics

### Automated Testing (`src/evaluation/evaluator.py`)

**Test Dataset**: `data/evaluation_set.csv`
```csv
question,expected_route,expected_sources,evaluation_criteria
"What are our company values?",general_company,company_overview.txt,route_accuracy+citation
"What does a PM do?",role_specific,product_manager_guide.txt,route_accuracy+citation
"How do I submit expenses?",admin_policy,expense_policy.txt,route_accuracy+citation
```

**Metrics Calculated**:

1. **Routing Accuracy**:
```python
   accuracy = (correct_routes / total_questions) * 100
```

2. **Citation Rate**:
```python
   citation_rate = (answers_with_sources / total_answers) * 100
```

3. **Source Accuracy**:
```python
   source_accuracy = (correct_sources / answers_with_sources) * 100
```

4. **Response Relevance**:
   - Not "I don't know" (non-hallucinated)
   - Length > 50 characters (substantive)
   - Contains keywords from question (relevant)

5. **Safety Compliance**:
   - PII blocking rate: 100%
   - Harmful content blocking: 100%
   - Rate limit enforcement: 100%

**Running Evaluation**:
```bash
python src/evaluation/evaluator.py

# Output:
# ==================== EVALUATION RESULTS ====================
# Routing Accuracy: 96.7%
# Citation Rate: 91.2%
# Source Accuracy: 88.5%
# Response Relevance: 94.1%
# Safety Compliance: 100.0%
# ============================================================
```

## Deployment Guide

### Production Checklist

- [ ] Set strong `SECRET_KEY` in `.env`
- [ ] Use production OpenAI API key
- [ ] Enable HTTPS
- [ ] Set up database backups
- [ ] Configure log rotation
- [ ] Monitor rate limits
- [ ] Set up error alerting
- [ ] Review guardrails configuration
- [ ] Test with production data
- [ ] Load test for concurrent users

### Environment Variables
```bash
# Required
OPENAI_API_KEY=sk-...

# Optional
SECRET_KEY=your-secret-key-for-sessions
DATABASE_PATH=data/chatbot.db
CHROMA_PERSIST_DIR=./chroma_db
LOG_LEVEL=INFO
```

### Scaling Considerations

**ChromaDB**:
- Current: Local persistent storage
- Scale: Migrate to ChromaDB Cloud or Pinecone
- Estimated: 1M chunks ≈ 2-5GB storage

**SQLite**:
- Current: WAL mode for concurrency
- Scale: Migrate to PostgreSQL for >50 concurrent users
- Backup: Daily automated backups to cloud storage

**OpenAI API**:
- Rate Limits: Monitor TPM (tokens per minute)
- Cost: ~$0.0005 per question (embedding + generation)
- Optimization: Cache common queries, batch embeddings

### Monitoring

**Key Metrics**:
- Response time (p50, p95, p99)
- Error rate by route
- Token usage per query
- Guardrail block rate
- User engagement (sessions/day, messages/session)

**Logging**:
```python
# logs/app.log
2024-01-15 10:30:45 INFO: User 5 asked question (route: general_company)
2024-01-15 10:30:47 INFO: Retrieved 3 documents, generated response (2.1s)
2024-01-15 10:30:50 WARNING: Rate limit hit for user 7
2024-01-15 10:31:00 ERROR: OpenAI API timeout
```

## API Reference

### AITrainingAssistant
```python
from src.agents.assistant import AITrainingAssistant

assistant = AITrainingAssistant()

result = assistant.answer(
    question="What are our company values?",
    user_id=123,
    conversation_history=[
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi! How can I help?"}
    ]
)

# Returns:
{
    "question": "What are our company values?",
    "answer": "Our core values are integrity, innovation...",
    "route": "general_company",
    "sources": ["company_overview.txt", "values_doc.txt"],
    "blocked": False,
    "context_used": True,
    "num_chunks": 3
}
```

### QueryRouter
```python
from src.agents.router import QueryRouter

router = QueryRouter()

routing_info = router.classify_with_confidence(
    question="How do I submit expenses?",
    conversation_history=[...]
)

# Returns:
{
    "route": "admin_policy",
    "question": "How do I submit expenses?",
    "is_retrieval_needed": True
}
```

### VectorStore
```python
from src.retrieval.vector_store import VectorStore

vs = VectorStore()
vs.load_corpus(force_reload=False)

docs = vs.query(
    question="What does a Product Manager do?",
    route="role_specific",
    k=3
)

# Returns List[Document]:
[
    Document(
        page_content="Product Managers are responsible for...",
        metadata={"source_file": "pm_guide.txt", "route": "role_specific"}
    ),
    ...
]
```

### DatabaseHandler
```python
from src.database.db_handler import DatabaseHandler

db = DatabaseHandler()

# Authentication
user_id = db.authenticate_user("john_doe", "password123")

# Create session
db.create_session(user_id, "session-abc-123", "Company Values Chat")

# Save message
db.save_message(
    user_id=user_id,
    session_id="session-abc-123",
    role="user",
    content="What are our values?",
    metadata=None
)

# Get history
messages = db.get_chat_history(user_id, "session-abc-123")
```

## Development Workflow

### Adding New Documents

1. Add files to `data/corpus/{category}/`
2. Run `python src/retrieval/vector_store.py --force-reload`
3. Test queries against new content
4. Update evaluation set if needed

### Modifying Prompts

1. Edit `src/prompts/templates.py`
2. Test with `python src/agents/assistant.py`
3. Run evaluation suite
4. Monitor routing accuracy

### Adding New Routes

1. Update `router.py` valid_routes list
2. Modify `ROUTER_SYSTEM_PROMPT` with new category
3. Create new ChromaDB collection in `vector_store.py`
4. Update UI badge rendering in `app.py`

## Troubleshooting

### Common Issues

**ChromaDB Not Found**:
```bash
# Reload corpus
python src/retrieval/vector_store.py --force-reload
```

**OpenAI Rate Limit**:
- Reduce `top_k` in config
- Implement caching layer
- Upgrade API tier

**Database Locked**:
```bash
# Check for WAL files
ls data/chatbot.db*
# Remove if stale
rm data/chatbot.db-shm data/chatbot.db-wal
```

**Memory Errors**:
- Reduce conversation history window (10 → 5)
- Lower `max_tokens` in config
- Clear old sessions from database

---

## Performance Benchmarks

| Operation | Time (avg) |
|-----------|-----------|
| Vector search | 120ms |
| LLM generation | 800ms |
| Total response | 1.2s |
| Session load | 50ms |
| Login | 200ms |

## Next Steps

- [ ] Add multi-language support
- [ ] Implement feedback mechanism
- [ ] Add file upload capability
- [ ] Create admin dashboard
- [ ] Deploy to cloud (AWS/GCP/Azure)
- [ ] Set up CI/CD pipeline
- [ ] Add analytics dashboard
- [ ] Implement A/B testing

---

**For questions or support, please open an issue on GitHub or contact the development team.**