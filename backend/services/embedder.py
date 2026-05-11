import os, logging, hashlib, httpx

logger = logging.getLogger(__name__)

HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")
HF_MODEL_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"

_cache: dict[str, list[float]] = {}

def _cache_key(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()

def embed_texts(texts: list[str], model_name: str = "") -> list[list[float]]:
    results, uncached_indices, uncached_texts = [], [], []
    for i, t in enumerate(texts):
        k = _cache_key(t)
        if k in _cache:
            results.append(_cache[k])
        else:
            results.append(None)
            uncached_indices.append(i)
            uncached_texts.append(t)

    for start in range(0, len(uncached_texts), 32):
        batch = uncached_texts[start:start + 32]
        headers = {"Authorization": f"Bearer {HF_API_TOKEN}"} if HF_API_TOKEN else {}
        resp = httpx.post(
            HF_MODEL_URL, headers=headers,
            json={"inputs": batch, "options": {"wait_for_model": True}},
            timeout=60.0
        )
    resp.raise_for_status()
    data = resp.json()

    # /models/ endpoint returns list of lists (one per input) — handle both formats
    if isinstance(data[0][0], list):
        # Returns [[[token embeddings]]] — mean pool across tokens
        import numpy as np
        embs = [list(np.mean(d, axis=0)) for d in data]
    else:
        embs = data  # Already sentence embeddings

    return results

def embed_query(query: str, model_name: str = "") -> list[float]:
    return embed_texts([query])[0]