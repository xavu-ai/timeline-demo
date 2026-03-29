"""Application configuration via environment variables."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "app"
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/app"
    PORT: int = 6100
    CORS_ORIGINS: list[str] = ["http://localhost:8100"]

    class Config:
        env_file = ".env"


settings = Settings()
