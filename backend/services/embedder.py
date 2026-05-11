"""
Embedder — uses HuggingFace InferenceClient (official SDK, handles auth correctly).
No local model loaded = no memory crash on Render free tier.
"""
import os, logging, hashlib

logger = logging.getLogger(__name__)

HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")
_cache: dict = {}


def embed_texts(texts: list[str], model_name: str = "") -> list[list[float]]:
    from huggingface_hub import InferenceClient
    import numpy as np

    client = InferenceClient(token=HF_API_TOKEN if HF_API_TOKEN else None)

    results, uncached_idx, uncached_texts = [], [], []
    for i, t in enumerate(texts):
        k = hashlib.md5(t.encode()).hexdigest()
        if k in _cache:
            results.append(_cache[k])
        else:
            results.append(None)
            uncached_idx.append(i)
            uncached_texts.append(t)

    for start in range(0, len(uncached_texts), 32):
        batch = uncached_texts[start:start + 32]
        raw = client.feature_extraction(
            batch,
            model="sentence-transformers/all-MiniLM-L6-v2",
        )
        # raw is numpy array shape (n_texts, n_tokens, hidden) or (n_texts, hidden)
        arr = raw if hasattr(raw, 'shape') else __import__('numpy').array(raw)
        if arr.ndim == 3:
            # Mean pool over tokens
            embs = arr.mean(axis=1).tolist()
        else:
            embs = arr.tolist()

        for idx, emb in zip(uncached_idx[start:start + 32], embs):
            _cache[hashlib.md5(texts[idx].encode()).hexdigest()] = emb
            results[idx] = emb

    return results


def embed_query(query: str, model_name: str = "") -> list[float]:
    return embed_texts([query])[0]