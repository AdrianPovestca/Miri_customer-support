# 🤖 AI Customer Support Playbook

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/status-in%20development-orange)

A practical open-source guide for building AI-powered customer support systems using Retrieval-Augmented Generation (RAG), semantic search, and modern support workflows.

This project demonstrates how to design and implement an intelligent customer support chatbot that retrieves relevant information from a knowledge base and uses an LLM to generate accurate, natural-sounding responses to customer queries.

## 🎯 Project Goals

This educational project demonstrates:

- 📚 **Knowledge Base Design** - Structure customer support documentation for optimal retrieval
- 🔍 **Semantic Search** - Move beyond keyword matching with TF-IDF ranking
- 🎯 **RAG Architecture** - Retrieve relevant documents and generate context-aware responses
- 📝 **Prompt Engineering** - Craft effective prompts for customer support scenarios
- ✅ **Best Practices** - Python development standards, testing, logging, and documentation
- 🚀 **LLM Integration** - Real AI-generated responses grounded in retrieved knowledge

## ✨ Features

- ✅ **Realistic Knowledge Base** - 11 markdown files covering account, orders, shipping, returns, refunds, payments, products, technical support, password reset, refund policy, and FAQ for an online shoe store
- ✅ **TF-IDF Retriever** - Text normalization, stop word removal, partial matching, relevance scoring
- ✅ **AI-Generated Responses** - Answers are written by an LLM, grounded strictly in the retrieved knowledge base content (not hallucinated)
- ✅ **Graceful Fallback** - If the LLM is unavailable, disabled, or the API call fails, the bot automatically falls back to template-based responses so it never breaks
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
│   ├── chatbot.py                 # Main CLI application entry point
│   ├── config.py                  # Configuration and environment settings
│   ├── logger.py                  # Structured logging setup
│   ├── models.py                  # Document data model
│   ├── document_loader.py         # Load documents from knowledge base
│   ├── retriever.py               # TF-IDF search and ranking
│   ├── responder.py               # AI-generated + template-based responses
│   └── prompts.py                 # Prompt templates and user-facing messages
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
| Search | TF-IDF + Text Processing | Relevance ranking and retrieval |
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

### Configure your `.env`

```
OPENAI_API_KEY=your-key-here
OPENAI_BASE_URL=https://api.groq.com/openai/v1
USE_AI_GENERATION=true
```

Leave `OPENAI_API_KEY` empty (or set `USE_AI_GENERATION=false`) to run the bot with template-only responses, no LLM required.

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
You: How do I reset my password?

Assistant:
To reset your password, follow these steps:
1. Navigate to the login page.
2. Select Forgot Password.
...
```

### Example Queries

**Account & Login**
- "How do I reset my password?"
- "Can I change my email address?"

**Orders & Shipping**
- "Can I track my order?"
- "How long does shipping take?"

**Returns & Refunds**
- "What is your return policy?"
- "Can I return items after 30 days?"

**Payments**
- "Do you accept PayPal?"
- "What payment methods do you accept?"

## 📊 How It Works

```
User Query
    ↓
[Text Normalization] → lowercase, remove punctuation, remove stop words
    ↓
[TF-IDF Retriever] → score and rank all knowledge base documents
    ↓
[Threshold Filter] → keep only results above MIN_SCORE_THRESHOLD
    ↓
[LLM Generation] → Groq writes a natural answer grounded in the top matches
    ↓                       ↓ (if this fails or is disabled)
    ↓                [Template Fallback] → return the matched document as-is
    ↓
Display Response
```

The system prompt instructs the LLM to answer **only** from the retrieved context and to say so honestly when it doesn't have the information, rather than inventing policies or prices.

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

### Phase 2: LLM Integration ✅ (mostly complete)
- [x] OpenAI-compatible API integration (via Groq, free tier)
- [x] Prompt engineering framework (`prompts.py`, grounded system prompt)
- [x] Response generation with automatic template fallback
- [ ] LangChain integration (not used — direct API calls kept it simpler)
- [ ] Context management (multi-turn conversation memory)

### Phase 3: Vector Search
- [ ] ChromaDB integration
- [ ] Sentence Transformers embeddings
- [ ] Semantic similarity scoring
- [ ] Embedding caching

### Phase 4: Production
- [ ] FastAPI REST API
- [ ] Docker containerization
- [ ] Performance optimization
- [ ] Monitoring and analytics

### Phase 5: Advanced Features
- [ ] Multi-language support
- [ ] Conversation history
- [ ] User feedback loop
- [ ] Analytics dashboard

## 💡 Key Learnings

This project teaches:
- **Information Retrieval** - TF-IDF, text normalization, ranking algorithms
- **RAG Patterns** - Document retrieval, context augmentation, grounded response generation
- **LLM Integration** - Calling an OpenAI-compatible API, prompt design, graceful degradation
- **Python Best Practices** - Type hints, docstrings, error handling, logging
- **Debugging** - Diagnosing import errors, environment variable loading, relevance thresholds

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Last Updated:** July 5, 2026
**Current Version:** 0.2.0
**Maintenance Status:** Active Development
