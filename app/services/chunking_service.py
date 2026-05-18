from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.logging import logger


# These values are tuned for log data specifically —
# logs tend to have meaningful boundaries at newlines
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64


def chunk_logs(raw_logs: str, incident_id: str) -> list[dict]:
    """
    Split raw log text into overlapping chunks for embedding.

    Uses RecursiveCharacterTextSplitter which tries to split on
    natural boundaries (newlines, spaces) before hard character limits.
    This keeps log lines intact where possible.

    Args:
        raw_logs: The full raw log string to chunk.
        incident_id: Used to tag each chunk with its source incident.

    Returns:
        A list of chunk dicts, each containing the text and metadata.
    """
    if not raw_logs or not raw_logs.strip():
        logger.warning(f"Empty log content received for incident {incident_id}")
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        # Try splitting on these boundaries in order
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = splitter.split_text(raw_logs)

    # Wrap each chunk with metadata so we know where it came from
    result = [
        {
            "text": chunk,
            "metadata": {
                "incident_id": incident_id,
                "chunk_index": i,
                "total_chunks": len(chunks),
            },
        }
        for i, chunk in enumerate(chunks)
    ]

    logger.info(
        f"Log chunking complete | incident_id={incident_id} | "
        f"chunks={len(result)} | avg_size={sum(len(c['text']) for c in result) // max(len(result), 1)} chars"
    )

    return result