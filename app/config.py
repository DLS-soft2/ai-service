from importlib.metadata import PackageNotFoundError, version

from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_default_service_version() -> str:
    """Derive the default service version from installed package metadata."""
    try:
        return version("ai-service")
    except PackageNotFoundError:
        return "0.1.0"


class Settings(BaseSettings):
    """Configuration loaded from environment variables with sensible defaults."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = "ai-service"
    service_version: str = _get_default_service_version()

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:1b"
    ollama_timeout_seconds: int = 120


settings = Settings()
