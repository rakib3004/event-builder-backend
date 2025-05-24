from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Event Builder API"
    API_V1_STR: str = "/api/v1"

    # PostgreSQL
    POSTGRES_SERVER: str = "192.168.52.212"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "112233"
    POSTGRES_DB: str = "simple_event_builder"
    DATABASE_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9100"
    MINIO_ACCESS_KEY: str = "TkYEaMlzMK97WOZLEV8j"
    MINIO_SECRET_KEY: str = "cNHZ7uBx7hzE3XMjoe7qhQdcYk95YiOYr4EBt6lF"
    MINIO_BUCKET_NAME: str = "event-images"
    MINIO_SECURE: bool = False # Set to True if using HTTPS

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:4200"] # Angular dev server

    class Config:
        case_sensitive = True
        env_file = ".env" # Optional: if you use a .env file

settings = Settings()


