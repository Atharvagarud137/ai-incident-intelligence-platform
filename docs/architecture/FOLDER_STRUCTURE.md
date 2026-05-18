# Folder Structure Documentation

# AI Incident Intelligence Platform

---

# 1. Overview

The project follows a modular, scalable backend architecture designed for:
- maintainability
- separation of concerns
- scalable AI workflows
- enterprise-grade extensibility

The structure is intentionally organized to support:
- API services
- AI/RAG pipelines
- vector retrieval workflows
- future microservice expansion

---

# 2. Root Project Structure

```text
ai-incident-intelligence-platform/
│
├── app/
├── docs/
├── scripts/
├── tests/
├── venv/
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# 3. Root Directory Responsibilities

| Directory/File | Purpose |
|---|---|
| app/ | Core backend application |
| docs/ | Project documentation |
| scripts/ | Utility and automation scripts |
| tests/ | Test cases and validation |
| venv/ | Python virtual environment |
| main.py | FastAPI application entry point |
| requirements.txt | Python dependencies |
| README.md | Project overview |
| .gitignore | Git exclusion rules |

---

# 4. Application Layer Structure

```text
app/
│
├── api/
├── core/
├── models/
├── rag/
├── services/
└── utils/
```

---

# 5. app/api/

## Purpose
Contains API route definitions and endpoint handlers.

---

## Responsibilities
- route registration
- request handling
- response formatting
- API organization

---

## Planned Contents

```text
api/
├── ingestion.py
├── query.py
├── incidents.py
└── health.py
```

---

# 6. app/core/

## Purpose
Contains core application configuration and shared backend setup.

---

## Responsibilities
- environment configuration
- application settings
- logging configuration
- shared backend utilities

---

## Planned Contents

```text
core/
├── config.py
├── logging.py
└── constants.py
```

---

# 7. app/models/

## Purpose
Contains request/response schemas and data models.

---

## Responsibilities
- Pydantic schemas
- validation models
- API request structures
- response contracts

---

## Planned Contents

```text
models/
├── ingestion_models.py
├── query_models.py
└── response_models.py
```

---

# 8. app/rag/

## Purpose
Contains all RAG-related AI pipeline logic.

---

## Responsibilities
- embeddings
- retrieval
- chunking
- prompt construction
- vector operations

---

## Planned Contents

```text
rag/
├── embeddings.py
├── retriever.py
├── chunking.py
├── prompts.py
└── vector_store.py
```

---

# 9. app/services/

## Purpose
Contains business logic and operational workflows.

---

## Responsibilities
- ingestion workflows
- AI orchestration
- query handling
- operational services

---

## Planned Contents

```text
services/
├── ingestion_service.py
├── query_service.py
├── incident_service.py
└── llm_service.py
```

---

# 10. app/utils/

## Purpose
Contains reusable helper utilities.

---

## Responsibilities
- file handling
- text utilities
- formatting helpers
- shared utility functions

---

## Planned Contents

```text
utils/
├── file_utils.py
├── text_utils.py
└── validation_utils.py
```

---

# 11. Documentation Structure

```text
docs/
│
├── architecture/
├── api/
├── ai-ml/
├── deployment/
└── product/
```

---

# 12. Documentation Responsibilities

| Directory | Purpose |
|---|---|
| architecture/ | System design documentation |
| api/ | API specifications |
| ai-ml/ | AI pipeline documentation |
| deployment/ | Deployment documentation |
| product/ | Product and roadmap documentation |

---

# 13. Testing Structure

```text
tests/
├── api/
├── rag/
├── services/
└── integration/
```

---

# Planned Test Categories

- unit tests
- API tests
- RAG pipeline tests
- integration tests
- future AI evaluation tests

---

# 14. Scripts Directory

```text
scripts/
```

---

## Purpose
Contains utility and automation scripts.

---

## Future Responsibilities
- database initialization
- embedding generation
- maintenance tasks
- deployment automation

---

# 15. Future Enterprise Expansion

Future architectural additions may include:

```text
app/
├── agents/
├── database/
├── middleware/
├── observability/
├── config/
└── ingestion/
```

These are intentionally excluded from the MVP to maintain architectural simplicity.

---

# 16. Architectural Principles

The folder structure follows:
- separation of concerns
- modular design
- maintainable backend practices
- scalable AI engineering
- enterprise-oriented organization

---

# 17. Design Philosophy

The structure is designed to:
- support long-term scalability
- simplify onboarding
- improve maintainability
- isolate responsibilities
- enable future microservice evolution

The goal is to build:
- a production-style AI platform
instead of
- a monolithic experimental AI project.

---

---

# Updates

## Update 1 — Actual Folder Structure (2026-05-18)

**Status:** Core structure implemented. Some planned directories revised.  
**Last Updated:** 2026-05-18

---

### Actual Root Structure (as implemented)

```text
ai-incident-intelligence-platform/
│
├── app/                        # Core backend application
├── alembic/                    # Database migration scripts
├── docs/                       # Project documentation
├── tests/                      # Test suite
├── data/                       # Runtime data (ChromaDB persist dir) — not committed
├── logs/                       # Application logs — not committed
├── venv/                       # Python virtual environment — not committed
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration
├── .env                        # Environment variables — not committed
├── .env.example                # Environment variable template — committed
├── .gitignore                  # Git exclusion rules
└── README.md                   # Project overview
```

---

### Actual app/ Structure (as implemented)

```text
app/
│
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       └── incidents.py        # Incident CRUD + log ingest endpoint
│
├── core/
│   ├── __init__.py
│   ├── config.py               # Pydantic Settings — all env vars loaded here
│   ├── database.py             # SQLAlchemy engine, session factory, health check
│   ├── logging.py              # Loguru configuration
│   └── providers/
│       ├── __init__.py         # get_llm_provider() factory function
│       ├── base.py             # BaseLLMProvider abstract interface
│       ├── gemini_provider.py  # Gemini API implementation
│       └── ollama_provider.py  # Ollama local LLM implementation
│
├── models/
│   ├── __init__.py
│   ├── base.py                 # DeclarativeBase + TimestampMixin
│   └── incident.py             # Incident SQLAlchemy model
│
├── schemas/
│   ├── __init__.py
│   └── incident.py             # Pydantic request/response schemas
│
└── services/
    ├── __init__.py
    ├── chunking_service.py     # Log chunking (RecursiveCharacterTextSplitter)
    ├── embedding_service.py    # Embedding generation (sentence-transformers)
    ├── incident_service.py     # Incident CRUD business logic
    └── vector_store_service.py # ChromaDB store/query/delete operations
