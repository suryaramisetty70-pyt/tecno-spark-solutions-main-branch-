"""
Agent management service - business logic for agent operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

from db.models import Agent, AgentInstance, AgentTool, AgentMetric
from api.schemas.agent_schemas import (
    AgentRequest, AgentConfigRequest, AgentEnableRequest, AgentToolRequest
)

logger = logging.getLogger(__name__)


class AgentService:
    """Agent management service"""

    @staticmethod
    async def create_agent(db: AsyncSession, agent_data: AgentRequest) -> Agent:
        """Create/register new agent"""
        try:
            agent = Agent(
                name=agent_data.name,
                description=agent_data.description,
                version=agent_data.version,
                capabilities=",".join([cap.value for cap in agent_data.capabilities]),
                status="active",
                enabled_by_default=agent_data.enabled_by_default,
                requires_authentication=agent_data.requires_authentication,
                author=agent_data.author,
                documentation_url=agent_data.documentation_url,
                config=agent_data.config or {},
                downloads=0,
                rating=0.0,
                total_reviews=0
            )
            db.add(agent)
            await db.commit()
            await db.refresh(agent)
            logger.info(f"Agent created: id={agent.id}, name={agent.name}")
            return agent

        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Integrity error creating agent: {e}")
            raise ValueError("Agent with this name already exists")
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating agent: {e}")
            raise

    @staticmethod
    async def get_agent(db: AsyncSession, agent_id: int) -> Optional[Agent]:
        """Get agent by ID"""
        try:
            result = await db.execute(
                select(Agent).where(Agent.id == agent_id)
            )
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error fetching agent: {e}")
            raise

    @staticmethod
    async def get_agent_by_name(db: AsyncSession, name: str) -> Optional[Agent]:
        """Get agent by name"""
        try:
            result = await db.execute(
                select(Agent).where(Agent.name == name)
            )
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error fetching agent: {e}")
            raise

    @staticmethod
    async def list_agents(
        db: AsyncSession, skip: int = 0, limit: int = 50
    ) -> tuple[List[Agent], int]:
        """List all agents with pagination"""
        try:
            # Get total count
            count_result = await db.execute(select(Agent))
            total = len(count_result.scalars().all())

            # Get paginated results
            result = await db.execute(
                select(Agent).offset(skip).limit(limit).order_by(Agent.created_at.desc())
            )
            agents = result.scalars().all()
            return agents, total

        except Exception as e:
            logger.error(f"Error listing agents: {e}")
            raise

    @staticmethod
    async def update_agent_config(
        db: AsyncSession, agent_id: int, config_data: AgentConfigRequest
    ) -> Agent:
        """Update agent configuration"""
        try:
            agent = await AgentService.get_agent(db, agent_id)
            if not agent:
                raise ValueError("Agent not found")

            agent.config = config_data.config
            agent.updated_at = datetime.utcnow()

            await db.commit()
            await db.refresh(agent)
            logger.info(f"Agent config updated: id={agent_id}")
            return agent

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating agent config: {e}")
            raise

    @staticmethod
    async def enable_agent_for_user(
        db: AsyncSession, user_id: int, agent_id: int, enable_data: AgentEnableRequest
    ) -> AgentInstance:
        """Enable/disable agent for user"""
        try:
            agent = await AgentService.get_agent(db, agent_id)
            if not agent:
                raise ValueError("Agent not found")

            # Check if instance exists
            result = await db.execute(
                select(AgentInstance).where(
                    AgentInstance.user_id == user_id
                ).where(AgentInstance.agent_id == agent_id)
            )
            instance = result.scalars().first()

            if not instance:
                # Create new instance
                instance = AgentInstance(
                    user_id=user_id,
                    agent_id=agent_id,
                    enabled=enable_data.enabled,
                    status="active",
                    permissions=enable_data.permissions or [],
                    config=agent.config,
                    usage_count=0
                )
                db.add(instance)
            else:
                # Update existing instance
                instance.enabled = enable_data.enabled
                if enable_data.permissions is not None:
                    instance.permissions = enable_data.permissions
                instance.updated_at = datetime.utcnow()

            await db.commit()
            await db.refresh(instance)
            logger.info(f"Agent instance updated: user_id={user_id}, agent_id={agent_id}")
            return instance

        except Exception as e:
            await db.rollback()
            logger.error(f"Error enabling agent for user: {e}")
            raise

    @staticmethod
    async def get_user_agents(
        db: AsyncSession, user_id: int, enabled_only: bool = False
    ) -> List[AgentInstance]:
        """Get all agents for user"""
        try:
            query = select(AgentInstance).where(AgentInstance.user_id == user_id)

            if enabled_only:
                query = query.where(AgentInstance.enabled == True)

            query = query.order_by(AgentInstance.created_at.desc())
            result = await db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error fetching user agents: {e}")
            raise

    @staticmethod
    async def get_agent_instance(
        db: AsyncSession, user_id: int, agent_id: int
    ) -> Optional[AgentInstance]:
        """Get agent instance for user"""
        try:
            result = await db.execute(
                select(AgentInstance).where(
                    AgentInstance.user_id == user_id
                ).where(AgentInstance.agent_id == agent_id)
            )
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error fetching agent instance: {e}")
            raise

    @staticmethod
    async def register_tool(
        db: AsyncSession, agent_id: int, tool_data: AgentToolRequest
    ) -> AgentTool:
        """Register tool for agent"""
        try:
            agent = await AgentService.get_agent(db, agent_id)
            if not agent:
                raise ValueError("Agent not found")

            tool = AgentTool(
                agent_id=agent_id,
                tool_name=tool_data.tool_name,
                description=tool_data.description,
                input_schema=tool_data.input_schema,
                output_schema=tool_data.output_schema,
                requires_auth=tool_data.requires_auth
            )
            db.add(tool)
            await db.commit()
            await db.refresh(tool)
            logger.info(f"Tool registered: agent_id={agent_id}, tool={tool.tool_name}")
            return tool

        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Integrity error registering tool: {e}")
            raise ValueError("Tool already exists for this agent")
        except Exception as e:
            await db.rollback()
            logger.error(f"Error registering tool: {e}")
            raise

    @staticmethod
    async def get_agent_tools(db: AsyncSession, agent_id: int) -> List[AgentTool]:
        """Get all tools for agent"""
        try:
            result = await db.execute(
                select(AgentTool).where(AgentTool.agent_id == agent_id).order_by(AgentTool.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching agent tools: {e}")
            raise

    @staticmethod
    async def record_execution(
        db: AsyncSession,
        user_id: int,
        agent_id: int,
        execution_time_ms: float,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """Record agent execution"""
        try:
            instance = await AgentService.get_agent_instance(db, user_id, agent_id)
            if instance:
                instance.usage_count += 1
                instance.last_used = datetime.utcnow()
                await db.commit()

            # Record metric
            metric = AgentMetric(
                agent_id=agent_id,
                user_id=user_id,
                execution_time_ms=execution_time_ms,
                success=success,
                error=error,
                timestamp=datetime.utcnow()
            )
            db.add(metric)
            await db.commit()
            logger.info(f"Execution recorded: agent_id={agent_id}, success={success}")

        except Exception as e:
            logger.error(f"Error recording execution: {e}")

    @staticmethod
    async def get_agent_metrics(
        db: AsyncSession, agent_id: int, user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get agent metrics"""
        try:
            query = select(AgentMetric).where(AgentMetric.agent_id == agent_id)

            if user_id:
                query = query.where(AgentMetric.user_id == user_id)

            result = await db.execute(query)
            metrics = result.scalars().all()

            if not metrics:
                return {
                    "agent_id": agent_id,
                    "total_executions": 0,
                    "successful_executions": 0,
                    "failed_executions": 0,
                    "average_execution_time_ms": 0,
                    "success_rate": 0,
                    "most_common_error": None
                }

            total = len(metrics)
            successful = len([m for m in metrics if m.success])
            failed = total - successful
            avg_time = sum(m.execution_time_ms for m in metrics) / total if total > 0 else 0

            # Get most common error
            errors = [m.error for m in metrics if m.error]
            most_common_error = None
            if errors:
                most_common_error = max(set(errors), key=errors.count)

            return {
                "agent_id": agent_id,
                "total_executions": total,
                "successful_executions": successful,
                "failed_executions": failed,
                "average_execution_time_ms": round(avg_time, 2),
                "success_rate": round((successful / total * 100) if total > 0 else 0, 2),
                "most_common_error": most_common_error,
                "last_executed": max([m.timestamp for m in metrics]) if metrics else None
            }

        except Exception as e:
            logger.error(f"Error fetching agent metrics: {e}")
            raise

    @staticmethod
    async def get_agent_status(db: AsyncSession, agent_id: int) -> Dict[str, Any]:
        """Get agent status"""
        try:
            agent = await AgentService.get_agent(db, agent_id)
            if not agent:
                raise ValueError("Agent not found")

            metrics = await AgentService.get_agent_metrics(db, agent_id)

            return {
                "agent_id": agent.id,
                "agent_name": agent.name,
                "status": agent.status,
                "uptime_percentage": 99.9,  # TODO: Calculate from metrics
                "last_health_check": datetime.utcnow(),
                "error_count_24h": metrics.get("failed_executions", 0),
                "execution_count_24h": metrics.get("total_executions", 0),
                "average_execution_time_ms": metrics.get("average_execution_time_ms", 0)
            }

        except Exception as e:
            logger.error(f"Error getting agent status: {e}")
            raise

    @staticmethod
    async def disable_agent(db: AsyncSession, agent_id: int) -> Agent:
        """Disable agent"""
        try:
            agent = await AgentService.get_agent(db, agent_id)
            if not agent:
                raise ValueError("Agent not found")

            agent.status = "disabled"
            agent.updated_at = datetime.utcnow()

            await db.commit()
            await db.refresh(agent)
            logger.info(f"Agent disabled: id={agent_id}")
            return agent

        except Exception as e:
            await db.rollback()
            logger.error(f"Error disabling agent: {e}")
            raise

    @staticmethod
    async def enable_agent(db: AsyncSession, agent_id: int) -> Agent:
        """Enable agent"""
        try:
            agent = await AgentService.get_agent(db, agent_id)
            if not agent:
                raise ValueError("Agent not found")

            agent.status = "active"
            agent.updated_at = datetime.utcnow()

            await db.commit()
            await db.refresh(agent)
            logger.info(f"Agent enabled: id={agent_id}")
            return agent

        except Exception as e:
            await db.rollback()
            logger.error(f"Error enabling agent: {e}")
            raise
