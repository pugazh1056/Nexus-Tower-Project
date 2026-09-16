from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Nexus Tower"
    app_version: str = "1.0.0"
    app_env: str = "development"
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    api_prefix: str = "/api"

    supabase_url: Optional[str] = "https://placeholder-project.supabase.co"
    supabase_key: Optional[str] = "placeholder-anon-key"
    supabase_secret_key: Optional[str] = None

    # Master Agent Orchestration Webhook Configuration
    master_webhook_url: Optional[str] = None
    master_webhook_timeout_seconds: float = 10.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
