"""
Model Router - Intelligently selects between local and cloud AI models
Routes requests to optimal model based on task, hardware, and cost
"""

import logging
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ModelProvider(str, Enum):
    """AI model providers"""
    OLLAMA_LOCAL = "ollama_local"
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    LLAMA = "llama"
    MISTRAL = "mistral"


class TaskComplexity(str, Enum):
    """Task complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


@dataclass
class LocalModel:
    """Local AI model configuration"""
    model_id: str
    name: str
    provider: ModelProvider
    parameter_count: int  # in billions (7 = 7B)
    requires_gpu: bool
    estimated_speed: str  # fast, medium, slow
    capabilities: list = field(default_factory=list)
    downloaded: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "name": self.name,
            "provider": self.provider.value,
            "parameter_count": self.parameter_count,
            "requires_gpu": self.requires_gpu,
            "estimated_speed": self.estimated_speed,
            "capabilities": self.capabilities
        }


@dataclass
class CloudModel:
    """Cloud AI model configuration"""
    model_id: str
    name: str
    provider: ModelProvider
    cost_per_1k_tokens: float
    capabilities: list = field(default_factory=list)
    available: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "name": self.name,
            "provider": self.provider.value,
            "cost_per_1k_tokens": self.cost_per_1k_tokens,
            "capabilities": self.capabilities,
            "available": self.available
        }


class ModelRouter:
    """
    Intelligently routes AI tasks to optimal models.
    Considers:
    - Task type and complexity
    - User hardware capabilities
    - Cost constraints
    - Privacy requirements
    - Performance requirements
    """

    def __init__(self):
        """Initialize model router"""
        self.logger = logging.getLogger(__name__)

        # Initialize available local models
        self.local_models = self._initialize_local_models()

        # Initialize available cloud models
        self.cloud_models = self._initialize_cloud_models()

        # Model performance metrics
        self.performance_metrics: Dict[str, Dict[str, Any]] = {}

        self.logger.info(
            f"✅ Model Router initialized with "
            f"{len(self.local_models)} local and "
            f"{len(self.cloud_models)} cloud models"
        )

    def _initialize_local_models(self) -> Dict[str, LocalModel]:
        """Initialize local model configurations"""
        return {
            "phi-2": LocalModel(
                model_id="phi-2",
                name="Microsoft Phi-2",
                provider=ModelProvider.LLAMA,
                parameter_count=2.7,
                requires_gpu=False,
                estimated_speed="fast",
                capabilities=["general", "reasoning", "fast"]
            ),
            "tinyllama": LocalModel(
                model_id="tinyllama",
                name="TinyLlama",
                provider=ModelProvider.LLAMA,
                parameter_count=1.1,
                requires_gpu=False,
                estimated_speed="fast",
                capabilities=["general", "lightweight", "fast"]
            ),
            "mistral-7b": LocalModel(
                model_id="mistral-7b",
                name="Mistral 7B",
                provider=ModelProvider.MISTRAL,
                parameter_count=7,
                requires_gpu=True,
                estimated_speed="medium",
                capabilities=["general", "reasoning", "coding", "balanced"]
            ),
            "llama2-7b": LocalModel(
                model_id="llama2-7b",
                name="Llama 2 7B",
                provider=ModelProvider.LLAMA,
                parameter_count=7,
                requires_gpu=True,
                estimated_speed="medium",
                capabilities=["general", "reasoning", "conversation"]
            ),
            "llama2-13b": LocalModel(
                model_id="llama2-13b",
                name="Llama 2 13B",
                provider=ModelProvider.LLAMA,
                parameter_count=13,
                requires_gpu=True,
                estimated_speed="slow",
                capabilities=["general", "complex_reasoning", "code_generation"]
            ),
            "neural-chat-7b": LocalModel(
                model_id="neural-chat-7b",
                name="Neural Chat 7B",
                provider=ModelProvider.MISTRAL,
                parameter_count=7,
                requires_gpu=True,
                estimated_speed="medium",
                capabilities=["conversation", "general", "optimized_for_chat"]
            )
        }

    def _initialize_cloud_models(self) -> Dict[str, CloudModel]:
        """Initialize cloud model configurations"""
        return {
            "deepseek-coder": CloudModel(
                model_id="deepseek-coder",
                name="DeepSeek Coder",
                provider=ModelProvider.DEEPSEEK,
                cost_per_1k_tokens=0.0001,
                capabilities=["coding", "technical", "reasoning"]
            ),
            "deepseek-chat": CloudModel(
                model_id="deepseek-chat",
                name="DeepSeek Chat",
                provider=ModelProvider.DEEPSEEK,
                cost_per_1k_tokens=0.00005,
                capabilities=["conversation", "general", "reasoning"]
            ),
            "qwen-max": CloudModel(
                model_id="qwen-max",
                name="Qwen Max",
                provider=ModelProvider.QWEN,
                cost_per_1k_tokens=0.00008,
                capabilities=["general", "reasoning", "multilingual"]
            ),
            "qwen-plus": CloudModel(
                model_id="qwen-plus",
                name="Qwen Plus",
                provider=ModelProvider.QWEN,
                cost_per_1k_tokens=0.00004,
                capabilities=["conversation", "general", "cost_effective"]
            )
        }

    async def route(
        self,
        task_type: str,
        task_description: str,
        user_hardware: Dict[str, Any],
        privacy_required: bool = False,
        cost_limit: Optional[float] = None,
        speed_required: bool = False
    ) -> Dict[str, Any]:
        """
        Route task to optimal model.

        Args:
            task_type: Type of task (summarization, coding, reasoning, etc)
            task_description: Description of the task
            user_hardware: Hardware info (has_gpu, ram_gb, cpu_cores, etc)
            privacy_required: If True, prefer local models
            cost_limit: Maximum cost per 1k tokens
            speed_required: If True, prefer faster models

        Returns:
            Routing decision with model configuration
        """
        # Analyze task complexity
        complexity = await self._analyze_complexity(task_type, task_description)

        # Determine if local model is suitable
        can_use_local = not privacy_required and user_hardware.get("has_gpu", False)

        # If privacy required or no GPU, use local
        if privacy_required or not user_hardware.get("has_gpu", False):
            selected_model = await self._select_local_model(
                complexity,
                speed_required,
                user_hardware
            )
            return {
                "model_id": selected_model.model_id,
                "model_name": selected_model.name,
                "provider": "local",
                "provider_name": selected_model.provider.value,
                "type": "local",
                "reason": "Privacy required or local execution preferred",
                "execution_location": "local",
                "estimated_latency_ms": 500 if selected_model.requires_gpu else 200,
                "cost": 0.0
            }

        # Otherwise, consider cloud options
        if complexity == TaskComplexity.SIMPLE:
            # Use cheapest option for simple tasks
            selected_model = await self._select_cloud_model(cost_limit, "cheap")
        elif complexity == TaskComplexity.MODERATE:
            # Balance cost and quality
            selected_model = await self._select_cloud_model(cost_limit, "balanced")
        else:
            # Use best model for complex tasks
            selected_model = await self._select_cloud_model(cost_limit, "best")

        if selected_model:
            return {
                "model_id": selected_model.model_id,
                "model_name": selected_model.name,
                "provider": "cloud",
                "provider_name": selected_model.provider.value,
                "type": "cloud",
                "reason": f"Task complexity: {complexity.value}",
                "execution_location": "cloud",
                "estimated_latency_ms": 1000,
                "cost_per_1k_tokens": selected_model.cost_per_1k_tokens
            }

        # Fallback to local model
        fallback = await self._select_local_model(
            TaskComplexity.MODERATE,
            False,
            user_hardware
        )
        return {
            "model_id": fallback.model_id,
            "model_name": fallback.name,
            "provider": "local_fallback",
            "type": "local",
            "reason": "Cloud models unavailable, using fallback",
            "execution_location": "local"
        }

    async def _analyze_complexity(
        self,
        task_type: str,
        task_description: str
    ) -> TaskComplexity:
        """Analyze task complexity"""
        task_type_lower = task_type.lower()

        simple_keywords = ["summarize", "translate", "format", "extract"]
        complex_keywords = ["reason", "analyze", "code", "debug", "optimize"]

        if any(kw in task_type_lower for kw in simple_keywords):
            return TaskComplexity.SIMPLE

        if any(kw in task_type_lower for kw in complex_keywords):
            return TaskComplexity.COMPLEX

        return TaskComplexity.MODERATE

    async def _select_local_model(
        self,
        complexity: TaskComplexity,
        speed_required: bool,
        user_hardware: Dict[str, Any]
    ) -> LocalModel:
        """Select best local model"""
        candidates = list(self.local_models.values())

        # Filter by hardware
        if not user_hardware.get("has_gpu", False):
            candidates = [m for m in candidates if not m.requires_gpu]

        if not candidates:
            candidates = list(self.local_models.values())

        # Select based on complexity
        if complexity == TaskComplexity.SIMPLE:
            if speed_required:
                # Use smallest model
                return min(candidates, key=lambda m: m.parameter_count)
            else:
                return candidates[0]

        elif complexity == TaskComplexity.MODERATE:
            # Find balanced option
            balanced = [m for m in candidates if 5 <= m.parameter_count <= 10]
            return balanced[0] if balanced else candidates[0]

        else:  # COMPLEX
            # Use largest available
            return max(candidates, key=lambda m: m.parameter_count)

    async def _select_cloud_model(
        self,
        cost_limit: Optional[float],
        strategy: str = "balanced"
    ) -> Optional[CloudModel]:
        """Select best cloud model"""
        candidates = [m for m in self.cloud_models.values() if m.available]

        if not candidates:
            return None

        if strategy == "cheap":
            return min(candidates, key=lambda m: m.cost_per_1k_tokens)

        elif strategy == "best":
            # Prefer powerful models
            return candidates[0]

        else:  # balanced
            # Find middle-ground option
            mid_cost = sum(m.cost_per_1k_tokens for m in candidates) / len(candidates)
            return min(candidates, key=lambda m: abs(m.cost_per_1k_tokens - mid_cost))

    def list_available_models(self) -> Dict[str, Any]:
        """List all available models"""
        return {
            "local_models": [m.to_dict() for m in self.local_models.values()],
            "cloud_models": [m.to_dict() for m in self.cloud_models.values()],
            "total_local": len(self.local_models),
            "total_cloud": len(self.cloud_models)
        }

    async def record_performance(
        self,
        model_id: str,
        task_type: str,
        latency_ms: int,
        success: bool,
        cost: float = 0.0
    ) -> None:
        """Record model performance metrics"""
        if model_id not in self.performance_metrics:
            self.performance_metrics[model_id] = {
                "total_tasks": 0,
                "successful_tasks": 0,
                "avg_latency_ms": 0,
                "total_cost": 0.0,
                "by_task_type": {}
            }

        metrics = self.performance_metrics[model_id]
        metrics["total_tasks"] += 1
        if success:
            metrics["successful_tasks"] += 1
        metrics["avg_latency_ms"] = (
            (metrics["avg_latency_ms"] + latency_ms) / 2
        )
        metrics["total_cost"] += cost

        if task_type not in metrics["by_task_type"]:
            metrics["by_task_type"][task_type] = {"count": 0, "avg_latency": 0}

        metrics["by_task_type"][task_type]["count"] += 1
