from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """
    Abstract base class for all LLM providers.

    Any new provider (Gemini, Ollama, OpenAI, etc.) must implement
    these methods. This is what lets us swap providers via config
    without touching any business logic.
    """

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        """
        Generate a response from the LLM given a prompt.

        Args:
            prompt: The user prompt / query.
            system_prompt: Optional system-level instruction for the model.

        Returns:
            The model's response as a string.
        """
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check whether this provider is reachable and configured correctly.
        Used at startup to validate the environment before accepting requests.
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable name of the provider, used in logs."""
        pass