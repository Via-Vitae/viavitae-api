"""Application settings via Pydantic Settings.

Values come from the environment (12-factor). Nothing secret has a default;
a missing required value fails fast at startup instead of degrading silently.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["dev", "staging", "prod"]
SupportedLocale = Literal["lt", "en", "ru", "pl", "de"]


class Settings(BaseSettings):
    """Runtime configuration for every ViaVitae service module."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # application
    app_name: str = "viavitae-api"
    app_version: str = "0.1.0"
    environment: Environment = "dev"
    api_prefix: str = "v1"
    default_locale: SupportedLocale = "lt"
    log_level: str = "INFO"
    log_json: bool = True

    # network
    cors_allow_origins: list[str] = Field(default_factory=lambda: ["https://viavitae.eu"])
    trusted_hosts: list[str] = Field(default_factory=lambda: ["api.viavitae.eu"])
    request_timeout_seconds: float = 5.0

    # data
    database_url: SecretStr
    redis_url: SecretStr | None = None
    statement_timeout_ms: int = 5000

    # integrations (EU-resident instances only — see docs/architecture.md)
    bitrix24_webhook_url: SecretStr | None = None
    stripe_secret_key: SecretStr | None = None
    stripe_webhook_secret: SecretStr | None = None
    paysera_project_id: str | None = None
    paysera_sign_password: SecretStr | None = None

    # ai pastoral assistant
    llm_provider: Literal["self-hosted", "eu-saas"] = "self-hosted"
    llm_base_url: str | None = None
    llm_api_key: SecretStr | None = None
    embedding_model: str = "bge-m3"
    rag_top_k: int = 6
    ai_publication_requires_approval: bool = True

    # notifications
    smtp_url: SecretStr | None = None
    sms_provider_url: SecretStr | None = None

    @field_validator("database_url", mode="before")
    @classmethod
    def _require_async_driver(cls, value: object) -> object:
        """PostgreSQL URLs must use an async driver."""
        if isinstance(value, str) and value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @field_validator("cors_allow_origins", "trusted_hosts", mode="before")
    @classmethod
    def _split_csv(cls, value: object) -> object:
        """Allow comma-separated lists in environment variables."""
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached settings instance."""
    return Settings()


settings = get_settings()
