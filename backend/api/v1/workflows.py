"""
Workflow management API endpoints
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from api.dependencies.auth_dependencies import get_db_session, get_current_user
from api.schemas.auth_schemas import CurrentUser
from api.schemas.workflow_schemas import (
    WorkflowCreateRequest, WorkflowResponse, WorkflowUpdateRequest,
    WorkflowStepCreateRequest, WorkflowStepResponse, TriggerCreateRequest,
    TriggerResponse, WorkflowExecutionCreateRequest, WorkflowExecutionResponse,
    StepExecutionResponse, WorkflowListResponse, WorkflowExecutionListResponse,
    WorkflowStatsResponse, ErrorResponse, ExecutionStatus
)
from services.workflow_service import WorkflowService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow_data: WorkflowCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create new workflow"""
    try:
        workflow = await WorkflowService.create_workflow(db, current_user.id, workflow_data)

        return WorkflowResponse(
            id=workflow.id,
            user_id=workflow.user_id,
            name=workflow.name,
            description=workflow.description,
            category=workflow.category,
            status=workflow.status,
            enabled=workflow.enabled,
            step_count=workflow.step_count or 0,
            execution_count=workflow.execution_count or 0,
            success_count=workflow.success_count or 0,
            failure_count=workflow.failure_count or 0,
            last_executed=workflow.last_executed,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at
        )

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return {
            "status_code": 400,
            "message": "Bad Request",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error creating workflow"
        }


@router.get("", response_model=WorkflowListResponse, status_code=status.HTTP_200_OK)
async def list_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """List user's workflows"""
    try:
        workflows, total = await WorkflowService.list_workflows(db, current_user.id, skip, limit)

        return WorkflowListResponse(
            total=total,
            page=skip // limit + 1,
            per_page=limit,
            workflows=[
                WorkflowResponse(
                    id=w.id,
                    user_id=w.user_id,
                    name=w.name,
                    description=w.description,
                    category=w.category,
                    status=w.status,
                    enabled=w.enabled,
                    step_count=w.step_count or 0,
                    execution_count=w.execution_count or 0,
                    success_count=w.success_count or 0,
                    failure_count=w.failure_count or 0,
                    last_executed=w.last_executed,
                    created_at=w.created_at,
                    updated_at=w.updated_at
                )
                for w in workflows
            ]
        )

    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error listing workflows"
        }


