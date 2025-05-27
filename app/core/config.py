from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Event Builder API"
    API_V1_STR: str = "/api/v1"

    # PostgreSQL Configuration
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "P0StGr35**")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "202.4.127.189")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5632")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "event_builder")
    DATABASE_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    # MinIO Configuration
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9100")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "replica-event-images")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "False").lower() == "true"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:4200"] # Angular dev server

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()