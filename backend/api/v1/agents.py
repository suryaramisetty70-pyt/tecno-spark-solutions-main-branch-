"""
Agent management API endpoints
"""

from fastapi import APIRouter, Depends, status, Query, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from api.dependencies.auth_dependencies import get_db_session, get_current_user
from api.schemas.auth_schemas import CurrentUser
from api.schemas.agent_schemas import (
    AgentRequest, AgentResponse, AgentConfigRequest, AgentEnableRequest,
    AgentInstanceResponse, AgentStatusResponse, AgentMetricsResponse,
    AgentListResponse, UserAgentListResponse, AgentToolRequest, AgentToolResponse,
    ErrorResponse
)
from services.agent_service import AgentService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


class ChatRequest(BaseModel):
    user_id: str = "guest"
    intent: str
    agent_id: str = "personal_assistant"
    context: dict = {}


from api.v1.auth import get_current_user
from db.models import User

@router.post("/chat")
async def agent_chat(
    request_data: ChatRequest, 
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Chat with an AI agent - processes user intent and returns agent response"""
    core = request.app.state.buddy_core
    
    # If the user is chatting with the personal assistant, use dynamic routing
    if request_data.agent_id == "personal_assistant" or not request_data.agent_id:
        result = await core.route_intent(
            user_id=str(current_user.id),
            intent=request_data.intent,
            context=request_data.context or {}
        )
        
        response_text = result.response
        if isinstance(response_text, dict) and "message" in response_text:
            response_text = response_text["message"]
            
        return {
            "agent_id": result.agent_id,
            "response": response_text,
            "status": result.status,
            "message": response_text
        }
        
    agent = core.get_agent(request_data.agent_id)
    
    if not agent:
        # Fallback to general AI provider if agent not found
        response_text = await core.ai_provider.generate_response(
            system_prompt="You are a helpful AI assistant for Buddy AI OS.",
            user_prompt=request_data.intent
        )
    else:
        # Call the actual agent
        response_text = await agent(request_data.intent, request_data.context or {})
    
    return {
        "agent_id": request_data.agent_id,
        "response": response_text,
        "status": "success",
        "message": response_text
    }


@router.get("", response_model=AgentListResponse, status_code=status.HTTP_200_OK)
async def list_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session)
):
    """List all available agents"""
    try:
        agents, total = await AgentService.list_agents(db, skip, limit)

        return AgentListResponse(
            total=total,
            page=skip // limit + 1,
            per_page=limit,
            agents=[
                AgentResponse(
                    id=agent.id,
                    name=agent.name,
                    description=agent.description,
                    version=agent.version,
                    capabilities=agent.capabilities.split(","),
                    status=agent.status,
                    enabled_by_default=agent.enabled_by_default,
                    requires_authentication=agent.requires_authentication,
                    author=agent.author,
                    documentation_url=agent.documentation_url,
                    created_at=agent.created_at,
                    updated_at=agent.updated_at,
                    downloads=agent.downloads,
                    rating=agent.rating,
                    total_reviews=agent.total_reviews
                )
                for agent in agents
            ]
        )

    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error listing agents"
        }


@router.get("/{agent_id}", response_model=AgentResponse, status_code=status.HTTP_200_OK)
async def get_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Get agent details"""
    try:
        agent = await AgentService.get_agent(db, agent_id)
        if not agent:
            return {
                "status_code": 404,
                "message": "Not Found",
                "detail": "Agent not found"
            }

        return AgentResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            version=agent.version,
            capabilities=agent.capabilities.split(","),
            status=agent.status,
            enabled_by_default=agent.enabled_by_default,
            requires_authentication=agent.requires_authentication,
            author=agent.author,
            documentation_url=agent.documentation_url,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
            downloads=agent.downloads,
            rating=agent.rating,
            total_reviews=agent.total_reviews
        )

    except Exception as e:
        logger.error(f"Error fetching agent: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error fetching agent"
        }


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Register new agent (admin only)"""
    try:
        agent = await AgentService.create_agent(db, agent_data)

        return AgentResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            version=agent.version,
            capabilities=agent.capabilities.split(","),
            status=agent.status,
            enabled_by_default=agent.enabled_by_default,
            requires_authentication=agent.requires_authentication,
            author=agent.author,
            documentation_url=agent.documentation_url,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
            downloads=agent.downloads,
            rating=agent.rating,
            total_reviews=agent.total_reviews
        )

    except ValueError as e:
        logger.warning(f"Validation error creating agent: {e}")
        return {
            "status_code": 400,
            "message": "Bad Request",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error creating agent"
        }


@router.get("/{agent_id}/status", response_model=AgentStatusResponse, status_code=status.HTTP_200_OK)
async def get_agent_status(
    agent_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Get agent status"""
    try:
        status_data = await AgentService.get_agent_status(db, agent_id)

        return AgentStatusResponse(
            agent_id=status_data["agent_id"],
            agent_name=status_data["agent_name"],
            status=status_data["status"],
            uptime_percentage=status_data["uptime_percentage"],
            last_health_check=status_data["last_health_check"],
            error_count_24h=status_data["error_count_24h"],
            execution_count_24h=status_data["execution_count_24h"],
            average_execution_time_ms=status_data["average_execution_time_ms"]
        )

    except ValueError as e:
        logger.warning(f"Agent not found: {e}")
        return {
            "status_code": 404,
            "message": "Not Found",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error getting agent status"
        }


