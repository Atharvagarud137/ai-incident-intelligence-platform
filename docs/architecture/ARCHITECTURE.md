# System Architecture Document

# AI Incident Intelligence Platform

---

# 1. Architecture Overview

AI Incident Intelligence Platform is designed as a modular, scalable, AI-powered incident analysis system.

The architecture follows a layered backend design with:
- API layer
- service layer
- AI/RAG layer
- vector storage
- relational database storage
- LLM integration

The system is designed for:
- scalability
- maintainability
- modular AI workflows
- enterprise-grade extensibility

---

# 2. High-Level System Architecture

```text
                    ┌────────────────────┐
                    │     Client UI      │
                    │ Streamlit/Next.js  │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │    FastAPI APIs    │
                    │  Backend Services  │
                    └─────────┬──────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼

┌────────────────┐   ┌────────────────┐   ┌────────────────┐
│ Log Ingestion  │   │  RAG Pipeline  │   │ Incident Engine│
│    Service     │   │                │   │                │
└────────────────┘   └────────────────┘   └────────────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │  Embedding Engine  │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │    Vector Store    │
                    │     ChromaDB       │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │    LLM Provider    │
                    │ Gemini / OpenAI    │
                    └────────────────────┘
```

---

# 3. Architectural Goals

The system architecture is designed to achieve:

- Modular backend services
- AI workflow extensibility
- Scalable RAG pipelines
- Clean API separation
- Efficient semantic retrieval
- Maintainable enterprise structure
- Containerized deployment readiness

---

# 4. Core Architectural Components

# 4.1 Client Layer

## Purpose
Provides user interaction with the platform.

## Planned Frontend Options
- Streamlit (MVP)
- Next.js (Future enhancement)

## Responsibilities
- Upload logs
- Submit incident queries
- Display AI-generated summaries
- Display retrieval results

---

# 4.2 API Layer

## Technology
- FastAPI

## Responsibilities
- Expose REST APIs
- Handle requests/responses
- Validate payloads
- Route service calls
- Manage API lifecycle

## Planned API Categories
- Log ingestion APIs
- Query APIs
- Incident APIs
- Health check APIs

---

# 4.3 Log Ingestion Service

## Responsibilities
- Parse uploaded logs
- Normalize log formats
- Preprocess text
- Chunk log content
- Prepare embedding payloads

## Supported Formats
- .txt
- .log
- .json
- .csv

---

# 4.4 RAG Pipeline

## Responsibilities
- Generate embeddings
- Perform semantic retrieval
- Retrieve contextual incidents
- Build grounded prompts
- Generate AI responses

## Pipeline Flow

```text
User Query
    ↓
Embedding Generation
    ↓
Vector Similarity Search
    ↓
Context Retrieval
    ↓
Prompt Construction
    ↓
LLM Response Generation
```

---

# 4.5 Embedding Layer

## Purpose
Convert logs and incidents into semantic vector representations.

## Planned Embedding Models
- sentence-transformers
- HuggingFace embeddings
- Gemini embeddings (future)

---

# 4.6 Vector Database

## Technology
- ChromaDB

## Responsibilities
- Store embeddings
- Perform vector similarity search
- Retrieve semantically relevant incidents

## Future Enhancements
- Pinecone
- FAISS
- Weaviate

---

# 4.7 Relational Database

## Technology
- PostgreSQL

## Responsibilities
- Store metadata
- Incident tracking
- User/session data
- Operational records

---

# 4.8 LLM Layer

## Planned Providers
- Gemini API
- OpenAI API

## Responsibilities
- Generate summaries
- Explain incidents
- Provide RCA assistance
- Generate contextual insights

---

# 5. Backend Folder Architecture

```text
app/
│
├── api/          # API routes/endpoints
├── core/         # Core configurations/settings
├── models/       # Data models/schemas
├── rag/          # RAG pipeline logic
├── services/     # Business logic/services
└── utils/        # Helper utilities
```

---

# 6. Data Flow Architecture

# 6.1 Log Upload Flow

```text
Client Upload
      ↓
FastAPI Endpoint
      ↓
Log Parsing
      ↓
Chunking
      ↓
Embedding Generation
      ↓
Vector Database Storage
```

---

# 6.2 Incident Query Flow

```text
User Query
      ↓
Embedding Generation
      ↓
Semantic Retrieval
      ↓
Relevant Context Retrieval
      ↓
Prompt Construction
      ↓
LLM Processing
      ↓
Incident Intelligence Response
```

---

# 7. Security Considerations

## Planned Security Features
- Environment variable secrets
- Secure API handling
- Input validation
- Future RBAC integration

## Secrets Handling
Sensitive credentials will be stored using:
- .env files
- environment variables

No secrets will be hardcoded.

---

# 8. Scalability Considerations

The architecture supports future:
- microservice separation
- distributed AI pipelines
- multi-agent systems
- scalable vector databases
- cloud deployment
- Kubernetes orchestration

---

# 9. Deployment Architecture

## Containerization
- Docker
- Docker Compose

## Planned Deployment Options
- Render
- Railway
- AWS
- GCP

---

# 10. Observability Strategy

## Planned Monitoring
- application logs
- API metrics
- retrieval latency
- AI response monitoring

## Future Enhancements
- Prometheus
- Grafana
- OpenTelemetry

---

# 11. Future Architecture Enhancements

## Phase 2
- Incident clustering engine
- RCA engine
- anomaly detection services

