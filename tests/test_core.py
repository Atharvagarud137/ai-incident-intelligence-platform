import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from main import app
from app.core.config import settings
from app.core.providers.base import BaseLLMProvider
from app.core.providers.gemini_provider import GeminiProvider
from app.core.providers.ollama_provider import OllamaProvider
from app.core.providers import get_llm_provider


# =============================================================================
# Config Tests
# =============================================================================

class TestConfig:
    """Verify the settings object loads correctly from .env"""

    def test_app_name_is_set(self):
        assert settings.app_name == "AI Incident Intelligence Platform"

    def test_app_version_is_set(self):
        assert settings.app_version is not None
        assert len(settings.app_version) > 0

    def test_llm_provider_is_valid(self):
        assert settings.llm_provider in ["gemini", "ollama"]

    def test_gemini_api_key_is_loaded(self):
        # We just check it's not empty — never log or print the actual key
        assert settings.gemini_api_key != ""
        assert settings.gemini_api_key != "your_gemini_api_key_here"

    def test_chroma_persist_dir_is_set(self):
        assert settings.chroma_persist_dir is not None

    def test_embedding_model_is_set(self):
        assert settings.embedding_model == "all-MiniLM-L6-v2"


# =============================================================================
# LLM Provider Abstraction Tests
# =============================================================================

class TestBaseLLMProvider:
    """Ensure the abstract interface is enforced correctly."""

    def test_cannot_instantiate_base_provider(self):
        # BaseLLMProvider is abstract — direct instantiation must fail
        with pytest.raises(TypeError):
            BaseLLMProvider()

    def test_get_llm_provider_returns_gemini_by_default(self):
        with patch("app.core.providers.settings") as mock_settings:
            mock_settings.llm_provider = "gemini"
            mock_settings.gemini_api_key = settings.gemini_api_key
            mock_settings.gemini_model = settings.gemini_model

            with patch("app.core.providers.GeminiProvider") as mock_gemini:
                get_llm_provider()
                mock_gemini.assert_called_once()

    def test_get_llm_provider_returns_ollama_when_configured(self):
        with patch("app.core.providers.settings") as mock_settings:
            mock_settings.llm_provider = "ollama"

            with patch("app.core.providers.OllamaProvider") as mock_ollama:
                get_llm_provider()
                mock_ollama.assert_called_once()

    def test_get_llm_provider_raises_on_unknown_provider(self):
        with patch("app.core.providers.settings") as mock_settings:
            mock_settings.llm_provider = "unknown_provider"

            with pytest.raises(ValueError, match="Unknown LLM provider"):
                get_llm_provider()


# =============================================================================
# Gemini Provider Tests (mocked — no real API calls)
# =============================================================================

class TestGeminiProvider:
    """Test Gemini provider behaviour without hitting the real API."""

    @patch("app.core.providers.gemini_provider.genai")
    def test_initialisation_succeeds_with_valid_key(self, mock_genai):
        mock_genai.GenerativeModel.return_value = MagicMock()
        provider = GeminiProvider()
        assert provider.provider_name == "gemini"

    @patch("app.core.providers.gemini_provider.genai")
    def test_initialisation_fails_without_api_key(self, mock_genai):
        with patch("app.core.providers.gemini_provider.settings") as mock_settings:
            mock_settings.gemini_api_key = ""
            mock_settings.gemini_model = "gemini-2.0-flash"

            with pytest.raises(ValueError, match="GEMINI_API_KEY is not set"):
                GeminiProvider()

    @patch("app.core.providers.gemini_provider.genai")
    @pytest.mark.asyncio
    async def test_generate_returns_text(self, mock_genai):
        # Simulate a successful Gemini response
        mock_response = MagicMock()
        mock_response.text = "Incident root cause: high memory usage on node-3."

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        provider = GeminiProvider()
        result = await provider.generate("What caused this incident?")

        assert result == "Incident root cause: high memory usage on node-3."

    @patch("app.core.providers.gemini_provider.genai")
    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(self, mock_genai):
        mock_response = MagicMock()
        mock_response.text = "Summary: CPU spike at 03:42 UTC."

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        provider = GeminiProvider()
        result = await provider.generate(
            prompt="Summarise this log.",
            system_prompt="You are an SRE assistant."
        )

        assert "CPU spike" in result
        # Verify system prompt was prepended to the full prompt
        call_args = mock_model.generate_content.call_args[0][0]
        assert "You are an SRE assistant." in call_args

    @patch("app.core.providers.gemini_provider.genai")
    @pytest.mark.asyncio
    async def test_is_available_returns_true_on_success(self, mock_genai):
        mock_response = MagicMock()
        mock_response.text = "OK"

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        provider = GeminiProvider()
        result = await provider.is_available()
        assert result is True

    @patch("app.core.providers.gemini_provider.genai")
    @pytest.mark.asyncio
    async def test_is_available_returns_false_on_failure(self, mock_genai):
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API error")
        mock_genai.GenerativeModel.return_value = mock_model

        provider = GeminiProvider()
        result = await provider.is_available()
        assert result is False


# =============================================================================
# Ollama Provider Tests (mocked — Ollama not required to be running)
# =============================================================================

class TestOllamaProvider:
    """Test Ollama provider behaviour without requiring a local Ollama instance."""

    def test_initialisation_succeeds(self):
        provider = OllamaProvider()
        assert provider.provider_name == "ollama"

    @patch("app.core.providers.ollama_provider.ollama")
    @pytest.mark.asyncio
    async def test_generate_returns_text(self, mock_ollama):
        mock_ollama.chat.return_value = {
            "message": {"content": "Database connection pool exhausted."}
        }

        provider = OllamaProvider()
        result = await provider.generate("What caused this incident?")

        assert result == "Database connection pool exhausted."

    @patch("app.core.providers.ollama_provider.ollama")
    @pytest.mark.asyncio
    async def test_generate_includes_system_prompt(self, mock_ollama):
        mock_ollama.chat.return_value = {
            "message": {"content": "High CPU usage detected."}
        }

        provider = OllamaProvider()
        await provider.generate(
            prompt="Analyse this log.",
            system_prompt="You are an SRE expert."
        )

        # Verify system prompt was included in the messages list
        call_messages = mock_ollama.chat.call_args[1]["messages"]
        roles = [m["role"] for m in call_messages]
        assert "system" in roles

    @patch("app.core.providers.ollama_provider.ollama")
    @pytest.mark.asyncio
    async def test_is_available_returns_true_when_ollama_running(self, mock_ollama):
        mock_ollama.list.return_value = {"models": []}
        provider = OllamaProvider()
        result = await provider.is_available()
        assert result is True

    @patch("app.core.providers.ollama_provider.ollama")
    @pytest.mark.asyncio
    async def test_is_available_returns_false_when_ollama_not_running(self, mock_ollama):
        mock_ollama.list.side_effect = Exception("Connection refused")
        provider = OllamaProvider()
        result = await provider.is_available()
        assert result is False


# =============================================================================
# API Endpoint Tests
# =============================================================================

@pytest.mark.asyncio
class TestAPIEndpoints:
    """Test the FastAPI endpoints directly without a running server."""

    async def test_root_endpoint_returns_200(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/")
        assert response.status_code == 200

    async def test_root_endpoint_returns_correct_fields(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/")
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"

    async def test_health_endpoint_returns_200(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health")
        assert response.status_code == 200

    async def test_health_endpoint_returns_healthy(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health")
        assert response.json() == {"status": "healthy"}