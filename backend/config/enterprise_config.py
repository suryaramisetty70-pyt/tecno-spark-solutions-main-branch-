"""Enterprise-Grade Configuration Management"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    username: str = os.getenv("DB_USER", "postgres")
    password: str = os.getenv("DB_PASSWORD", "")
    database: str = os.getenv("DB_NAME", "buddy_ai")
    pool_size: int = int(os.getenv("DB_POOL_SIZE", "10"))
    max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    use_sqlite: bool = os.getenv("USE_SQLITE", "true").lower() == "true"

@dataclass
class APIConfig:
    """API configuration"""
    host: str = os.getenv("API_HOST", "0.0.0.0")
    port: int = int(os.getenv("API_PORT", "8000"))
    workers: int = int(os.getenv("API_WORKERS", "4"))
    reload: bool = os.getenv("API_RELOAD", "false").lower() == "true"
    cors_origins: Optional[list] = None
    rate_limit: int = int(os.getenv("RATE_LIMIT", "100"))

@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire: int = int(os.getenv("TOKEN_EXPIRE", "1800"))
    password_min_length: int = int(os.getenv("PWD_MIN_LENGTH", "8"))
    enable_https: bool = os.getenv("ENABLE_HTTPS", "true").lower() == "true"
    max_login_attempts: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))

@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    enable_metrics: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    enable_logging: bool = os.getenv("ENABLE_LOGGING", "true").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    sentry_dsn: Optional[str] = os.getenv("SENTRY_DSN")
    metrics_port: int = int(os.getenv("METRICS_PORT", "9090"))

class Config:
    """Main configuration class"""

    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = self.environment == "development"
        self.database = DatabaseConfig()
        self.api = APIConfig()
        self.security = SecurityConfig()
        self.monitoring = MonitoringConfig()
        self.validate()

    def validate(self) -> None:
        """Validate configuration"""
        if self.environment not in ["development", "staging", "production"]:
            raise ValueError(f"Invalid environment: {self.environment}")

        if self.environment == "production" and self.security.secret_key == "change-me-in-production":
            raise ValueError("SECRET_KEY must be changed in production")

        logger.info(f"Configuration loaded for {self.environment} environment")

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "environment": self.environment,
            "debug": self.debug,
            "database": {
                "host": self.database.host,
                "port": self.database.port,
                "database": self.database.database,
                "pool_size": self.database.pool_size,
                "use_sqlite": self.database.use_sqlite
            },
            "api": {
                "host": self.api.host,
                "port": self.api.port,
                "workers": self.api.workers,
                "rate_limit": self.api.rate_limit
            },
            "security": {
                "jwt_algorithm": self.security.jwt_algorithm,
                "token_expire": self.security.access_token_expire,
                "password_min_length": self.security.password_min_length,
                "https_enabled": self.security.enable_https
            },
            "monitoring": {
                "metrics_enabled": self.monitoring.enable_metrics,
                "logging_enabled": self.monitoring.enable_logging,
                "log_level": self.monitoring.log_level
            }
        }

@lru_cache(maxsize=1)
def get_config() -> Config:
    """Get singleton configuration instance"""
    return Config()
