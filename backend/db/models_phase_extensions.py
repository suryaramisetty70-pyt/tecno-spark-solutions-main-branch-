"""
Extended SQLAlchemy Models for All 5 Phases
New tables for: Multi-tenancy, Agent Scaling, Company Integration, Security, Global Scale
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text,
    JSON, Index, Table, UniqueConstraint, Numeric
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# ==================== PHASE 2: MULTI-TENANCY ====================

class Organization(Base):
    """Organizations/Companies using Tecno Spark"""
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True)
    description = Column(Text)
    logo_url = Column(String(500))
    website = Column(String(500))

    # Plan & Limits
    plan_tier = Column(String(50), default="free")  # free, pro, enterprise
    max_users = Column(Integer, default=5)
    max_agents = Column(Integer, default=50)
    max_workflows = Column(Integer, default=20)
    max_api_calls_per_month = Column(Integer, default=10000)

    # Features
    sso_enabled = Column(Boolean, default=False)
    custom_domain_enabled = Column(Boolean, default=False)
    white_label_enabled = Column(Boolean, default=False)

    # Status & Dates
    status = Column(String(50), default="active")  # active, suspended, deleted
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    members = relationship("OrganizationMember", back_populates="organization")
    teams = relationship("Team", back_populates="organization")
    agents = relationship("AgentV2", back_populates="organization")
    workflows = relationship("WorkflowV2", back_populates="organization")
    integrations = relationship("IntegrationV2", back_populates="organization")
    api_keys = relationship("OrganizationAPIKey", back_populates="organization")
    audit_logs = relationship("AuditLogV2", back_populates="organization")

    __table_args__ = (
        Index('idx_org_status', 'status'),
        Index('idx_org_plan', 'plan_tier'),
    )


class OrganizationMember(Base):
    """Organization member with role"""
    __tablename__ = "organization_members"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), default="member")  # admin, manager, member, viewer
    permissions = Column(JSON, default={})  # Custom permissions
    is_owner = Column(Boolean, default=False)
    invited_at = Column(DateTime, default=datetime.utcnow)
    joined_at = Column(DateTime)

    organization = relationship("Organization", back_populates="members")
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint('organization_id', 'user_id', name='uq_org_user'),
        Index('idx_org_member_role', 'organization_id', 'role'),
    )


class Team(Base):
    """Teams within organizations"""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    permissions = Column(JSON, default={})

    organization = relationship("Organization", back_populates="teams")

    __table_args__ = (
        Index('idx_team_org', 'organization_id'),
    )


# ==================== PHASE 1: AGENT SCALABILITY ====================

class AgentCategory(Base):
    """Agent categories (Finance, Healthcare, etc)"""
    __tablename__ = "agent_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True)
    description = Column(Text)
    icon_url = Column(String(500))
    agent_count = Column(Integer, default=0)

    __table_args__ = (
        Index('idx_category_name', 'name'),
    )


class AgentV2(Base):
    """Scalable Agent Registry (replaces hardcoded lists)"""
    __tablename__ = "agents_v2"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("agent_categories.id"))
    description = Column(Text)

    # Capabilities & Configuration
    capabilities = Column(JSON, default=[])  # Dynamic capabilities list
    tools = Column(JSON, default=[])
    version = Column(String(20), default="1.0.0")
    status = Column(String(50), default="active")  # active, inactive, beta
    is_public = Column(Boolean, default=True)

    # Organization-specific (multi-tenant)
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    # Metadata
    created_by = Column(String(255))
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)

    # Dates
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="agents")
    tools_rel = relationship("AgentTool", back_populates="agent")
    instances = relationship("AgentInstance", back_populates="agent")
    registrations = relationship("AgentRegistrationV2", back_populates="agent")

    __table_args__ = (
        Index('idx_agent_category', 'category_id'),
        Index('idx_agent_status', 'status'),
        Index('idx_agent_public', 'is_public'),
        Index('idx_agent_org', 'organization_id'),
    )


class AgentTool(Base):
    """Tools/capabilities per agent"""
    __tablename__ = "agent_tools"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents_v2.id"), nullable=False)
    tool_name = Column(String(255), nullable=False)
    description = Column(Text)
    input_schema = Column(JSON)
    output_schema = Column(JSON)

    agent = relationship("AgentV2", back_populates="tools_rel")


class AgentInstance(Base):
    """Per-user agent instance with configuration"""
    __tablename__ = "agent_instances"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents_v2.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Instance state
    status = Column(String(50), default="idle")  # idle, processing, error
    config = Column(JSON, default={})
    performance_metrics = Column(JSON, default={})

    # Usage
    execution_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    last_execution = Column(DateTime)
    avg_execution_time = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    agent = relationship("AgentV2", back_populates="instances")

    __table_args__ = (
        UniqueConstraint('agent_id', 'organization_id', 'user_id', name='uq_agent_org_user'),
        Index('idx_agent_instance_org', 'organization_id'),
        Index('idx_agent_instance_user', 'user_id'),
    )


class AgentRegistrationV2(Base):
    """User-agent permissions and preferences"""
    __tablename__ = "agent_registrations_v2"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents_v2.id"), nullable=False)

    # Permissions
    enabled = Column(Boolean, default=True)
    permissions = Column(JSON, default={})

    # Custom settings
    priority = Column(Integer, default=0)
    is_favorite = Column(Boolean, default=False)
    custom_config = Column(JSON, default={})

    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("AgentV2", back_populates="registrations")

    __table_args__ = (
        UniqueConstraint('organization_id', 'user_id', 'agent_id', name='uq_reg_org_user_agent'),
        Index('idx_reg_enabled', 'enabled'),
    )


# ==================== PHASE 4: COMPANY INTEGRATION ====================

class Company(Base):
    """1000+ Companies integrated"""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    slug = Column(String(255), unique=True)
    category = Column(String(100))  # Finance, Healthcare, Social, etc
    industry = Column(String(100))
    country = Column(String(100))
    website = Column(String(500))

    # API & Integration
    has_api = Column(Boolean, default=False)
    api_documentation_url = Column(String(500))
    api_type = Column(String(50))  # rest, graphql, grpc

    # Metadata
    logo_url = Column(String(500))
    description = Column(Text)
    founded_year = Column(Integer)
    employee_count = Column(String(50))

    # Tecno Spark stats
    agent_count = Column(Integer, default=0)
    user_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    agents = relationship("CompanyAgent", back_populates="company")
    integrations = relationship("CompanyIntegration", back_populates="company")

    __table_args__ = (
        Index('idx_company_category', 'category'),
        Index('idx_company_industry', 'industry'),
    )


class CompanyAgent(Base):
    """Mapping between 1000 companies and 1000 agents"""
    __tablename__ = "company_agents"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents_v2.id"), nullable=False)

    # Relevance & Confidence
    confidence_score = Column(Float, default=0.0)  # 0-1
    is_verified = Column(Boolean, default=False)
    custom_config = Column(JSON, default={})

    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="agents")

    __table_args__ = (
        UniqueConstraint('company_id', 'agent_id', name='uq_company_agent'),
        Index('idx_company_agent_score', 'confidence_score'),
    )


class CompanyIntegration(Base):
    """Integration endpoints for each company"""
    __tablename__ = "company_integrations"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    service_name = Column(String(100))  # gmail, slack, twitter, etc

    # API Details
    api_endpoint = Column(String(500))
    auth_type = Column(String(50))  # oauth2, api_key, jwt, none
    documentation_url = Column(String(500))

    # Free Tier
    has_free_tier = Column(Boolean, default=True)
    free_tier_limits = Column(JSON, default={})

    # Status
    status = Column(String(50), default="available")  # available, limited, unavailable

    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="integrations")


# ==================== PHASE 3: ENTERPRISE SECURITY ====================

class AuditLogV2(Base):
    """Enterprise audit trail (immutable)"""
    __tablename__ = "audit_logs_v2"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Action Details
    action = Column(String(100), nullable=False)  # login, execute_agent, update_workflow, etc
    resource_type = Column(String(100))  # user, agent, workflow, etc
    resource_id = Column(String(255))

    # Outcome
    result = Column(String(50))  # success, failure
    error_message = Column(Text)

    # Context
    ip_address = Column(String(50))
    user_agent = Column(String(500))

    # Immutable hash (for WORM compliance)
    entry_hash = Column(String(256))

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_audit_org', 'organization_id'),
        Index('idx_audit_user', 'user_id'),
        Index('idx_audit_action', 'action'),
        Index('idx_audit_created', 'created_at'),
    )


class TokenBlacklist(Base):
    """Revoked JWT tokens (for logout)"""
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    token_jti = Column(String(500), unique=True, nullable=False)  # JWT ID
    user_id = Column(Integer, ForeignKey("users.id"))

    revoked_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)  # TTL
    reason = Column(String(255))  # logout, password_change, compromised

    __table_args__ = (
        Index('idx_blacklist_expires', 'expires_at'),
    )


class EncryptedCredential(Base):
    """Encrypted API credentials storage"""
    __tablename__ = "encrypted_credentials"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    credential_type = Column(String(100))  # api_key, oauth_token, etc
    service_name = Column(String(100))  # stripe, twilio, etc

    # Encrypted value (use encryption service)
    encrypted_value = Column(Text, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    expires_at = Column(DateTime)

    __table_args__ = (
        Index('idx_cred_org_service', 'organization_id', 'service_name'),
    )


# ==================== PHASE 5: GLOBAL SCALE ====================

class WorkflowV2(Base):
    """Workflows with multi-tenant support"""
    __tablename__ = "workflows_v2"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Workflow configuration
    steps = Column(JSON, default=[])
    triggers = Column(JSON, default=[])

    # Execution settings
    is_active = Column(Boolean, default=True)
    max_concurrent_runs = Column(Integer, default=1)
    timeout_seconds = Column(Integer, default=300)

    # Stats
    total_runs = Column(Integer, default=0)
    total_failures = Column(Integer, default=0)
    avg_duration = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="workflows")

    __table_args__ = (
        Index('idx_workflow_org', 'organization_id'),
        Index('idx_workflow_active', 'is_active'),
    )


class IntegrationV2(Base):
    """Third-party integrations per organization"""
    __tablename__ = "integrations_v2"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    service_name = Column(String(100))  # gmail, slack, stripe, etc
    status = Column(String(50), default="connected")  # connected, error, disconnected

    # Config
    config = Column(JSON, default={})
    credential_id = Column(Integer, ForeignKey("encrypted_credentials.id"))

    # Metadata
    last_sync = Column(DateTime)
    error_count = Column(Integer, default=0)
    last_error = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="integrations")

    __table_args__ = (
        Index('idx_integration_org_service', 'organization_id', 'service_name'),
    )


class OrganizationAPIKey(Base):
    """API keys for organizations"""
    __tablename__ = "organization_api_keys"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    name = Column(String(255))
    key_hash = Column(String(256), unique=True)

    # Permissions
    permissions = Column(JSON, default={})

    # Usage tracking
    last_used = Column(DateTime)
    request_count = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    organization = relationship("Organization", back_populates="api_keys")

    __table_args__ = (
        Index('idx_api_key_org', 'organization_id'),
        Index('idx_api_key_active', 'is_active'),
    )


# ==================== USAGE METRICS & ANALYTICS ====================

class UsageMetric(Base):
    """Usage tracking for analytics"""
    __tablename__ = "usage_metrics"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    metric_type = Column(String(100))  # api_calls, agents_executed, workflows_run
    metric_value = Column(Integer, default=1)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_metric_org_type', 'organization_id', 'metric_type'),
        Index('idx_metric_date', 'created_at'),
    )


class PerformanceMetric(Base):
    """Performance tracking"""
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    operation = Column(String(100))  # agent_execution, workflow_run, etc
    duration_ms = Column(Integer)
    success = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_perf_org', 'organization_id'),
        Index('idx_perf_created', 'created_at'),
    )
