from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    GEMINI_API_KEY: str
    MODEL_NAME: str = "gemini-3.0-pro"
    EMBEDDINGS_MODEL: str = "gemini-embedding-2"
    JWT_SECRET: str
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
