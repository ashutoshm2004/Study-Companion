"""Local embeddings using sentence-transformers — free, no API key needed."""
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_model(model_name: str):
    logger.info(f"Loading embedding model: {model_name} (first run downloads ~90MB)")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_name)
    logger.info("Embedding model ready.")
    return model


def embed_texts(texts: list[str], model_name: str = "all-MiniLM-L6-v2") -> list[list[float]]:
    model = _get_model(model_name)
    return model.encode(texts, show_progress_bar=False, batch_size=32).tolist()


def embed_query(query: str, model_name: str = "all-MiniLM-L6-v2") -> list[float]:
    return embed_texts([query], model_name)[0]