## Phase 3
- Multi-agent orchestration
- real-time streaming
- Slack/Jira integrations
- autonomous remediation workflows

---

# 12. Architectural Principles

The project follows:

- modular design
- separation of concerns
- service-oriented structure
- scalable AI workflows
- maintainable backend architecture
- enterprise-grade engineering practices

---

---

# Updates

## Update 1 — Core Architecture Implementation (2026-05-18)

**Status:** Backend foundation implemented and operational.  
**Last Updated:** 2026-05-18

---

### Implemented Components

The following architectural components are live:

| Component | Status | Technology |
|---|---|---|
| API Layer | ✅ Live | FastAPI 0.111.0 + Uvicorn |
| Config Architecture | ✅ Live | Pydantic Settings + `.env` |
| Logging | ✅ Live | Loguru |
| LLM Provider Layer | ✅ Live | Provider abstraction (Strategy Pattern) |
| Log Ingestion Service | ✅ Live | FastAPI + PostgreSQL |
| Chunking Service | ✅ Live | LangChain `RecursiveCharacterTextSplitter` |
| Embedding Layer | ✅ Live | `sentence-transformers` `all-MiniLM-L6-v2` |
| Vector Database | ✅ Live | ChromaDB (persistent, local) |
| Relational Database | ✅ Live | PostgreSQL 17 + SQLAlchemy 2.0 + Alembic |
| Health Check APIs | ✅ Live | `GET /` and `GET /health` |
| Test Suite | ✅ Live | pytest (25/25 passing) |

---

### Actual Folder Structure (as implemented)

```text
app/
│
├── api/
│   └── v1/
│       ├── __init__.py
│       └── incidents.py        # Incident CRUD + log ingest endpoint
│
├── core/
│   ├── config.py               # Pydantic Settings — loads from .env
│   ├── database.py             # SQLAlchemy engine, session, health check
│   ├── logging.py              # Loguru setup
│   └── providers/
│       ├── __init__.py         # get_llm_provider() factory
│       ├── base.py             # BaseLLMProvider abstract interface
│       ├── gemini_provider.py  # Gemini implementation
│       └── ollama_provider.py  # Ollama implementation
│
├── models/
│   ├── base.py                 # DeclarativeBase + TimestampMixin
│   └── incident.py             # Incident model (PostgreSQL table)
│
├── schemas/
│   └── incident.py             # Pydantic request/response schemas
│
├── services/
│   ├── chunking_service.py     # Log chunking pipeline
│   ├── embedding_service.py    # Embedding generation (sentence-transformers)
│   ├── incident_service.py     # Incident CRUD business logic
│   └── vector_store_service.py # ChromaDB operations
│
tests/
│   └── test_core.py            # 25 unit tests (config, providers, endpoints)
│
alembic/                        # Database migrations
main.py                         # FastAPI app entry point
requirements.txt                # Python dependencies
.env                            # Environment variables (not committed)
.env.example                    # Environment variable template (committed)
pytest.ini                      # Pytest configuration
```

---

### LLM Provider Architecture (as implemented)

The LLM layer was implemented using the **Strategy Pattern** — a key architectural decision that keeps the platform provider-agnostic.

```text
RAG Pipeline / Services
        ↓
  get_llm_provider()        ← factory function, reads LLM_PROVIDER from .env
        ↓
  BaseLLMProvider           ← abstract interface (generate, is_available, provider_name)
        ↓
  ┌─────────────────────────────┐
  │  GeminiProvider             │  ← active (gemini-2.5-flash, free tier)
  │  OllamaProvider             │  ← available (swap via .env, no code changes)
  └─────────────────────────────┘
```

Switching providers requires only:
```env
LLM_PROVIDER=ollama   # was: gemini
```

No application code changes needed.

---

### Database Architecture (as implemented)

**ORM:** SQLAlchemy 2.0 (modern `Mapped` style)  
**Migrations:** Alembic  
**Driver:** psycopg2-binary

**Tables live in PostgreSQL:**

| Table | Description |
|---|---|
| `incidents` | Core incident records with severity, status, RCA, and raw logs |
| `alembic_version` | Migration tracking (managed by Alembic) |

**Connection pooling:**
- Pool size: 5 (configurable via `DATABASE_POOL_SIZE`)
- Max overflow: 10 (configurable via `DATABASE_MAX_OVERFLOW`)
- Pool recycle: 1800s (prevents stale connections)

---

### Ingest Pipeline Data Flow (as implemented)

```text
POST /api/v1/incidents/ingest
        ↓
Pydantic validation (LogIngestRequest)
        ↓
incident_service.create_incident()  →  PostgreSQL (incidents table)
        ↓
chunking_service.chunk_logs()       →  RecursiveCharacterTextSplitter (512 chars, 64 overlap)
        ↓
vector_store_service.store_chunks() →  embed_texts() → ChromaDB upsert
        ↓
LogIngestResponse (incident_id, message, chunks_created)
```

---

### Section 4.8 — LLM Layer Correction

The original spec listed `Gemini API` and `OpenAI API` as planned providers. The implemented architecture uses:

- **Active:** Gemini (`gemini-2.5-flash`) via provider abstraction
- **Available:** Ollama (local LLMs — `mistral:7b`, `llama3.2:3b`)
- **Future:** OpenAI, Anthropic (add by implementing `BaseLLMProvider`)

OpenAI is not integrated in the current implementation — it has no free tier and the zero-budget constraint is in effect.