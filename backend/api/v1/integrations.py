"""
Integration management API endpoints
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from api.dependencies.auth_dependencies import get_db_session, get_current_user
from api.schemas.auth_schemas import CurrentUser
from api.schemas.integration_schemas import (
    IntegrationConnectRequest, IntegrationResponse, IntegrationUpdateRequest,
    ServiceCredentialRequest, ServiceCredentialResponse, IntegrationTestRequest,
    IntegrationTestResponse, IntegrationSyncRequest, IntegrationSyncResponse,
    WebhookEventRequest, WebhookLogResponse, IntegrationListResponse,
    IntegrationMetricsResponse, ErrorResponse, ServiceCatalogResponse
)
from services.integration_service import IntegrationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/integrations", tags=["integrations"])


@router.get("", response_model=IntegrationListResponse, status_code=status.HTTP_200_OK)
async def list_integrations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """List user's integrations"""
    try:
        integrations, total = await IntegrationService.list_integrations(
            db, current_user.id, skip, limit
        )

        return IntegrationListResponse(
            total=total,
            page=skip // limit + 1,
            per_page=limit,
            integrations=[
                IntegrationResponse(
                    id=i.id,
                    user_id=i.user_id,
                    service=i.service,
                    service_type=i.service_type,
                    name=i.name,
                    description=i.description,
                    status=i.status,
                    is_active=i.is_active,
                    auth_method=i.auth_method,
                    webhook_url=i.webhook_url,
                    webhook_secret=i.webhook_secret if i.status == "connected" else None,
                    synced_at=i.synced_at,
                    expires_at=i.expires_at,
                    error_message=i.error_message,
                    usage_count=i.usage_count or 0,
                    last_used=i.last_used,
                    created_at=i.created_at,
                    updated_at=i.updated_at
                )
                for i in integrations
            ]
        )

    except Exception as e:
        logger.error(f"Error listing integrations: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error listing integrations"
        }


