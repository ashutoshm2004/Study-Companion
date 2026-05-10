"""ChromaDB wrapper — one collection per document."""
import logging
from datetime import datetime
from pathlib import Path

import chromadb
from chromadb.config import Settings

from config import CHROMA_PERSIST_DIR

logger = logging.getLogger(__name__)
_client = None


def _get_client():
    global _client
    if _client is None:
        Path(CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False),
        )
    return _client


def _col_name(document_id: str) -> str:
    return f"doc_{document_id}"


def store_chunks(document_id: str, chunks: list[dict], embeddings: list[list[float]], filename: str):
    client = _get_client()
    name = _col_name(document_id)
    try:
        client.delete_collection(name)
    except Exception:
        pass
    col = client.create_collection(
        name=name,
        metadata={"filename": filename, "uploaded_at": datetime.utcnow().isoformat(), "num_chunks": len(chunks)},
    )
    col.add(
        ids=[f"chunk_{i}" for i in range(len(chunks))],
        documents=[c["text"] for c in chunks],
        embeddings=embeddings,
        metadatas=[{"page": c.get("page", 1), "chunk_index": c.get("chunk_index", i)} for i, c in enumerate(chunks)],
    )
    logger.info(f"Stored {len(chunks)} chunks for doc {document_id}")


def retrieve_chunks(document_id: str, query_embedding: list[float], top_k: int = 5) -> list[dict]:
    col = _get_client().get_collection(_col_name(document_id))
    n = min(top_k, col.count())
    if n == 0:
        return []
    res = col.query(query_embeddings=[query_embedding], n_results=n, include=["documents", "metadatas", "distances"])
    return [
        {"text": t, "page": m.get("page", 1), "relevance_score": round(max(0.0, 1.0 - d), 3)}
        for t, m, d in zip(res["documents"][0], res["metadatas"][0], res["distances"][0])
    ]


def retrieve_all_chunks(document_id: str, max_chunks: int = 20) -> list[dict]:
    col = _get_client().get_collection(_col_name(document_id))
    limit = min(col.count(), max_chunks)
    res = col.get(limit=limit, include=["documents", "metadatas"])
    return [{"text": t, "page": m.get("page", 1)} for t, m in zip(res["documents"], res["metadatas"])]


def list_documents() -> list[dict]:
    docs = []
    for col in _get_client().list_collections():
        m = col.metadata or {}
        docs.append({
            "document_id": col.name.replace("doc_", "", 1),
            "filename": m.get("filename", "Unknown"),
            "num_chunks": m.get("num_chunks", 0),
            "uploaded_at": m.get("uploaded_at", ""),
        })
    return docs


def delete_document(document_id: str) -> bool:
    try:
        _get_client().delete_collection(_col_name(document_id))
        return True
    except Exception:
        return False


def document_exists(document_id: str) -> bool:
    try:
        _get_client().get_collection(_col_name(document_id))
        return True
    except Exception:
        return False
