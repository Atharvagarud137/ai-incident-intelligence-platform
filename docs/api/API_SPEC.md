# API Specification Document

# AI Incident Intelligence Platform

---

# 1. API Overview

The platform exposes REST APIs for:
- log ingestion
- semantic querying
- incident retrieval
- AI-generated summaries
- health monitoring

The APIs are implemented using FastAPI.

---

# 2. API Design Principles

The API design follows:
- RESTful conventions
- modular endpoint grouping
- JSON request/response structures
- stateless communication
- scalable service separation

---

# 3. Base URL Structure

```text
/api/v1/
```

---

# 4. Core API Modules

| Module | Purpose |
|---|---|
| ingestion | Upload and process logs |
| query | RAG-based querying |
| incidents | Incident retrieval |
| health | Service monitoring |

---

# 5. Log Ingestion APIs

# 5.1 Upload Logs

## Endpoint

```http
POST /api/v1/ingestion/upload
```

---

## Purpose

Upload operational logs for preprocessing, chunking, embedding, and vector storage.

---

## Supported File Types

- .txt
- .log
- .json
- .csv

---

## Request Type

```http
multipart/form-data
```

---

## Request Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| file | File | Yes | Log file upload |

---

## Success Response

```json
{
  "status": "success",
  "message": "Log file processed successfully",
  "chunks_created": 42
}
```

---

## Failure Response

```json
{
  "status": "error",
  "message": "Unsupported file type"
}
```

---

# 6. Query APIs

# 6.1 Incident Query API

## Endpoint

```http
POST /api/v1/query/ask
```

---

## Purpose

Perform RAG-based querying against operational incidents and logs.

---

## Request Body

```json
{
  "query": "What caused the payment failure?"
}
```

---

## Success Response

```json
{
  "status": "success",
  "query": "What caused the payment failure?",
  "response": "The incident was likely caused by database timeout errors.",
  "retrieved_chunks": 4
}
```

---

## Failure Response

```json
{
  "status": "error",
  "message": "Query processing failed"
}
```

---

# 7. Incident APIs

# 7.1 Retrieve Similar Incidents

## Endpoint

```http
POST /api/v1/incidents/similar
```

---

## Purpose

Retrieve semantically similar historical incidents.

---

## Request Body

```json
{
  "query": "database timeout issue"
}
```

---

## Success Response

```json
{
  "status": "success",
  "results": [
    {
      "incident_id": "INC001",
      "similarity_score": 0.91,
      "summary": "Previous timeout incident"
    }
  ]
}
```

---

# 8. Health Check APIs

# 8.1 Health Check Endpoint

## Endpoint

```http
GET /api/v1/health
```

---

## Purpose

Verify backend service availability.

---

## Success Response

```json
{
  "status": "healthy"
}
```

---

# 9. Future APIs

## Planned APIs

### RCA APIs
```http
POST /api/v1/rca/analyze
```

---

### Anomaly Detection APIs
```http
POST /api/v1/anomaly/detect
```

---

### Incident Clustering APIs
```http
POST /api/v1/incidents/cluster
```

---

### Agent Workflow APIs
```http
POST /api/v1/agents/execute
```

---

# 10. Request Validation Strategy

The platform will use:
- Pydantic models
- schema validation
- type validation
- structured error responses

---

# 11. API Response Standards

All responses follow:

```json
{
  "status": "success | error",
  "message": "response message"
}
```

---

# 12. Error Handling Strategy

## Planned Error Categories

| Error Type | Example |
|---|---|
| Validation Errors | Invalid request payload |
| File Errors | Unsupported file type |
| AI Errors | LLM processing failure |
| Retrieval Errors | No relevant context found |
| Internal Errors | Unexpected backend failure |

---

# 13. Authentication Strategy (Future)

MVP excludes authentication.

Future plans include:
- JWT authentication
- RBAC
- API tokens
- enterprise access control

---

# 14. API Security Considerations

## Planned Security Features

- request validation
- payload sanitization
- environment-based secrets
- rate limiting (future)
- secure API handling

---

# 15. API Performance Goals

| Metric | Target |
|---|---|
| Health Check Response | < 500ms |
| Query Response | < 5 seconds |
| Upload Processing | Efficient chunking performance |

---

# 16. API Versioning Strategy

API versioning format:

```text
/api/v1/
```

Future versions:
```text
/api/v2/
```

---

# 17. Future Enhancements

