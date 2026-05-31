"""Enterprise-Grade Logging & Monitoring"""
import logging
import logging.config
import json
from datetime import datetime
from typing import Dict, Any, Optional

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        return json.dumps(log_data, default=str)

class PerformanceLogger:
    """Log performance metrics"""

    def __init__(self):
        self.logger = logging.getLogger("performance")

    def log_api_call(self, method: str, endpoint: str, status: int, duration: float) -> None:
        """Log API call performance"""
        self.logger.info(
            f"API call: {method} {endpoint} -> {status} ({duration*1000:.2f}ms)"
        )

    def log_database_query(self, query: str, duration: float, rows: int) -> None:
        """Log database query performance"""
        self.logger.info(
            f"DB query executed in {duration*1000:.2f}ms, returned {rows} rows"
        )

    def log_agent_execution(self, agent_name: str, action: str, duration: float, success: bool) -> None:
        """Log agent execution"""
        status = "success" if success else "failed"
        self.logger.info(
            f"Agent {agent_name} executed action {action} in {duration*1000:.2f}ms ({status})"
        )

class SecurityLogger:
    """Log security events"""

    def __init__(self):
        self.logger = logging.getLogger("security")

    def log_login_attempt(self, user_id: str, success: bool, ip_address: str) -> None:
        """Log login attempt"""
        status = "success" if success else "failed"
        self.logger.warning(f"Login attempt {status}: user={user_id}, ip={ip_address}")

    def log_permission_denied(self, user_id: str, resource: str, ip_address: str) -> None:
        """Log permission denied"""
        self.logger.warning(f"Permission denied: user={user_id}, resource={resource}, ip={ip_address}")

    def log_api_key_generated(self, user_id: str, key_name: str) -> None:
        """Log API key generation"""
        self.logger.info(f"API key generated: user={user_id}, name={key_name}")

    def log_suspicious_activity(self, user_id: str, activity: str, ip_address: str) -> None:
        """Log suspicious activity"""
        self.logger.critical(f"Suspicious activity: user={user_id}, activity={activity}, ip={ip_address}")

def setup_logging():
    """Setup enterprise logging configuration"""
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JSONFormatter,
            },
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "json",
                "filename": "logs/buddy_ai.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10
            },
            "security_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "WARNING",
                "formatter": "json",
                "filename": "logs/security.log",
                "maxBytes": 10485760,
                "backupCount": 10
            },
            "performance_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": "logs/performance.log",
                "maxBytes": 10485760,
                "backupCount": 10
            },
        },
        "loggers": {
            "": {
                "level": "DEBUG",
                "handlers": ["console", "file"]
            },
            "security": {
                "level": "WARNING",
                "handlers": ["security_file", "console"],
                "propagate": False
            },
            "performance": {
                "level": "INFO",
                "handlers": ["performance_file"],
                "propagate": False
            },
        }
    }

    logging.config.dictConfig(logging_config)
    logging.info("Logging system initialized")
