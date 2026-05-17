import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.providers.base import BaseLLMProvider
from app.core.config import settings
from app.core.logging import logger


class GeminiProvider(BaseLLMProvider):
    """
    Gemini API provider (Google AI Studio free tier).
    Uses gemini-1.5-flash by default — most generous free tier limits.
    """

    def __init__(self):
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not set in your .env file.")

        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        logger.info(f"GeminiProvider initialised | model={settings.gemini_model}")

    @property
    def provider_name(self) -> str:
        return "gemini"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        """
        Send a prompt to Gemini and return the response text.
        Retries up to 3 times with exponential backoff on failure —
        handles transient API errors gracefully.
        """
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = self.model.generate_content(full_prompt)
            return response.text

        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise

    async def is_available(self) -> bool:
        """Verify the API key works by making a minimal test call."""
        try:
            response = self.model.generate_content("Reply with the word OK only.")
            return bool(response.text)
        except Exception as e:
            logger.warning(f"Gemini availability check failed: {e}")
            return False