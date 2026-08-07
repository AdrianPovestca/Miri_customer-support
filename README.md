<div align="center">

# miri

**An AI customer support platform that learns from your business — not a fixed script.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/status-live-brightgreen)
[![Live Demo](https://img.shields.io/badge/demo-live-16352a)](https://ai-customer-support-playbook.onrender.com/chat-ui)

[Live Demo](https://ai-customer-support-playbook.onrender.com/chat-ui) · [Dashboard](https://ai-customer-support-playbook.onrender.com/dashboard) · [Admin Panel](https://ai-customer-support-playbook.onrender.com/admin)

</div>

---

## What is this?

**miri** is a Retrieval-Augmented Generation (RAG) customer support platform. Point it at a business's own documents — policies, FAQs, product catalogs — and it answers customer questions naturally, in whatever language they write in, while staying honest about what it doesn't know.

It started as a learning project (build a support bot for a demo shoe store) and grew into something more useful: a **business-agnostic platform**. Swap the knowledge base, set a company name, and the same codebase serves a completely different business — no code changes required.

A live instance is running right now, configured as a fictional retail brand, with a small product catalog (boots, apparel) and a full support knowledge base (shipping, returns, payments, account help). Try it: **[ai-customer-support-playbook.onrender.com/chat-ui](https://ai-customer-support-playbook.onrender.com/chat-ui)**

---

## Why it's not just "another chatbot wrapper"

- **It's honest.** The system prompt draws a hard line: casual conversation and general knowledge get answered naturally, but anything specific to the business (prices, policies, procedures) comes *only* from the uploaded documents. If the answer isn't there, it says so — it doesn't invent a return policy.
- **It's business-agnostic.** `COMPANY_NAME` and `BUSINESS_TYPE` are just environment variables. The knowledge base is fully swappable through the admin panel — no redeploy needed.
- **It's memory-conscious.** Semantic search normally requires loading an embedding model into RAM. On a free-tier server with 512MB total, that's not viable — so embeddings can be computed via a remote API instead, keeping full search quality with near-zero local memory footprint.
- **It degrades gracefully, everywhere.** No AI key configured? Falls back to template answers. Vector search unavailable? Falls back to TF-IDF. Nothing breaks; it just gets a little simpler.

---

## Features

| | |
|---|---|
| 🔍 **Semantic Search** | ChromaDB + Sentence Transformers understand meaning, not just keywords — "Is PayPal an option?" correctly matches "What payment methods do you accept?" |
| 🌍 **Multi-Language** | Detects the customer's language (confidence-gated, to avoid misfires on short text) and replies fluently in it — tested in English, Romanian, German, Russian |
| 💬 **Conversation Memory** | Persisted to SQLite; understands follow-ups ("What if it doesn't arrive?") using prior context, not just the current message |
| 🛍️ **Product Recommendations** | When a customer describes a need ("boots for everyday wear, budget $150") instead of asking a direct question, it proactively recommends a matching product with price |
| 👍 **Feedback Loop** | Every response can be rated helpful/not helpful; tracked and summarized for review |
| 📊 **Live Dashboard** | Auto-refreshing view of request volume, response times, AI vs. fallback rate, and satisfaction rate |
| 🔐 **Admin Panel** | Upload/replace/delete knowledge base files (auto-reindexes), browse and manage stored conversations — token-protected |
| 🐳 **Dockerized** | One command to run anywhere: `docker compose up --build` |
| 🚀 **REST API** | FastAPI-based, with a plain browser chat UI (`/chat-ui`) for non-technical use |

---

## Try it

**[→ Open the live chat](https://ai-customer-support-playbook.onrender.com/chat-ui)**

Some things to try:
- *"How do I reset my password?"* — grounded knowledge base answer
- *"Cum îmi resetez parola?"* — same question, in Romanian
- *"I need boots for everyday wear, budget around $150"* — proactive product recommendation
- *"How are you?"* — natural small talk, not a rigid refusal

> **Note:** the free hosting tier spins down after inactivity — the first request after a while may take 20–30 seconds to wake up.

---

## Architecture

```
Customer message
      │
      ▼
┌─────────────────┐     ┌──────────────────────┐
│ Language         │     │ Conversation history  │
│ detection        │     │ (SQLite, persisted)   │
└────────┬─────────┘     └──────────┬───────────┘
         │                          │
         ▼                          ▼
┌──────────────────────────────────────────────┐
│  Semantic search (remote embeddings via HF)   │
│  ──── falls back to ────                      │
│  TF-IDF keyword search                        │
└────────────────────┬───────────────────────────┘
                      ▼
┌──────────────────────────────────────────────┐
│  LLM generation (Groq, OpenAI-compatible)     │
│  grounded in retrieved context + history      │
│  ──── falls back to ────                      │
│  Raw knowledge base template                  │
└────────────────────┬───────────────────────────┘
                      ▼
              Response + feedback prompt
                      │
                      ▼
              Analytics (timing, AI vs. fallback)
```

Every layer has a fallback. The bot never hard-fails — it just gets simpler.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| LLM | Groq (OpenAI-compatible API) |
| Semantic Search | ChromaDB + Sentence Transformers (local or via Hugging Face Inference API) |
| Keyword Search Fallback | TF-IDF (scikit-learn-style, hand-rolled) |
| Language Detection | langdetect |
| Persistence | SQLite |
| Containerization | Docker + Docker Compose |
| Hosting | Render |
| Testing | pytest |

---

## Running it yourself

### Prerequisites
Python 3.8+, pip, Git.

### Setup

```bash
git clone https://github.com/AdrianPovestca/Miri_ai-customer-support.git
cd Miri_ai-customer-support

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
```

### Configure `.env`

```dotenv
# LLM (Groq's free tier works well)
OPENAI_API_KEY=your-groq-key
OPENAI_BASE_URL=https://api.groq.com/openai/v1
USE_AI_GENERATION=true

# Semantic search
USE_VECTOR_SEARCH=true
# "local" loads the model directly (needs ~500MB RAM).
# "remote" calls Hugging Face's free Inference API instead — use this on
# small hosts. Needs a free token with "Inference" scope.
EMBEDDING_PROVIDER=remote
HF_API_TOKEN=your-hf-token

# Business identity — change these to deploy for a different business
COMPANY_NAME=Miri
BUSINESS_TYPE=retail fashion store

# Admin panel protection (leave empty for open access during local dev)
ADMIN_TOKEN=
```

### Run

```bash
cd src
uvicorn api:app --reload --port 8000
```

Then open:
- `http://localhost:8000/chat-ui` — chat interface
- `http://localhost:8000/dashboard` — analytics
- `http://localhost:8000/admin` — manage knowledge base & conversations

Or, with Docker:

```bash
docker compose up --build
```

### CLI mode

```bash
cd src
python chatbot.py
```

---

## Deploying to production

This repo deploys as-is to any platform that runs a `Dockerfile` (Render, Fly.io, Railway). On the free tier of most hosts, set `EMBEDDING_PROVIDER=remote` — loading the embedding model locally can exceed a 512MB memory limit and get the process killed.

The live demo runs on [Render](https://render.com)'s free web service tier.

---

## Project structure

```
Miri_ai-customer-support/
├── src/
│   ├── api.py                 # FastAPI app: chat, dashboard, admin, feedback
│   ├── chatbot.py              # CLI entry point
│   ├── static/
│   │   ├── chat.html           # Browser chat UI
│   │   ├── dashboard.html      # Analytics dashboard
│   │   └── admin.html          # Admin panel (KB upload, conversation browser)
│   ├── embeddings.py           # Semantic search (local or remote HF embeddings)
│   ├── retriever.py            # TF-IDF fallback search
│   ├── responder.py            # Response generation (AI + template fallback)
│   ├── prompts.py              # System prompt, business-agnostic
│   ├── language.py             # Language detection
│   ├── feedback.py             # Feedback storage & summary
│   ├── analytics.py            # Request monitoring
│   ├── database.py             # Persistent conversation history (SQLite)
│   ├── document_loader.py
│   ├── models.py
│   ├── config.py
│   └── logger.py
├── knowledge_base/              # Swappable per business — currently a demo retail catalog
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Roadmap (complete)

- [x] **Foundation** — knowledge base, TF-IDF retriever, tests, logging
- [x] **LLM Integration** — Groq, grounded prompting, conversation memory
- [x] **Vector Search** — ChromaDB + Sentence Transformers, local or remote
- [x] **Production** — REST API, Docker, monitoring dashboard, live deployment
- [x] **Advanced Features** — multi-language, persistent history, feedback loop, admin panel, product recommendations

## What's next

- Persistent disk on hosting (current free tier resets on redeploy)
- Multi-tenant support (multiple businesses on one deployment)
- A/B testing prompt variations against feedback data

---

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">
<sub>Built as a learning project, shipped as a working product.</sub>
</div>