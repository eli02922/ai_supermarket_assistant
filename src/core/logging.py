from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, RedisDsn, Field
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql://user:password@localhost:5432/supermarket_ai"
    )
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: RedisDsn = Field(default="redis://localhost:6379")

    # LLM
    OPENAI_API_KEY: str = Field(default="")
    LLM_MODEL: str = "gpt-4"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # ML
    MLFLOW_TRACKING_URI: str = Field(default="http://localhost:5000")
    MODEL_REGISTRY_PATH: str = "./models"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://localhost:8000"])

    # Data
    DATA_GENERATION_BATCH_SIZE: int = 10000
    FORECAST_HORIZON_DAYS: int = 30

    # RAG
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 200
    RAG_COLLECTION_NAME: str = "supermarket_docs"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "./logs/app.log"
    JSON_LOGS: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()