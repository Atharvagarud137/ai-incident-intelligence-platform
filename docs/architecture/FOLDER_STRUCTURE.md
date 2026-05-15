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