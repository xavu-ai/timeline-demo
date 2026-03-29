"""Application configuration via environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "app"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/app"
    PORT: int = 6100
    CORS_ORIGINS: list[str] = ["http://localhost:8100"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
