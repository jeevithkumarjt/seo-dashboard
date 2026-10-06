from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    api_base_url: str = "http://localhost:8000"
    next_public_api_base_url: str = "http://localhost:8000"
    pagespeed_api_key: str | None = None
    gsc_client_id: str | None = None
    gsc_client_secret: str | None = None
    gsc_redirect_uri: str = "http://localhost:8000/api/v1/integrations/google/callback"
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    alert_from: str | None = None
    discord_webhook_url: str | None = None
    slack_webhook_url: str | None = None
    serp_delay_seconds: float = 5
    crawler_delay_seconds: float = 0.5
    crawler_user_agent: str = "InternalSEOAuditBot/1.0"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
