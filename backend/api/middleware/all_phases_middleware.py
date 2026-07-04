"""
Middleware implementations for all 5 phases
- Tenant context extraction
- RBAC enforcement
- Rate limiting
- Security headers
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import jwt
import json

class TenantMiddleware(BaseHTTPMiddleware):
    """Extract and validate tenant context from JWT"""

    def __init__(self, app, secret_key: str):
        super().__init__(app)
        self.secret_key = secret_key

    async def dispatch(self, request: Request, call_next):
        # Skip auth for health endpoints
        if request.url.path in ["/health", "/ready", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        try:
            scheme, token = auth_header.split()

            if scheme.lower() != "bearer":
                raise HTTPException(status_code=401, detail="Invalid auth scheme")

            # Decode JWT
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])

            # Attach to request state
            request.state.user_id = payload.get("user_id")
            request.state.organization_id = payload.get("org_id")
            request.state.role = payload.get("role", "member")
            request.state.permissions = payload.get("permissions", {})

        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except ValueError:
            raise HTTPException(status_code=401, detail="Invalid Authorization header")

        response = await call_next(request)
        return response


class RBACMiddleware(BaseHTTPMiddleware):
    """Enforce RBAC permissions"""

    RESOURCE_ACTION_MAPPING = {
        "/api/v1/agents": {"GET": "read", "POST": "create"},
        "/api/v1/agents/{id}": {"GET": "read", "PUT": "update", "DELETE": "delete"},
        "/api/v1/agents/{id}/execute": {"POST": "execute"},
        "/api/v1/workflows": {"GET": "read", "POST": "create"},
        "/api/v1/admin": {"GET": "read", "POST": "create"},
    }

    PERMISSIONS_BY_ROLE = {
        "admin": {"agent": ["create", "read", "update", "delete", "execute"], "workflow": ["create", "read", "update", "delete", "execute"], "admin": ["read", "create"]},
        "manager": {"agent": ["read", "execute"], "workflow": ["create", "read", "execute"]},
        "member": {"agent": ["read", "execute"], "workflow": ["read", "execute"]},
        "viewer": {"agent": ["read"], "workflow": ["read"]},
    }

    async def dispatch(self, request: Request, call_next):
        # Skip RBAC for public endpoints
        if request.url.path in ["/health", "/ready", "/auth/login", "/auth/register"]:
            return await call_next(request)

        # Get user role
        role = getattr(request.state, "role", "viewer")

        # Determine resource and action
        path = request.url.path
        method = request.method

        resource = None
        if "/agents" in path:
            resource = "agent"
        elif "/workflows" in path:
            resource = "workflow"
        elif "/admin" in path:
            resource = "admin"

        action = None
        if method == "GET":
            action = "read"
        elif method == "POST":
            action = "create"
        elif method == "PUT":
            action = "update"
        elif method == "DELETE":
            action = "delete"

        # Check permission
        if resource and action:
            role_perms = self.PERMISSIONS_BY_ROLE.get(role, {})
            resource_actions = role_perms.get(resource, [])

            if action not in resource_actions:
                return JSONResponse(
                    status_code=403,
                    content={"detail": f"Permission denied: {resource}:{action}"}
                )

        response = await call_next(request)
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Implement distributed rate limiting"""

    def __init__(self, app, redis_client):
        super().__init__(app)
        self.redis = redis_client

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for non-API calls
        if not request.url.path.startswith("/api"):
            return await call_next(request)

        # Get user identifier
        user_id = getattr(request.state, "user_id", None)
        role = getattr(request.state, "role", "guest")
        ip_address = request.client.host if request.client else "unknown"

        key = f"rate_limit:{user_id or ip_address}"

        # Apply tiered limits
        limits = {
            "admin": 10000,
            "manager": 1000,
            "member": 100,
            "guest": 50
        }

        limit = limits.get(role, 50)

        # Check rate limit (per minute)
        current = int(self.redis.incr(key) or 0)

        if current == 1:
            self.redis.expire(key, 60)

        if current > limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"}
            )

        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit - current))

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"

        return response


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Log all actions for audit trail"""

    def __init__(self, app, audit_logger):
        super().__init__(app)
        self.audit_logger = audit_logger

    async def dispatch(self, request: Request, call_next):
        # Record request start
        user_id = getattr(request.state, "user_id", None)
        org_id = getattr(request.state, "organization_id", None)

        response = await call_next(request)

        # Log action if auditable
        auditable_actions = [
            "POST", "PUT", "DELETE",
            "GET /api/v1/admin"
        ]

        method_path = f"{request.method} {request.url.path}"

        if any(action in method_path for action in auditable_actions):
            await self.audit_logger.log_action(
                org_id=org_id,
                user_id=user_id,
                action=request.method,
                resource_type=self._extract_resource_type(request.url.path),
                resource_id=self._extract_resource_id(request.url.path),
                result="success" if response.status_code < 400 else "error",
                error_message=None if response.status_code < 400 else f"Status: {response.status_code}",
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("User-Agent")
            )

        return response

    def _extract_resource_type(self, path: str) -> str:
        """Extract resource type from path"""

        if "/agents" in path:
            return "agent"
        elif "/workflows" in path:
            return "workflow"
        elif "/integrations" in path:
            return "integration"
        elif "/users" in path:
            return "user"
        return "unknown"

    def _extract_resource_id(self, path: str) -> str:
        """Extract resource ID from path"""

        parts = path.strip("/").split("/")
        if len(parts) > 2:
            return parts[-1]
        return ""
