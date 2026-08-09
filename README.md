<div align="center">
<img src="assets/logo.svg" width="340" alt="miri">
</div>

<br>

**miri** is a customer support platform that answers from a business's own documents instead of a fixed script. Point it at a company's policies, FAQs, and product catalog, and it holds a natural conversation — in whatever language the customer writes in — while staying strictly honest about what it actually knows.

It began as a small learning exercise: build a support bot for a fictional shoe store. It grew into something more useful — a platform where the business itself is a configuration detail, not something baked into the code. Change a company name, upload a new set of documents, and the same system serves a different business entirely.

A live instance is running now, standing in as a small retail brand with its own catalog and support documentation.

<div align="center">

**[Try the live demo →](https://ai-customer-support-playbook.onrender.com/chat-ui)**

[dashboard](https://ai-customer-support-playbook.onrender.com/dashboard) · [admin panel](https://ai-customer-support-playbook.onrender.com/admin)

[![License: MIT](https://img.shields.io/badge/License-MIT-16352a)](LICENSE)
![Python 3.8+](https://img.shields.io/badge/python-3.8+-5c4a30)
![Status](https://img.shields.io/badge/status-live-16352a)

<img src="assets/banner.svg" width="100%" alt="">

</div>

<br>

---

## The idea

Most support bots fail in one of two ways: they're either too rigid, refusing anything that isn't a verbatim match to a script, or too loose, confidently inventing answers about things they were never told. Neither builds trust.

miri draws a clear line. Ask it how its day is going, or something about the wider world, and it answers like any capable assistant would — no need to consult a document for that. Ask it something specific to the business — a return window, a shipping cost, whether a product exists — and it answers *only* from what it's actually been given. If the answer isn't there, it says so plainly, rather than guessing.

That distinction is the whole design.

---

## How it's built

A customer's message moves through a short pipeline, each stage with a fallback so the system never fails outright — it only ever gets a little simpler.

The message is first checked for language, then matched against the knowledge base through semantic search: an embedding model that understands meaning rather than exact wording, so "Is PayPal an option?" correctly surfaces a document titled "What payment methods do you accept?" If that search is unavailable for any reason, a keyword-based search steps in instead.

Alongside the current message, the system pulls in the ongoing conversation from a persistent store, so a question like "what if it doesn't arrive?" is understood in light of whatever was asked just before it — not as an isolated fragment.

That context — the retrieved documents, the conversation so far, and the detected language — is handed to a language model, instructed to answer only from what was retrieved when the topic calls for it, and to speak naturally otherwise. If no model is configured, or the call fails, the system falls back to returning the raw matched document rather than breaking.

```
message
  │
  ├─ language detected
  ├─ history loaded (SQLite)
  │
  ▼
semantic search ── unavailable ──▶ keyword search
  │
  ▼
language model, grounded in context ── unavailable ──▶ raw document fallback
  │
  ▼
response, logged for monitoring, open for feedback
```

The embedding step deserves a note of its own. Semantic search normally means loading a model into memory — several hundred megabytes, easily more than a free hosting tier allows. miri can instead call a hosted inference API for that single step, keeping the same search quality with almost no memory footprint on the server itself. It's a small architectural choice, but the kind that decides whether a project can actually run somewhere for free or not.

---

## What it does

**Understands, not just matches.** Semantic search over the knowledge base, with a keyword-based fallback when it isn't available.

**Speaks the customer's language.** Detects the language of each message — with a confidence threshold, so a short ambiguous phrase in English doesn't get mistaken for something else — and replies fluently in kind.

**Remembers the conversation.** History is persisted, not held only in memory, and a short follow-up is read in the context of what came before it.

**Recommends, when asked to.** A customer describing a need rather than asking a direct question — a budget, an occasion, a style — gets a proposed product with a price, not a request to rephrase.

**Learns from feedback.** Every response can be marked helpful or not, and that signal is tracked and summarized rather than discarded.

**Is administered, not just deployed.** A protected panel lets someone replace the knowledge base entirely, inspect any stored conversation, or remove one — without touching code.

**Shows its own health.** A live dashboard tracks request volume, response time, and how often the system relied on the language model versus its fallback.

---

## Built with

| | |
|---|---|
| API | FastAPI, Uvicorn |
| Language model | Groq, via an OpenAI-compatible interface |
| Semantic search | ChromaDB with Sentence Transformers — local, or through a hosted inference API |
| Fallback search | A small hand-written TF-IDF implementation |
| Persistence | SQLite |
| Packaging | Docker |
| Hosting | Render |

---

## Running it

```bash
git clone https://github.com/AdrianPovestca/Miri_customer-support.git
cd Miri_customer-support

python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
```

The `.env` file needs a language model key and, if using semantic search on a memory-constrained host, a Hugging Face token for the remote embedding path:

```dotenv
OPENAI_API_KEY=your-groq-key
OPENAI_BASE_URL=https://api.groq.com/openai/v1

USE_VECTOR_SEARCH=true
EMBEDDING_PROVIDER=remote
HF_API_TOKEN=your-hf-token

COMPANY_NAME=Miri
BUSINESS_TYPE=retail fashion store
```

Then run it:

```bash
cd src
uvicorn api:app --reload --port 8000
```

`/chat-ui` is the conversation itself; `/dashboard` shows how the system is performing; `/admin` manages what it knows.

A `docker compose up --build` works equally well, and a plain terminal interface is available through `python chatbot.py` for anyone who'd rather not open a browser at all.

---

## Where it stands

Every stage of the original plan is built and running: a knowledge base with a working retriever, a language model layered grounded on top of it, semantic search replacing keyword matching, a production-shaped API with monitoring and containerization, and the features that turn a working demo into something closer to a product — multiple languages, memory that survives a restart, a way to learn from feedback, and an interface for someone non-technical to manage it.

What's left is less about the system working and more about how far it could go: a persistent disk on hosting, so a redeploy doesn't reset stored conversation history; genuine multi-tenancy, so one deployment could serve several businesses at once instead of one; and using the feedback already being collected to actually refine how the assistant responds, rather than only displaying it.

---

<div align="center">
<sub>MIT licensed. Built to learn how far a small idea could be taken.</sub>
</div>