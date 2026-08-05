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

Embedding provider:
- "local" (default): loads the sentence-transformers model directly into
  this process. Needs ~500MB+ RAM — fine for Codespaces/local dev, but can
  exceed the memory limit on small free hosting tiers (e.g. Render's 512MB
  free plan), causing the process to be killed.
- "remote": calls Hugging Face's free Inference API instead, via a small
  custom embedding function (not chromadb's built-in one, which pointed at
  an outdated endpoint). Same model, same search quality, near-zero RAM
  footprint on this server. Requires HF_API_TOKEN (free, from
  huggingface.co/settings/tokens).

If chromadb / sentence-transformers aren't installed, or anything goes
wrong building/querying the index, callers should catch the exception and
fall back to retriever.search() (TF-IDF).
"""

import logging
import re
from pathlib import Path
from typing import List, Dict

from config import (
    KNOWLEDGE_BASE_DIR, EMBEDDING_MODEL, CHROMA_PERSIST_DIR, TOP_K_RESULTS,
    EMBEDDING_PROVIDER, HF_API_TOKEN,
)
from models import Document

logger = logging.getLogger(__name__)

CATEGORY_PATTERN = re.compile(r"^#\s+(.+)$", re.MULTILINE)
QA_PATTERN = re.compile(r"^##\s+(.+?)\n(.*?)(?=^##\s+|\Z)", re.MULTILINE | re.DOTALL)

_collection = None  # lazily initialized, cached for the lifetime of the process


class _RemoteHFEmbeddingFunction:
    """
    Minimal, self-contained Hugging Face Inference API embedding function.
    Written directly (rather than relying on chromadb's built-in wrapper)
    for full control over the endpoint and error handling.
    """

    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"

    def name(self) -> str:
        return "remote-hf-embedding-function"

    def __call__(self, input):
        import requests

        response = requests.post(
            self.api_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"inputs": input, "options": {"wait_for_model": True}},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()


def _chunk_knowledge_base() -> List[Document]:
    """
    Split every markdown file into one Document per Q&A entry, instead of
    one Document per file. This gives the embedding model much more
    precise, focused text to match against.
    """
    chunks: List[Document] = []
    md_files = sorted(Path(KNOWLEDGE_BASE_DIR).glob("*.md")) + sorted(Path(KNOWLEDGE_BASE_DIR).glob("*.txt"))

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

        if not found_any:
            chunks.append(Document(title=path.stem, filename=path.name, content=text))

    return chunks


def _build_embedding_function():
    """Choose local vs. remote embedding computation based on EMBEDDING_PROVIDER."""
    if EMBEDDING_PROVIDER == "remote" and HF_API_TOKEN:
        logger.info(f"Using remote Hugging Face Inference API for embeddings ({EMBEDDING_MODEL})")
        return _RemoteHFEmbeddingFunction(
            api_key=HF_API_TOKEN,
            model_name=f"sentence-transformers/{EMBEDDING_MODEL}",
        )

    if EMBEDDING_PROVIDER == "remote" and not HF_API_TOKEN:
        logger.warning(
            "EMBEDDING_PROVIDER=remote but HF_API_TOKEN is not set — "
            "falling back to loading the model locally."
        )

    from chromadb.utils import embedding_functions
    logger.info(f"Loading local sentence-transformers model ({EMBEDDING_MODEL})")
    return embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)


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

    embedding_fn = _build_embedding_function()

    client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))
    collection = client.get_or_create_collection(
        name="knowledge_base",
        embedding_function=embedding_fn,
    )

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

    Returns:
        List of {"document": Document, "score": float} — same shape as
        retriever.search(), so it's a drop-in alternative.
    """
    top_k = top_k or TOP_K_RESULTS
    collection = _get_collection()

    results = collection.query(query_texts=[query], n_results=top_k)

    output = []
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for content, meta, distance in zip(documents, metadatas, distances):
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


def rebuild_index() -> int:
    """
    Delete and rebuild the vector index from whatever files currently exist
    in knowledge_base/. Call this after uploading, replacing, or deleting
    knowledge base documents, or after switching EMBEDDING_PROVIDER.

    Returns the number of chunks indexed.
    """
    global _collection
    import chromadb

    client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))
    try:
        client.delete_collection("knowledge_base")
    except Exception:
        pass

    _collection = None
    collection = _get_collection()
    return collection.count()


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