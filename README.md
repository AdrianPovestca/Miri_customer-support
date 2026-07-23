# 🤖 AI Customer Support Playbook

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/status-complete-brightgreen)

A practical open-source guide for building AI-powered customer support systems using Retrieval-Augmented Generation (RAG), semantic vector search, and modern LLM workflows — from a simple keyword-matching chatbot all the way to a multi-language, persistent, monitored REST API with an admin panel.

This project demonstrates how to design and implement an intelligent customer support chatbot that retrieves relevant information from a knowledge base using semantic search, remembers conversations across sessions and restarts, responds in the customer's own language, collects user feedback, and exposes all of this through a production-style API with monitoring and administration tools.

## 🎯 Project Goals

This educational project demonstrates:

- 📚 **Knowledge Base Design** - Structure customer support documentation for optimal retrieval
- 🔍 **Semantic Search** - Vector embeddings (ChromaDB + Sentence Transformers), with TF-IDF as a fallback
- 🎯 **RAG Architecture** - Retrieve relevant documents and generate context-aware responses
- 💬 **Conversation Memory** - Multi-turn context, persisted to a database across restarts
- 🌍 **Multi-Language Support** - Auto-detects the customer's language and replies in kind
- 👍 **Feedback Loops** - Collects and reports on response quality
- 📝 **Prompt Engineering** - Craft effective, grounded prompts for customer support scenarios
- 🐳 **Production Readiness** - REST API, Docker, monitoring, and an admin interface
- ✅ **Best Practices** - Python development standards, testing, logging, and documentation

## ✨ Features

- ✅ **Realistic Knowledge Base** - 11 markdown files covering account, orders, shipping, returns, refunds, payments, products, technical support, password reset, refund policy, and FAQ for an online shoe store
- ✅ **Semantic Vector Search** - ChromaDB + Sentence Transformers understand meaning, not just keywords
- ✅ **TF-IDF Retriever** - Original keyword-based retriever, kept as an automatic fallback
- ✅ **AI-Generated Responses** - Answers are written by an LLM, grounded strictly in the retrieved knowledge base content (not hallucinated)
- ✅ **Multi-Turn Conversation Memory** - Understands follow-up questions and references to earlier parts of the conversation
- ✅ **Multi-Language Support** - Detects the customer's language (with a confidence threshold to avoid false positives on short text) and replies fluently in it, translating grounded English knowledge base content on the fly
- ✅ **User Feedback Loop** - 👍/👎 on every response, tracked and summarized (satisfaction rate, recent negative feedback for review)
- ✅ **Persistent Conversation History** - Stored in SQLite, survives API restarts (previously in-memory only)
- ✅ **Graceful Fallback, Everywhere** - If vector search, language detection, or the LLM is unavailable or fails, the bot automatically falls back to a simpler method so it never breaks
- ✅ **REST API** - FastAPI-based `/chat` endpoint with per-session conversation memory
- ✅ **Dockerized** - Runs the same way anywhere with `docker compose up --build`
- ✅ **Analytics Dashboard** - Live, auto-refreshing visual dashboard (`/dashboard`) built on the `/stats` endpoint
- ✅ **Admin Interface** - Browse, inspect, and delete stored conversations (`/admin`), with optional token protection
- ✅ **Comprehensive Testing** - pytest suite covering core modules
- ✅ **Professional Logging** - Structured logging for debugging and monitoring
- ✅ **Command-Line Interface** - Interactive chatbot for testing and demonstration, feedback loop included

## 📁 Folder Structure

```
ai-customer-support-playbook/
├── docs/                          # Project documentation
│   ├── architecture.md
│   ├── customer-support.md
│   └── rag-guide.md
├── knowledge_base/                # Customer support documentation (11 files)
│   ├── account.md
│   ├── orders.md
│   ├── shipping.md
│   ├── returns.md
│   ├── refunds.md
│   ├── refund-policy.md
│   ├── payments.md
│   ├── products.md
│   ├── technical.md
│   ├── password-reset.md
│   └── faq.md
├── src/                           # Source code
│   ├── chatbot.py                 # CLI entry point, conversation history, feedback prompt
│   ├── api.py                     # FastAPI REST API, dashboard + admin routes
│   ├── static/
│   │   ├── dashboard.html         # Live analytics dashboard UI
│   │   └── admin.html             # Admin panel UI
│   ├── database.py                # SQLite-backed persistent conversation history
│   ├── analytics.py                # Lightweight request monitoring
│   ├── feedback.py                # User feedback (thumbs up/down) storage and summary
│   ├── language.py                 # Language detection for multi-language replies
│   ├── config.py                  # Configuration and environment settings
│   ├── logger.py                  # Structured logging setup
│   ├── models.py                  # Document data model
│   ├── document_loader.py         # Load documents from knowledge base
│   ├── retriever.py               # TF-IDF search and ranking (fallback)
│   ├── embeddings.py              # ChromaDB + Sentence Transformers semantic search
│   ├── responder.py               # AI-generated + template-based responses
│   └── prompts.py                 # Prompt templates and user-facing messages
├── chroma_db/                      # Persisted vector index (auto-generated, gitignored)
├── conversations.db                 # SQLite conversation history (auto-generated, gitignored)
├── tests/                         # Pytest test suite
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .gitignore
├── README.md
└── LICENSE
```

