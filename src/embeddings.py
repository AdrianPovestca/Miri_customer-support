"""
embeddings.py
-------------
Phase 3: Vector Search.

Builds a semantic (embedding-based) search index over the knowledge base
using ChromaDB + Sentence Transformers, as an alternative to the TF-IDF
retriever in retriever.py.

Unlike the TF-IDF retriever (which treats each whole .md file as one
document), this module splits each file into individual Q&A chunks, so
matching is much more precise.

If chromadb / sentence-transformers aren't installed, or anything goes
wrong building/querying the index, callers should catch the exception and
fall back to retriever.search() (TF-IDF). This module never silently
returns wrong results — it either works correctly or raises.
"""

import logging
import re
from pathlib import Path
from typing import List, Dict

from config import KNOWLEDGE_BASE_DIR, EMBEDDING_MODEL, CHROMA_PERSIST_DIR, TOP_K_RESULTS
from models import Document

logger = logging.getLogger(__name__)

CATEGORY_PATTERN = re.compile(r"^#\s+(.+)$", re.MULTILINE)
QA_PATTERN = re.compile(r"^##\s+(.+?)\n(.*?)(?=^##\s+|\Z)", re.MULTILINE | re.DOTALL)

_collection = None  # lazily initialized, cached for the lifetime of the process


def _chunk_knowledge_base() -> List[Document]:
    """
    Split every markdown file into one Document per Q&A entry, instead of
    one Document per file. This gives the embedding model much more
    precise, focused text to match against.
    """
    chunks: List[Document] = []
    md_files = sorted(Path(KNOWLEDGE_BASE_DIR).glob("*.md"))

    for path in md_files:
        text = path.read_text(encoding="utf-8")
        category_match = CATEGORY_PATTERN.search(text)
        category = category_match.group(1).strip() if category_match else path.stem.title()

        found_any = False
        for match in QA_PATTERN.finditer(text):
            question = match.group(1).strip()
            answer = match.group(2).strip()
            if question and answer:
                found_any = True
                chunks.append(
                    Document(
                        title=question,
                        filename=path.name,
                        content=f"{category} — {question}\n{answer}",
                    )
                )

        # Fallback: if a file has no "## Question" headings, index it whole
        if not found_any:
            chunks.append(Document(title=path.stem, filename=path.name, content=text))

    return chunks


def _get_collection():
    """
    Get (or lazily build) the ChromaDB collection. The collection is
    persisted to disk under CHROMA_PERSIST_DIR, so embeddings are only
    computed once and reused across runs (embedding caching).
    """
    global _collection
    if _collection is not None:
        return _collection

    import chromadb
    from chromadb.utils import embedding_functions

    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

    client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))
    collection = client.get_or_create_collection(
        name="knowledge_base",
        embedding_function=embedding_fn,
    )

    # Build the index only if it's empty (cached across runs otherwise).
    if collection.count() == 0:
        logger.info("Building vector index for the first time (this may take a moment)...")
        chunks = _chunk_knowledge_base()
        collection.add(
            ids=[f"{doc.filename}-{i}" for i, doc in enumerate(chunks)],
            documents=[doc.content for doc in chunks],
            metadatas=[{"title": doc.title, "filename": doc.filename} for doc in chunks],
        )
        logger.info(f"Vector index built with {len(chunks)} chunks.")
    else:
        logger.info(f"Reusing cached vector index ({collection.count()} chunks).")

    _collection = collection
    return _collection


def semantic_search(query: str, top_k: int = None) -> List[Dict]:
    """
    Search the knowledge base using semantic (embedding-based) similarity.

    Args:
        query: The user's question.
        top_k: Number of results to return (defaults to config.TOP_K_RESULTS).

    Returns:
        List of {"document": Document, "score": float} — same shape as
        retriever.search(), so it's a drop-in alternative. Score is a
        similarity score in roughly [0, 1], higher = more relevant.
    """
    top_k = top_k or TOP_K_RESULTS
    collection = _get_collection()

    results = collection.query(query_texts=[query], n_results=top_k)

    output = []
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for content, meta, distance in zip(documents, metadatas, distances):
        # Chroma returns a distance (lower = more similar); convert to a
        # 0-1 similarity score so it's comparable in spirit to TF-IDF scores.
        similarity = 1.0 / (1.0 + distance)
        output.append({
            "document": Document(
                title=meta.get("title", ""),
                filename=meta.get("filename", ""),
                content=content,
            ),
            "score": similarity,
        })

    return output


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

    test_queries = [
        "How do I reset my password?",
        "Can I track my order?",
        "Do you take PayPal?",
    ]
    for q in test_queries:
        print(f"\nQuery: {q}")
        for r in semantic_search(q):
            print(f"  - {r['document'].filename} ({r['document'].title}): {r['score']:.4f}")