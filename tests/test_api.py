import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.core.database import get_db
from app.models.base import Base
from app.models.incident import IncidentSeverity, IncidentStatus


# =============================================================================
# Shared Test Database Setup
# =============================================================================

# Module-level shared engine — all tests in this file use the same DB
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False}
)
TestSession = sessionmaker(bind=TEST_ENGINE)


def get_test_db():
    """
    Returns a session backed by the shared in-memory SQLite engine.
    All requests within a test see the same data.
    """
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def override_db():
    """
    Creates tables before each test and drops them after.
    Ensures complete isolation between tests while sharing the engine.
    """
    Base.metadata.create_all(TEST_ENGINE)
    app.dependency_overrides[get_db] = get_test_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(TEST_ENGINE)


# =============================================================================
# Health & Root Endpoint Tests
# =============================================================================

@pytest.mark.asyncio
class TestHealthEndpoints:

    async def test_root_returns_200(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/")
        assert response.status_code == 200

    async def test_root_returns_platform_name(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/")
        assert response.json()["name"] == "AI Incident Intelligence Platform"

    async def test_root_returns_running_status(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/")
        assert response.json()["status"] == "running"

    async def test_health_returns_200(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health")
        assert response.status_code == 200

    async def test_health_returns_healthy(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health")
        assert response.json() == {"status": "healthy"}


# =============================================================================
# Incident CRUD Endpoint Tests
# =============================================================================

@pytest.mark.asyncio
class TestIncidentEndpoints:

    async def test_list_incidents_returns_200(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/incidents/")
        assert response.status_code == 200

    async def test_list_incidents_returns_empty_list_initially(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/incidents/")
        assert response.json() == []

    async def test_get_incident_returns_404_for_missing_id(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/incidents/non-existent-id")
        assert response.status_code == 404

    async def test_get_incident_404_contains_detail_message(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/incidents/non-existent-id")
        assert "detail" in response.json()

    async def test_update_incident_returns_404_for_missing_id(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.patch(
                "/api/v1/incidents/non-existent-id",
                json={"status": "resolved"}
            )
        assert response.status_code == 404

    async def test_delete_incident_returns_404_for_missing_id(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.delete("/api/v1/incidents/non-existent-id")
        assert response.status_code == 404

    async def test_list_incidents_filter_by_severity(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/incidents/?severity=critical")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_list_incidents_filter_by_status(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/incidents/?status=open")
        assert response.status_code == 200

    async def test_list_incidents_pagination_params(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/incidents/?skip=0&limit=10")
        assert response.status_code == 200

    async def test_list_incidents_invalid_limit_returns_422(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/incidents/?limit=200")
        assert response.status_code == 422


# =============================================================================
# Log Ingest Endpoint Tests
# =============================================================================

@pytest.mark.asyncio
class TestIngestEndpoint:

    @patch("app.api.v1.incidents.chunk_logs")
    @patch("app.api.v1.incidents.store_chunks")
    async def test_ingest_returns_201(self, mock_store, mock_chunk):
        mock_chunk.return_value = [{"text": "log chunk", "metadata": {"incident_id": "x", "chunk_index": 0, "total_chunks": 1}}]
        mock_store.return_value = 1

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/incidents/ingest",
                json={
                    "title": "CPU spike on prod",
                    "severity": "high",
                    "raw_logs": "ERROR: CPU usage at 98% on node-prod-3",
                }
            )
        assert response.status_code == 201

    @patch("app.api.v1.incidents.chunk_logs")
    @patch("app.api.v1.incidents.store_chunks")
    async def test_ingest_returns_incident_id(self, mock_store, mock_chunk):
        mock_chunk.return_value = []
        mock_store.return_value = 0

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/incidents/ingest",
                json={
                    "title": "Memory leak detected",
                    "severity": "critical",
                    "raw_logs": "CRITICAL: OOM killer triggered on node-1",
                }
            )
        data = response.json()
        assert "incident_id" in data
        assert len(data["incident_id"]) == 36  # UUID format

    @patch("app.api.v1.incidents.chunk_logs")
    @patch("app.api.v1.incidents.store_chunks")
    async def test_ingest_returns_chunks_created(self, mock_store, mock_chunk):
        mock_chunk.return_value = [
            {"text": "chunk 1", "metadata": {"incident_id": "x", "chunk_index": 0, "total_chunks": 2}},
            {"text": "chunk 2", "metadata": {"incident_id": "x", "chunk_index": 1, "total_chunks": 2}},
        ]
        mock_store.return_value = 2

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/incidents/ingest",
                json={
                    "title": "DB connection failure",
                    "severity": "critical",
                    "raw_logs": "ERROR: connection pool exhausted. Max: 10",
                }
            )
        assert response.json()["chunks_created"] == 2

    async def test_ingest_missing_title_returns_422(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/incidents/ingest",
                json={
                    "severity": "high",
                    "raw_logs": "ERROR: something failed",
                }
            )
        assert response.status_code == 422

    async def test_ingest_missing_raw_logs_returns_422(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/incidents/ingest",
                json={
                    "title": "Some incident",
                    "severity": "high",
                }
            )
        assert response.status_code == 422

    async def test_ingest_title_too_short_returns_422(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/incidents/ingest",
                json={
                    "title": "ab",
                    "severity": "high",
                    "raw_logs": "ERROR: something failed",
                }
            )
        assert response.status_code == 422

    async def test_ingest_invalid_severity_returns_422(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/incidents/ingest",
                json={
                    "title": "Some incident",
                    "severity": "catastrophic",
                    "raw_logs": "ERROR: something failed",
                }
            )
        assert response.status_code == 422


# =============================================================================
# RAG Query Endpoint Tests
# =============================================================================

@pytest.mark.asyncio
class TestQueryEndpoints:

    @patch("app.api.v1.query.query_incident")
    async def test_ask_returns_200(self, mock_query):
        mock_query.return_value = {
            "response": "The service failed due to DB exhaustion.",
            "chunks_used": 2,
            "sources": [],
        }

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/query/ask",
                json={"query": "What caused the payment failure?"}
            )
        assert response.status_code == 200

    @patch("app.api.v1.query.query_incident")
    async def test_ask_returns_correct_fields(self, mock_query):
        mock_query.return_value = {
            "response": "CPU spike caused by runaway process.",
            "chunks_used": 1,
            "sources": [{"incident_id": "inc-001", "chunk_index": 0, "similarity_score": 0.85}],
        }

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/query/ask",
                json={"query": "What caused the CPU spike?", "top_k": 3}
            )
        data = response.json()
        assert "query" in data
        assert "response" in data
        assert "chunks_used" in data
        assert "sources" in data

    async def test_ask_query_too_short_returns_422(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/query/ask",
                json={"query": "why"}
            )
        assert response.status_code == 422

    async def test_ask_missing_query_returns_422(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/query/ask",
                json={}
            )
        assert response.status_code == 422

    async def test_rca_returns_404_for_missing_incident(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/query/rca/non-existent-incident-id"
            )
        assert response.status_code == 404

    @patch("app.api.v1.query.generate_rca")
    async def test_rca_returns_200_for_existing_incident(self, mock_rca):
        mock_rca.return_value = {
            "rca": "1. Root Cause: DB connection exhaustion.",
            "chunks_analyzed": 2,
        }

        with patch("app.api.v1.incidents.chunk_logs", return_value=[]):
            with patch("app.api.v1.incidents.store_chunks", return_value=0):
                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test"
                ) as client:
                    ingest_response = await client.post(
                        "/api/v1/incidents/ingest",
                        json={
                            "title": "Payment service failure",
                            "severity": "critical",
                            "raw_logs": "ERROR: connection pool exhausted",
                        }
                    )
                    incident_id = ingest_response.json()["incident_id"]

                    rca_response = await client.post(
                        f"/api/v1/query/rca/{incident_id}"
                    )

        assert rca_response.status_code == 200

    @patch("app.api.v1.query.generate_rca")
    async def test_rca_returns_correct_fields(self, mock_rca):
        mock_rca.return_value = {
            "rca": "Root cause: max_connections reached.",
            "chunks_analyzed": 3,
        }

        with patch("app.api.v1.incidents.chunk_logs", return_value=[]):
            with patch("app.api.v1.incidents.store_chunks", return_value=0):
                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test"
                ) as client:
                    ingest_response = await client.post(
                        "/api/v1/incidents/ingest",
                        json={
                            "title": "DB connection failure",
                            "severity": "critical",
                            "raw_logs": "ERROR: connection refused",
                        }
                    )
                    incident_id = ingest_response.json()["incident_id"]

                    rca_response = await client.post(
                        f"/api/v1/query/rca/{incident_id}"
                    )

        data = rca_response.json()
        assert "incident_id" in data
        assert "rca" in data
        assert "chunks_analyzed" in data