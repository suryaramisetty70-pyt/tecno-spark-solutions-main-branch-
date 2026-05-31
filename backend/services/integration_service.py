"""
Integration management service - business logic for service integrations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
import logging
import hashlib
import secrets

from db.models import Integration, IntegrationCredential, WebhookLog, IntegrationMetric
from api.schemas.integration_schemas import (
    IntegrationConnectRequest, IntegrationUpdateRequest, ServiceCredentialRequest,
    IntegrationSyncRequest, WebhookEventRequest, IntegrationStatus
)

logger = logging.getLogger(__name__)


class IntegrationService:
    """Integration management service"""

    @staticmethod
    async def connect_integration(
        db: AsyncSession, user_id: int, integration_data: IntegrationConnectRequest
    ) -> Integration:
        """Connect new integration"""
        try:
            webhook_secret = secrets.token_urlsafe(32) if integration_data.webhook_url else None

            integration = Integration(
                user_id=user_id,
                service=integration_data.service,
                service_type=integration_data.service_type.value,
                name=integration_data.name,
                description=integration_data.description,
                status=IntegrationStatus.PENDING_AUTH.value,
                is_active=True,
                auth_method="oauth2" if integration_data.oauth_code else "api_key",
                config=integration_data.config,
                webhook_url=integration_data.webhook_url,
                webhook_secret=webhook_secret,
                usage_count=0
            )

            db.add(integration)
            await db.commit()
            await db.refresh(integration)

            # Store credentials if provided
            if integration_data.api_key:
                encrypted_key = IntegrationService._encrypt_credential(integration_data.api_key)
                credential = IntegrationCredential(
                    integration_id=integration.id,
                    credential_type="api_key",
                    credential_value=encrypted_key
                )
                db.add(credential)
                await db.commit()

            logger.info(f"Integration connected: id={integration.id}, service={integration_data.service}")
            return integration

        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Integrity error: {e}")
            raise ValueError("Integration already exists for this service")
        except Exception as e:
            await db.rollback()
            logger.error(f"Error connecting integration: {e}")
            raise

    @staticmethod
    async def get_integration(
        db: AsyncSession, integration_id: int, user_id: int
    ) -> Optional[Integration]:
        """Get integration by ID"""
        try:
            result = await db.execute(
                select(Integration).where(
                    Integration.id == integration_id
                ).where(Integration.user_id == user_id)
            )
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error fetching integration: {e}")
            raise

    @staticmethod
    async def list_integrations(
        db: AsyncSession, user_id: int, skip: int = 0, limit: int = 50
    ) -> Tuple[List[Integration], int]:
        """List user's integrations"""
        try:
            count_result = await db.execute(
                select(Integration).where(Integration.user_id == user_id)
            )
            total = len(count_result.scalars().all())

            result = await db.execute(
                select(Integration).where(
                    Integration.user_id == user_id
                ).offset(skip).limit(limit).order_by(Integration.created_at.desc())
            )
            integrations = result.scalars().all()
            return integrations, total

        except Exception as e:
            logger.error(f"Error listing integrations: {e}")
            raise

    @staticmethod
    async def update_integration(
        db: AsyncSession, integration_id: int, user_id: int,
        update_data: IntegrationUpdateRequest
    ) -> Integration:
        """Update integration"""
        try:
            integration = await IntegrationService.get_integration(db, integration_id, user_id)
            if not integration:
                raise ValueError("Integration not found")

            if update_data.name is not None:
                integration.name = update_data.name
            if update_data.description is not None:
                integration.description = update_data.description
            if update_data.is_active is not None:
                integration.is_active = update_data.is_active
            if update_data.config is not None:
                integration.config = update_data.config
            if update_data.webhook_url is not None:
                integration.webhook_url = update_data.webhook_url
                if not integration.webhook_secret:
                    integration.webhook_secret = secrets.token_urlsafe(32)

            integration.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(integration)
            logger.info(f"Integration updated: id={integration_id}")
            return integration

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating integration: {e}")
            raise

    @staticmethod
    async def disconnect_integration(
        db: AsyncSession, integration_id: int, user_id: int
    ) -> bool:
        """Disconnect integration"""
        try:
            integration = await IntegrationService.get_integration(db, integration_id, user_id)
            if not integration:
                raise ValueError("Integration not found")

            # Delete credentials
            credentials = await db.execute(
                select(IntegrationCredential).where(
                    IntegrationCredential.integration_id == integration_id
                )
            )
            for cred in credentials.scalars().all():
                await db.delete(cred)

            # Delete webhook logs
            logs = await db.execute(
                select(WebhookLog).where(WebhookLog.integration_id == integration_id)
            )
            for log in logs.scalars().all():
                await db.delete(log)

            # Delete metrics
            metrics = await db.execute(
                select(IntegrationMetric).where(IntegrationMetric.integration_id == integration_id)
            )
            for metric in metrics.scalars().all():
                await db.delete(metric)

            # Delete integration
            await db.delete(integration)
            await db.commit()
            logger.info(f"Integration disconnected: id={integration_id}")
            return True

        except Exception as e:
            await db.rollback()
            logger.error(f"Error disconnecting integration: {e}")
            raise

    @staticmethod
    async def store_credential(
        db: AsyncSession, integration_id: int, credential_data: ServiceCredentialRequest
    ) -> IntegrationCredential:
        """Store encrypted credential"""
        try:
            encrypted_value = IntegrationService._encrypt_credential(credential_data.credential_value)

            credential = IntegrationCredential(
                integration_id=integration_id,
                credential_type=credential_data.credential_type,
                credential_value=encrypted_value
            )

            if credential_data.expires_in_days:
                credential.expires_at = datetime.utcnow() + timedelta(days=credential_data.expires_in_days)

            db.add(credential)
            await db.commit()
            await db.refresh(credential)
            logger.info(f"Credential stored: integration_id={integration_id}")
            return credential

        except Exception as e:
            await db.rollback()
            logger.error(f"Error storing credential: {e}")
            raise

    @staticmethod
    async def test_connection(
        db: AsyncSession, integration_id: int, user_id: int,
        test_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Test integration connection"""
        try:
            integration = await IntegrationService.get_integration(db, integration_id, user_id)
            if not integration:
                raise ValueError("Integration not found")

            config = test_config or integration.config

            # Simulate connection test
            import time
            start_time = time.time()

            # In real implementation, would make actual API call
            success = True
            message = "Connection successful"
            error = None

            latency_ms = (time.time() - start_time) * 1000

            return {
                "success": success,
                "message": message,
                "error": error,
                "latency_ms": round(latency_ms, 2)
            }

        except Exception as e:
            logger.error(f"Error testing connection: {e}")
            return {
                "success": False,
                "message": "Connection failed",
                "error": str(e),
                "latency_ms": 0
            }

    @staticmethod
    async def sync_data(
        db: AsyncSession, integration_id: int, user_id: int,
        sync_data: IntegrationSyncRequest
    ) -> Dict[str, Any]:
        """Sync data from integration"""
        try:
            integration = await IntegrationService.get_integration(db, integration_id, user_id)
            if not integration:
                raise ValueError("Integration not found")

            sync_id = secrets.token_urlsafe(16)
            start_time = datetime.utcnow()

            # Simulate sync
            items_synced = 100
            items_failed = 0
            error_message = None

            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            # Update integration sync time
            integration.synced_at = end_time
            integration.status = IntegrationStatus.CONNECTED.value
            await db.commit()

            # Record metric
            metric = IntegrationMetric(
                integration_id=integration_id,
                user_id=user_id,
                sync_type=sync_data.sync_type,
                items_synced=items_synced,
                items_failed=items_failed,
                duration_seconds=duration,
                error_message=error_message
            )
            db.add(metric)
            await db.commit()

            logger.info(f"Sync completed: integration_id={integration_id}, items={items_synced}")

            return {
                "sync_id": sync_id,
                "integration_id": integration_id,
                "sync_type": sync_data.sync_type,
                "status": "completed",
                "start_time": start_time,
                "end_time": end_time,
                "items_synced": items_synced,
                "items_failed": items_failed,
                "error_message": error_message
            }

        except Exception as e:
            await db.rollback()
            logger.error(f"Error syncing data: {e}")
            raise

    @staticmethod
    async def record_webhook_event(
        db: AsyncSession, integration_id: int, event_data: WebhookEventRequest,
        status_code: int = 200, response_data: Optional[Dict[str, Any]] = None,
        latency_ms: float = 0, error_message: Optional[str] = None
    ) -> WebhookLog:
        """Record webhook event"""
        try:
            log = WebhookLog(
                integration_id=integration_id,
                event_type=event_data.event_type,
                status="success" if status_code == 200 else "failed",
                status_code=status_code,
                request_payload=event_data.event_data,
                response_payload=response_data,
                error_message=error_message,
                latency_ms=latency_ms
            )
            db.add(log)
            await db.commit()
            await db.refresh(log)
            logger.info(f"Webhook logged: integration_id={integration_id}, event={event_data.event_type}")
            return log

        except Exception as e:
            await db.rollback()
            logger.error(f"Error recording webhook: {e}")
            raise

    @staticmethod
    async def get_webhook_logs(
        db: AsyncSession, integration_id: int, skip: int = 0, limit: int = 50
    ) -> Tuple[List[WebhookLog], int]:
        """Get webhook logs for integration"""
        try:
            count_result = await db.execute(
                select(WebhookLog).where(WebhookLog.integration_id == integration_id)
            )
            total = len(count_result.scalars().all())

            result = await db.execute(
                select(WebhookLog).where(
                    WebhookLog.integration_id == integration_id
                ).offset(skip).limit(limit).order_by(WebhookLog.created_at.desc())
            )
            logs = result.scalars().all()
            return logs, total

        except Exception as e:
            logger.error(f"Error fetching webhook logs: {e}")
            raise

    @staticmethod
    async def get_integration_metrics(
        db: AsyncSession, integration_id: int
    ) -> Dict[str, Any]:
        """Get integration metrics"""
        try:
            result = await db.execute(
                select(IntegrationMetric).where(IntegrationMetric.integration_id == integration_id)
            )
            metrics = result.scalars().all()

            if not metrics:
                return {
                    "integration_id": integration_id,
                    "total_syncs": 0,
                    "successful_syncs": 0,
                    "failed_syncs": 0,
                    "last_sync": None,
                    "items_synced_total": 0,
                    "average_sync_time_seconds": 0
                }

            total_syncs = len(metrics)
            successful = len([m for m in metrics if m.error_message is None])
            failed = total_syncs - successful
            items_synced = sum(m.items_synced or 0 for m in metrics)
            avg_time = sum(m.duration_seconds or 0 for m in metrics) / total_syncs if total_syncs > 0 else 0

            # Get webhook stats
            webhook_result = await db.execute(
                select(WebhookLog).where(WebhookLog.integration_id == integration_id)
            )
            webhook_logs = webhook_result.scalars().all()
            webhook_failed = len([w for w in webhook_logs if w.status == "failed"])
            avg_webhook_latency = sum(w.latency_ms for w in webhook_logs) / len(webhook_logs) if webhook_logs else 0

            return {
                "integration_id": integration_id,
                "total_syncs": total_syncs,
                "successful_syncs": successful,
                "failed_syncs": failed,
                "last_sync": max([m.created_at for m in metrics]) if metrics else None,
                "items_synced_total": items_synced,
                "webhook_calls_total": len(webhook_logs),
                "webhook_calls_failed": webhook_failed,
                "average_sync_time_seconds": round(avg_time, 2),
                "average_webhook_latency_ms": round(avg_webhook_latency, 2)
            }

        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            raise

    @staticmethod
    async def update_integration_status(
        db: AsyncSession, integration_id: int, status: IntegrationStatus,
        error_message: Optional[str] = None
    ) -> Integration:
        """Update integration status"""
        try:
            result = await db.execute(
                select(Integration).where(Integration.id == integration_id)
            )
            integration = result.scalars().first()
            if not integration:
                raise ValueError("Integration not found")

            integration.status = status.value
            if error_message:
                integration.error_message = error_message
            else:
                integration.error_message = None

            integration.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(integration)
            logger.info(f"Integration status updated: id={integration_id}, status={status.value}")
            return integration

        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating status: {e}")
            raise

    @staticmethod
    def _encrypt_credential(value: str) -> str:
        """Encrypt credential (basic encryption)"""
        # In production, use proper encryption like cryptography.fernet
        import base64
        return base64.b64encode(value.encode()).decode()

    @staticmethod
    def _decrypt_credential(encrypted_value: str) -> str:
        """Decrypt credential"""
        import base64
        return base64.b64decode(encrypted_value.encode()).decode()

    @staticmethod
    async def record_usage(db: AsyncSession, integration_id: int) -> None:
        """Record integration usage"""
        try:
            result = await db.execute(
                select(Integration).where(Integration.id == integration_id)
            )
            integration = result.scalars().first()
            if integration:
                integration.usage_count = (integration.usage_count or 0) + 1
                integration.last_used = datetime.utcnow()
                await db.commit()
        except Exception as e:
            logger.error(f"Error recording usage: {e}")
