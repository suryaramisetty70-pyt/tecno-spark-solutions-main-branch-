"""
PHASE 3: Enterprise Security
Encryption, token management, audit logging, rate limiting
"""

import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional
from cryptography.fernet import Fernet
import jwt
import json

class EncryptionService:
    """Encrypt/decrypt sensitive fields"""

    def __init__(self, master_key: str):
        self.cipher = Fernet(master_key.encode() if len(master_key) < 44 else master_key)

    def encrypt_field(self, plaintext: str) -> str:
        """Encrypt sensitive data"""

        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt_field(self, ciphertext: str) -> str:
        """Decrypt sensitive data"""

        return self.cipher.decrypt(ciphertext.encode()).decode()


class TokenService:
    """JWT token management with revocation"""

    def __init__(self, secret_key: str, redis_client):
        self.secret_key = secret_key
        self.redis = redis_client

    def create_access_token(self, user_id: int, org_id: int, role: str, expires_hours: int = 1) -> str:
        """Create JWT access token"""

        payload = {
            "user_id": user_id,
            "org_id": org_id,
            "role": role,
            "type": "access",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=expires_hours),
            "jti": hashlib.sha256(f"{user_id}:{org_id}:{datetime.utcnow()}".encode()).hexdigest()[:16]
        }

        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def create_refresh_token(self, user_id: int, org_id: int, expires_days: int = 30) -> str:
        """Create refresh token"""

        payload = {
            "user_id": user_id,
            "org_id": org_id,
            "type": "refresh",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=expires_days),
            "jti": hashlib.sha256(f"{user_id}:{org_id}:refresh:{datetime.utcnow()}".encode()).hexdigest()[:16]
        }

        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT"""

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])

            # Check if token is blacklisted
            jti = payload.get("jti")
            if self.redis.exists(f"blacklist:{jti}"):
                return None

            return payload

        except jwt.InvalidTokenError:
            return None

    def revoke_token(self, token: str) -> bool:
        """Add token to blacklist (on logout)"""

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            jti = payload.get("jti")
            exp_timestamp = payload.get("exp")

            # Calculate TTL
            ttl = int(exp_timestamp - datetime.utcnow().timestamp())

            if ttl > 0:
                self.redis.setex(f"blacklist:{jti}", ttl, "1")

            return True

        except jwt.InvalidTokenError:
            return False


class AuditLogger:
    """Enterprise audit logging (immutable)"""

    def __init__(self, db_session):
        self.db = db_session

    async def log_action(self,
                        org_id: int,
                        user_id: Optional[int],
                        action: str,
                        resource_type: str,
                        resource_id: str,
                        result: str,
                        error_message: Optional[str] = None,
                        ip_address: Optional[str] = None,
                        user_agent: Optional[str] = None) -> bool:
        """Log action immutably"""

        # Create immutable hash
        hash_input = f"{org_id}:{user_id}:{action}:{resource_type}:{datetime.utcnow()}"
        entry_hash = hashlib.sha256(hash_input.encode()).hexdigest()

        audit_log = AuditLogV2(
            organization_id=org_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            result=result,
            error_message=error_message,
            ip_address=ip_address,
            user_agent=user_agent,
            entry_hash=entry_hash
        )

        try:
            self.db.add(audit_log)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            return False

    def get_audit_logs(self, org_id: int, limit: int = 100) -> list:
        """Get audit logs for organization"""

        logs = self.db.query(AuditLogV2).filter(
            AuditLogV2.organization_id == org_id
        ).order_by(
            AuditLogV2.created_at.desc()
        ).limit(limit).all()

        return [
            {
                "id": log.id,
                "action": log.action,
                "resource_type": log.resource_type,
                "result": log.result,
                "created_at": log.created_at.isoformat(),
                "user_id": log.user_id
            }
            for log in logs
        ]


class PasswordService:
    """Secure password hashing"""

    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password with bcrypt"""

        return PasswordService.pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""

        return PasswordService.pwd_context.verify(plain_password, hashed_password)


class RateLimitService:
    """Distributed rate limiting with Redis"""

    def __init__(self, redis_client):
        self.redis = redis_client

    def check_rate_limit(self, key: str, limit: int, window_seconds: int) -> bool:
        """Check if request exceeds rate limit"""

        current = self.redis.incr(key)

        if current == 1:
            # First request in window - set expiry
            self.redis.expire(key, window_seconds)

        return current <= limit

    def get_remaining_requests(self, key: str, limit: int) -> int:
        """Get remaining requests in window"""

        current = int(self.redis.get(key) or 0)
        return max(0, limit - current)

    def apply_tiered_limits(self, user_id: int, role: str, action: str) -> bool:
        """Apply different limits by role"""

        key = f"rate_limit:{user_id}:{action}"

        if role == "admin":
            # Admins: unlimited
            return True
        elif role == "manager":
            # Managers: 1000 req/min
            return self.check_rate_limit(key, 1000, 60)
        else:
            # Others: 100 req/min
            return self.check_rate_limit(key, 100, 60)


class ComplianceValidator:
    """Validate compliance requirements"""

    @staticmethod
    def validate_data_retention(org_id: int, data_type: str) -> bool:
        """Check GDPR data retention policies"""

        # GDPR: max 30 days for certain data types
        retention_days = {
            "failed_login_attempt": 30,
            "api_access_log": 90,
            "temporary_session": 30,
            "audit_log": 2555  # 7 years for compliance
        }

        return retention_days.get(data_type, 365)

    @staticmethod
    def validate_encryption_required(data_type: str) -> bool:
        """Check if data type requires encryption"""

        sensitive_types = [
            "email",
            "phone_number",
            "ssn",
            "health_data",
            "financial_data",
            "api_key",
            "password"
        ]

        return data_type in sensitive_types

    @staticmethod
    def validate_audit_required(action: str) -> bool:
        """Check if action requires audit logging"""

        auditable_actions = [
            "login",
            "logout",
            "create_user",
            "delete_user",
            "modify_permissions",
            "execute_agent",
            "access_data",
            "modify_data",
            "delete_data"
        ]

        return action in auditable_actions
