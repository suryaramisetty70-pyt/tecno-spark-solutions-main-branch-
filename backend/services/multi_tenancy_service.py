"""
PHASE 2: Multi-Tenancy & RBAC
Organization isolation, tenant scoping, permission enforcement
"""

from typing import Optional, Dict, List
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
import jwt

class TenantContext:
    """Extract and manage tenant context from JWT"""

    @staticmethod
    def extract_from_jwt(token: str, secret_key: str) -> Dict:
        """Extract organization_id from JWT claims"""

        try:
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])

            return {
                "organization_id": payload.get("org_id"),
                "user_id": payload.get("user_id"),
                "role": payload.get("role", "member"),
                "permissions": payload.get("permissions", {})
            }

        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    @staticmethod
    def add_to_request(request: Request, tenant_data: Dict) -> None:
        """Attach tenant context to request state"""

        request.state.organization_id = tenant_data["organization_id"]
        request.state.user_id = tenant_data["user_id"]
        request.state.role = tenant_data["role"]
        request.state.permissions = tenant_data["permissions"]


class RBACService:
    """
    Role-Based Access Control
    Permission matrix: admin > manager > user > viewer
    """

    PERMISSIONS_BY_ROLE = {
        "admin": {
            "agent": ["create", "read", "update", "delete", "execute", "configure"],
            "workflow": ["create", "read", "update", "delete", "execute", "schedule"],
            "integration": ["create", "read", "update", "delete"],
            "organization": ["manage_users", "manage_billing", "manage_security", "manage_integrations"],
            "audit": ["read", "export"]
        },
        "manager": {
            "agent": ["read", "execute", "configure"],
            "workflow": ["create", "read", "update", "execute", "schedule"],
            "integration": ["read"],
            "organization": [],
            "audit": ["read"]
        },
        "member": {
            "agent": ["read", "execute"],
            "workflow": ["read", "execute"],
            "integration": [],
            "organization": [],
            "audit": []
        },
        "viewer": {
            "agent": ["read"],
            "workflow": ["read"],
            "integration": [],
            "organization": [],
            "audit": []
        }
    }

    @staticmethod
    def check_permission(role: str, resource: str, action: str) -> bool:
        """Check if role has permission for resource:action"""

        role_perms = RBACService.PERMISSIONS_BY_ROLE.get(role, {})
        resource_perms = role_perms.get(resource, [])

        return action in resource_perms

    @staticmethod
    def require_permission(resource: str, action: str):
        """Decorator for endpoint permission checks"""

        async def check(request: Request):
            role = getattr(request.state, "role", "viewer")

            if not RBACService.check_permission(role, resource, action):
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: {resource}:{action}"
                )

        return Depends(check)


class TenantScopingService:
    """
    Tenant-scoped database queries
    Ensure all queries filter by organization_id
    """

    @staticmethod
    def scope_query(query, model, org_id: int):
        """Add tenant filtering to query"""

        if hasattr(model, 'organization_id'):
            return query.filter(model.organization_id == org_id)

        return query

    @staticmethod
    def scope_agent_query(db: Session, org_id: int):
        """Scoped query for agents"""

        return db.query(AgentV2).filter(
            (AgentV2.organization_id == org_id) |
            (AgentV2.is_public == True)
        )

    @staticmethod
    def scope_workflow_query(db: Session, org_id: int):
        """Scoped query for workflows"""

        return db.query(WorkflowV2).filter(
            WorkflowV2.organization_id == org_id
        )

    @staticmethod
    def scope_integration_query(db: Session, org_id: int):
        """Scoped query for integrations"""

        return db.query(IntegrationV2).filter(
            IntegrationV2.organization_id == org_id
        )


class OrganizationService:
    """CRUD operations for organizations"""

    @staticmethod
    def create_org(db: Session, name: str, owner_id: int, plan_tier: str = "free") -> Organization:
        """Create new organization"""

        from slugify import slugify

        org = Organization(
            name=name,
            slug=slugify(name),
            plan_tier=plan_tier,
            max_users=5 if plan_tier == "free" else (100 if plan_tier == "pro" else None),
            max_agents=50 if plan_tier == "free" else (500 if plan_tier == "pro" else None),
        )

        db.add(org)
        db.commit()

        # Add owner as admin
        member = OrganizationMember(
            organization_id=org.id,
            user_id=owner_id,
            role="admin",
            is_owner=True
        )

        db.add(member)
        db.commit()

        return org

    @staticmethod
    def add_member(db: Session, org_id: int, user_id: int, role: str = "member") -> OrganizationMember:
        """Add user to organization"""

        member = OrganizationMember(
            organization_id=org_id,
            user_id=user_id,
            role=role
        )

        db.add(member)
        db.commit()

        return member

    @staticmethod
    def get_org(db: Session, org_id: int) -> Optional[Organization]:
        """Get organization"""

        return db.query(Organization).filter(
            Organization.id == org_id
        ).first()

    @staticmethod
    def get_user_orgs(db: Session, user_id: int) -> List[Organization]:
        """Get all organizations for user"""

        members = db.query(OrganizationMember).filter(
            OrganizationMember.user_id == user_id
        ).all()

        orgs = []
        for member in members:
            org = db.query(Organization).get(member.organization_id)
            if org:
                orgs.append(org)

        return orgs

    @staticmethod
    def check_org_limit(db: Session, org_id: int, resource_type: str) -> bool:
        """Check if organization exceeded limits"""

        org = db.query(Organization).get(org_id)

        if resource_type == "users":
            count = db.query(OrganizationMember).filter(
                OrganizationMember.organization_id == org_id
            ).count()
            return count < org.max_users

        elif resource_type == "agents":
            count = db.query(AgentRegistrationV2).filter(
                AgentRegistrationV2.organization_id == org_id
            ).count()
            return count < org.max_agents

        return True
