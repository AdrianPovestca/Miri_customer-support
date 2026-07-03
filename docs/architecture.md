# Architecture Guide

## System Overview

The AI Customer Support Playbook is a modular application designed to demonstrate RAG (Retrieval-Augmented Generation) patterns for customer support. The system follows a clean architecture approach with clear separation of concerns.

```
User Query
    ↓
[Document Loader] → Loads markdown files from knowledge_base/
    ↓
[Text Normalization] → Lowercase, remove punctuation, filter stop words
    ↓
[Tokenizer] → Split into meaningful tokens
    ↓
[TF-IDF Retriever] → Calculate relevance scores and rank documents
    ↓
[Response Formatter] → Format results for display
    ↓
Display Response
```

## Core Components

### 1. Document Loader (`document_loader.py`)

**Responsibility:** Load and parse markdown documents from the knowledge base

**Key Features:**
- Recursively reads all `.md` files from `knowledge_base/` directory
- Converts raw text into `Document` objects
- Handles encoding issues and file errors gracefully
- Logs all operations for debugging

**Data Model:**
```python
Document(
    title: str           # Document title (used for display)
    filename: str        # Source file name
    content: str         # Full document content
)
```

### 2. Text Processing Pipeline

#### Text Normalization (`retriever.py::normalize_text`)
- Converts text to lowercase
- Removes punctuation and special characters
- Reduces multiple spaces to single spaces
- Strips leading/trailing whitespace

#### Tokenization (`retriever.py::tokenize_and_filter`)
- Splits normalized text into words
- Removes stop words (common words like "the", "a", "is")
- Filters out very short tokens (<2 characters)
- Returns only meaningful terms

### 3. Retriever (`retriever.py`)

**Responsibility:** Semantic search using TF-IDF ranking

**Algorithm:**
1. **Term Frequency (TF):** How often a term appears in a document
   - `TF(term, doc) = count(term) / total_terms(doc)`

2. **Inverse Document Frequency (IDF):** How rare a term is across all documents
   - `IDF(term) = log(total_documents / documents_with_term)`

3. **TF-IDF Score:** Combined relevance metric
   - `TF-IDF(term, doc) = TF(term, doc) * IDF(term)`
   - Final score is normalized to 0-1 range

**Configuration:**
- `TOP_K_RESULTS`: Number of results to return (default: 3)
- `MIN_SCORE_THRESHOLD`: Minimum relevance score to include (default: 0.1)
- `STOP_WORDS`: Set of common words to filter

### 4. Response Formatter (`responder.py`)

**Responsibility:** Format search results for user display

**Features:**
- Returns the top-ranked document
- Includes relevance score
- Provides helpful message if no results found
- Formats output with markdown

### 5. Chatbot (`chatbot.py`)

**Responsibility:** Main application entry point

**Features:**
- Loads knowledge base
- Provides interactive chat interface
- Handles user input and queries
- Displays formatted responses
- Manages conversation flow

## Data Flow

### Search Query Flow

```
User Input: "How do I reset my password?"
    ↓
normalize_text() → "how do i reset my password"
    ↓
tokenize_and_filter() → ["reset", "password"]
    ↓
calculate_tfidf_score() for each document
    ↓
Results: [
    {document: account.md, score: 0.85},
    {document: returns.md, score: 0.42}
]
    ↓
generate_response() → Formatted markdown response
    ↓
Display to user
```

### Document Loading Flow

```
Application Startup
    ↓
load_documents() called
    ↓
Find all *.md files in knowledge_base/
    ↓
For each file:
    - Read file content
    - Create Document object
    - Add to list
    ↓
Return list of Document objects
    ↓
Ready for search
```

## Configuration

The `config.py` module centralizes all configuration:

```python
# Retriever settings
TOP_K_RESULTS = 3                    # Return top 3 results
MIN_SCORE_THRESHOLD = 0.1            # Filter results below 10%
STOP_WORDS = {...}                   # Common words to ignore

# Paths
KNOWLEDGE_BASE_DIR = "knowledge_base/"
DOCS_DIR = "docs/"
LOGS_DIR = "logs/"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/app.log"
```

## Logging Architecture

The application uses Python's built-in `logging` module with:

1. **File Handler:** Stores all logs in `logs/app.log` with rotation
   - Rotates when file reaches 10MB
   - Keeps up to 5 backup files
   - Records DEBUG level and above

2. **Console Handler:** Displays logs to terminal
   - Shows INFO level and above
   - Formatted with timestamp and level

3. **Log Levels:**
   - `DEBUG`: Detailed information for debugging
   - `INFO`: General informational messages
   - `WARNING`: Warning messages
   - `ERROR`: Error messages with traceback
   - `CRITICAL`: Critical failures

## Module Dependencies

```
chatbot.py (main entry point)
    ├── document_loader.py
    │   └── document.py
    ├── retriever.py
    │   ├── document_loader.py
    │   └── config.py
    ├── responder.py
    │   └── document.py
    ├── prompts.py
    └── logger.py

Tests
    ├── conftest.py (fixtures)
    ├── test_document_loader.py
    ├── test_retriever.py
    └── test_responder.py
```

## Extension Points

### Adding New Features

1. **Custom Search Algorithm:**
   - Modify `retriever.py::calculate_tfidf_score()`
   - Implement new ranking algorithm
   - Update tests in `test_retriever.py`

2. **Response Formatting:**
   - Extend `responder.py::generate_response()`
   - Add new formatting options
   - Update response tests

3. **New Knowledge Base:**
   - Add markdown files to `knowledge_base/`
   - Files are auto-loaded on startup
   - No code changes needed

4. **LLM Integration (Future):**
   - Add `llm_client.py` module
   - Integrate with OpenAI/Anthropic API
   - Modify `responder.py` to use LLM for generation
   - Keep retrieval logic unchanged

## Testing Architecture

Tests are organized by module:

- `test_document_loader.py`: Document loading and parsing
- `test_retriever.py`: Text processing, scoring, and ranking
- `test_responder.py`: Response formatting

Each test uses:
- Pytest fixtures for mock data
- Clear test names describing behavior
- Assertions on expected outcomes
- Edge case coverage

## Performance Considerations

### Current Implementation
- **Complexity:** O(n*m) where n=documents, m=query terms
- **Memory:** Stores all documents in memory
- **Scalability:** Works well for up to 10,000 documents

### Future Optimizations
- **Vector Embeddings:** Use pre-computed embeddings with ChromaDB
- **Semantic Search:** Leverage transformer models for better matching
- **Caching:** Cache search results for common queries
- **Async:** Non-blocking document loading and searching

## Security Considerations

1. **Input Validation:**
   - Text normalization prevents injection attacks
   - Stop word filtering removes malicious patterns

2. **File Handling:**
   - Whitelist markdown files only
   - Handle encoding errors safely

3. **Logging:**
   - No sensitive data in logs
   - Separate debug and production logs

## Future Roadmap

See roadmap.md for detailed feature plans.