## 🛠 Technologies Used

| Component | Technology | Purpose |
|---|---|---|
| Language | Python 3.8+ | Core implementation language |
| Semantic Search | ChromaDB + Sentence Transformers | Meaning-based retrieval, not just keywords |
| Keyword Search | TF-IDF + Text Processing | Fallback relevance ranking |
| LLM | Groq API (OpenAI-compatible) | Free-tier AI-generated responses |
| Language Detection | langdetect | Detects the customer's language for multi-language replies |
| API | FastAPI + Uvicorn | REST API, dashboard, and admin routes |
| Persistence | SQLite | Conversation history that survives restarts |
| Containerization | Docker + Docker Compose | Portable, reproducible deployment |
| Testing | pytest | Unit and integration tests |
| Logging | Python logging | Structured logging and debugging |
| Environment | python-dotenv | Configuration management |

> **Note on the LLM provider:** the code uses the standard `openai` Python package, pointed at a configurable `OPENAI_BASE_URL`. By default this targets [Groq](https://console.groq.com), which offers a generous free tier with no credit card required. Swapping to OpenAI itself just means changing `OPENAI_BASE_URL` and `OPENAI_API_KEY` in `.env`.

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip
- Git

### Setup

```bash
git clone https://github.com/AdrianPovestca/ai-customer-support-playbook.git
cd ai-customer-support-playbook

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your OPENAI_API_KEY (a free Groq key works great)
```

> **Note:** `sentence-transformers` and `chromadb` are sizeable dependencies — installation may take a few minutes, and the first run will download an embedding model (~90MB) automatically.

### Configure your `.env`

```
OPENAI_API_KEY=your-key-here
OPENAI_BASE_URL=https://api.groq.com/openai/v1
USE_AI_GENERATION=true
USE_VECTOR_SEARCH=true
ADMIN_TOKEN=
```

Leave `OPENAI_API_KEY` empty (or set `USE_AI_GENERATION=false`) to run the bot with template-only responses, no LLM required. Set `USE_VECTOR_SEARCH=false` to use the original TF-IDF retriever instead. Set `ADMIN_TOKEN` to any secret value to require it (via the `X-Admin-Token` header) on all `/admin` routes — leave it empty for open access during local development.

## 🚀 Usage (CLI)

```bash
cd src
python chatbot.py
```

Example session:

```
============================================================
🤖 AI Customer Support Playbook
============================================================
Knowledge base loaded: 11 document(s)
------------------------------------------------------------
Hello! 👋

How can I help you today?
------------------------------------------------------------
You: Cum îmi resetez parola?

Assistant:
Pentru a vă reseta parola, accesați pagina de logare și selectați
"Am uitat parola"...

Was this helpful? (y/n, Enter to skip): y
You: exit

Assistant:
Thanks for reaching out! Have a great day. 👋
------------------------------------------------------------
Session feedback: 1 👍  0 👎  (100.0% satisfaction)
------------------------------------------------------------
```

Type `reset` at any time to clear the conversation and start fresh. The bot understands follow-ups ("What if it doesn't arrive?" after a shipping question) and replies in whatever language you write in — tested with English, Romanian, German, and Russian.

## 🐳 Running with Docker

```bash
docker compose up --build
```

Builds and runs the API in a container (CPU-only PyTorch to keep the image lean), using your local `.env` for secrets and persisting both the vector index (`chroma_db/`) and conversation history (`conversations.db`) outside the container.

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"message": "How do I reset my password?", "session_id": "demo"}'
```

## 📈 Monitoring

Visit `/dashboard` in a browser for a live, auto-refreshing view, or query it directly:

```bash
curl http://localhost:8000/stats
```

Returns request volume, average response time, AI-generation vs. template-fallback rate, and user feedback (satisfaction rate, recent negative feedback) — useful for spotting issues like a misconfigured API key (which silently falls back to templates) or a cold-start delay on the first request after the server starts.

## 👍 Feedback

Every `/chat` response includes a `response_id`. Submit feedback against it:

```bash
curl -X POST http://localhost:8000/feedback -H "Content-Type: application/json" -d '{"response_id": "<id-from-chat-response>", "rating": "negative", "comment": "too generic"}'
```

## 🔐 Admin Panel

Visit `/admin` in a browser to list all stored conversations, inspect any of them message-by-message, or delete them. Protected by `ADMIN_TOKEN` if one is set in `.env`.

## 📊 How It Works

```
User Query
    ↓