```

---

### Actual tests/ Structure (as implemented)

```text
tests/
├── __init__.py
└── test_core.py                # 25 unit tests covering config, providers, and endpoints
```

---

### Actual alembic/ Structure (as implemented)

```text
alembic/
├── env.py                      # Alembic environment — uses app settings for DB URL
├── script.py.mako              # Migration script template
├── README
└── versions/
    └── 830de44311a7_create_incidents_table.py   # Initial migration
```

---

### Deviations from Original Plan

| Original Plan | Actual Implementation | Reason |
|---|---|---|
| `app/models/` — Pydantic schemas | `app/models/` — SQLAlchemy ORM models only | Pydantic schemas moved to `app/schemas/` for cleaner separation |
| `app/rag/` — RAG pipeline logic | Moved to `app/services/` | Services layer is sufficient for current pipeline complexity |
| `app/utils/` | Not yet created | No shared utilities needed yet — will be added as needed |
| `app/core/constants.py` | Not created | Constants managed via `config.py` settings |
| `tests/api/`, `tests/rag/`, etc. | Single `tests/test_core.py` | Flat structure appropriate for current test count; will be split as tests grow |
| `scripts/` | Not yet created | No automation scripts needed at this stage |

---

### New Directories Not in Original Plan

| Directory | Purpose |
|---|---|
| `app/schemas/` | Pydantic request/response models (separated from SQLAlchemy models) |
| `app/core/providers/` | LLM provider implementations (Strategy Pattern) |
| `alembic/` | Database migration management |
| `data/` | ChromaDB persistent storage (runtime, not committed) |
| `logs/` | Application log files (runtime, not committed) |