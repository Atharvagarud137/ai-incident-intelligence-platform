# Technology Stack Document

# AI Incident Intelligence Platform

---

# 1. Technology Stack Overview

The AI Incident Intelligence Platform uses a modern AI/backend engineering stack focused on:
- scalability
- modularity
- rapid development
- AI workflow support
- containerized deployment
- enterprise extensibility

The stack is intentionally designed for:
- MVP delivery
- future production scalability
- maintainable AI engineering

---

# 2. Backend Technologies

# 2.1 Python 3.11

## Purpose
Primary backend programming language.

---

## Why Python?

Python was selected because of:
- strong AI ecosystem support
- mature backend frameworks
- extensive ML/LLM libraries
- rapid development capabilities
- strong community adoption

---

## Alternatives Considered
- Node.js
- Go
- Java

---

## Tradeoffs

| Pros | Cons |
|---|---|
| Excellent AI ecosystem | Slower than compiled languages |
| Fast development | Higher runtime memory usage |
| Extensive libraries | Dynamic typing complexity |

---

# 2.2 FastAPI

## Purpose
REST API framework for backend services.

---

## Why FastAPI?

FastAPI was selected because of:
- high performance
- async support
- automatic OpenAPI generation
- Pydantic validation
- clean developer experience

---

## Alternatives Considered
- Flask
- Django
- Express.js

---

## Tradeoffs

| Pros | Cons |
|---|---|
| Excellent performance | Smaller ecosystem than Flask |
| Built-in validation | Slight learning curve |
| Async-first architecture | |

---

# 3. AI & Machine Learning Stack

# 3.1 LangChain / LangGraph

## Purpose
AI orchestration and RAG workflow management.

---

## Why LangChain?

Selected for:
- RAG abstractions
- retrieval workflows
- LLM integration
- prompt orchestration

---

## Why LangGraph? (Future)

Selected for:
- agent orchestration
- multi-step AI workflows
- stateful AI execution

---

## Tradeoffs

| Pros | Cons |
|---|---|
| Rapid AI workflow development | Can become abstraction-heavy |
| Strong ecosystem | Fast-changing APIs |

---

# 3.2 Sentence Transformers

## Purpose
Generate semantic embeddings for logs and incidents.

---

## Initial Model

```text
all-MiniLM-L6-v2
```

---

## Why This Model?

Chosen because:
- lightweight
- fast inference
- strong semantic performance
- free/open-source
- local execution support

---

## Alternatives Considered
- OpenAI embeddings
- Gemini embeddings
- BGE embeddings

---

# 3.3 Gemini API / OpenAI API

## Purpose
Large Language Model (LLM) inference.

---

## Why Gemini Initially?

Chosen because:
- generous free tier
- strong reasoning performance
- easy API access

---

## Future LLM Flexibility

The architecture supports:
- Gemini
- OpenAI
- local LLMs
- future provider abstraction

---

# 4. Database Technologies

# 4.1 PostgreSQL

## Purpose
Relational metadata storage.

---

## Responsibilities
- incident metadata
- operational records
- future user/session handling

---

## Why PostgreSQL?

Chosen because:
- enterprise reliability
- strong SQL capabilities
- scalability
- open-source ecosystem

---

## Alternatives Considered
- MySQL
- MongoDB
- SQLite

---

## Tradeoffs

| Pros | Cons |
|---|---|
| Reliable and scalable | Slightly heavier setup |
| Excellent SQL support | |

---

# 4.2 ChromaDB

## Purpose
Vector database for semantic retrieval.

---

## Why ChromaDB?

Chosen because:
- lightweight setup
- local development simplicity
- good RAG support
- beginner-friendly vector workflows

---

## Alternatives Considered
- Pinecone
- Weaviate
- FAISS

---

## Future Migration Options

The architecture supports future migration to:
- Pinecone
- Weaviate
- cloud vector databases

---

# 5. Frontend Technologies

# 5.1 Streamlit (MVP)

## Purpose
Rapid frontend prototyping.

---

## Why Streamlit?

Chosen because:
- fast development
- easy AI integration
- lightweight UI creation

---

## Tradeoffs

| Pros | Cons |
|---|---|
| Fast MVP creation | Limited frontend flexibility |
| Easy Python integration | Less enterprise-grade |

---

# 5.2 Next.js (Future)

## Purpose
Enterprise-grade frontend interface.

---

## Why Next.js?

Chosen because:
- scalability
- production-grade UI support
- React ecosystem
- API integration capabilities

---

# 6. DevOps & Deployment

# 6.1 Docker

## Purpose
Containerized deployment.

---

## Why Docker?

Chosen because:
- environment consistency
- deployment portability
- scalable infrastructure support

---

# 6.2 Docker Compose

## Purpose
Multi-container orchestration.

---

## Responsibilities
- backend services
- PostgreSQL
- vector database services

---

# 6.3 GitHub Actions (Future)

## Purpose
CI/CD automation.

---

## Planned Usage
- automated testing
- deployment workflows
- build pipelines

---

# 7. Development Tooling

# 7.1 VS Code

## Purpose
Primary development IDE.

---

## Why VS Code?

Chosen because:
- lightweight
- excellent Python support
- Docker integration
- strong extension ecosystem

---

# 7.2 Postman / Thunder Client

## Purpose
API testing and validation.

---

# 7.3 Git & GitHub

