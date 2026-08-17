from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_provider: str = "gemini"
    llm_model: str = "gemini-2.5-flash"
    gemini_api_key: str = ""
    llm_api_key: str = ""  # For OpenAI/other fallback
    llm_timeout: int = 15

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def validate_provider(self) -> Self:
        if self.llm_provider == "gemini" and not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY must be configured when LLM_PROVIDER is 'gemini'")
        return self


settings = Settings()