[Language Detection] → identify the customer's language (confidently, or default to English)
    ↓
[Semantic Search] → ChromaDB + Sentence Transformers rank chunks by meaning
    ↓            ↓ (if unavailable or it fails)
    ↓     [TF-IDF Fallback] → keyword-based scoring and threshold filter
    ↓
[Conversation History] → loaded from SQLite, prior turns included for context
    ↓
[LLM Generation] → Groq writes a natural answer, in the customer's language, grounded in the top matches
    ↓                       ↓ (if this fails or is disabled)
    ↓                [Template Fallback] → return the matched document as-is (English only)
    ↓
Display Response + response_id for feedback
    ↓
[Analytics] → request logged (timing, AI vs. fallback, results found)
```

Every layer degrades gracefully — the bot never breaks, it just gets simpler, and it's always honest about the limitation (e.g. noting when a non-English answer had to fall back to English).

## 🧪 Testing

```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=term-missing
```

## 🗺️ Roadmap

### Phase 1: Foundation ✅
- [x] Project structure
- [x] Knowledge base with realistic Q&A
- [x] TF-IDF retriever with text processing
- [x] Comprehensive tests
- [x] Logging system

### Phase 2: LLM Integration ✅
- [x] OpenAI-compatible API integration (via Groq, free tier)
- [x] Prompt engineering framework (`prompts.py`, grounded system prompt)
- [x] Response generation with automatic template fallback
- [x] Context management (multi-turn conversation memory)
- [ ] LangChain integration (not used — direct API calls kept it simpler and easier to explain)

### Phase 3: Vector Search ✅
- [x] ChromaDB integration
- [x] Sentence Transformers embeddings
- [x] Semantic similarity scoring
- [x] Embedding caching (persisted index, built once)

### Phase 4: Production ✅
- [x] FastAPI REST API (`/chat`, `/health`, `/stats`, session-based conversation memory)
- [x] Docker containerization (CPU-only PyTorch to keep the image lean)
- [x] Performance optimization (response caching for repeated first questions, persisted embedding index)
- [x] Monitoring and analytics (`/stats` endpoint + visual `/dashboard`)

### Phase 5: Advanced Features ✅
- [x] Multi-language support (auto-detected, confidence-gated to avoid false positives)
- [x] Conversation history (persisted to SQLite, survives restarts)
- [x] User feedback loop (👍/👎, satisfaction rate, CLI + API)
- [x] Analytics dashboard (live, auto-refreshing HTML dashboard)
- [x] Admin interface (session browser, inspection, deletion, optional token auth)

## 💡 Key Learnings

This project teaches:
- **Information Retrieval** - TF-IDF vs. semantic vector search, when each one wins
- **RAG Patterns** - Document retrieval, context augmentation, grounded response generation
- **LLM Integration** - Calling an OpenAI-compatible API, prompt design, graceful degradation
- **Conversation Design** - Multi-turn memory, context-aware retrieval, follow-up question handling
- **Multi-Language Systems** - Language detection pitfalls (short/ambiguous text), confidence thresholds
- **Production Concerns** - REST APIs, containerization, monitoring, basic admin tooling, and where the honest limits of a portfolio-scale implementation are (in-memory vs. persisted state, simple token auth vs. real authentication)
- **Python Best Practices** - Type hints, docstrings, error handling, logging
- **Debugging** - Diagnosing import errors, environment variable loading, relevance thresholds, git merge conflicts, disk space issues in Docker builds

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Last Updated:** July 23, 2026
**Current Version:** 1.0.0
**Maintenance Status:** Feature-complete (Phases 1–5); open to further refinement