## Purpose
Version control and repository management.

---

# 8. Security Strategy

## Planned Security Features
- environment variable secrets
- .env configuration
- API validation
- future RBAC integration

---

# 9. Scalability Strategy

The stack is designed for:
- modular services
- scalable AI workflows
- future microservices
- cloud deployment support

---

# 10. Technology Selection Principles

Technologies were selected based on:
- scalability
- maintainability
- AI ecosystem compatibility
- development speed
- deployment flexibility
- enterprise extensibility

---

# 11. Future Technology Enhancements

Potential future additions:
- Redis
- Kafka
- Kubernetes
- Prometheus
- Grafana
- OpenTelemetry
- MLflow

These are intentionally excluded from the MVP to avoid premature complexity.

---

# 12. Stack Philosophy

The stack prioritizes:
- engineering clarity
- modular architecture
- scalable AI systems
- maintainable development
- practical enterprise readiness

The goal is to build:
- a production-style AI platform
rather than
- a notebook-based AI demo project.

---

---

# Updates

## Update 1 — Stack Implementation (2026-05-18)

**Status:** Core stack implemented and operational.  
**Last Updated:** 2026-05-18

---

### Implemented Technologies (with actual versions)

| Technology | Version | Status |
|---|---|---|
| Python | 3.11.9 | ✅ Active |
| FastAPI | 0.111.0 | ✅ Active |
| Uvicorn | 0.29.0 | ✅ Active |
| Pydantic | 2.7.1 | ✅ Active |
| Pydantic Settings | 2.2.1 | ✅ Active |
| SQLAlchemy | 2.0.30 | ✅ Active |
| Alembic | 1.13.1 | ✅ Active |
| psycopg2-binary | 2.9.9 | ✅ Active |
| PostgreSQL | 17.10.1 | ✅ Active |
| ChromaDB | 0.5.3 | ✅ Active |
| sentence-transformers | 3.0.1 | ✅ Active |
| google-generativeai | 0.7.2 | ✅ Active |
| langchain | 0.2.5 | ✅ Active |
| langchain-community | 0.2.5 | ✅ Active |
| langchain-google-genai | 1.0.7 | ✅ Active |
| langchain-text-splitters | 0.2.4 | ✅ Active |
| ollama | 0.2.1 | ✅ Available (fallback) |
| loguru | 0.7.2 | ✅ Active |
| tenacity | 8.3.0 | ✅ Active |
| httpx | 0.27.0 | ✅ Active |
| pytest | 8.2.2 | ✅ Active |
| pytest-asyncio | 0.23.7 | ✅ Active |
| python-dotenv | 1.0.1 | ✅ Active |

---

### Section 3.3 — LLM Stack Revision

The original spec described a simple Gemini/OpenAI selection. The implemented architecture uses a **provider abstraction layer** (Strategy Pattern) that makes the LLM backend fully swappable via environment variable.

**Active model:** `gemini-2.5-flash` (free tier)

Models tested during setup:

| Model | Outcome |
|---|---|
| `gemini-1.5-flash` | 404 — unavailable on API version v1beta |
| `gemini-2.0-flash` | 429 — daily quota is 0 on free tier |
| `gemini-2.0-flash-lite` | 429 — daily quota is 0 on free tier |
| `gemini-2.5-flash` | ✅ Working — selected as active model |

**OpenAI** is not integrated — it has no free tier and the zero-budget constraint is in effect.

---

### Section 3.2 — Sentence Transformers (as implemented)

| Parameter | Value |
|---|---|
| Model | `all-MiniLM-L6-v2` |
| Embedding dimensions | 384 |
| Inference | Local CPU (no GPU required) |
| Model size | ~90MB (downloaded once, cached by HuggingFace) |
| Loading strategy | Lazy init, cached at module level |

---

### Section 4.2 — ChromaDB (as implemented)

| Parameter | Value |
|---|---|
| Mode | Persistent (disk-backed) |
| Persist directory | `./data/chroma` (configurable) |
| Collection | `incident_logs` |
| Similarity metric | Cosine similarity (`hnsw:space=cosine`) |
| Telemetry | Disabled (`anonymized_telemetry=False`) |

---

### Section 4.1 — PostgreSQL (as implemented)

| Parameter | Value |
|---|---|
| Version | 17.10.1 |
| ORM | SQLAlchemy 2.0 (modern `Mapped` column style) |
| Migrations | Alembic |
| Driver | psycopg2-binary |
| Pool size | 5 (configurable) |
| Max overflow | 10 (configurable) |
| Pool recycle | 1800s |

**Live tables:**
- `incidents` — core incident records
- `alembic_version` — migration tracking

---

### New Technology Additions (Not in Original Spec)

| Technology | Purpose | Why Added |
|---|---|---|
| Alembic | Database migrations | Production-grade schema management |
| Loguru | Structured logging | Cleaner than Python's built-in `logging` |
| Tenacity | Retry logic | Handles Gemini API transient failures gracefully |
| pytest-asyncio | Async test support | Required for testing async FastAPI endpoints |

---

### Dependency Conflict Notes

During setup, the following version conflict was encountered and resolved:

- `langchain-google-genai` has strict version requirements on `google-generativeai`
- Resolution: `google-generativeai==0.7.2` + `langchain-google-genai==1.0.7` are compatible

If reinstalling from scratch, use the pinned versions in `requirements.txt` exactly.