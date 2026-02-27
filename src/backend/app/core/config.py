"""
config.py — Application Configuration
Reads from environment variables (.env file).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # ── Application ───────────────────────────────────────────────────────────
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    API_PREFIX: str = "/api/v1"

    # ── Database (SQL Server) ─────────────────────────────────────────────────
    DB_HOST: str = "db"
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    DATABASE_URL: str

    # ── JWT ───────────────────────────────────────────────────────────────────
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_EXPIRE_DAYS: int

    # ── CORS ──────────────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # ── Azure OpenAI ──────────────────────────────────────────────────────────

    GEMINI_API_KEY: str
    GEMINI_EMBEDDING_MODEL: str = "models/text-embedding-004"
    MAX_TOKENS: int = 1024
    TEMPERATURE: float = 0.7

    # ── Embeddings (local fallback) ───────────────────────────────────────────
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    FAISS_INDEX_PATH: str = "/app/data/faiss_index"

    # ── Tavily Web Search ────────────────────────────────────────────────────
    TAVILY_API_KEY: str = ""
    TAVILY_MAX_RESULTS: int = 5
    REQUEST_TIMEOUT_SECONDS: int = 15

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra = "ignore"
    )

settings = Settings()
