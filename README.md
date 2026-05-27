# AI Incident Intelligence Platform

An enterprise-grade AI platform for DevOps and SRE teams that ingests operational logs, performs semantic search, and generates AI-powered Root Cause Analysis using a RAG (Retrieval-Augmented Generation) pipeline.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5.3-orange)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![Tests](https://img.shields.io/badge/Tests-59%20passing-brightgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## What It Does

You feed it logs. It tells you what went wrong and why.

```
POST /api/v1/incidents/ingest   ← send raw logs
POST /api/v1/query/ask          ← ask questions about the incident
POST /api/v1/query/rca/{id}     ← get a structured Root Cause Analysis
```

**Example RCA output** (generated from real log data):

```
1. Incident Summary — payment-service experienced a critical failure due to
   inability to acquire database connections.

2. Root Cause — PostgreSQL reached its max_connections limit (98/100),
   refusing new connections for payment_user.

3. Contributing Factors — connection pool exhaustion, circuit breaker opened
   on api-gateway after 5 consecutive failures.

4. Recommended Actions — implement PgBouncer connection pooler, add alerting
   at 80% connection utilization threshold.
```

---

## Architecture

```
POST /api/v1/incidents/ingest
        │
        ▼
┌─────────────────┐     ┌──────────────────────┐
│   PostgreSQL    │     │  Chunking Pipeline    │
│  incident store │     │  RecursiveCharacter   │
│                 │     │  TextSplitter         │
└─────────────────┘     └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │  Embedding Service   │
                        │  all-MiniLM-L6-v2    │
                        │  (384 dimensions)    │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │      ChromaDB        │
                        │   Vector Store       │
                        │  cosine similarity   │
                        └──────────────────────┘
                                   │
                         POST /api/v1/query/ask
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │   LLM Provider       │
                        │   (abstracted)       │
                        ├──────────────────────┤
                        │  Gemini 2.5 Flash ✓  │
                        │  Ollama (local)  ✓   │
                        └──────────────────────┘
```

The LLM provider is **fully abstracted** via the Strategy Pattern — switching from Gemini to Ollama requires a single `.env` change, no code modifications.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI 0.111, Python 3.11 |
| AI Orchestration | LangChain 0.2.5 |
| LLM (primary) | Google Gemini 2.5 Flash (free tier) |
| LLM (fallback) | Ollama (local, zero-cost) |
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` |
| Vector Database | ChromaDB 0.5.3 (persistent) |
| Relational Database | PostgreSQL 17 + SQLAlchemy 2.0 |
| Migrations | Alembic |
| Logging | Loguru |
| Containerization | Docker + Docker Compose |
| Testing | pytest (25 tests) |

---

## Getting Started

### Prerequisites

- Python 3.11
- Docker + Docker Compose
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### Option A — Run with Docker (recommended)

```bash
# Clone the repo
git clone https://github.com/Atharvagarud137/ai-incident-intelligence-platform.git
cd ai-incident-intelligence-platform

# Copy and configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Start everything
docker-compose up --build
```

The API will be available at `http://localhost:8000`.  
Swagger UI: `http://localhost:8000/docs`

### Option B — Run locally

```bash
# Clone and set up environment
git clone https://github.com/Atharvagarud137/ai-incident-intelligence-platform.git
cd ai-incident-intelligence-platform
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — add GEMINI_API_KEY and DATABASE_URL

# Run database migrations
alembic upgrade head

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## API Reference

Full interactive documentation available at `http://localhost:8000/docs`.

### Ingest Logs

```http
POST /api/v1/incidents/ingest
Content-Type: application/json

{
  "title": "Payment service outage",
  "severity": "critical",
  "raw_logs": "2026-05-20 09:00:01 ERROR payment-service: connection pool exhausted..."
}
```

```json
{
  "incident_id": "1eabe6f0-591f-4c1e-903a-87ec958df0e6",
  "message": "Logs ingested and processed successfully.",
  "chunks_created": 2
}
```

### Ask a Question (RAG Query)

```http
POST /api/v1/query/ask
Content-Type: application/json

{
  "query": "What caused the payment service to fail?",
  "incident_id": "1eabe6f0-591f-4c1e-903a-87ec958df0e6",
  "top_k": 5
}
```

```json
{
  "query": "What caused the payment service to fail?",
  "response": "The payment service failed because it was unable to acquire database connections, leading to its connection pool being exhausted...",
  "chunks_used": 2,
  "sources": [...]
}
```

### Generate Root Cause Analysis

```http
POST /api/v1/query/rca/{incident_id}
```

Returns a structured RCA report covering incident summary, timeline, root cause, contributing factors, impact, and recommended actions.

### Other Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/incidents/` | List all incidents (filterable) |
| GET | `/api/v1/incidents/{id}` | Get incident by ID |
| PATCH | `/api/v1/incidents/{id}` | Update incident |
| DELETE | `/api/v1/incidents/{id}` | Delete incident |
| GET | `/health` | Health check |

---

## Project Structure

```
ai-incident-intelligence-platform/
│
├── app/
│   ├── api/v1/
│   │   ├── incidents.py        # Incident CRUD + log ingest
│   │   └── query.py            # RAG query + RCA generation
│   ├── core/
│   │   ├── config.py           # Pydantic Settings
│   │   ├── database.py         # SQLAlchemy engine + session
│   │   ├── logging.py          # Loguru configuration
│   │   └── providers/          # LLM provider abstraction
│   │       ├── base.py         # Abstract interface
│   │       ├── gemini_provider.py
│   │       └── ollama_provider.py
│   ├── models/                 # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic request/response schemas
│   └── services/
│       ├── chunking_service.py
│       ├── embedding_service.py
│       ├── incident_service.py
│       ├── rag_service.py
│       └── vector_store_service.py
│
├── alembic/                    # Database migrations
├── docs/                       # Architecture, API, and AI pipeline docs
├── tests/
│   └── test_core.py            # 25 unit tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── main.py
└── .env.example
```

---

## Configuration

Copy `.env.example` to `.env` and configure:

```env
# LLM Provider — switch between "gemini" and "ollama" with no code changes
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Database
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/incident_platform

# ChromaDB
CHROMA_PERSIST_DIR=./data/chroma
```

---

## Running Tests

```bash
pytest tests/test_core.py -v
```

```
25 passed in 1.94s
```

---

## Roadmap

### Phase 1 — Foundation (Complete ✅)
- [x] FastAPI backend + config architecture
- [x] LLM provider abstraction layer (Gemini + Ollama)
- [x] Log ingestion pipeline
- [x] Chunking + embedding pipeline
- [x] ChromaDB vector store
- [x] RAG query engine
- [x] AI-powered RCA generation
- [x] PostgreSQL + Alembic migrations
- [x] Docker + Docker Compose
- [x] Test suite (25 tests)

### Phase 2 — Intelligence (Planned)
- [ ] Incident clustering
- [ ] Anomaly detection
- [ ] Severity prediction
- [ ] Dashboard UI

### Phase 3 — Enterprise (Planned)
- [ ] Slack / Jira integrations
- [ ] JWT authentication
- [ ] CI/CD pipeline
- [ ] Cloud deployment

---

## Documentation

Detailed documentation is available in the `docs/` directory:

- [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md) — System architecture
- [`docs/ai-ml/AI_PIPELINE.md`](docs/ai-ml/AI_PIPELINE.md) — AI pipeline design
- [`docs/ai-ml/LLM_PROVIDER_ANALYSIS.md`](docs/ai-ml/LLM_PROVIDER_ANALYSIS.md) — LLM provider decision
- [`docs/api/API_SPEC.md`](docs/api/API_SPEC.md) — API specification
- [`docs/product/ROADMAP.md`](docs/product/ROADMAP.md) — Development roadmap

---

## License

MIT License — see [LICENSE](LICENSE) for details.