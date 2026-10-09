"""
Application configuration loaded from environment variables.
Uses pydantic-settings for type-safe config with validation.
"""
from functools import lru_cache
from typing import List, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_env: Literal["development", "production", "test"] = "development"
    log_level: str = "INFO"

    # PostgreSQL
    postgres_user: str = "crimenet"
    postgres_password: str = "crimenet_dev"
    postgres_db: str = "crimenet_db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def sync_database_url(self) -> str:
        """For Alembic migrations (sync driver)."""
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "crimenet_neo4j"

    # Auth
    secret_key: str = "CHANGE_ME_IN_PRODUCTION"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    algorithm: str = "HS256"
    # Local prototype mode: serve the app as a shared demo without a login flow.
    auth_disabled: bool = False

    # LLM
    llm_provider: Literal["openai", "anthropic", "gemini", "mock"] = "mock"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    llm_model: str = "gpt-4o-mini"

    # File storage
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 50

    # CORS
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    # External APIs
    google_maps_api_key: str = ""
    nominatim_user_agent: str = "crimenet-prototype"


@lru_cache
def get_settings() -> Settings:
    return Settings()
