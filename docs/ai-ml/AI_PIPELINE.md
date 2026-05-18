# AI Pipeline Architecture

# AI Incident Intelligence Platform

---

# 1. AI Pipeline Overview

The AI pipeline is responsible for:
- log ingestion
- preprocessing
- chunking
- embedding generation
- semantic retrieval
- prompt construction
- LLM-based response generation

The system follows a Retrieval-Augmented Generation (RAG) architecture to ensure grounded and context-aware AI responses.

---

# 2. Core AI Workflow

```text
Log Upload
    ↓
Preprocessing
    ↓
Chunking
    ↓
Embedding Generation
    ↓
Vector Database Storage
    ↓
User Query
    ↓
Query Embedding
    ↓
Semantic Retrieval
    ↓
Context Construction
    ↓
Prompt Engineering
    ↓
LLM Response Generation
    ↓
Incident Intelligence Output
```

---

# 3. Log Ingestion Pipeline

## Purpose
Convert raw operational logs into structured semantic data for AI retrieval.

## Supported Formats
- .txt
- .log
- .json
- .csv

## Responsibilities
- file parsing
- text extraction
- normalization
- metadata extraction
- timestamp preservation

---

# 4. Preprocessing Strategy

## Planned Preprocessing Steps

### Text Cleaning
- remove invalid characters
- normalize whitespace
- remove redundant formatting

### Metadata Preservation
Retain:
- timestamps
- service names
- log levels
- trace IDs
- error codes

### Structured Context Extraction
Extract:
- error messages
- stack traces
- operational events
- incident patterns

---

# 5. Chunking Strategy

## Purpose
Split large log files into semantically meaningful chunks.

---

## Initial Chunking Approach

### Chunk Type
- text-based chunking

### Chunk Size
- 500 to 1000 characters

### Chunk Overlap
- 100 to 200 characters

---

## Why Overlap Is Needed

Overlap preserves contextual continuity between chunks.

Without overlap:
- incident sequences may break
- stack traces lose continuity
- retrieval quality degrades

---

## Future Enhancements
- semantic chunking
- recursive chunking
- adaptive chunk sizing

---

# 6. Embedding Strategy

## Purpose
Convert text into vector representations for semantic search.

---

## Planned Embedding Models

### MVP Models
- sentence-transformers
- all-MiniLM-L6-v2

### Future Models
- BGE embeddings
- Gemini embeddings
- OpenAI embeddings

---

## Embedding Responsibilities
- semantic similarity representation
- retrieval optimization
- contextual search support

---

# 7. Vector Database Strategy

## MVP Vector Database
- ChromaDB

---

## Responsibilities
- vector storage
- semantic similarity search
- contextual retrieval

---

## Stored Data
Each vector entry contains:
- chunk text
- embedding vector
- metadata
- timestamps
- source identifiers

---

# 8. Query Processing Pipeline

## User Query Flow

```text
User Query
    ↓
Query Embedding
    ↓
Similarity Search
    ↓
Top-K Retrieval
    ↓
Context Aggregation
    ↓
Prompt Construction
    ↓
LLM Generation
```

---

# 9. Retrieval Strategy

## Retrieval Type
- semantic similarity retrieval

---

## Retrieval Method
- cosine similarity search

---

## Initial Retrieval Parameters

### Top-K Retrieval
- retrieve top 3-5 relevant chunks

### Similarity Threshold
- configurable threshold filtering

---

## Future Enhancements
- hybrid search
- reranking models
- metadata filtering
- contextual ranking

---

# 10. Prompt Engineering Strategy

## Purpose
Generate grounded and context-aware responses.

---

## Prompt Structure

```text
System Instructions
    +
Retrieved Context
    +
User Query
    +
Response Constraints
```

---

## Example Prompt Flow

```text
You are an AI incident analysis assistant.

Use only the provided operational context to answer.

Retrieved Context:
[retrieved chunks]

User Query:
[query]

Generate:
- concise explanation
- probable root cause
- relevant operational insight
```

---

# 11. Hallucination Mitigation

## Planned Techniques

### Grounded Context Injection
Responses must rely on retrieved context.

---

### Retrieval-Constrained Generation
Limit model responses to retrieved evidence.

---

### Context Filtering
Remove irrelevant retrieved chunks.

---

### Future Enhancements
- confidence scoring
- response verification
- citation-based grounding

---

# 12. AI Response Types

The system may generate:

- incident summaries
- operational insights
- probable root causes
- incident correlations
- failure explanations

---

# 13. Planned AI Features

## Phase 2
- anomaly detection
- RCA generation
- incident clustering
- severity prediction

