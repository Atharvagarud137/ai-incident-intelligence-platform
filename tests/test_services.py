import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.incident import Incident, IncidentSeverity, IncidentStatus
from app.schemas.incident import IncidentCreate, IncidentUpdate
from app.services.incident_service import (
    create_incident,
    get_incident,
    get_all_incidents,
    update_incident,
    delete_incident,
)
from app.services.chunking_service import chunk_logs
from app.services.embedding_service import embed_texts, embed_single
from app.services.vector_store_service import store_chunks, query_similar_chunks
from app.services.rag_service import query_incident, generate_rca


# =============================================================================
# Test Database Setup — uses SQLite in-memory for isolation
# =============================================================================

@pytest.fixture
def db_session():
    """
    Creates a fresh in-memory SQLite database for each test.
    Completely isolated — no data bleeds between tests.
    """
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


# =============================================================================
# Incident Service Tests
# =============================================================================

class TestIncidentService:
    """Tests for CRUD operations on the Incident model."""

    def test_create_incident_success(self, db_session):
        data = IncidentCreate(
            title="Database connection failure",
            severity=IncidentSeverity.HIGH,
            raw_logs="ERROR: Connection pool exhausted",
        )
        incident = create_incident(db_session, data)

        assert incident.id is not None
        assert incident.title == "Database connection failure"
        assert incident.severity == IncidentSeverity.HIGH
        assert incident.status == IncidentStatus.OPEN
        assert incident.raw_logs == "ERROR: Connection pool exhausted"

    def test_create_incident_generates_uuid(self, db_session):
        data = IncidentCreate(title="Test incident", severity=IncidentSeverity.LOW)
        incident = create_incident(db_session, data)

        # UUID format: 8-4-4-4-12 characters
        assert len(incident.id) == 36
        assert incident.id.count("-") == 4

    def test_create_incident_default_status_is_open(self, db_session):
        data = IncidentCreate(title="Test incident", severity=IncidentSeverity.MEDIUM)
        incident = create_incident(db_session, data)
        assert incident.status == IncidentStatus.OPEN

    def test_get_incident_returns_correct_incident(self, db_session):
        data = IncidentCreate(title="CPU spike", severity=IncidentSeverity.CRITICAL)
        created = create_incident(db_session, data)

        fetched = get_incident(db_session, created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.title == "CPU spike"

    def test_get_incident_returns_none_for_missing_id(self, db_session):
        result = get_incident(db_session, "non-existent-id-12345")
        assert result is None

    def test_get_all_incidents_returns_all(self, db_session):
        for i in range(3):
            create_incident(
                db_session,
                IncidentCreate(title=f"Incident {i}", severity=IncidentSeverity.LOW),
            )
        incidents = get_all_incidents(db_session)
        assert len(incidents) == 3

    def test_get_all_incidents_filters_by_status(self, db_session):
        create_incident(db_session, IncidentCreate(title="Open incident", severity=IncidentSeverity.LOW))
        inc = create_incident(db_session, IncidentCreate(title="Resolved incident", severity=IncidentSeverity.LOW))
        update_incident(db_session, inc.id, IncidentUpdate(status=IncidentStatus.RESOLVED))

        open_incidents = get_all_incidents(db_session, status=IncidentStatus.OPEN)
        assert len(open_incidents) == 1
        assert open_incidents[0].title == "Open incident"

    def test_get_all_incidents_filters_by_severity(self, db_session):
        create_incident(db_session, IncidentCreate(title="High incident", severity=IncidentSeverity.HIGH))
        create_incident(db_session, IncidentCreate(title="Low incident", severity=IncidentSeverity.LOW))

        high_incidents = get_all_incidents(db_session, severity=IncidentSeverity.HIGH)
        assert len(high_incidents) == 1
        assert high_incidents[0].title == "High incident"

    def test_update_incident_updates_fields(self, db_session):
        data = IncidentCreate(title="Original title", severity=IncidentSeverity.LOW)
        created = create_incident(db_session, data)

        updated = update_incident(
            db_session,
            created.id,
            IncidentUpdate(title="Updated title", status=IncidentStatus.INVESTIGATING),
        )

        assert updated.title == "Updated title"
        assert updated.status == IncidentStatus.INVESTIGATING

    def test_update_incident_only_updates_provided_fields(self, db_session):
        data = IncidentCreate(title="Original", severity=IncidentSeverity.HIGH)
        created = create_incident(db_session, data)

        update_incident(db_session, created.id, IncidentUpdate(status=IncidentStatus.RESOLVED))

        # Title should remain unchanged
        fetched = get_incident(db_session, created.id)
        assert fetched.title == "Original"
        assert fetched.severity == IncidentSeverity.HIGH

    def test_update_incident_returns_none_for_missing_id(self, db_session):
        result = update_incident(db_session, "non-existent-id", IncidentUpdate(title="New title"))
        assert result is None

    def test_delete_incident_removes_from_db(self, db_session):
        data = IncidentCreate(title="To be deleted", severity=IncidentSeverity.LOW)
        created = create_incident(db_session, data)

        result = delete_incident(db_session, created.id)
        assert result is True
        assert get_incident(db_session, created.id) is None

    def test_delete_incident_returns_false_for_missing_id(self, db_session):
        result = delete_incident(db_session, "non-existent-id")
        assert result is False


# =============================================================================
# Chunking Service Tests
# =============================================================================

class TestChunkingService:
    """Tests for the log chunking pipeline."""

    def test_chunk_logs_returns_list(self):
        logs = "2026-05-20 ERROR service crashed\n2026-05-20 CRITICAL memory exhausted"
        chunks = chunk_logs(logs, "test-incident-001")
        assert isinstance(chunks, list)
        assert len(chunks) > 0

    def test_chunk_logs_contains_text_and_metadata(self):
        logs = "2026-05-20 ERROR connection refused"
        chunks = chunk_logs(logs, "test-incident-001")
        assert "text" in chunks[0]
        assert "metadata" in chunks[0]

    def test_chunk_logs_metadata_contains_incident_id(self):
        logs = "2026-05-20 ERROR timeout on node-1"
        chunks = chunk_logs(logs, "incident-abc-123")
        assert chunks[0]["metadata"]["incident_id"] == "incident-abc-123"

    def test_chunk_logs_metadata_contains_chunk_index(self):
        logs = "2026-05-20 ERROR timeout on node-1"
        chunks = chunk_logs(logs, "test-incident-001")
        assert chunks[0]["metadata"]["chunk_index"] == 0

    def test_chunk_logs_empty_string_returns_empty_list(self):
        chunks = chunk_logs("", "test-incident-001")
        assert chunks == []

    def test_chunk_logs_whitespace_only_returns_empty_list(self):
        chunks = chunk_logs("   \n\n  ", "test-incident-001")
        assert chunks == []

    def test_chunk_logs_large_text_creates_multiple_chunks(self):
        # Generate a log large enough to require multiple chunks (>512 chars)
        logs = "\n".join([
            f"2026-05-20 10:00:{i:02d} ERROR Service timeout on node-{i} — connection refused by upstream"
            for i in range(20)
        ])
        chunks = chunk_logs(logs, "test-incident-large")
        assert len(chunks) > 1

    def test_chunk_logs_total_chunks_metadata_is_accurate(self):
        logs = "\n".join([
            f"2026-05-20 10:00:{i:02d} ERROR Service timeout on node-{i}"
            for i in range(20)
        ])
        chunks = chunk_logs(logs, "test-incident-001")
        for chunk in chunks:
            assert chunk["metadata"]["total_chunks"] == len(chunks)


# =============================================================================
# Embedding Service Tests (mocked — no model loading in tests)
# =============================================================================

class TestEmbeddingService:
    """Tests for embedding generation — model is mocked to avoid slow loading."""

    @patch("app.services.embedding_service._model")
    def test_embed_texts_returns_list(self, mock_model):
        mock_model.encode.return_value = MagicMock()
        mock_model.encode.return_value.tolist.return_value = [[0.1, 0.2, 0.3]]

        result = embed_texts(["test log entry"])
        assert isinstance(result, list)

    @patch("app.services.embedding_service._model")
    def test_embed_texts_empty_input_returns_empty_list(self, mock_model):
        result = embed_texts([])
        assert result == []
        mock_model.encode.assert_not_called()

    @patch("app.services.embedding_service.embed_texts")
    def test_embed_single_returns_first_element(self, mock_embed_texts):
        mock_embed_texts.return_value = [[0.1, 0.2, 0.3]]
        result = embed_single("test query")
        assert result == [0.1, 0.2, 0.3]

    @patch("app.services.embedding_service.embed_texts")
    def test_embed_single_empty_returns_empty_list(self, mock_embed_texts):
        mock_embed_texts.return_value = []
        result = embed_single("")
        assert result == []


# =============================================================================
# Vector Store Service Tests (mocked — no ChromaDB in tests)
# =============================================================================

class TestVectorStoreService:
    """Tests for ChromaDB operations — fully mocked."""

    @patch("app.services.vector_store_service.get_collection")
    @patch("app.services.vector_store_service.embed_texts")
    def test_store_chunks_returns_correct_count(self, mock_embed, mock_collection):
        mock_embed.return_value = [[0.1] * 384, [0.2] * 384]
        mock_col = MagicMock()
        mock_collection.return_value = mock_col

        chunks = [
            {"text": "log line 1", "metadata": {"incident_id": "inc-001", "chunk_index": 0, "total_chunks": 2}},
            {"text": "log line 2", "metadata": {"incident_id": "inc-001", "chunk_index": 1, "total_chunks": 2}},
        ]
        result = store_chunks(chunks)
        assert result == 2

    @patch("app.services.vector_store_service.get_collection")
    @patch("app.services.vector_store_service.embed_texts")
    def test_store_chunks_calls_upsert(self, mock_embed, mock_collection):
        mock_embed.return_value = [[0.1] * 384]
        mock_col = MagicMock()
        mock_collection.return_value = mock_col

        chunks = [
            {"text": "log line 1", "metadata": {"incident_id": "inc-001", "chunk_index": 0, "total_chunks": 1}},
        ]
        store_chunks(chunks)
        mock_col.upsert.assert_called_once()

    def test_store_chunks_empty_input_returns_zero(self):
        result = store_chunks([])
        assert result == 0

    @patch("app.services.vector_store_service.get_collection")
    @patch("app.services.vector_store_service.embed_single")
    def test_query_similar_chunks_returns_list(self, mock_embed, mock_collection):
        mock_embed.return_value = [0.1] * 384
        mock_col = MagicMock()
        mock_col.query.return_value = {
            "documents": [["log chunk text"]],
            "metadatas": [[{"incident_id": "inc-001", "chunk_index": 0}]],
            "distances": [[0.3]],
        }
        mock_collection.return_value = mock_col

        results = query_similar_chunks("what caused the failure?", incident_id="inc-001")
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0]["text"] == "log chunk text"
        assert results[0]["similarity_score"] == 0.7  # 1 - 0.3

    @patch("app.services.vector_store_service.get_collection")
    @patch("app.services.vector_store_service.embed_single")
    def test_query_similar_chunks_empty_results(self, mock_embed, mock_collection):
        mock_embed.return_value = [0.1] * 384
        mock_col = MagicMock()
        mock_col.query.return_value = {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        mock_collection.return_value = mock_col

        results = query_similar_chunks("what caused the failure?")
        assert results == []


# =============================================================================
# RAG Service Tests (mocked — no real LLM calls)
# =============================================================================

class TestRAGService:
    """Tests for the RAG query engine and RCA generation."""

    @pytest.mark.asyncio
    @patch("app.services.rag_service.query_similar_chunks")
    @patch("app.services.rag_service.get_llm_provider")
    async def test_query_incident_returns_response(self, mock_provider, mock_chunks):
        mock_chunks.return_value = [
            {
                "text": "CPU usage at 98% on node-prod-3",
                "metadata": {"incident_id": "inc-001", "chunk_index": 0},
                "similarity_score": 0.85,
            }
        ]
        mock_llm = MagicMock()
        mock_llm.generate = AsyncMock(return_value="The CPU spike was caused by a runaway process.")
        mock_provider.return_value = mock_llm

        result = await query_incident("What caused the CPU spike?", incident_id="inc-001")

        assert "response" in result
        assert result["chunks_used"] == 1
        assert "sources" in result
        assert result["response"] == "The CPU spike was caused by a runaway process."

    @pytest.mark.asyncio
    @patch("app.services.rag_service.query_similar_chunks")
    async def test_query_incident_no_chunks_returns_message(self, mock_chunks):
        mock_chunks.return_value = []

        result = await query_incident("What caused the failure?")

        assert result["chunks_used"] == 0
        assert "No relevant log data" in result["response"]

    @pytest.mark.asyncio
    @patch("app.services.rag_service.query_similar_chunks")
    @patch("app.services.rag_service.get_llm_provider")
    async def test_generate_rca_returns_rca_and_chunk_count(self, mock_provider, mock_chunks):
        mock_chunks.return_value = [
            {
                "text": "ERROR: connection pool exhausted",
                "metadata": {"incident_id": "inc-001", "chunk_index": 0},
                "similarity_score": 0.9,
            }
        ]
        mock_llm = MagicMock()
        mock_llm.generate = AsyncMock(return_value="1. Incident Summary: DB connection failure.\n2. Root Cause: max_connections reached.")
        mock_provider.return_value = mock_llm

        result = await generate_rca("inc-001")

        assert "rca" in result
        assert result["chunks_analyzed"] == 1
        assert "Root Cause" in result["rca"]

    @pytest.mark.asyncio
    @patch("app.services.rag_service.query_similar_chunks")
    async def test_generate_rca_no_chunks_returns_message(self, mock_chunks):
        mock_chunks.return_value = []

        result = await generate_rca("inc-001")

        assert result["chunks_analyzed"] == 0
        assert "No log data found" in result["rca"]