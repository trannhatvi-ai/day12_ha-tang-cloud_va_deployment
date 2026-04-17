from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "my-production-agent"
    app_version: str = "1.0.0"
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    redis_url: str = "redis://redis:6379/0"
    agent_api_key: str = "change-me"

    rate_limit_per_minute: int = 10
    monthly_budget_usd: float = 10.0
    estimated_cost_per_request_usd: float = 0.02
    conversation_ttl_seconds: int = 604800


settings = Settings()
