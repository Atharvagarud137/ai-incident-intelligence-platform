from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.core.logging import logger

# Module-level model instance — loaded once when the service is first imported,
# not on every request. SentenceTransformer models are expensive to load.
_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    """
    Returns the embedding model, loading it on first call.
    Subsequent calls return the cached instance.
    """
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _model = SentenceTransformer(settings.embedding_model)
        logger.info("Embedding model loaded successfully")
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Convert a list of text strings into embedding vectors.

    Args:
        texts: List of strings to embed.

    Returns:
        List of embedding vectors (each a list of floats).
    """
    if not texts:
        return []

    model = get_embedding_model()

    # encode() returns numpy arrays — convert to plain Python lists
    # so they're JSON-serialisable and ChromaDB-compatible
    embeddings = model.encode(texts, show_progress_bar=False)

    logger.info(f"Embeddings generated | count={len(texts)} | dim={len(embeddings[0])}")

    return embeddings.tolist()


def embed_single(text: str) -> list[float]:
    """
    Embed a single string — convenience wrapper used for query embedding.
    """
    results = embed_texts([text])
    return results[0] if results else []