@router.get("/{workflow_id}", response_model=WorkflowResponse, status_code=status.HTTP_200_OK)
async def get_workflow(
    workflow_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get workflow details"""
    try:
        workflow = await WorkflowService.get_workflow(db, workflow_id, current_user.id)
        if not workflow:
            return {
                "status_code": 404,
                "message": "Not Found",
                "detail": "Workflow not found"
            }

        return WorkflowResponse(
            id=workflow.id,
            user_id=workflow.user_id,
            name=workflow.name,
            description=workflow.description,
            category=workflow.category,
            status=workflow.status,
            enabled=workflow.enabled,
            step_count=workflow.step_count or 0,
            execution_count=workflow.execution_count or 0,
            success_count=workflow.success_count or 0,
            failure_count=workflow.failure_count or 0,
            last_executed=workflow.last_executed,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at
        )

    except Exception as e:
        logger.error(f"Error fetching workflow: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error fetching workflow"
        }


@router.put("/{workflow_id}", response_model=WorkflowResponse, status_code=status.HTTP_200_OK)
async def update_workflow(
    workflow_id: int,
    workflow_data: WorkflowUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update workflow"""
    try:
        workflow = await WorkflowService.update_workflow(db, workflow_id, current_user.id, workflow_data)

        return WorkflowResponse(
            id=workflow.id,
            user_id=workflow.user_id,
            name=workflow.name,
            description=workflow.description,
            category=workflow.category,
            status=workflow.status,
            enabled=workflow.enabled,
            step_count=workflow.step_count or 0,
            execution_count=workflow.execution_count or 0,
            success_count=workflow.success_count or 0,
            failure_count=workflow.failure_count or 0,
            last_executed=workflow.last_executed,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at
        )

    except ValueError as e:
        logger.warning(f"Workflow not found: {e}")
        return {
            "status_code": 404,
            "message": "Not Found",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error updating workflow: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error updating workflow"
        }


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete workflow"""
    try:
        await WorkflowService.delete_workflow(db, workflow_id, current_user.id)
        return None

    except ValueError as e:
        logger.warning(f"Workflow not found: {e}")
        return {
            "status_code": 404,
            "message": "Not Found",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error deleting workflow: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error deleting workflow"
        }


@router.post("/{workflow_id}/steps", response_model=WorkflowStepResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow_step(
    workflow_id: int,
    step_data: WorkflowStepCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create workflow step"""
    try:
        step_data.workflow_id = workflow_id
        step = await WorkflowService.create_workflow_step(db, step_data)

        return WorkflowStepResponse(
            id=step.id,
            workflow_id=step.workflow_id,
            step_order=step.step_order,
            step_type=step.step_type,
            name=step.name,
            description=step.description,
            config=step.config or {},
            agent_id=step.agent_id,
            condition=step.condition,
            input_mapping=step.input_mapping,
            output_mapping=step.output_mapping,
            on_success_next_step=step.on_success_next_step,
            on_failure_next_step=step.on_failure_next_step,
            retry_count=step.retry_count or 0,
            retry_delay_seconds=step.retry_delay_seconds or 0,
            timeout_seconds=step.timeout_seconds,
            created_at=step.created_at,
            updated_at=step.updated_at
        )

    except Exception as e:
        logger.error(f"Error creating workflow step: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error creating step"
        }


@router.get("/{workflow_id}/steps", response_model=list[WorkflowStepResponse], status_code=status.HTTP_200_OK)
async def get_workflow_steps(
    workflow_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get workflow steps"""
    try:
        steps = await WorkflowService.get_workflow_steps(db, workflow_id)

        return [
            WorkflowStepResponse(
                id=s.id,
                workflow_id=s.workflow_id,
                step_order=s.step_order,
                step_type=s.step_type,
                name=s.name,
                description=s.description,
                config=s.config or {},
                agent_id=s.agent_id,
                condition=s.condition,
                input_mapping=s.input_mapping,
                output_mapping=s.output_mapping,
                on_success_next_step=s.on_success_next_step,
                on_failure_next_step=s.on_failure_next_step,
                retry_count=s.retry_count or 0,
                retry_delay_seconds=s.retry_delay_seconds or 0,
                timeout_seconds=s.timeout_seconds,
                created_at=s.created_at,
                updated_at=s.updated_at
            )
            for s in steps
        ]

    except Exception as e:
        logger.error(f"Error fetching workflow steps: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error fetching steps"
        }


@router.post("/{workflow_id}/triggers", response_model=TriggerResponse, status_code=status.HTTP_201_CREATED)
async def create_trigger(
    workflow_id: int,
    trigger_data: TriggerCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create workflow trigger"""
    try:
        trigger_data.workflow_id = workflow_id
        trigger = await WorkflowService.create_trigger(db, trigger_data)

        return TriggerResponse(
            id=trigger.id,
            workflow_id=trigger.workflow_id,
            trigger_type=trigger.trigger_type,
            name=trigger.name,
            description=trigger.description,
            condition=trigger.condition,
            schedule_cron=trigger.schedule_cron,
            event_type=trigger.event_type,
            webhook_path=trigger.webhook_path,
            enabled=trigger.enabled,
            last_triggered=trigger.last_triggered,
            trigger_count=trigger.trigger_count or 0,
            created_at=trigger.created_at,
            updated_at=trigger.updated_at
        )

    except Exception as e:
        logger.error(f"Error creating trigger: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error creating trigger"
        }


@router.get("/{workflow_id}/triggers", response_model=list[TriggerResponse], status_code=status.HTTP_200_OK)
async def get_workflow_triggers(
    workflow_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get workflow triggers"""
    try:
        triggers = await WorkflowService.get_workflow_triggers(db, workflow_id)

        return [
            TriggerResponse(
                id=t.id,
                workflow_id=t.workflow_id,
                trigger_type=t.trigger_type,
                name=t.name,
                description=t.description,
                condition=t.condition,
                schedule_cron=t.schedule_cron,
                event_type=t.event_type,
                webhook_path=t.webhook_path,
                enabled=t.enabled,
                last_triggered=t.last_triggered,
                trigger_count=t.trigger_count or 0,
                created_at=t.created_at,
                updated_at=t.updated_at
            )
            for t in triggers
        ]

    except Exception as e:
        logger.error(f"Error fetching triggers: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error fetching triggers"
        }


@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse, status_code=status.HTTP_201_CREATED)
async def execute_workflow(
    workflow_id: int,
    execution_data: WorkflowExecutionCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Execute workflow"""
    try:
        execution_data.workflow_id = workflow_id
        execution = await WorkflowService.execute_workflow(db, current_user.id, execution_data)

        return WorkflowExecutionResponse(
            id=execution.id,
            workflow_id=execution.workflow_id,
            workflow_name="",
            user_id=execution.user_id,
            trigger_id=execution.trigger_id,
            status=execution.status,
            start_time=execution.start_time,
            end_time=execution.end_time,
            duration_seconds=execution.duration_seconds,
            input_data=execution.input_data,
            output_data=execution.output_data,
            error_message=execution.error_message,
            step_executions_count=0,
            current_step=execution.current_step,
            progress_percentage=execution.progress_percentage or 0
        )

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return {
            "status_code": 400,
            "message": "Bad Request",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error executing workflow"
        }


@router.get("/{workflow_id}/executions", response_model=WorkflowExecutionListResponse, status_code=status.HTTP_200_OK)
async def list_executions(
    workflow_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """List workflow executions"""
    try:
        executions, total = await WorkflowService.list_executions(
            db, current_user.id, workflow_id, skip, limit
        )

        return WorkflowExecutionListResponse(
            total=total,
            page=skip // limit + 1,
            per_page=limit,
            executions=[
                WorkflowExecutionResponse(
                    id=e.id,
                    workflow_id=e.workflow_id,
                    workflow_name="",
                    user_id=e.user_id,
                    trigger_id=e.trigger_id,
                    status=e.status,
                    start_time=e.start_time,
                    end_time=e.end_time,
                    duration_seconds=e.duration_seconds,
                    input_data=e.input_data,
                    output_data=e.output_data,
                    error_message=e.error_message,
                    step_executions_count=0,
                    current_step=e.current_step,
                    progress_percentage=e.progress_percentage or 0
                )
                for e in executions
            ]
        )

    except Exception as e:
        logger.error(f"Error listing executions: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error listing executions"
        }


@router.get("/executions/{execution_id}", response_model=WorkflowExecutionResponse, status_code=status.HTTP_200_OK)
async def get_execution(
    execution_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get execution details"""
    try:
        execution = await WorkflowService.get_execution(db, execution_id, current_user.id)
        if not execution:
            return {
                "status_code": 404,
                "message": "Not Found",
                "detail": "Execution not found"
            }

        return WorkflowExecutionResponse(
            id=execution.id,
            workflow_id=execution.workflow_id,
            workflow_name="",
            user_id=execution.user_id,
            trigger_id=execution.trigger_id,
            status=execution.status,
            start_time=execution.start_time,
            end_time=execution.end_time,
            duration_seconds=execution.duration_seconds,
            input_data=execution.input_data,
            output_data=execution.output_data,
            error_message=execution.error_message,
            step_executions_count=0,
            current_step=execution.current_step,
            progress_percentage=execution.progress_percentage or 0
        )

    except Exception as e:
        logger.error(f"Error fetching execution: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error fetching execution"
        }


@router.post("/executions/{execution_id}/cancel", response_model=WorkflowExecutionResponse, status_code=status.HTTP_200_OK)
async def cancel_execution(
    execution_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Cancel workflow execution"""
    try:
        execution = await WorkflowService.cancel_execution(db, execution_id, current_user.id)

        return WorkflowExecutionResponse(
            id=execution.id,
            workflow_id=execution.workflow_id,
            workflow_name="",
            user_id=execution.user_id,
            trigger_id=execution.trigger_id,
            status=execution.status,
            start_time=execution.start_time,
            end_time=execution.end_time,
            duration_seconds=execution.duration_seconds,
            input_data=execution.input_data,
            output_data=execution.output_data,
            error_message=execution.error_message,
            step_executions_count=0,
            current_step=execution.current_step,
            progress_percentage=execution.progress_percentage or 0
        )

    except ValueError as e:
        logger.warning(f"Error: {e}")
        return {
            "status_code": 400,
            "message": "Bad Request",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error cancelling execution: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error cancelling execution"
        }


@router.get("/{workflow_id}/stats", response_model=WorkflowStatsResponse, status_code=status.HTTP_200_OK)
async def get_workflow_stats(
    workflow_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get workflow statistics"""
    try:
        stats = await WorkflowService.get_workflow_stats(db, workflow_id)

        return WorkflowStatsResponse(
            workflow_id=stats["workflow_id"],
            workflow_name="",
            total_executions=stats["total_executions"],
            successful_executions=stats["successful_executions"],
            failed_executions=stats["failed_executions"],
            average_duration_seconds=stats["average_duration_seconds"],
            success_rate=stats["success_rate"],
            last_execution=stats["last_execution"],
            most_common_error=stats["most_common_error"]
        )

    except Exception as e:
        logger.error(f"Error getting workflow stats: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error getting stats"
        }


@router.post("/{workflow_id}/pause", response_model=WorkflowResponse, status_code=status.HTTP_200_OK)
async def pause_workflow(
    workflow_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Pause workflow"""
    try:
        workflow = await WorkflowService.pause_workflow(db, workflow_id, current_user.id)

        return WorkflowResponse(
            id=workflow.id,
            user_id=workflow.user_id,
            name=workflow.name,
            description=workflow.description,
            category=workflow.category,
            status=workflow.status,
            enabled=workflow.enabled,
            step_count=workflow.step_count or 0,
            execution_count=workflow.execution_count or 0,
            success_count=workflow.success_count or 0,
            failure_count=workflow.failure_count or 0,
            last_executed=workflow.last_executed,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at
        )

    except ValueError as e:
        logger.warning(f"Workflow not found: {e}")
        return {
            "status_code": 404,
            "message": "Not Found",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error pausing workflow: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error pausing workflow"
        }


@router.post("/{workflow_id}/resume", response_model=WorkflowResponse, status_code=status.HTTP_200_OK)
async def resume_workflow(
    workflow_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Resume workflow"""
    try:
        workflow = await WorkflowService.resume_workflow(db, workflow_id, current_user.id)

        return WorkflowResponse(
            id=workflow.id,
            user_id=workflow.user_id,
            name=workflow.name,
            description=workflow.description,
            category=workflow.category,
            status=workflow.status,
            enabled=workflow.enabled,
            step_count=workflow.step_count or 0,
            execution_count=workflow.execution_count or 0,
            success_count=workflow.success_count or 0,
            failure_count=workflow.failure_count or 0,
            last_executed=workflow.last_executed,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at
        )

    except ValueError as e:
        logger.warning(f"Workflow not found: {e}")
        return {
            "status_code": 404,
            "message": "Not Found",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error resuming workflow: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error resuming workflow"
        }
