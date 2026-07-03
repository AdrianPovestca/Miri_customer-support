"""
Improved semantic search retriever using TF-IDF ranking.

This module implements document retrieval with:
- Text normalization (lowercase, punctuation removal)
- Stop word filtering
- Partial word matching
- TF-IDF scoring for relevance ranking
- Configurable result thresholds
"""

import logging
import re
from typing import List, Dict, Tuple
from collections import Counter
import math

from config import TOP_K_RESULTS, MIN_SCORE_THRESHOLD, STOP_WORDS
from document import Document
from document_loader import load_documents

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison.

    Performs:
    - Lowercase conversion
    - Punctuation removal
    - Multiple space reduction

    Args:
        text: Raw text to normalize

    Returns:
        Normalized text string
    """
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation and special characters, keep only alphanumeric and spaces
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    # Reduce multiple spaces to single space
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_and_filter(text: str) -> List[str]:
    """
    Tokenize text and remove stop words.

    Args:
        text: Normalized text to tokenize

    Returns:
        List of meaningful tokens (words)
    """
    words = text.split()
    # Filter out stop words
    filtered = [w for w in words if w not in STOP_WORDS and len(w) > 1]
    return filtered


def calculate_term_frequency(tokens: List[str]) -> Dict[str, float]:
    """
    Calculate term frequency for tokens.

    TF(term) = (count of term) / (total number of terms)

    Args:
        tokens: List of tokens

    Returns:
        Dictionary mapping terms to their frequencies
    """
    if not tokens:
        return {}

    counter = Counter(tokens)
    total = len(tokens)
    return {term: count / total for term, count in counter.items()}


def calculate_idf(documents: List[Document], term: str) -> float:
    """
    Calculate inverse document frequency for a term.

    IDF(term) = log(total documents / documents containing term)

    Args:
        documents: List of all documents
        term: Term to calculate IDF for

    Returns:
        IDF score for the term
    """
    if not documents:
        return 0.0

    # Count documents containing the term
    docs_with_term = 0
    for doc in documents:
        tokens = tokenize_and_filter(normalize_text(doc.content))
        if term in tokens:
            docs_with_term += 1

    # Avoid division by zero
    if docs_with_term == 0:
        return 0.0

    return math.log(len(documents) / docs_with_term)


def calculate_tfidf_score(
    query_tokens: List[str],
    document: Document,
    all_documents: List[Document],
) -> float:
    """
    Calculate TF-IDF score between query and document.

    TF-IDF = TF(term) * IDF(term) for all terms, then averaged

    Args:
        query_tokens: Processed query tokens
        document: Document to score
        all_documents: All documents in knowledge base

    Returns:
        TF-IDF relevance score (0.0 to 1.0)
    """
    if not query_tokens:
        return 0.0

    doc_tokens = tokenize_and_filter(normalize_text(document.content))
    if not doc_tokens:
        return 0.0

    # Calculate document term frequency
    doc_tf = calculate_term_frequency(doc_tokens)

    # Calculate TF-IDF score
    total_score = 0.0
    matched_terms = 0

    for term in query_tokens:
        if term in doc_tf:
            idf = calculate_idf(all_documents, term)
            tfidf = doc_tf[term] * idf
            total_score += tfidf
            matched_terms += 1

    # Normalize by number of matched terms to avoid length bias
    if matched_terms == 0:
        return 0.0

    # Normalize score to 0-1 range
    normalized_score = min(total_score / len(query_tokens), 1.0)
    return normalized_score


def search(query: str) -> List[Dict[str, any]]:
    """
    Search the knowledge base for documents matching the query.

    Performs:
    1. Text normalization and tokenization
    2. TF-IDF scoring against all documents
    3. Filtering by minimum threshold
    4. Ranking by score
    5. Returning top-k results

    Args:
        query: User search query

    Returns:
        List of result dicts with 'document' and 'score' keys,
        sorted by relevance (highest first)
    """
    logger.info(f"Searching for: {query}")

    # Normalize and tokenize query
    normalized_query = normalize_text(query)
    query_tokens = tokenize_and_filter(normalized_query)

    if not query_tokens:
        logger.warning("Query has no meaningful tokens after filtering")
        return []

    logger.debug(f"Query tokens: {query_tokens}")

    # Load documents
    documents = load_documents()
    if not documents:
        logger.warning("No documents available to search")
        return []

    # Score all documents
    results = []
    for document in documents:
        score = calculate_tfidf_score(query_tokens, document, documents)

        # Apply threshold
        if score > MIN_SCORE_THRESHOLD:
            results.append(
                {
                    "document": document,
                    "score": score,
                }
            )
            logger.debug(f"Matched {document.filename}: score={score:.4f}")

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    # Return top-k results
    top_results = results[:TOP_K_RESULTS]
    logger.info(f"Found {len(top_results)} results out of {len(results)} matches")

    return top_results


if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Test the retriever
    test_queries = [
        "How do I reset my password?",
        "What is the shipping cost?",
        "Can I return shoes after 30 days?",
    ]

    for test_query in test_queries:
        print(f"\nQuery: {test_query}")
        results = search(test_query)
        for result in results:
            print(f"  - {result['document'].filename}: {result['score']:.4f}")