Future API capabilities may include:
- streaming responses
- WebSocket support
- asynchronous processing
- batch ingestion
- real-time incident analysis

---

# 18. API Architecture Principles

The APIs follow:
- modular design
- RESTful architecture
- service separation
- scalable backend practices
- maintainable API contracts

---

---

# Updates

## Update 1 — API Implementation (2026-05-18)

**Status:** Core incident APIs implemented and live.  
**Last Updated:** 2026-05-18

---

### Implemented Endpoints

The following endpoints are live and tested. All are accessible via Swagger UI at `http://localhost:8000/docs`.

---

#### POST /api/v1/incidents/ingest

Primary log ingestion endpoint. Replaces the planned `POST /api/v1/ingestion/upload`.

**Request body:**

```json
{
  "title": "High CPU usage on production server",
  "severity": "high",
  "raw_logs": "2026-05-18 10:00:01 ERROR CPU usage at 98%..."
}
```

**Success response (201):**

```json
{
  "incident_id": "b68cf463-ee90-424c-9ebe-acd7e033a68e",
  "message": "Logs ingested and processed successfully.",
  "chunks_created": 2
}
```

**What happens internally:**
1. Incident record created in PostgreSQL
2. Raw logs chunked via `RecursiveCharacterTextSplitter`
3. Chunks embedded via `all-MiniLM-L6-v2`
4. Embeddings stored in ChromaDB with incident metadata

---

#### GET /api/v1/incidents/

List all incidents with optional filtering and pagination.

**Query parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| skip | int | No | 0 | Pagination offset |
| limit | int | No | 50 | Max results (1–100) |
| status | string | No | null | Filter by status (`open`, `investigating`, `resolved`, `closed`) |
| severity | string | No | null | Filter by severity (`low`, `medium`, `high`, `critical`) |

**Success response (200):** Array of incident objects.

---

#### GET /api/v1/incidents/{incident_id}

Fetch a single incident by ID.

**Success response (200):**

```json
{
  "id": "b68cf463-ee90-424c-9ebe-acd7e033a68e",
  "title": "High CPU usage on production server",
  "description": null,
  "severity": "high",
  "status": "open",
  "rca_summary": null,
  "raw_logs": "...",
  "created_at": "2026-05-18T09:20:23Z",
  "updated_at": "2026-05-18T09:20:23Z"
}
```

**Error response (404):**

```json
{
  "detail": "Incident {incident_id} not found."
}
```

---

#### PATCH /api/v1/incidents/{incident_id}

Partially update an incident. Only provided fields are updated.

**Request body (all fields optional):**

```json
{
  "status": "investigating",
  "severity": "critical",
  "rca_summary": "Root cause identified as memory leak in payment service."
}
```

**Success response (200):** Updated incident object.

---

#### DELETE /api/v1/incidents/{incident_id}

Permanently delete an incident.

**Success response (204):** No content.

**Error response (404):**

```json
{
  "detail": "Incident {incident_id} not found."
}
```

---

#### GET /

Root endpoint — returns platform metadata.

**Success response (200):**

```json
{
  "name": "AI Incident Intelligence Platform",
  "version": "0.1.0",
  "status": "running",
  "environment": "development"
}
```

---

#### GET /health

Health check endpoint.

**Success response (200):**

```json
{
  "status": "healthy"
}
```

---

### Data Models

#### IncidentSeverity (enum)
`low` | `medium` | `high` | `critical`

#### IncidentStatus (enum)
`open` | `investigating` | `resolved` | `closed`

---

### Validation

All request bodies are validated using Pydantic v2. Invalid payloads return a `422 Unprocessable Entity` with field-level error details:

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "String should have at least 3 characters",
      "type": "string_too_short"
    }
  ]
}
```

---

### Deviations from Original Spec

| Original Plan | Implemented |
|---|---|
| `POST /api/v1/ingestion/upload` (file upload) | `POST /api/v1/incidents/ingest` (JSON body with raw log text) |
| `GET /api/v1/health` | `GET /health` (root level, not versioned) |
| Response envelope `{"status": "success", ...}` | Direct object responses per FastAPI/OpenAPI conventions |

File upload support (`multipart/form-data`) is planned for Phase 2.

---

### Swagger UI

Full interactive API documentation is auto-generated and available at:

```
http://localhost:8000/docs
```

ReDoc documentation is also available at:

```
http://localhost:8000/redoc
```

OpenAPI JSON schema at:

```
http://localhost:8000/openapi.json
```