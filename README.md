# 🤖 AI Customer Support Playbook

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/status-in%20development-orange)

A practical open-source guide for building AI-powered customer support systems using Retrieval-Augmented Generation (RAG), semantic vector search, and modern LLM workflows.

This project demonstrates how to design and implement an intelligent customer support chatbot that retrieves relevant information from a knowledge base using semantic search, remembers the ongoing conversation, and uses an LLM to generate accurate, natural-sounding responses.

## 🎯 Project Goals

This educational project demonstrates:

- 📚 **Knowledge Base Design** - Structure customer support documentation for optimal retrieval
- 🔍 **Semantic Search** - Vector embeddings (ChromaDB + Sentence Transformers), with TF-IDF as a fallback
- 🎯 **RAG Architecture** - Retrieve relevant documents and generate context-aware responses
- 💬 **Conversation Memory** - Multi-turn context so follow-up questions are understood
- 📝 **Prompt Engineering** - Craft effective, grounded prompts for customer support scenarios
- ✅ **Best Practices** - Python development standards, testing, logging, and documentation
- 🚀 **LLM Integration** - Real AI-generated responses grounded in retrieved knowledge

## ✨ Features

- ✅ **Realistic Knowledge Base** - 11 markdown files covering account, orders, shipping, returns, refunds, payments, products, technical support, password reset, refund policy, and FAQ for an online shoe store
- ✅ **Semantic Vector Search** - ChromaDB + Sentence Transformers understand meaning, not just keywords (e.g. "Is PayPal an option?" correctly matches "What payment methods do you accept?")
- ✅ **TF-IDF Retriever** - Original keyword-based retriever, kept as an automatic fallback
- ✅ **Embedding Caching** - The vector index is built once and persisted to disk, not recomputed on every run
- ✅ **AI-Generated Responses** - Answers are written by an LLM, grounded strictly in the retrieved knowledge base content (not hallucinated)
- ✅ **Multi-Turn Conversation Memory** - The bot understands follow-up questions and references to earlier parts of the conversation (type `reset` anytime to start fresh)
- ✅ **Graceful Fallback, Everywhere** - If vector search, or the LLM, is unavailable or fails, the bot automatically falls back to a simpler method so it never breaks
- ✅ **Comprehensive Testing** - pytest suite covering core modules
- ✅ **Professional Logging** - Structured logging for debugging and monitoring
- ✅ **Command-Line Interface** - Interactive chatbot for testing and demonstration

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
│   ├── chatbot.py                 # Main CLI application entry point, conversation history
│   ├── config.py                  # Configuration and environment settings
│   ├── logger.py                  # Structured logging setup
│   ├── models.py                  # Document data model
│   ├── document_loader.py         # Load documents from knowledge base
│   ├── retriever.py               # TF-IDF search and ranking (fallback)
│   ├── embeddings.py              # ChromaDB + Sentence Transformers semantic search
│   ├── responder.py               # AI-generated + template-based responses
│   └── prompts.py                 # Prompt templates and user-facing messages
├── chroma_db/                      # Persisted vector index (auto-generated, gitignored)
├── tests/                         # Pytest test suite
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
```

Leave `OPENAI_API_KEY` empty (or set `USE_AI_GENERATION=false`) to run the bot with template-only responses, no LLM required. Set `USE_VECTOR_SEARCH=false` to use the original TF-IDF retriever instead.

## 🚀 Usage

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
  • account.md
  • faq.md
  • orders.md
  ...
------------------------------------------------------------
Hello! 👋

How can I help you today?
------------------------------------------------------------
You: Is PayPal an option for payment?

Assistant:
Yes, we accept PayPal as a payment method, alongside major credit cards,
Apple Pay, and Google Pay.

You: What if they charge me twice?
```

The bot understands "they" refers to PayPal/payments from the previous turn, thanks to conversation memory. Type `reset` at any time to clear the conversation and start fresh.

### Example Queries

**Account & Login**
- "I forgot my login password" *(semantic match, no exact keywords needed)*
- "Can I change my email address?"

**Orders & Shipping**
- "Can I track my order?"
- "How long does shipping take?"

**Returns & Refunds**
- "What happens if my shoes arrive damaged?" *(matches "defective shoe" content semantically)*
- "Can I return items after 30 days?"

**Payments**
- "Do you take PayPal?"
- "What payment methods do you accept?"

## 📊 How It Works

```
User Query
    ↓
[Semantic Search] → ChromaDB + Sentence Transformers rank chunks by meaning
    ↓            ↓ (if unavailable or it fails)
    ↓     [TF-IDF Fallback] → keyword-based scoring and threshold filter
    ↓
[Conversation History] → prior turns are included for context
    ↓
[LLM Generation] → Groq writes a natural answer grounded in the top matches
    ↓                       ↓ (if this fails or is disabled)
    ↓                [Template Fallback] → return the matched document as-is
    ↓
Display Response
```

The system prompt instructs the LLM to answer **only** from the retrieved context and to say so honestly when it doesn't have the information, rather than inventing policies or prices. Every layer degrades gracefully — the bot never breaks, it just gets simpler.

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

### Phase 4: Production
- [ ] FastAPI REST API
- [ ] Docker containerization
- [ ] Performance optimization
- [ ] Monitoring and analytics

### Phase 5: Advanced Features
- [ ] Multi-language support
- [ ] User feedback loop
- [ ] Analytics dashboard
- [ ] Admin interface

## 💡 Key Learnings

This project teaches:
- **Information Retrieval** - TF-IDF vs. semantic vector search, when each one wins
- **RAG Patterns** - Document retrieval, context augmentation, grounded response generation
- **LLM Integration** - Calling an OpenAI-compatible API, prompt design, graceful degradation
- **Conversation Design** - Multi-turn memory, follow-up question handling
- **Python Best Practices** - Type hints, docstrings, error handling, logging
- **Debugging** - Diagnosing import errors, environment variable loading, relevance thresholds, git merge conflicts

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Last Updated:** July 6, 2026
**Current Version:** 0.3.0
**Maintenance Status:** Active Development