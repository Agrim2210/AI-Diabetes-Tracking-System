from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # ── Direct URL (used on Render) ───────────────────────────
    DATABASE_URL: Optional[str] = None

    # ── Individual parts (used locally) ──────────────────────
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "diabetes_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""

    # ── JWT ───────────────────────────────────────────────────
    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ── App ───────────────────────────────────────────────────
    APP_ENV: str = "development"

    def get_database_url(self) -> str:
        # Render provides DATABASE_URL directly — use it if available
        if self.DATABASE_URL:
            # Render gives postgres:// but SQLAlchemy needs postgresql://
            url = self.DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            return url
        # Local development — build from parts
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()