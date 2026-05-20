from app.core.providers import get_llm_provider
from app.services.vector_store_service import query_similar_chunks
from app.core.logging import logger


# System prompt that shapes how the LLM responds to incident queries.
# Keeps responses grounded in the retrieved log context.
RAG_SYSTEM_PROMPT = """You are an expert Site Reliability Engineer (SRE) and incident analyst.

Your job is to analyze operational logs and incidents, and provide clear, accurate, and actionable insights.

Rules you must follow:
- Base your response ONLY on the provided log context. Do not invent or assume information not present in the logs.
- If the context does not contain enough information to answer, say so clearly.
- Be concise and precise — SRE teams need fast, accurate answers during incidents.
- When identifying root causes, explain the chain of events clearly.
- Use technical language appropriate for a DevOps/SRE audience.
"""

RCA_SYSTEM_PROMPT = """You are an expert Site Reliability Engineer (SRE) performing a Root Cause Analysis (RCA).

Your job is to analyze the provided operational logs and produce a structured RCA report.

Your response must follow this exact structure:
1. **Incident Summary** — Brief description of what happened.
2. **Timeline** — Key events in chronological order (if timestamps are available).
3. **Root Cause** — The most probable root cause based on the logs.
4. **Contributing Factors** — Secondary factors that worsened the incident.
5. **Impact** — What services or systems were affected.
6. **Recommended Actions** — Concrete steps to prevent recurrence.

Rules:
- Base your analysis ONLY on the provided log context.
- If information is insufficient for any section, state "Insufficient log data" for that section.
- Be specific — reference actual log entries where possible.
"""


async def query_incident(
    query: str,
    incident_id: str = None,
    top_k: int = 5,
) -> dict:
    """
    Core RAG query function.
    Retrieves relevant log chunks and generates an AI response.

    Args:
        query: The user's question about the incident.
        incident_id: Optional — scope the search to a specific incident.
        top_k: Number of chunks to retrieve for context.

    Returns:
        Dict containing the AI response and retrieval metadata.
    """
    logger.info(f"RAG query received | query='{query[:60]}' | incident_id={incident_id}")

    # Step 1 — retrieve the most relevant log chunks from ChromaDB
    chunks = query_similar_chunks(query, incident_id=incident_id, top_k=top_k)

    if not chunks:
        logger.warning(f"No relevant chunks found for query: '{query[:60]}'")
        return {
            "response": "No relevant log data found for your query. Please ingest logs first.",
            "chunks_used": 0,
            "sources": [],
        }

    # Step 2 — build the context block from retrieved chunks
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Log Chunk {i} | Similarity: {chunk['similarity_score']}]\n{chunk['text']}"
        )
    context = "\n\n---\n\n".join(context_parts)

    # Step 3 — construct the prompt with retrieved context
    prompt = f"""Retrieved Log Context:
{context}

---

Question: {query}

Provide a clear, concise answer based strictly on the log context above."""

    # Step 4 — send to LLM and get response
    provider = get_llm_provider()
    response_text = await provider.generate(
        prompt=prompt,
        system_prompt=RAG_SYSTEM_PROMPT,
    )

    logger.info(
        f"RAG query complete | chunks_used={len(chunks)} | "
        f"response_length={len(response_text)} chars"
    )

    return {
        "response": response_text,
        "chunks_used": len(chunks),
        "sources": [
            {
                "incident_id": c["metadata"].get("incident_id"),
                "chunk_index": c["metadata"].get("chunk_index"),
                "similarity_score": c["similarity_score"],
            }
            for c in chunks
        ],
    }


async def generate_rca(incident_id: str) -> dict:
    """
    Generate a structured Root Cause Analysis for a specific incident.
    Retrieves all available log chunks for the incident and runs
    them through the RCA-specific prompt.

    Args:
        incident_id: The incident to analyze.

    Returns:
        Dict containing the RCA report and metadata.
    """
    logger.info(f"RCA generation started | incident_id={incident_id}")

    # Retrieve all chunks for this incident with a broad query
    chunks = query_similar_chunks(
        query="error failure crash timeout critical warning",
        incident_id=incident_id,
        top_k=10,
    )

    if not chunks:
        return {
            "rca": "No log data found for this incident. Please ingest logs first.",
            "chunks_analyzed": 0,
        }

    # Build context from all retrieved chunks
    context_parts = [chunk["text"] for chunk in chunks]
    context = "\n\n".join(context_parts)

    prompt = f"""Operational Log Data for Incident {incident_id}:

{context}

---

Generate a complete Root Cause Analysis report for this incident based strictly on the log data above."""

    provider = get_llm_provider()
    rca_text = await provider.generate(
        prompt=prompt,
        system_prompt=RCA_SYSTEM_PROMPT,
    )

    logger.info(
        f"RCA generation complete | incident_id={incident_id} | "
        f"chunks_analyzed={len(chunks)}"
    )

    return {
        "rca": rca_text,
        "chunks_analyzed": len(chunks),
    }