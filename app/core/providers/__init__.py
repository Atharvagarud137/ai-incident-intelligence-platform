from app.core.config import settings
from app.core.providers.base import BaseLLMProvider
from app.core.providers.gemini_provider import GeminiProvider
from app.core.providers.ollama_provider import OllamaProvider
from app.core.logging import logger


def get_llm_provider() -> BaseLLMProvider:
    """
    Factory function — returns the correct LLM provider based on
    the LLM_PROVIDER value in .env. This is the only place in the
    codebase that knows which provider is active.
    """
    provider = settings.llm_provider.lower()

    if provider == "gemini":
        return GeminiProvider()
    elif provider == "ollama":
        return OllamaProvider()
    else:
        raise ValueError(
            f"Unknown LLM provider: '{provider}'. "
            f"Valid options are: 'gemini', 'ollama'"
        )


__all__ = ["get_llm_provider", "BaseLLMProvider"]