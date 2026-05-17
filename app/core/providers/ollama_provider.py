import ollama
from app.core.providers.base import BaseLLMProvider
from app.core.config import settings
from app.core.logging import logger


class OllamaProvider(BaseLLMProvider):
    """
    Ollama local LLM provider.
    Requires Ollama to be installed and running on the local machine.
    No API key needed — fully private, no data leaves your machine.
    """

    def __init__(self):
        self.model = settings.ollama_model
        self.base_url = settings.ollama_base_url
        logger.info(f"OllamaProvider initialised | model={self.model} | url={self.base_url}")

    @property
    def provider_name(self) -> str:
        return "ollama"

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        """
        Send a prompt to the local Ollama instance and return the response.
        """
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            response = ollama.chat(model=self.model, messages=messages)
            return response["message"]["content"]

        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise

    async def is_available(self) -> bool:
        """Check if Ollama is running and the configured model is available."""
        try:
            ollama.list()
            return True
        except Exception as e:
            logger.warning(f"Ollama availability check failed: {e}")
            return False