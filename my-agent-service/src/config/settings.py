from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "My Agent Service"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # API Security
    API_KEY: str = "default-api-key"

    # LLM Settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL_NAME: str = "gpt-4-turbo"

    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL_NAME: str = "claude-3-5-sonnet-latest"

    # LangChain / LangSmith Tracing
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "my-agent-service"

    # Database & Integrations
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    VECTOR_DB_URL: str = "http://localhost:6333"

    # CORS Allow List
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
