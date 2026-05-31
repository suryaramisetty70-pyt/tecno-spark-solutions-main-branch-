"""
Workflow management service - business logic for workflow operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
import logging

from db.models import Workflow, WorkflowStep, WorkflowTrigger, WorkflowExecution, StepExecution
from api.schemas.workflow_schemas import (
    WorkflowCreateRequest, WorkflowUpdateRequest, WorkflowStepCreateRequest,
    TriggerCreateRequest, WorkflowExecutionCreateRequest, ExecutionStatus
)

logger = logging.getLogger(__name__)


class WorkflowService:
    """Workflow management service"""

    @staticmethod
    async def create_workflow(db: AsyncSession, user_id: int, workflow_data: WorkflowCreateRequest) -> Workflow:
        """Create new workflow"""
        try:
            workflow = Workflow(
                user_id=user_id,
                name=workflow_data.name,
                description=workflow_data.description,
                category=workflow_data.category,
                status="draft",
                enabled=workflow_data.enabled,
                step_count=0,
                execution_count=0,
                success_count=0,
                failure_count=0
            )
            db.add(workflow)
            await db.commit()
            await db.refresh(workflow)
            logger.info(f"Workflow created: id={workflow.id}, user_id={user_id}")
            return workflow

        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Integrity error creating workflow: {e}")
            raise ValueError("Error creating workflow")
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating workflow: {e}")
            raise

    @staticmethod
    async def get_workflow(db: AsyncSession, workflow_id: int, user_id: int) -> Optional[Workflow]:
        """Get workflow by ID"""
        try:
            result = await db.execute(
                select(Workflow).where(
                    Workflow.id == workflow_id
                ).where(Workflow.user_id == user_id)
            )
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error fetching workflow: {e}")
            raise

    @staticmethod
    async def list_workflows(
        db: AsyncSession, user_id: int, skip: int = 0, limit: int = 50
    ) -> Tuple[List[Workflow], int]:
        """List workflows for user"""
        try:
            count_result = await db.execute(
                select(Workflow).where(Workflow.user_id == user_id)
            )
            total = len(count_result.scalars().all())

            result = await db.execute(
                select(Workflow).where(
                    Workflow.user_id == user_id
                ).offset(skip).limit(limit).order_by(Workflow.created_at.desc())
            )
            workflows = result.scalars().all()
            return workflows, total

        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            raise

    @staticmethod
    async def update_workflow(
        db: AsyncSession, workflow_id: int, user_id: int, workflow_data: WorkflowUpdateRequest
    ) -> Workflow:
        """Update workflow"""
        try:
            workflow = await WorkflowService.get_workflow(db, workflow_id, user_id)
            if not workflow:
                raise ValueError("Workflow not found")

            if workflow_data.name is not None:
                workflow.name = workflow_data.name
            if workflow_data.description is not None:
                workflow.description = workflow_data.description
            if workflow_data.category is not None:
                workflow.category = workflow_data.category
            if workflow_data.enabled is not None:
                workflow.enabled = workflow_data.enabled
            if workflow_data.status is not None:
                workflow.status = workflow_data.status

            workflow.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(workflow)
            logger.info(f"Workflow updated: id={workflow_id}")
            return workflow

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating workflow: {e}")
            raise

    @staticmethod
    async def delete_workflow(db: AsyncSession, workflow_id: int, user_id: int) -> bool:
        """Delete workflow"""
        try:
            workflow = await WorkflowService.get_workflow(db, workflow_id, user_id)
            if not workflow:
                raise ValueError("Workflow not found")

            # Delete related data
            steps = await WorkflowService.get_workflow_steps(db, workflow_id)
            for step in steps:
                await db.delete(step)

            triggers = await WorkflowService.get_workflow_triggers(db, workflow_id)
            for trigger in triggers:
                await db.delete(trigger)

            executions = await db.execute(
                select(WorkflowExecution).where(WorkflowExecution.workflow_id == workflow_id)
            )
            for execution in executions.scalars().all():
                await db.delete(execution)

            await db.delete(workflow)
            await db.commit()
            logger.info(f"Workflow deleted: id={workflow_id}")
            return True

        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting workflow: {e}")
            raise

    @staticmethod
    async def create_workflow_step(
        db: AsyncSession, step_data: WorkflowStepCreateRequest
    ) -> WorkflowStep:
        """Create workflow step"""
        try:
            step = WorkflowStep(
                workflow_id=step_data.workflow_id,
                step_order=step_data.step_order,
                step_type=step_data.step_type.value,
                name=step_data.name,
                description=step_data.description,
                config=step_data.config,
                agent_id=step_data.agent_id,
                condition=step_data.condition,
                input_mapping=step_data.input_mapping,
                output_mapping=step_data.output_mapping,
                on_success_next_step=step_data.on_success_next_step,
                on_failure_next_step=step_data.on_failure_next_step,
                retry_count=step_data.retry_count,
                retry_delay_seconds=step_data.retry_delay_seconds,
                timeout_seconds=step_data.timeout_seconds
            )
            db.add(step)

            # Update workflow step count
            workflow = await WorkflowService.get_workflow(db, step_data.workflow_id, 0)
            if workflow:
                workflow.step_count = (workflow.step_count or 0) + 1
                workflow.updated_at = datetime.utcnow()

            await db.commit()
            await db.refresh(step)
            logger.info(f"Workflow step created: id={step.id}, workflow_id={step_data.workflow_id}")
            return step

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating workflow step: {e}")
            raise

    @staticmethod
    async def get_workflow_steps(db: AsyncSession, workflow_id: int) -> List[WorkflowStep]:
        """Get all steps for workflow"""
        try:
            result = await db.execute(
                select(WorkflowStep).where(
                    WorkflowStep.workflow_id == workflow_id
                ).order_by(WorkflowStep.step_order.asc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching workflow steps: {e}")
            raise

    @staticmethod
    async def create_trigger(
        db: AsyncSession, trigger_data: TriggerCreateRequest
    ) -> WorkflowTrigger:
        """Create workflow trigger"""
        try:
            trigger = WorkflowTrigger(
                workflow_id=trigger_data.workflow_id,
                trigger_type=trigger_data.trigger_type.value,
                name=trigger_data.name,
                description=trigger_data.description,
                condition=trigger_data.condition,
                schedule_cron=trigger_data.schedule_cron,
                event_type=trigger_data.event_type,
                webhook_path=trigger_data.webhook_path,
                enabled=trigger_data.enabled,
                input_data=trigger_data.input_data,
                trigger_count=0
            )
            db.add(trigger)
            await db.commit()
            await db.refresh(trigger)
            logger.info(f"Trigger created: id={trigger.id}, workflow_id={trigger_data.workflow_id}")
            return trigger

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating trigger: {e}")
            raise

    @staticmethod
    async def get_workflow_triggers(db: AsyncSession, workflow_id: int) -> List[WorkflowTrigger]:
        """Get all triggers for workflow"""
        try:
            result = await db.execute(
                select(WorkflowTrigger).where(
                    WorkflowTrigger.workflow_id == workflow_id
                ).order_by(WorkflowTrigger.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching workflow triggers: {e}")
            raise

    @staticmethod
    async def execute_workflow(
        db: AsyncSession, user_id: int, execution_data: WorkflowExecutionCreateRequest
    ) -> WorkflowExecution:
        """Execute workflow"""
        try:
            workflow = await WorkflowService.get_workflow(db, execution_data.workflow_id, user_id)
            if not workflow:
                raise ValueError("Workflow not found")

            if not workflow.enabled:
                raise ValueError("Workflow is disabled")

            execution = WorkflowExecution(
                workflow_id=execution_data.workflow_id,
                user_id=user_id,
                trigger_id=execution_data.trigger_id,
                status=ExecutionStatus.PENDING.value,
                start_time=datetime.utcnow(),
                input_data=execution_data.input_data,
                progress_percentage=0
            )
            db.add(execution)

            # Update workflow execution count
            workflow.execution_count = (workflow.execution_count or 0) + 1
            workflow.updated_at = datetime.utcnow()

            # Update trigger count if applicable
            if execution_data.trigger_id:
                trigger_result = await db.execute(
                    select(WorkflowTrigger).where(WorkflowTrigger.id == execution_data.trigger_id)
                )
                trigger = trigger_result.scalars().first()
                if trigger:
                    trigger.trigger_count = (trigger.trigger_count or 0) + 1
                    trigger.last_triggered = datetime.utcnow()

            await db.commit()
            await db.refresh(execution)
            logger.info(f"Workflow execution created: id={execution.id}, workflow_id={execution_data.workflow_id}")
            return execution

        except Exception as e:
            await db.rollback()
            logger.error(f"Error executing workflow: {e}")
            raise

    @staticmethod
    async def get_execution(
        db: AsyncSession, execution_id: int, user_id: int
    ) -> Optional[WorkflowExecution]:
        """Get workflow execution"""
        try:
            result = await db.execute(
                select(WorkflowExecution).where(
                    WorkflowExecution.id == execution_id
                ).where(WorkflowExecution.user_id == user_id)
            )
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error fetching execution: {e}")
            raise

    @staticmethod
    async def list_executions(
        db: AsyncSession, user_id: int, workflow_id: Optional[int] = None,
        skip: int = 0, limit: int = 50
    ) -> Tuple[List[WorkflowExecution], int]:
        """List workflow executions"""
        try:
            query = select(WorkflowExecution).where(WorkflowExecution.user_id == user_id)

            if workflow_id:
                query = query.where(WorkflowExecution.workflow_id == workflow_id)

            count_result = await db.execute(query)
            total = len(count_result.scalars().all())

            query = query.offset(skip).limit(limit).order_by(WorkflowExecution.start_time.desc())
            result = await db.execute(query)
            executions = result.scalars().all()
            return executions, total

        except Exception as e:
            logger.error(f"Error listing executions: {e}")
            raise

    @staticmethod
    async def update_execution_status(
        db: AsyncSession, execution_id: int, status: ExecutionStatus,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> WorkflowExecution:
        """Update execution status"""
        try:
            result = await db.execute(
                select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
            )
            execution = result.scalars().first()
            if not execution:
                raise ValueError("Execution not found")

            execution.status = status.value
            if output_data is not None:
                execution.output_data = output_data
            if error_message is not None:
                execution.error_message = error_message

            if status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED]:
                execution.end_time = datetime.utcnow()
                if execution.start_time:
                    execution.duration_seconds = (execution.end_time - execution.start_time).total_seconds()

                # Update workflow stats
                workflow = await db.execute(
                    select(Workflow).where(Workflow.id == execution.workflow_id)
                )
                wf = workflow.scalars().first()
                if wf:
                    if status == ExecutionStatus.COMPLETED:
                        wf.success_count = (wf.success_count or 0) + 1
                    elif status == ExecutionStatus.FAILED:
                        wf.failure_count = (wf.failure_count or 0) + 1
                    wf.last_executed = datetime.utcnow()
                    wf.updated_at = datetime.utcnow()

            await db.commit()
            await db.refresh(execution)
            logger.info(f"Execution status updated: id={execution_id}, status={status.value}")
            return execution

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating execution status: {e}")
            raise

    @staticmethod
    async def record_step_execution(
        db: AsyncSession, execution_id: int, step_id: int, step_order: int,
        step_name: str, status: ExecutionStatus, input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None, error_message: Optional[str] = None,
        duration_seconds: Optional[float] = None, retry_attempt: int = 0
    ) -> StepExecution:
        """Record step execution"""
        try:
            step_exec = StepExecution(
                execution_id=execution_id,
                step_id=step_id,
                step_order=step_order,
                step_name=step_name,
                status=status.value,
                start_time=datetime.utcnow(),
                input_data=input_data,
                output_data=output_data,
                error_message=error_message,
                retry_attempt=retry_attempt
            )

            if status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
                step_exec.end_time = datetime.utcnow()
                step_exec.duration_seconds = duration_seconds

            db.add(step_exec)

            # Update execution progress
            execution = await db.execute(
                select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
            )
            exec_obj = execution.scalars().first()
            if exec_obj:
                exec_obj.current_step = step_order
                exec_obj.status = status.value

            await db.commit()
            await db.refresh(step_exec)
            logger.info(f"Step execution recorded: step_id={step_id}, execution_id={execution_id}")
            return step_exec

        except Exception as e:
            await db.rollback()
            logger.error(f"Error recording step execution: {e}")
            raise

    @staticmethod
    async def get_workflow_stats(db: AsyncSession, workflow_id: int) -> Dict[str, Any]:
        """Get workflow statistics"""
        try:
            result = await db.execute(
                select(WorkflowExecution).where(WorkflowExecution.workflow_id == workflow_id)
            )
            executions = result.scalars().all()

            if not executions:
                return {
                    "workflow_id": workflow_id,
                    "total_executions": 0,
                    "successful_executions": 0,
                    "failed_executions": 0,
                    "average_duration_seconds": 0,
                    "success_rate": 0,
                    "last_execution": None,
                    "most_common_error": None
                }

            successful = len([e for e in executions if e.status == ExecutionStatus.COMPLETED.value])
            failed = len([e for e in executions if e.status == ExecutionStatus.FAILED.value])
            total = len(executions)

            durations = [e.duration_seconds for e in executions if e.duration_seconds]
            avg_duration = sum(durations) / len(durations) if durations else 0

            errors = [e.error_message for e in executions if e.error_message]
            most_common_error = None
            if errors:
                most_common_error = max(set(errors), key=errors.count)

            return {
                "workflow_id": workflow_id,
                "total_executions": total,
                "successful_executions": successful,
                "failed_executions": failed,
                "average_duration_seconds": round(avg_duration, 2),
                "success_rate": round((successful / total * 100) if total > 0 else 0, 2),
                "last_execution": max([e.start_time for e in executions]) if executions else None,
                "most_common_error": most_common_error
            }

        except Exception as e:
            logger.error(f"Error getting workflow stats: {e}")
            raise

    @staticmethod
    async def cancel_execution(db: AsyncSession, execution_id: int, user_id: int) -> WorkflowExecution:
        """Cancel workflow execution"""
        try:
            execution = await WorkflowService.get_execution(db, execution_id, user_id)
            if not execution:
                raise ValueError("Execution not found")

            if execution.status in [ExecutionStatus.COMPLETED.value, ExecutionStatus.FAILED.value, ExecutionStatus.CANCELLED.value]:
                raise ValueError(f"Cannot cancel execution with status {execution.status}")

            execution.status = ExecutionStatus.CANCELLED.value
            execution.end_time = datetime.utcnow()
            if execution.start_time:
                execution.duration_seconds = (execution.end_time - execution.start_time).total_seconds()

            await db.commit()
            await db.refresh(execution)
            logger.info(f"Execution cancelled: id={execution_id}")
            return execution

        except Exception as e:
            await db.rollback()
            logger.error(f"Error cancelling execution: {e}")
            raise

    @staticmethod
    async def pause_workflow(db: AsyncSession, workflow_id: int, user_id: int) -> Workflow:
        """Pause workflow"""
        try:
            workflow = await WorkflowService.get_workflow(db, workflow_id, user_id)
            if not workflow:
                raise ValueError("Workflow not found")

            workflow.status = "paused"
            workflow.updated_at = datetime.utcnow()

            await db.commit()
            await db.refresh(workflow)
            logger.info(f"Workflow paused: id={workflow_id}")
            return workflow

        except Exception as e:
            await db.rollback()
            logger.error(f"Error pausing workflow: {e}")
            raise

    @staticmethod
    async def resume_workflow(db: AsyncSession, workflow_id: int, user_id: int) -> Workflow:
        """Resume workflow"""
        try:
            workflow = await WorkflowService.get_workflow(db, workflow_id, user_id)
            if not workflow:
                raise ValueError("Workflow not found")

            workflow.status = "active"
            workflow.updated_at = datetime.utcnow()

            await db.commit()
            await db.refresh(workflow)
            logger.info(f"Workflow resumed: id={workflow_id}")
            return workflow

        except Exception as e:
            await db.rollback()
            logger.error(f"Error resuming workflow: {e}")
            raise
