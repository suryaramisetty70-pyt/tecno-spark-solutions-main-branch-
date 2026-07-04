"""
Buddy Core - Central Intelligence & Orchestration Engine
The brain of the entire Buddy AI OS system
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio

from core.intent_router import IntentRouter, IntentCategory
from core.event_bus import EventBus, EventType
from core.memory_engine import MemoryEngine, MemoryType
from core.workflow_engine import WorkflowEngine
from core.model_router import ModelRouter
from core.ai_provider import AIProvider

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result from processing user intent"""
    agent_id: str
    status: str
    response: Any
    timestamp: datetime
    processing_time: float
    confidence: float = 1.0


class BuddyCore:
    """
    Central orchestration engine that coordinates all agents.
    Handles intent routing, memory management, workflow execution, and multi-agent coordination.
    """

    def __init__(self):
        """Initialize Buddy Core"""
        self.logger = logging.getLogger(__name__)

        # Core agents registry
        self.agents: Dict[str, Any] = {}

        # Core engines
        self.intent_router = IntentRouter()
        self.memory_engine = MemoryEngine()
        self.event_bus = EventBus()
        self.workflow_engine = WorkflowEngine()
        self.model_router = ModelRouter()
        self.ai_provider = AIProvider()

        self._load_all_agents()
        self.logger.info("🧠 Buddy Core initialized with all components")

    def _load_all_agents(self):
        """Dynamically load and wake up all agents from the agents directory."""
        import os
        import importlib
        import inspect
        from pathlib import Path
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        agents_dir = Path(os.path.join(base_dir, "agents"))
        
        loaded_count = 0
        for agent_file in agents_dir.glob("*_agent.py"):
            if agent_file.name in ["base_agent.py", "enhanced_base_agent.py"]:
                continue
            try:
                module_name = f"agents.{agent_file.stem}"
                spec = importlib.util.spec_from_file_location(module_name, agent_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if name.endswith("Agent") and name not in ["BaseAgent", "EnhancedBaseAgent"]:
                        try:
                            # Instantiate and register
                            if "core" in inspect.signature(obj.__init__).parameters:
                                agent_instance = obj(self)
                            else:
                                agent_instance = obj()
                                
                            agent_id = getattr(agent_instance, "id", None) or agent_file.stem.replace("_agent", "")
                            self.register_agent(agent_id, agent_instance)
                            loaded_count += 1
                        except Exception as instantiate_error:
                            self.logger.debug(f"Skipping {name}: {instantiate_error}")
                        break
            except Exception as e:
                self.logger.warning(f"Failed to load agent file {agent_file.name}: {e}")
                
        self.logger.info(f"✅ Automatically woke up and registered {loaded_count} specialized agents!")

    async def initialize(self) -> None:
        """Initialize all core components"""
        self.logger.info("Initializing Buddy Core components...")

        # All components are initialized in __init__
        # This method is for async initialization if needed in the future

        self.logger.info("✅ All Buddy Core components ready")
        self.logger.info(f"📊 Status:")
        self.logger.info(f"   - Intent Router: {self.intent_router.get_router_stats()}")
        self.logger.info(f"   - Memory Engine: {self.memory_engine.get_memory_stats()}")
        self.logger.info(f"   - Event Bus: {self.event_bus.get_bus_stats()}")
        self.logger.info(f"   - Workflow Engine: {self.workflow_engine.get_workflow_stats()}")
        self.logger.info(f"   - Model Router: Available models {len(self.model_router.local_models)} local + {len(self.model_router.cloud_models)} cloud")

    def register_agent(self, agent_id: str, agent: Any) -> None:
        """
        Register an agent with Buddy Core.

        Args:
            agent_id: Unique agent identifier
            agent: Agent instance
        """
        self.agents[agent_id] = agent

        # Register agent capabilities with intent router
        if hasattr(agent, "capabilities"):
            for capability in agent.capabilities:
                self.intent_router.add_agent_capability(
                    agent_id=agent_id,
                    category=capability.get("category"),
                    skills=capability.get("skills", []),
                    priority=capability.get("priority", 5)
                )

        self.logger.info(f"✅ Agent registered: {agent.name} ({agent_id})")

    def get_agent(self, agent_id: str) -> Optional[Any]:
        """Get registered agent by ID"""
        return self.agents.get(agent_id)

    def list_agents(self) -> Dict[str, Any]:
        """List all registered agents"""
        return {
            agent_id: agent.get_info()
            for agent_id, agent in self.agents.items()
        }

    async def route_intent(
        self,
        user_id: str,
        intent: str,
        context: Dict[str, Any]
    ) -> ProcessingResult:
        """
        Route user intent to appropriate agent(s).

        The intent router analyzes the user's intent and determines:
        1. Which agent(s) should handle it
        2. In what order (if multiple agents)
        3. With what context and memory

        Args:
            user_id: User ID
            intent: User's intention/command
            context: Additional context

        Returns:
            Processing result from agent
        """
        start_time = datetime.now()

        try:
            self.logger.info(f"🎯 Routing intent: {intent[:50]}...")

            # Publish intent received event
            await self.event_bus.publish(
                EventType.INTENT_RECEIVED,
                source_agent="buddy_core",
                data={"user_id": user_id, "intent": intent}
            )

            # Classify intent
            category, confidence = await self.intent_router.classify_intent(
                intent,
                context
            )

            self.logger.info(f"📊 Intent classified: {category.value} (confidence: {confidence:.2f})")

            # Select appropriate agents
            agents = await self.intent_router.select_agents(category, context)

            if not agents:
                self.logger.warning(f"No agents available for category: {category.value}")
                processing_time = (datetime.now() - start_time).total_seconds()
                return ProcessingResult(
                    agent_id="buddy_core",
                    status="no_agents",
                    response={"message": "No agents available for this request"},
                    timestamp=datetime.now(),
                    processing_time=processing_time,
                    confidence=0.0
                )

            # Get primary agent
            primary_agent_id = agents[0][0]
            primary_agent = self.agents.get(primary_agent_id)

            if not primary_agent:
                self.logger.error(f"Agent not registered: {primary_agent_id}")
                processing_time = (datetime.now() - start_time).total_seconds()
                return ProcessingResult(
                    agent_id="buddy_core",
                    status="agent_not_found",
                    response={"message": f"Agent {primary_agent_id} not registered"},
                    timestamp=datetime.now(),
                    processing_time=processing_time,
                    confidence=0.0
                )

            # Retrieve relevant memory for context
            memories = await self.memory_engine.retrieve_memory(
                user_id=user_id,
                query=intent,
                top_k=3
            )

            # Enhance context with memory
            enhanced_context = {
                **context,
                "memories": memories,
                "user_id": user_id,
                "intent_category": category.value,
                "confidence": confidence
            }

            # Execute agent
            self.logger.info(f"🤖 Executing agent: {primary_agent.name}")
            agent_result = await primary_agent(intent, enhanced_context)

            # Save to memory
            await self.memory_engine.save_memory(
                user_id=user_id,
                memory_type=MemoryType.CONVERSATION,
                content=f"User: {intent}\nAgent Response: {str(agent_result)}",
                metadata={"agent_id": primary_agent_id, "category": category.value},
                tags=[category.value, primary_agent_id]
            )

            # Publish intent processed event
            await self.event_bus.publish(
                EventType.INTENT_PROCESSED,
                source_agent="buddy_core",
                data={"user_id": user_id, "agent_id": primary_agent_id, "status": "success"}
            )

            processing_time = (datetime.now() - start_time).total_seconds()

            result = ProcessingResult(
                agent_id=primary_agent_id,
                status="success",
                response=agent_result,
                timestamp=datetime.now(),
                processing_time=processing_time,
                confidence=confidence
            )

            self.logger.info(f"✅ Intent processed in {processing_time:.2f}s by {primary_agent.name}")
            return result

        except Exception as e:
            self.logger.error(f"❌ Error routing intent: {e}", exc_info=True)
            processing_time = (datetime.now() - start_time).total_seconds()
            return ProcessingResult(
                agent_id="buddy_core",
                status="error",
                response={"error": str(e)},
                timestamp=datetime.now(),
                processing_time=processing_time,
                confidence=0.0
            )

    async def save_memory(
        self,
        user_id: str,
        memory_type: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Save information to long-term memory.

        Args:
            user_id: User ID
            memory_type: Type of memory (conversation, note, document, etc)
            content: Content to save
            metadata: Additional metadata

        Returns:
            Memory ID
        """
        self.logger.info(f"💾 Saving memory: {memory_type}")

        # Convert string memory type to enum
        try:
            mem_type = MemoryType[memory_type.upper()]
        except KeyError:
            mem_type = MemoryType.CUSTOM

        memory_id = await self.memory_engine.save_memory(
            user_id=user_id,
            memory_type=mem_type,
            content=content,
            metadata=metadata or {}
        )

        # Publish memory saved event
        await self.event_bus.publish(
            EventType.MEMORY_SAVED,
            source_agent="buddy_core",
            data={"user_id": user_id, "memory_id": memory_id, "type": memory_type}
        )

        return memory_id

    async def retrieve_memory(
        self,
        user_id: str,
        query: str,
        memory_type: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories for context.

        Uses semantic search on vector embeddings to find relevant memories.

        Args:
            user_id: User ID
            query: Search query
            memory_type: Optional filter by memory type
            top_k: Number of results to return

        Returns:
            List of relevant memories
        """
        self.logger.info(f"🔍 Retrieving memories for: {query[:50]}...")

        # Convert string memory type to enum if provided
        mem_type = None
        if memory_type:
            try:
                mem_type = MemoryType[memory_type.upper()]
            except KeyError:
                pass

        memories = await self.memory_engine.retrieve_memory(
            user_id=user_id,
            query=query,
            memory_type=mem_type,
            top_k=top_k
        )

        # Publish memory retrieved event
        await self.event_bus.publish(
            EventType.MEMORY_RETRIEVED,
            source_agent="buddy_core",
            data={"user_id": user_id, "query": query, "results": len(memories)}
        )

        return memories

    async def execute_workflow(
        self,
        user_id: str,
        workflow_id: str,
        trigger_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute a multi-step workflow coordinating multiple agents.

        Args:
            user_id: User ID
            workflow_id: Workflow ID
            trigger_data: Data that triggered the workflow

        Returns:
            Workflow execution result
        """
        self.logger.info(f"⚙️ Executing workflow: {workflow_id}")

        # Publish workflow started event
        await self.event_bus.publish(
            EventType.WORKFLOW_STARTED,
            source_agent="buddy_core",
            data={"user_id": user_id, "workflow_id": workflow_id}
        )

        # Execute workflow
        execution_id = await self.workflow_engine.execute_workflow(
            workflow_id=workflow_id,
            user_id=user_id,
            trigger_data=trigger_data or {},
            agent_callable=self._call_agent
        )

        # Get execution status
        execution_status = await self.workflow_engine.get_workflow_status(execution_id)

        if execution_status.get("status") == "completed":
            await self.event_bus.publish(
                EventType.WORKFLOW_COMPLETED,
                source_agent="buddy_core",
                data={"workflow_id": workflow_id, "execution_id": execution_id}
            )
        else:
            await self.event_bus.publish(
                EventType.WORKFLOW_FAILED,
                source_agent="buddy_core",
                data={"workflow_id": workflow_id, "execution_id": execution_id}
            )

        return execution_status

    async def _call_agent(
        self,
        agent_id: str,
        action: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call an agent to execute an action"""
        agent = self.agents.get(agent_id)
        if not agent:
            return {"error": f"Agent {agent_id} not registered"}

        try:
            return await agent.execute_action(action, parameters)
        except Exception as e:
            self.logger.error(f"Error calling agent {agent_id}: {e}")
            return {"error": str(e)}

    async def select_model(
        self,
        task_type: str,
        user_hardware: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Select best AI model based on task and hardware.

        Chooses between:
        - Local models (via Ollama) for privacy/speed
        - Cloud APIs (DeepSeek, Qwen) for complex tasks

        Args:
            task_type: Type of task (summarization, reasoning, coding, etc)
            user_hardware: Hardware info (GPU, CPU, RAM)

        Returns:
            Model configuration
        """
        self.logger.info(f"🤖 Selecting model for task: {task_type}")

        model_config = await self.model_router.route(
            task_type=task_type,
            task_description="",
            user_hardware=user_hardware,
            privacy_required=user_hardware.get("privacy_required", False),
            speed_required=user_hardware.get("speed_required", False)
        )

        self.logger.info(
            f"✅ Model selected: {model_config.get('model_name')} "
            f"({model_config.get('provider')})"
        )

        return model_config

    async def coordinate_agents(
        self,
        agents: List[str],
        shared_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordinate multiple agents working together.

        Args:
            agents: List of agent IDs to coordinate
            shared_context: Shared context for all agents

        Returns:
            Coordination result
        """
        self.logger.info(f"🤝 Coordinating {len(agents)} agents")

        results = []

        for agent_id in agents:
            agent = self.agents.get(agent_id)
            if agent:
                try:
                    result = await agent(
                        shared_context.get("intent", ""),
                        shared_context
                    )
                    results.append({
                        "agent_id": agent_id,
                        "status": "success",
                        "result": result
                    })
                except Exception as e:
                    results.append({
                        "agent_id": agent_id,
                        "status": "error",
                        "error": str(e)
                    })

        self.logger.info(f"✅ Coordination complete: {len(agents)} agents")
        return {"agents": agents, "results": results}

    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            "agents_registered": len(self.agents),
            "memory": self.memory_engine.get_memory_stats(),
            "event_bus": self.event_bus.get_bus_stats(),
            "workflows": self.workflow_engine.get_workflow_stats(),
            "models_available": {
                "local": len(self.model_router.local_models),
                "cloud": len(self.model_router.cloud_models)
            },
            "router_stats": self.intent_router.get_router_stats()
        }
