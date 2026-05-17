from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    Central configuration class for the platform.
    All values are loaded from the .env file automatically.
    Adding a new config value is as simple as adding a field here.
    """

    # Application
    app_name: str = Field(default="AI Incident Intelligence Platform")
    app_version: str = Field(default="0.1.0")
    app_env: str = Field(default="development")
    debug: bool = Field(default=False)

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    # LLM Provider — controls which AI backend is used
    llm_provider: str = Field(default="gemini")  # "gemini" or "ollama"
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-2.0-flash")

    # Ollama (local LLM fallback)
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="mistral:7b")

    # Embeddings
    embedding_model: str = Field(default="all-MiniLM-L6-v2")

    # ChromaDB
    chroma_persist_dir: str = Field(default="./data/chroma")

    # PostgreSQL
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/incident_platform"
    )
    database_pool_size: int = Field(default=5)
    database_max_overflow: int = Field(default=10)

    # Logging
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="./logs/app.log")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached instance of Settings.
    Using lru_cache means the .env file is read once at startup,
    not on every request — which matters at scale.
    """
    return Settings()


# Module-level shortcut so you can do: from app.core.config import settings
settings = get_settings()