from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Question Generator"
    APP_ENV: str = "development"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_question_generator"
    )
    VECTOR_DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_question_generator"
    )

    GEMINI_API_KEY: str
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "gemini-2.5-pro"
    
    EMBEDDING_MODEL: str = "text-embedding-004"
    EMBEDDING_DIMENSIONS: int = 3072

    MAX_FILE_SIZE_MB: int = 20
    MAX_GENERATION_ATTEMPTS: int = 3
    SIMILARITY_THRESHOLD: float = 0.85

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


settings = Settings()  # type: ignore