@router.get("/{agent_id}/metrics", response_model=AgentMetricsResponse, status_code=status.HTTP_200_OK)
async def get_agent_metrics(
    agent_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Get agent metrics"""
    try:
        metrics = await AgentService.get_agent_metrics(db, agent_id)

        return AgentMetricsResponse(
            agent_id=agent_id,
            agent_name=metrics.get("agent_name", ""),
            total_executions=metrics["total_executions"],
            successful_executions=metrics["successful_executions"],
            failed_executions=metrics["failed_executions"],
            average_execution_time_ms=metrics["average_execution_time_ms"],
            success_rate=metrics["success_rate"],
            most_common_error=metrics["most_common_error"],
            last_executed=metrics.get("last_executed"),
            daily_executions=[]
        )

    except Exception as e:
        logger.error(f"Error getting agent metrics: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error getting agent metrics"
        }


@router.put("/{agent_id}/config", response_model=AgentResponse, status_code=status.HTTP_200_OK)
async def update_agent_config(
    agent_id: int,
    config_data: AgentConfigRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Update agent configuration"""
    try:
        agent = await AgentService.update_agent_config(db, agent_id, config_data)

        return AgentResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            version=agent.version,
            capabilities=agent.capabilities.split(","),
            status=agent.status,
            enabled_by_default=agent.enabled_by_default,
            requires_authentication=agent.requires_authentication,
            author=agent.author,
            documentation_url=agent.documentation_url,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
            downloads=agent.downloads,
            rating=agent.rating,
            total_reviews=agent.total_reviews
        )

    except ValueError as e:
        logger.warning(f"Agent not found: {e}")
        return {
            "status_code": 404,
            "message": "Not Found",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error updating agent config: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error updating config"
        }


@router.post("/{agent_id}/enable", response_model=AgentInstanceResponse, status_code=status.HTTP_200_OK)
async def enable_agent_for_user(
    agent_id: int,
    enable_data: AgentEnableRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Enable agent for current user"""
    try:
        instance = await AgentService.enable_agent_for_user(
            db, current_user.id, agent_id, enable_data
        )

        agent = await AgentService.get_agent(db, agent_id)

        return AgentInstanceResponse(
            id=instance.id,
            user_id=instance.user_id,
            agent_id=instance.agent_id,
            agent_name=agent.name if agent else "",
            status=instance.status,
            enabled=instance.enabled,
            config=instance.config,
            permissions=instance.permissions or [],
            last_used=instance.last_used,
            usage_count=instance.usage_count,
            created_at=instance.created_at,
            updated_at=instance.updated_at
        )

    except ValueError as e:
        logger.warning(f"Error enabling agent: {e}")
        return {
            "status_code": 400,
            "message": "Bad Request",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error enabling agent for user: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error enabling agent"
        }


@router.post("/{agent_id}/disable", status_code=status.HTTP_200_OK)
async def disable_agent_for_user(
    agent_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Disable agent for current user"""
    try:
        instance = await AgentService.get_agent_instance(db, current_user.id, agent_id)
        if not instance:
            return {
                "status_code": 404,
                "message": "Not Found",
                "detail": "Agent not enabled for user"
            }

        instance.enabled = False
        instance.updated_at = __import__("datetime").datetime.utcnow()
        await db.commit()

        return {"message": "Agent disabled successfully"}

    except Exception as e:
        logger.error(f"Error disabling agent: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error disabling agent"
        }


@router.get("/user/agents", response_model=UserAgentListResponse, status_code=status.HTTP_200_OK)
async def get_user_agents(
    enabled_only: bool = Query(False),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all agents for current user"""
    try:
        instances = await AgentService.get_user_agents(db, current_user.id, enabled_only)
        enabled_count = len([i for i in instances if i.enabled])

        agents_response = []
        for instance in instances:
            agent = await AgentService.get_agent(db, instance.agent_id)
            agents_response.append(
                AgentInstanceResponse(
                    id=instance.id,
                    user_id=instance.user_id,
                    agent_id=instance.agent_id,
                    agent_name=agent.name if agent else "",
                    status=instance.status,
                    enabled=instance.enabled,
                    config=instance.config,
                    permissions=instance.permissions or [],
                    last_used=instance.last_used,
                    usage_count=instance.usage_count,
                    created_at=instance.created_at,
                    updated_at=instance.updated_at
                )
            )

        return UserAgentListResponse(
            total=len(instances),
            enabled_count=enabled_count,
            disabled_count=len(instances) - enabled_count,
            agents=agents_response
        )

    except Exception as e:
        logger.error(f"Error getting user agents: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error fetching agents"
        }


@router.post("/{agent_id}/tools", response_model=AgentToolResponse, status_code=status.HTTP_201_CREATED)
async def register_agent_tool(
    agent_id: int,
    tool_data: AgentToolRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Register tool for agent"""
    try:
        tool = await AgentService.register_tool(db, agent_id, tool_data)

        return AgentToolResponse(
            id=tool.id,
            agent_id=tool.agent_id,
            tool_name=tool.tool_name,
            description=tool.description,
            input_schema=tool.input_schema,
            output_schema=tool.output_schema,
            requires_auth=tool.requires_auth,
            created_at=tool.created_at
        )

    except ValueError as e:
        logger.warning(f"Error registering tool: {e}")
        return {
            "status_code": 400,
            "message": "Bad Request",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error registering tool: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error registering tool"
        }


@router.get("/{agent_id}/tools", response_model=list[AgentToolResponse], status_code=status.HTTP_200_OK)
async def get_agent_tools(
    agent_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Get all tools for agent"""
    try:
        tools = await AgentService.get_agent_tools(db, agent_id)

        return [
            AgentToolResponse(
                id=tool.id,
                agent_id=tool.agent_id,
                tool_name=tool.tool_name,
                description=tool.description,
                input_schema=tool.input_schema,
                output_schema=tool.output_schema,
                requires_auth=tool.requires_auth,
                created_at=tool.created_at
            )
            for tool in tools
        ]

    except Exception as e:
        logger.error(f"Error getting agent tools: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error fetching tools"
        }
