from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FMCG Supply Chain Management API"
    environment: str = "development"

    supabase_url: str = ""
    supabase_key: str = ""
    supabase_secret_key: str = ""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        extra="ignore"
    )


settings = Settings()
