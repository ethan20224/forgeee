from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "FORGE API"
    app_env: str = "development"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://speleg@localhost:5432/forge"
    database_url_sync: str = "postgresql://speleg@localhost:5432/forge"

    # Auth
    jwt_secret: str = "CHANGE-ME-IN-PRODUCTION-use-a-64-char-hex-string"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # DeepSeek
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-v4-flash"
    deepseek_vl_provider: str = "replicate"
    deepseek_vl_api_key: str = ""

    # Cloudflare R2
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "forge-photos"
    r2_public_url: str = ""

    # RevenueCat
    revenuecat_webhook_secret: str = ""

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    # Push Notifications
    expo_push_access_token: str = ""

    # PostHog
    posthog_api_key: str = ""
    posthog_host: str = "https://us.i.posthog.com"

    # CORS
    cors_origins: str = "http://localhost:8081,http://localhost:3000"

    # AI Simulation
    ai_simulation: bool = True

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: Application configuration via environment variables with Pydantic validation.

Flow:
1. Settings loaded from .env file and environment variables on first access
2. Cached via lru_cache so all modules share one instance
3. Imported via get_settings() wherever config is needed

Main Entry Point: get_settings()

Dependencies:
- pydantic_settings: env var parsing and validation
"""
