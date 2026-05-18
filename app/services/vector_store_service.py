import chromadb
from typing import Optional
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.core.logging import logger
from app.services.embedding_service import embed_texts, embed_single

# Collection name for storing incident log chunks
COLLECTION_NAME = "incident_logs"

# Module-level client instance — initialised once
from typing import Optional
_client: Optional[chromadb.PersistentClient] = None
_collection: Optional[object] = None

def get_chroma_client() -> chromadb.PersistentClient:
    """
    Returns a persistent ChromaDB client, creating it on first call.
    Data is stored on disk at the path defined in .env (CHROMA_PERSIST_DIR).
    """
    global _client
    if _client is None:
        logger.info(f"Initialising ChromaDB | persist_dir={settings.chroma_persist_dir}")
        _client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        logger.info("ChromaDB client initialised")
    return _client


def get_collection():
    """
    Returns the incident logs collection, creating it if it doesn't exist.
    """
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},  # cosine similarity for semantic search
        )
        logger.info(f"ChromaDB collection ready | name={COLLECTION_NAME}")
    return _collection


def store_chunks(chunks: list[dict]) -> int:
    """
    Embed and store a list of chunks in ChromaDB.

    Args:
        chunks: List of chunk dicts from chunking_service.chunk_logs()

    Returns:
        Number of chunks successfully stored.
    """
    if not chunks:
        return 0

    collection = get_collection()

    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    # Generate a unique ID for each chunk using incident_id + chunk_index
    ids = [
        f"{c['metadata']['incident_id']}_chunk_{c['metadata']['chunk_index']}"
        for c in chunks
    ]

    # Generate embeddings for all chunks in one batch
    embeddings = embed_texts(texts)

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    logger.info(
        f"Chunks stored in ChromaDB | count={len(chunks)} | "
        f"incident_id={chunks[0]['metadata']['incident_id']}"
    )

    return len(chunks)


def query_similar_chunks(query: str, incident_id: str = None, top_k: int = 5) -> list[dict]:
    """
    Find the most semantically similar chunks to a query string.

    Args:
        query: The search query (e.g. "What caused the CPU spike?")
        incident_id: Optional — filter results to a specific incident.
        top_k: Number of results to return.

    Returns:
        List of matching chunks with their text and metadata.
    """
    collection = get_collection()

    query_embedding = embed_single(query)

    # Build optional filter for incident-specific queries
    where_filter = {"incident_id": incident_id} if incident_id else None

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    # Reformat ChromaDB's response into a clean list of dicts
    chunks = []
    if results and results["documents"]:
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            chunks.append({
                "text": doc,
                "metadata": meta,
                "similarity_score": round(1 - dist, 4),  # convert distance to similarity
            })

    logger.info(
        f"Vector search complete | query='{query[:50]}' | results={len(chunks)}"
    )

    return chunks


def delete_incident_chunks(incident_id: str) -> None:
    """Remove all stored chunks for a given incident from ChromaDB."""
    collection = get_collection()
    collection.delete(where={"incident_id": incident_id})
    logger.info(f"ChromaDB chunks deleted | incident_id={incident_id}")