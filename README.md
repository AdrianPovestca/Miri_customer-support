# 🤖 AI Customer Support Playbook

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Status: In Development](https://img.shields.io/badge/status-in%20development-orange.svg)](#-project-status)

> A practical open-source guide for building AI-powered customer support systems using Retrieval-Augmented Generation (RAG), semantic search, and modern support workflows.

This project demonstrates how to design and implement an intelligent customer support chatbot that can retrieve relevant information from a knowledge base and provide accurate, helpful responses to customer queries.

## 🎯 Project Goals

This educational project demonstrates:

- 📚 **Knowledge Base Design** - Structure customer support documentation for optimal retrieval
- 🔍 **Semantic Search** - Move beyond keyword matching with TF-IDF ranking
- 🎯 **RAG Architecture** - Retrieve relevant documents and generate context-aware responses
- 📝 **Prompt Engineering** - Craft effective prompts for customer support scenarios
- ✅ **Best Practices** - Python development standards, testing, logging, and documentation
- 🚀 **Scalability** - Foundation for integration with LLMs and production systems

## ✨ Features

- ✅ **Realistic Knowledge Base** - 9 comprehensive markdown files with 200+ Q&A pairs for an online shoe store
- ✅ **Improved Retriever** - TF-IDF ranking, text normalization, stop word removal, partial matching
- ✅ **Comprehensive Testing** - pytest suite with 30+ tests covering all core modules
- ✅ **Professional Logging** - Structured logging for debugging and monitoring
- ✅ **Clean Architecture** - Modular design following Python best practices
- ✅ **Rich Documentation** - Architecture guide, development setup, contributing guidelines
- ✅ **Command-Line Interface** - Interactive chatbot for testing and demonstration

## 📁 Folder Structure

```
ai-customer-support-playbook/
├── docs/                          # Project documentation
│   ├── architecture.md            # System design and component overview
│   ├── development.md             # Development setup and guidelines
│   ├── contributing.md            # How to contribute to the project
│   └── roadmap.md                 # Feature roadmap and future plans
├── knowledge_base/                # Customer support documentation
│   ├── account.md                 # Account management Q&A
│   ├── orders.md                  # Order management Q&A
│   ├── shipping.md                # Shipping information Q&A
│   ├── returns.md                 # Returns and exchanges Q&A
│   ├── refunds.md                 # Refunds and credits Q&A
│   ├── payments.md                # Payment and billing Q&A
│   ├── products.md                # Products and sizing Q&A
│   ├── technical.md               # Technical support Q&A
│   └── faq.md                     # Frequently asked questions
├── src/                           # Source code
│   ├── __init__.py
│   ├── chatbot.py                 # Main CLI application entry point
│   ├── config.py                  # Configuration and environment settings
│   ├── logger.py                  # Structured logging setup
│   ├── document.py                # Document data model
│   ├── document_loader.py         # Load documents from knowledge base
│   ├── retriever.py               # Semantic search with TF-IDF ranking
│   ├── responder.py               # Format and return responses
│   └── prompts.py                 # Prompt templates for the assistant
├── tests/                         # Pytest test suite
│   ├── conftest.py                # Pytest fixtures and configuration
│   ├── test_document_loader.py    # Tests for document loading
│   ├── test_retriever.py          # Tests for search and ranking
│   └── test_responder.py          # Tests for response formatting
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
├── README.md                      # This file
└── LICENSE                        # MIT License

```

## 🛠 Technologies Used

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.8+ | Core implementation language |
| **Framework** | FastAPI | (Planned) REST API for production |
| **Search** | TF-IDF + Text Processing | Semantic ranking and retrieval |
| **Testing** | pytest | Unit and integration tests |
| **Logging** | Python logging | Structured logging and debugging |
| **Environment** | python-dotenv | Configuration management |
| **Validation** | Pydantic | Data validation and types |
| **Future** | LangChain | LLM integration and orchestration |
| **Future** | ChromaDB | Vector database for embeddings |
| **Future** | Sentence Transformers | Semantic embeddings |
| **Future** | OpenAI API | LLM-powered responses |

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/AdrianPovestca/ai-customer-support-playbook.git
   cd ai-customer-support-playbook
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file if needed
   ```

5. **Verify installation**
   ```bash
   python -m pytest tests/ -v
   ```

## 🚀 Usage

### Running the Chatbot

Start the interactive customer support chatbot:

```bash
cd src
python chatbot.py
```

You'll see output like:
```
==================================================
🤖 AI Customer Support Playbook
==================================================

Knowledge base loaded: 9 document(s)

• account.md
• orders.md
• shipping.md
• returns.md
• refunds.md
• payments.md
• products.md
• technical.md
• faq.md

--------------------------------------------------
Hello! 👋

How can I help you today?

You: How do I reset my password?
```

### Example Queries

Try asking these customer support questions:

**Account & Login**
- "How do I reset my password?"
- "Can I change my email address?"
- "How do I enable two-factor authentication?"

**Orders & Shipping**
- "How long does shipping take?"
- "Can I track my order?"
- "What shipping options are available?"

**Returns & Refunds**
- "What is your return policy?"
- "How long does a refund take?"
- "Can I return items after 30 days?"

**Products & Sizing**
- "What shoe brands do you carry?"
- "How do I find my shoe size?"
- "Do you have wide-size shoes?"

**Payments**
- "What payment methods do you accept?"
- "Is it safe to pay online?"
- "Do you offer payment plans?"

### Running Tests

Execute the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_retriever.py -v

# Run specific test
pytest tests/test_retriever.py::test_search_keyword_matching -v
```

### Viewing Logs

Logs are written to `logs/app.log` with both file and console output:

```bash
tail -f logs/app.log
```

## 📊 How It Works

### Architecture Overview

```
User Query
    ↓
[Text Normalization]
    ↓
[Document Loader] → Load markdown files from knowledge_base/
    ↓
[TF-IDF Retriever] → Search and rank documents
    ↓
[Result Formatter] → Format response for user
    ↓
Display Response
```

### Retrieval Process

1. **Load Documents** - Read all markdown files from `knowledge_base/`
2. **Normalize Query** - Convert to lowercase, remove punctuation, remove stop words
3. **Calculate TF-IDF Scores** - Rank documents by relevance
4. **Apply Threshold** - Filter low-scoring results
5. **Return Top Results** - Return top-k highest scoring documents
6. **Format Response** - Present results in user-friendly format

### Document Structure

Each markdown file in `knowledge_base/` follows this format:

```markdown
# Category Title

## Question 1?

Answer to question 1 with detailed information.

## Question 2?

Answer to question 2 with detailed information.
```

The system extracts Q&A pairs from these markdown files for semantic searching.

## 🧪 Testing

The project includes a comprehensive test suite:

- **30+ unit tests** covering all core modules
- **Fixtures** for mock documents and test data
- **Edge case testing** for search, ranking, and formatting
- **Coverage reports** for code quality metrics

### Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── test_document_loader.py  # Document loading tests
├── test_retriever.py        # Search and ranking tests
└── test_responder.py        # Response formatting tests
```

Run tests with coverage:
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` folder:

- **[Architecture Guide](docs/architecture.md)** - System design, components, and data flow
- **[Development Guide](docs/development.md)** - Setup, coding standards, and workflow
- **[Contributing Guide](docs/contributing.md)** - How to contribute to the project
- **[Roadmap](docs/roadmap.md)** - Planned features and enhancements

## 🗺️ Roadmap

### Phase 1: Foundation ✅
- [x] Project structure
- [x] Knowledge base with realistic Q&A
- [x] TF-IDF retriever with text processing
- [x] Comprehensive tests
- [x] Logging system
- [x] Documentation

### Phase 2: LLM Integration (In Progress)
- [ ] LangChain integration
- [ ] OpenAI API integration
- [ ] Prompt engineering framework
- [ ] Response generation
- [ ] Context management

### Phase 3: Vector Search
- [ ] ChromaDB integration
- [ ] Sentence Transformers embeddings
- [ ] Semantic search
- [ ] Similarity scoring
- [ ] Embedding caching

### Phase 4: Production
- [ ] FastAPI REST API
- [ ] Docker containerization
- [ ] Performance optimization
- [ ] Monitoring and analytics
- [ ] Production deployment guide

### Phase 5: Advanced Features
- [ ] Multi-language support
- [ ] Conversation history
- [ ] User feedback loop
- [ ] Analytics dashboard
- [ ] Admin interface

## 💡 Key Learnings

This project teaches:

1. **Information Retrieval** - TF-IDF, text normalization, ranking algorithms
2. **Python Best Practices** - Type hints, docstrings, error handling, logging
3. **Software Testing** - Unit tests, fixtures, mocking, coverage
4. **Documentation** - README, architecture guides, API documentation
5. **RAG Patterns** - Document retrieval, context augmentation, response generation
6. **Clean Code** - Modularity, separation of concerns, maintainability

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/contributing.md) for guidelines on:

- How to report issues
- How to submit pull requests
- Code style and standards
- Testing requirements
- Documentation standards

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Support

- 📚 Check the [FAQ](docs/faq.md) for common questions
- 🐛 Open an issue for bug reports
- 💬 Start a discussion for feature requests
- 📖 Read the documentation in `docs/`

## 🎓 Learning Resources

For deeper understanding of the concepts used in this project:

- **TF-IDF Ranking** - [Wikipedia: Tf–idf](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)
- **RAG Pattern** - [Lewis et al. 2020: Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401)
- **Python Logging** - [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- **pytest Best Practices** - [pytest Documentation](https://docs.pytest.org/)

## 🙏 Acknowledgments

- Open source community for excellent libraries and tools
- Contributors and reviewers
- Inspired by modern RAG-based systems in production

---

**Last Updated:** July 3, 2026  
**Current Version:** 0.2.0  
**Maintenance Status:** Active Development
