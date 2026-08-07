"""
diagnose.py
-----------
Run this to check every moving part at once, instead of debugging one
error at a time. Run from src/: python diagnose.py

Tests, in order:
1. Config loads correctly (keys present)
2. Groq/OpenAI connection actually works
3. Embedding provider (local or remote) actually works
4. Semantic search returns relevant results
5. Full response generation works end-to-end
"""

import sys

print("=" * 60)
print("DIAGNOSTIC CHECK")
print("=" * 60)

results = []

def check(name, fn):
    try:
        fn()
        print(f"✅ {name}")
        results.append(True)
    except Exception as e:
        print(f"❌ {name}")
        print(f"   Error: {e}")
        results.append(False)


# --- 1. Config ---
def check_config():
    from config import OPENAI_API_KEY, EMBEDDING_PROVIDER, HF_API_TOKEN, USE_VECTOR_SEARCH, USE_AI_GENERATION
    print(f"   OPENAI_API_KEY set: {bool(OPENAI_API_KEY)}")
    print(f"   USE_AI_GENERATION: {USE_AI_GENERATION}")
    print(f"   USE_VECTOR_SEARCH: {USE_VECTOR_SEARCH}")
    print(f"   EMBEDDING_PROVIDER: {EMBEDDING_PROVIDER}")
    print(f"   HF_API_TOKEN set: {bool(HF_API_TOKEN)}")
    assert OPENAI_API_KEY, "OPENAI_API_KEY is empty"

check("Config loads with keys present", check_config)


# --- 2. Groq connection ---
def check_groq():
    from config import OPENAI_API_KEY, OPENAI_BASE_URL, DEFAULT_MODEL
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    completion = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": "Say 'ok' and nothing else."}],
        max_tokens=10,
    )
    reply = completion.choices[0].message.content
    print(f"   Groq replied: {reply!r}")

check("Groq/OpenAI API connection works", check_groq)


# --- 3. Embedding provider ---
def check_embeddings():
    from config import EMBEDDING_PROVIDER, HF_API_TOKEN, EMBEDDING_MODEL
    if EMBEDDING_PROVIDER == "remote":
        import requests
        url = f"https://router.huggingface.co/hf-inference/models/sentence-transformers/{EMBEDDING_MODEL}/pipeline/feature-extraction"
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
            json={"inputs": ["test"], "options": {"wait_for_model": True}},
            timeout=30,
        )
        print(f"   HF API status: {resp.status_code}")
        resp.raise_for_status()
        embedding = resp.json()
        print(f"   Got embedding of length: {len(embedding[0]) if embedding else 'empty'}")
    else:
        print("   Using local embedding model (loads sentence-transformers directly)")

check("Embedding provider (remote/local) works", check_embeddings)


# --- 4. Semantic search ---
def check_search():
    from embeddings import semantic_search
    results = semantic_search("Do you offer international shipping?")
    print(f"   Got {len(results)} result(s)")
    for r in results[:3]:
        print(f"     - {r['document'].filename}: {r['score']:.4f}")
    assert results, "No results returned at all"
    assert any("shipping" in r['document'].filename.lower() for r in results), \
        "shipping.md not found in top results"

check("Semantic search finds relevant results", check_search)


# --- 5. Full response generation ---
def check_full_response():
    from embeddings import semantic_search
    from responder import generate_response_with_meta
    results = semantic_search("Do you offer international shipping?")
    text, used_ai = generate_response_with_meta(results, "Do you offer international shipping?", [])
    print(f"   used_ai_generation: {used_ai}")
    print(f"   Response: {text[:150]}...")
    assert used_ai, "Fell back to template instead of using AI"

check("Full response generation (search + AI)", check_full_response)


print("=" * 60)
passed = sum(results)
total = len(results)
print(f"RESULT: {passed}/{total} checks passed")
print("=" * 60)

if passed < total:
    sys.exit(1)