@router.get("/{integration_id}", response_model=IntegrationResponse, status_code=status.HTTP_200_OK)
async def get_integration(
    integration_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get integration details"""
    try:
        integration = await IntegrationService.get_integration(db, integration_id, current_user.id)
        if not integration:
            return {
                "status_code": 404,
                "message": "Not Found",
                "detail": "Integration not found"
            }

        return IntegrationResponse(
            id=integration.id,
            user_id=integration.user_id,
            service=integration.service,
            service_type=integration.service_type,
            name=integration.name,
            description=integration.description,
            status=integration.status,
            is_active=integration.is_active,
            auth_method=integration.auth_method,
            webhook_url=integration.webhook_url,
            webhook_secret=integration.webhook_secret if integration.status == "connected" else None,
            synced_at=integration.synced_at,
            expires_at=integration.expires_at,
            error_message=integration.error_message,
            usage_count=integration.usage_count or 0,
            last_used=integration.last_used,
            created_at=integration.created_at,
            updated_at=integration.updated_at
        )

    except Exception as e:
        logger.error(f"Error fetching integration: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error fetching integration"
        }


@router.post("", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def connect_integration(
    connect_data: IntegrationConnectRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Connect new integration"""
    try:
        integration = await IntegrationService.connect_integration(db, current_user.id, connect_data)

        return IntegrationResponse(
            id=integration.id,
            user_id=integration.user_id,
            service=integration.service,
            service_type=integration.service_type,
            name=integration.name,
            description=integration.description,
            status=integration.status,
            is_active=integration.is_active,
            auth_method=integration.auth_method,
            webhook_url=integration.webhook_url,
            webhook_secret=integration.webhook_secret,
            synced_at=integration.synced_at,
            expires_at=integration.expires_at,
            error_message=integration.error_message,
            usage_count=integration.usage_count or 0,
            last_used=integration.last_used,
            created_at=integration.created_at,
            updated_at=integration.updated_at
        )

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return {
            "status_code": 400,
            "message": "Bad Request",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error connecting integration: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error connecting integration"
        }


@router.put("/{integration_id}", response_model=IntegrationResponse, status_code=status.HTTP_200_OK)
async def update_integration(
    integration_id: int,
    update_data: IntegrationUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update integration"""
    try:
        integration = await IntegrationService.update_integration(
            db, integration_id, current_user.id, update_data
        )

        return IntegrationResponse(
            id=integration.id,
            user_id=integration.user_id,
            service=integration.service,
            service_type=integration.service_type,
            name=integration.name,
            description=integration.description,
            status=integration.status,
            is_active=integration.is_active,
            auth_method=integration.auth_method,
            webhook_url=integration.webhook_url,
            webhook_secret=integration.webhook_secret if integration.status == "connected" else None,
            synced_at=integration.synced_at,
            expires_at=integration.expires_at,
            error_message=integration.error_message,
            usage_count=integration.usage_count or 0,
            last_used=integration.last_used,
            created_at=integration.created_at,
            updated_at=integration.updated_at
        )

    except ValueError as e:
        logger.warning(f"Integration not found: {e}")
        return {
            "status_code": 404,
            "message": "Not Found",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error updating integration: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error updating integration"
        }


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect_integration(
    integration_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Disconnect integration"""
    try:
        await IntegrationService.disconnect_integration(db, integration_id, current_user.id)
        return None

    except ValueError as e:
        logger.warning(f"Integration not found: {e}")
        return {
            "status_code": 404,
            "message": "Not Found",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error disconnecting integration: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error disconnecting integration"
        }


@router.post("/{integration_id}/credentials", response_model=ServiceCredentialResponse, status_code=status.HTTP_201_CREATED)
async def store_credential(
    integration_id: int,
    credential_data: ServiceCredentialRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Store integration credential"""
    try:
        credential = await IntegrationService.store_credential(db, integration_id, credential_data)

        return ServiceCredentialResponse(
            id=credential.id,
            integration_id=credential.integration_id,
            credential_type=credential.credential_type,
            expires_at=credential.expires_at,
            created_at=credential.created_at,
            updated_at=credential.updated_at
        )

    except Exception as e:
        logger.error(f"Error storing credential: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error storing credential"
        }


@router.post("/{integration_id}/test", response_model=IntegrationTestResponse, status_code=status.HTTP_200_OK)
async def test_integration(
    integration_id: int,
    test_data: IntegrationTestRequest = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Test integration connection"""
    try:
        result = await IntegrationService.test_connection(
            db, integration_id, current_user.id,
            test_data.config if test_data else None
        )

        return IntegrationTestResponse(
            success=result["success"],
            message=result["message"],
            error=result.get("error"),
            latency_ms=result["latency_ms"]
        )

    except Exception as e:
        logger.error(f"Error testing integration: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error testing integration"
        }


@router.post("/{integration_id}/sync", response_model=IntegrationSyncResponse, status_code=status.HTTP_200_OK)
async def sync_integration(
    integration_id: int,
    sync_data: IntegrationSyncRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Sync data from integration"""
    try:
        result = await IntegrationService.sync_data(db, integration_id, current_user.id, sync_data)

        return IntegrationSyncResponse(
            sync_id=result["sync_id"],
            integration_id=result["integration_id"],
            sync_type=result["sync_type"],
            status=result["status"],
            start_time=result["start_time"],
            end_time=result["end_time"],
            items_synced=result["items_synced"],
            items_failed=result["items_failed"],
            error_message=result["error_message"]
        )

    except ValueError as e:
        logger.warning(f"Integration not found: {e}")
        return {
            "status_code": 404,
            "message": "Not Found",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Error syncing integration: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error syncing integration"
        }


@router.get("/{integration_id}/webhooks", response_model=list[WebhookLogResponse], status_code=status.HTTP_200_OK)
async def get_webhook_logs(
    integration_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get webhook logs for integration"""
    try:
        logs, total = await IntegrationService.get_webhook_logs(db, integration_id, skip, limit)

        return [
            WebhookLogResponse(
                id=log.id,
                integration_id=log.integration_id,
                event_type=log.event_type,
                status=log.status,
                status_code=log.status_code,
                request_payload=log.request_payload,
                response_payload=log.response_payload,
                error_message=log.error_message,
                latency_ms=log.latency_ms,
                created_at=log.created_at
            )
            for log in logs
        ]

    except Exception as e:
        logger.error(f"Error fetching webhook logs: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error fetching logs"
        }


@router.get("/{integration_id}/metrics", response_model=IntegrationMetricsResponse, status_code=status.HTTP_200_OK)
async def get_integration_metrics(
    integration_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get integration metrics"""
    try:
        metrics = await IntegrationService.get_integration_metrics(db, integration_id)

        return IntegrationMetricsResponse(
            integration_id=metrics["integration_id"],
            service_name="",
            total_syncs=metrics["total_syncs"],
            successful_syncs=metrics["successful_syncs"],
            failed_syncs=metrics["failed_syncs"],
            last_sync=metrics["last_sync"],
            items_synced_total=metrics["items_synced_total"],
            webhook_calls_total=metrics.get("webhook_calls_total", 0),
            webhook_calls_failed=metrics.get("webhook_calls_failed", 0),
            average_sync_time_seconds=metrics["average_sync_time_seconds"],
            average_webhook_latency_ms=metrics.get("average_webhook_latency_ms", 0)
        )

    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error getting metrics"
        }


@router.post("/{integration_id}/webhook", status_code=status.HTTP_200_OK)
async def receive_webhook(
    integration_id: int,
    event_data: WebhookEventRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Receive webhook event from integration"""
    try:
        log = await IntegrationService.record_webhook_event(
            db, integration_id, event_data,
            status_code=200
        )

        await IntegrationService.record_usage(db, integration_id)

        return {
            "message": "Webhook received",
            "event_id": log.id,
            "status": "processed"
        }

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {
            "status_code": 500,
            "message": "Internal Server Error",
            "detail": "Error processing webhook"
        }