---

## Phase 3
- agentic workflows
- autonomous remediation suggestions
- incident recommendation engine

---

# 14. Performance Considerations

## Key Optimization Areas
- retrieval latency
- embedding speed
- vector query efficiency
- prompt token size
- LLM response time

---

# 15. AI Pipeline Risks

## Technical Risks
- hallucinations
- irrelevant retrieval
- poor chunking
- noisy embeddings
- prompt drift

---

## Operational Risks
- large log volumes
- token cost scaling
- vector database growth

---

# 16. Evaluation Strategy

## Planned Evaluation Metrics

### Retrieval Metrics
- retrieval relevance
- semantic similarity quality

### AI Response Metrics
- groundedness
- contextual accuracy
- hallucination rate

### Operational Metrics
- latency
- throughput
- API response time

---

# 17. Future AI Enhancements

Future AI capabilities may include:
- graph-based incident analysis
- multi-agent orchestration
- memory-aware incident workflows
- adaptive retrieval systems
- self-improving retrieval pipelines

---

# 18. AI Pipeline Principles

The AI pipeline follows:
- grounded generation
- modular AI design
- retrieval-first architecture
- scalable vector workflows
- maintainable AI engineering practices

---

---

# Updates

## Update 1 — Pipeline Implementation (2026-05-18)

### Status
Core AI pipeline implemented and operational.

---

### LLM Provider

The platform uses a **provider abstraction layer** (Strategy Pattern) allowing the LLM backend to be swapped via a single environment variable with no code changes.

**Active provider:** Google Gemini (`gemini-2.5-flash`)
**Fallback provider:** Ollama (local, offline)
**Selection:** `LLM_PROVIDER=gemini` or `LLM_PROVIDER=ollama` in `.env`

Provider abstraction is implemented in:
- `app/core/providers/base.py` — abstract interface
- `app/core/providers/gemini_provider.py` — Gemini implementation
- `app/core/providers/ollama_provider.py` — Ollama implementation
- `app/core/providers/__init__.py` — factory function

---

### Chunking Implementation

**Implemented in:** `app/services/chunking_service.py`

Actual parameters used (refined from initial estimates):

| Parameter | Planned | Implemented |
|---|---|---|
| Chunk size | 500–1000 chars | 512 chars |
| Chunk overlap | 100–200 chars | 64 chars |
| Splitter | text-based | `RecursiveCharacterTextSplitter` |

**Splitting priority order:** `\n\n` → `\n` → ` ` → `""`

This preserves log line boundaries where possible, preventing mid-line splits on timestamped log entries.

Each chunk is tagged with:
- `incident_id`
- `chunk_index`
- `total_chunks`

---

### Embedding Implementation

**Implemented in:** `app/services/embedding_service.py`

| Parameter | Value |
|---|---|
| Model | `all-MiniLM-L6-v2` |
| Embedding dimensions | 384 |
| Library | `sentence-transformers==3.0.1` |
| Model loading | Lazy, cached at module level (loaded once on first use) |

The model is loaded once at startup and reused across all requests — avoids the ~5 second load time on every request.

---

### Vector Store Implementation

**Implemented in:** `app/services/vector_store_service.py`

| Parameter | Value |
|---|---|
| Database | ChromaDB (persistent) |
| Collection | `incident_logs` |
| Similarity metric | Cosine similarity |
| Persistence path | `./data/chroma` (configurable via `CHROMA_PERSIST_DIR`) |
| Telemetry | Disabled (`anonymized_telemetry=False`) |

**Key operations implemented:**
- `store_chunks()` — batch embed and upsert chunks
- `query_similar_chunks()` — semantic search with optional incident-level filtering
- `delete_incident_chunks()` — cleanup on incident deletion

Chunk IDs follow the format: `{incident_id}_chunk_{index}`

---

### Full Ingest Pipeline Flow (as implemented)

```text
POST /api/v1/incidents/ingest
    ↓
Validate request (Pydantic)
    ↓
Create incident record (PostgreSQL)
    ↓
chunk_logs() — RecursiveCharacterTextSplitter
    ↓
store_chunks() — embed_texts() → ChromaDB upsert
    ↓
Return incident_id + chunks_created
```

All four steps run synchronously within a single API request. Async processing is planned for Phase 2 when log volumes grow.

---

### Notes
- ChromaDB telemetry warnings (`capture() takes 1 positional argument`) are a known harmless issue with the ChromaDB version in use and do not affect functionality.
- The embedding model (`all-MiniLM-L6-v2`, ~90MB) is downloaded from HuggingFace on first run and cached locally.