"""Enhanced BaseAgent - Enterprise Grade Implementation"""
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

class EnhancedBaseAgent(ABC):
    """Enterprise-grade base agent with comprehensive error handling, logging, and monitoring"""

    def __init__(self):
        self.name: str = "BaseAgent"
        self.description: str = "Base agent class"
        self.capabilities: List[str] = []
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.version: str = "1.0.0"
        self.created_at: datetime = datetime.utcnow()
        self.execution_count: int = 0
        self.error_count: int = 0
        self.last_execution: Optional[datetime] = None
        self.performance_metrics: Dict[str, float] = {}
        self.is_available: bool = True
        self.permissions: List[str] = []
        logger.info(f"Agent {self.name} initialized")

    @abstractmethod
    def process_intent(self, intent: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process user intent and determine action"""
        pass

    @abstractmethod
    def execute_action(self, action: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute determined action"""
        pass

    @abstractmethod
    def register_tools(self) -> None:
        """Register available tools"""
        pass

    def validate_intent(self, intent: str) -> bool:
        """Validate intent format and content"""
        if not intent or len(intent.strip()) == 0:
            logger.warning(f"{self.name}: Invalid intent - empty string")
            return False
        if len(intent) > 5000:
            logger.warning(f"{self.name}: Invalid intent - exceeds max length")
            return False
        return True

    def validate_parameters(self, action: str, parameters: Dict[str, Any]) -> bool:
        """Validate parameters against tool requirements"""
        if action not in self.tools:
            logger.error(f"{self.name}: Unknown action {action}")
            return False

        tool = self.tools[action]
        required_params = tool.get('required_params', [])

        for param in required_params:
            if param not in parameters:
                logger.error(f"{self.name}: Missing required parameter {param}")
                return False

        return True

    def check_permissions(self, action: str) -> bool:
        """Check if agent has permission to perform action"""
        if not self.is_available:
            logger.warning(f"{self.name}: Agent is not available")
            return False
        return True

    def execute_with_error_handling(self, intent: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute intent with comprehensive error handling"""
        try:
            self.last_execution = datetime.utcnow()

            if not self.validate_intent(intent):
                return {"status": "error", "message": "Invalid intent format"}

            if not self.check_permissions("process_intent"):
                return {"status": "error", "message": "Insufficient permissions"}

            result = self.process_intent(intent, context)
            self.execution_count += 1

            logger.info(f"{self.name}: Processed intent successfully", extra={"result": result})
            return result

        except Exception as e:
            self.error_count += 1
            logger.error(f"{self.name}: Error processing intent: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"Error processing intent: {str(e)}",
                "agent": self.name,
                "timestamp": datetime.utcnow().isoformat()
            }

    def get_status(self) -> Dict[str, Any]:
        """Get agent status and metrics"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "available": self.is_available,
            "execution_count": self.execution_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.execution_count, 1),
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "capabilities": len(self.capabilities),
            "tools": len(self.tools),
            "uptime": (datetime.utcnow() - self.created_at).total_seconds()
        }

    def get_capabilities(self) -> List[Dict[str, str]]:
        """Return formatted capabilities"""
        return [{"name": cap, "agent": self.name} for cap in self.capabilities]

    def get_tools(self) -> Dict[str, Any]:
        """Return formatted tools"""
        return {
            "agent": self.name,
            "tool_count": len(self.tools),
            "tools": self.tools
        }

    def log_activity(self, action: str, status: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log agent activity"""
        activity = {
            "agent": self.name,
            "action": action,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        logger.info(json.dumps(activity))

    def handle_error(self, error: Exception, context: Optional[str] = None) -> Dict[str, Any]:
        """Handle errors gracefully"""
        self.error_count += 1
        error_info = {
            "agent": self.name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        }
        logger.error(json.dumps(error_info))
        return {
            "status": "error",
            "error": error_info
        }

    def reset_metrics(self) -> None:
        """Reset performance metrics"""
        self.execution_count = 0
        self.error_count = 0
        logger.info(f"{self.name}: Metrics reset")
