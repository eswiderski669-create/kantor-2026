# Pydantic Settings loads configuration from environment variables and, optionally,
# from `.env` files — avoids hard-coded secrets.

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Repository root (parent of `backend/`) so a `.env` at project root is visible locally.
_REPO_ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            _REPO_ROOT / ".env",
            Path(".env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Corporate RAG API"
    debug: bool = False

    database_url: str | None = None
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    ollama_base_url: str = "http://localhost:11434"

    @property
    def database_url_sync(self) -> str:
        # Alembic uses a synchronous driver; the app uses asyncpg — map URL without duplicating secrets.
        if not self.database_url:
            msg = (
                "DATABASE_URL must be set (e.g. in `.env` at the repository root "
                "or via environment variables)."
            )
            raise ValueError(msg)
        url = self.database_url.strip()
        if url.startswith("postgresql+asyncpg://"):
            return "postgresql+psycopg://" + url.removeprefix("postgresql+asyncpg://")
        if url.startswith("postgresql://"):
            return "postgresql+psycopg://" + url.removeprefix("postgresql://")
        return url


settings = Settings()
