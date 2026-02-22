"""
config.py — Application Configuration
Reads from environment variables (.env file).
"""

from pydantic_settings import BaseSettings
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
    DB_PORT: int = 1433
    DB_NAME: str = "account_intelligence_dev"
    DB_USER: str = "ai_user"
    DB_PASSWORD: str = "Dev_P@ssw0rd_2024!"

    @property
    def DATABASE_URL(self) -> str:
        """SQLAlchemy connection string for SQL Server via pyodbc."""
        return (
            f"mssql+pyodbc://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            "?driver=ODBC+Driver+18+for+SQL+Server"
            "&TrustServerCertificate=yes"
        )

    # ── JWT ───────────────────────────────────────────────────────────────────
    JWT_SECRET: str = "dev-super-secret-jwt-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480

    # ── CORS ──────────────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # ── Azure OpenAI ──────────────────────────────────────────────────────────
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""  # e.g. https://<resource>.openai.azure.com/
    AZURE_OPENAI_API_VERSION: str = "2024-02-01"
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-4o"  # nombre del deployment en Azure
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = "text-embedding-3-small"
    MAX_TOKENS: int = 1024
    TEMPERATURE: float = 0.7

    # ── Embeddings (local fallback) ───────────────────────────────────────────
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    FAISS_INDEX_PATH: str = "/app/data/faiss_index"

    # ── Tavily Web Search ────────────────────────────────────────────────────
    TAVILY_API_KEY: str = ""
    TAVILY_MAX_RESULTS: int = 5
    REQUEST_TIMEOUT_SECONDS: int = 15

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
