"""
Configuration and settings for Buddy AI OS Backend
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""

    # ==================== Basic Settings ====================
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # ==================== Server ====================
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        env="ALLOWED_HOSTS"
    )
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="CORS_ORIGINS"
    )

    # ==================== Security ====================
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_EXPIRE_MINUTES: int = Field(default=15, env="JWT_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # ==================== Database ====================
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost:5432/buddy_ai",
        env="DATABASE_URL"
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )

    # ==================== AI Models ====================
    # Local AI (Ollama)
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    DEFAULT_LOCAL_MODEL: str = Field(default="mistral", env="DEFAULT_LOCAL_MODEL")

    # Cloud AI (Optional fallback)
    DEEPSEEK_API_KEY: str = Field(default="", env="DEEPSEEK_API_KEY")
    DEEPSEEK_API_URL: str = Field(
        default="https://api.deepseek.com/v1",
        env="DEEPSEEK_API_URL"
    )
    QWEN_API_KEY: str = Field(default="", env="QWEN_API_KEY")

    # ==================== Email Integration ====================
    GMAIL_CLIENT_ID: str = Field(default="", env="GMAIL_CLIENT_ID")
    GMAIL_CLIENT_SECRET: str = Field(default="", env="GMAIL_CLIENT_SECRET")

    # ==================== Messaging ====================
    # WhatsApp (Twilio)
    TWILIO_ACCOUNT_SID: str = Field(default="", env="TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: str = Field(default="", env="TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: str = Field(default="", env="TWILIO_PHONE_NUMBER")

    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(default="", env="TELEGRAM_BOT_TOKEN")

    # ==================== API Keys ====================
    SERPAPI_API_KEY: str = Field(default="", env="SERPAPI_API_KEY")
    NEWSAPI_KEY: str = Field(default="", env="NEWSAPI_KEY")

    # ==================== Deployment ====================
    DOMAIN: str = Field(default="localhost", env="DOMAIN")
    DEPLOYMENT_ENVIRONMENT: str = Field(default="local", env="DEPLOYMENT_ENVIRONMENT")

    # ==================== Monitoring ====================
    SENTRY_DSN: str = Field(default="", env="SENTRY_DSN")

    class Config:
        """Pydantic config"""
        env_file = "../.env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export settings instance
settings = get_settings()
