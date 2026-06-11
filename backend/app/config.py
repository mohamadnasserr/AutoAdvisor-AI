from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AutoAdvisor AI"
    environment: str = "local"

    database_url: str

    upload_dir: str = "uploads"
    model_dir: str = "models"

    llm_provider: str = "none"
    openai_api_key: str | None = None
    gemini_api_key: str | None = None

    redis_url: str = "redis://localhost:6379/0"
    chat_memory_ttl_seconds: int = 1800
    chat_memory_max_messages: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()