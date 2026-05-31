"""
SQLAlchemy ORM Models for Buddy AI OS
All database tables defined here
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text,
    JSON, Index, Table, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


# ==================== USER MANAGEMENT ====================

class User(Base):
    """User account"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    preferences = relationship("UserPreference", back_populates="user")
    goals = relationship("UserGoal", back_populates="user")
    auth_tokens = relationship("AuthToken", back_populates="user")
    oauth_credentials = relationship("OAuthCredential", back_populates="user")
    api_keys = relationship("UserAPIKey", back_populates="user")
    agent_registrations = relationship("AgentRegistration", back_populates="user")
    memories = relationship("Memory", back_populates="user")
    conversations = relationship("ConversationThread", back_populates="user")
    workflows = relationship("Workflow", back_populates="user")
    integrations = relationship("Integration", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    documents = relationship("Document", back_populates="user")
    notes = relationship("Note", back_populates="user")
    saved_items = relationship("SavedItem", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    invoices = relationship("Invoice", back_populates="user")
    expenses = relationship("Expense", back_populates="user")
    accounts = relationship("Account", back_populates="user")
    budgets = relationship("Budget", back_populates="user")
    email_accounts = relationship("EmailAccount", back_populates="user")
    whatsapp_contacts = relationship("WhatsAppContact", back_populates="user")
    telegram_chats = relationship("TelegramChat", back_populates="user")
    calendar_events = relationship("CalendarEvent", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")
    bookings = relationship("Booking", back_populates="user")
    itineraries = relationship("Itinerary", back_populates="user")
    courses = relationship("Course", back_populates="user")
    assignments = relationship("Assignment", back_populates="user")
    exam_preps = relationship("ExamPrep", back_populates="user")
    contacts = relationship("Contact", back_populates="user")
    deals = relationship("Deal", back_populates="user")
    leads = relationship("Lead", back_populates="user")
    team_members = relationship("TeamMember", back_populates="user")

    __table_args__ = (
        Index('idx_email_active', 'email', 'is_active'),
        Index('idx_created_at', 'created_at'),
    )


class UserProfile(Base):
    """Extended user profile information"""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    bio = Column(Text)
    profile_picture_url = Column(String(500))
    phone_number = Column(String(20))
    date_of_birth = Column(DateTime)
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="en")
    theme = Column(String(20), default="dark")
    settings = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class UserPreference(Base):
    """User preferences and settings"""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pref_key = Column(String(255), nullable=False)
    pref_value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="preferences")

    __table_args__ = (
        UniqueConstraint('user_id', 'pref_key', name='uq_user_pref_key'),
        Index('idx_user_pref_key', 'user_id', 'pref_key'),
    )


class UserGoal(Base):
    """User goals and aspirations"""
    __tablename__ = "user_goals"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal = Column(Text, nullable=False)
    status = Column(String(50), default="active")  # active, completed, archived
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)

    user = relationship("User", back_populates="goals")


# ==================== AUTHENTICATION ====================

class AuthToken(Base):
    """JWT authentication tokens"""
    __tablename__ = "auth_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(500), unique=True, nullable=False, index=True)
    token_type = Column(String(50), nullable=False)  # access, refresh
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)

    user = relationship("User", back_populates="auth_tokens")


class OAuthCredential(Base):
    """OAuth 2.0 credentials for third-party services"""
    __tablename__ = "oauth_credentials"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String(100), nullable=False)  # google, github, microsoft
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="oauth_credentials")

    __table_args__ = (
        UniqueConstraint('user_id', 'provider', name='uq_oauth_user_provider'),
    )


class UserAPIKey(Base):
    """User API keys for programmatic access"""
    __tablename__ = "user_api_keys"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    last_used = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    user = relationship("User", back_populates="api_keys")


# ==================== AGENT SYSTEM ====================

class Agent(Base):
    """AI Agent definitions"""
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True)
    agent_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    version = Column(String(20), default="0.1.0")
    capabilities = Column(JSON)  # List of capabilities
    status = Column(String(50), default="active")  # active, inactive, beta
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    registrations = relationship("AgentRegistration", back_populates="agent")
    instances = relationship("AgentInstance", back_populates="agent")
    tools = relationship("AgentTool", back_populates="agent")


class AgentInstance(Base):
    """User-specific agent instances"""
    __tablename__ = "agent_instances"

    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="idle")  # idle, processing, error
    config = Column(JSON, default={})  # Agent-specific configuration
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    agent = relationship("Agent", back_populates="instances")

    __table_args__ = (
        Index('idx_agent_user', 'agent_id', 'user_id'),
    )


class AgentRegistration(Base):
    """User's agent registrations and permissions"""
    __tablename__ = "agent_registrations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    enabled = Column(Boolean, default=True)
    permissions = Column(JSON, default=[])  # List of permissions
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="agent_registrations")
    agent = relationship("Agent", back_populates="registrations")

    __table_args__ = (
        UniqueConstraint('user_id', 'agent_id', name='uq_user_agent'),
    )


# ==================== MEMORY & CONTEXT ====================

class Memory(Base):
    """Long-term memory storage"""
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(JSON)  # Vector embedding (stored in ChromaDB, reference here)
    memory_type = Column(String(50), nullable=False)  # conversation, note, document, fact
    tags = Column(JSON, default=[])
    meta_data = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="memories")

    __table_args__ = (
        Index('idx_user_memory_type', 'user_id', 'memory_type'),
    )


class ConversationThread(Base):
    """Conversation thread/session"""
    __tablename__ = "conversation_threads"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    messages = relationship("ConversationMessage", back_populates="thread")


class ConversationMessage(Base):
    """Individual messages in a conversation"""
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True)
    thread_id = Column(Integer, ForeignKey("conversation_threads.id"), nullable=False)
    sender = Column(String(50), nullable=False)  # user, agent, system
    agent_id = Column(String(100))  # If sender is agent
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    meta_data = Column(JSON, default={})

    thread = relationship("ConversationThread", back_populates="messages")


class ContextSnapshot(Base):
    """Snapshots of user context at specific times"""
    __tablename__ = "context_snapshots"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    context_json = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


# ==================== INTEGRATIONS & CREDENTIALS ====================

class Integration(Base):
    """Third-party service integrations"""
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service = Column(String(100), nullable=False, index=True)  # gmail, slack, etc
    api_key_encrypted = Column(Text, nullable=False)
    config = Column(JSON, default={})
    status = Column(String(50), default="connected")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="integrations")
    connection_logs = relationship("ConnectionLog", back_populates="integration")
    credentials = relationship("IntegrationCredential", back_populates="integration")
    webhook_logs = relationship("WebhookLog", back_populates="integration")

    __table_args__ = (
        Index('idx_user_service', 'user_id', 'service'),
    )


class ConnectionLog(Base):
    """Integration connection logs"""
    __tablename__ = "connection_logs"

    id = Column(Integer, primary_key=True)
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=False)
    status = Column(String(50), nullable=False)  # success, failure, timeout
    last_connected = Column(DateTime)
    error_message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    integration = relationship("Integration", back_populates="connection_logs")


# ==================== WORKFLOWS & AUTOMATION ====================

class Workflow(Base):
    """User automation workflows"""
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    definition_json = Column(JSON, nullable=False)  # Workflow definition
    status = Column(String(50), default="active")  # active, paused, archived
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="workflows")
    steps = relationship("WorkflowStep", back_populates="workflow")
    triggers = relationship("WorkflowTrigger", back_populates="workflow")
    executions = relationship("WorkflowExecution", back_populates="workflow")


class WorkflowStep(Base):
    """Individual steps in a workflow"""
    __tablename__ = "workflow_steps"

    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    step_order = Column(Integer, nullable=False)
    agent_id = Column(String(100), nullable=False)
    action = Column(String(255), nullable=False)
    config = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    workflow = relationship("Workflow", back_populates="steps")


class WorkflowTrigger(Base):
    """Workflow triggers"""
    __tablename__ = "triggers"

    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    trigger_type = Column(String(50), nullable=False)  # schedule, webhook, event
    condition_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    workflow = relationship("Workflow", back_populates="triggers")


class WorkflowExecution(Base):
    """Workflow execution history"""
    __tablename__ = "workflow_executions"

    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    status = Column(String(50), nullable=False)  # running, success, failure
    output = Column(JSON)
    error_message = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)

    workflow = relationship("Workflow", back_populates="executions")


# ==================== NOTIFICATIONS & EVENTS ====================

class Notification(Base):
    """User notifications"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notification_type = Column(String(50), nullable=False)  # alert, info, warning
    title = Column(String(255), nullable=False)
    content = Column(Text)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    read_at = Column(DateTime)

    user = relationship("User", back_populates="notifications")

    __table_args__ = (
        Index('idx_user_read', 'user_id', 'read'),
    )


class Event(Base):
    """System events"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(String(100), nullable=False, index=True)
    data_json = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class EventLog(Base):
    """Event processing logs"""
    __tablename__ = "event_logs"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    status = Column(String(50), nullable=False)
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


# ==================== ANALYTICS & MONITORING ====================

class UserActivity(Base):
    """User activity tracking"""
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_user_action', 'user_id', 'action'),
    )


class AgentMetric(Base):
    """Agent performance metrics"""
    __tablename__ = "agent_metrics"

    id = Column(Integer, primary_key=True)
    agent_id = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    metric_name = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_agent_metric', 'agent_id', 'metric_name'),
    )


class APIUsage(Base):
    """API endpoint usage tracking"""
    __tablename__ = "api_usages"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer)
    response_time_ms = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_endpoint_method', 'endpoint', 'method'),
    )


class PerformanceLog(Base):
    """System performance logs"""
    __tablename__ = "performance_logs"

    id = Column(Integer, primary_key=True)
    component = Column(String(100), nullable=False)
    metric = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


# ==================== SECURITY & AUDIT ====================

class AuditLog(Base):
    """Audit trail for compliance"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(255), nullable=False)
    resource = Column(String(255))
    status = Column(String(50), nullable=False)  # success, failure
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_user_action_time', 'user_id', 'action', 'timestamp'),
    )


class SecurityEvent(Base):
    """Security-related events"""
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_type = Column(String(100), nullable=False)  # login_failure, unauthorized_access
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class FailedAuthAttempt(Base):
    """Failed authentication attempts"""
    __tablename__ = "failed_auth_attempts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    email = Column(String(255))
    ip_address = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class BackupRecord(Base):
    """Database backup records"""
    __tablename__ = "backup_records"

    id = Column(Integer, primary_key=True)
    backup_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)  # success, failure
    location = Column(String(500))
    size_bytes = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


# ==================== CONTENT & KNOWLEDGE ====================

class Document(Base):
    """User documents"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    document_type = Column(String(50))  # pdf, txt, docx, etc
    file_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="documents")


class Note(Base):
    """User notes"""
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255))
    content = Column(Text, nullable=False)
    tags = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="notes")


class SavedItem(Base):
    """User saved items from web"""
    __tablename__ = "saved_items"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    source_url = Column(String(500), nullable=False)
    title = Column(String(255))
    content = Column(Text)
    content_type = Column(String(50))
    saved_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="saved_items")


# ==================== FINANCIAL DATA ====================

class Transaction(Base):
    """Financial transactions"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(50), nullable=False)  # income, expense, transfer
    category = Column(String(100))
    description = Column(Text)
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")


class Invoice(Base):
    """User invoices"""
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invoice_number = Column(String(100), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    client_name = Column(String(255), nullable=False)
    due_date = Column(DateTime)
    status = Column(String(50), default="pending")  # pending, sent, paid, overdue
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="invoices")


class Expense(Base):
    """User expenses"""
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)
    date = Column(DateTime, nullable=False)
    description = Column(Text)
    receipt_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="expenses")


class Account(Base):
    """User financial accounts"""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_name = Column(String(255), nullable=False)
    account_type = Column(String(50), nullable=False)  # bank, credit_card, savings
    balance = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    account_number = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="accounts")


class Budget(Base):
    """User budgets"""
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    period = Column(String(50), nullable=False)  # monthly, yearly
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="budgets")


# ==================== COMMUNICATION DATA ====================

class EmailAccount(Base):
    """User email accounts"""
    __tablename__ = "email_accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    email = Column(String(255), nullable=False)
    provider = Column(String(50), nullable=False)  # gmail, outlook
    sync_status = Column(String(50), default="syncing")
    last_synced = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="email_accounts")
    messages = relationship("EmailMessage", back_populates="email_account")


class EmailMessage(Base):
    """Email messages"""
    __tablename__ = "email_messages"

    id = Column(Integer, primary_key=True)
    email_account_id = Column(Integer, ForeignKey("email_accounts.id"), nullable=False)
    sender = Column(String(255), nullable=False)
    recipients = Column(JSON, default=[])
    subject = Column(String(500))
    body = Column(Text)
    timestamp = Column(DateTime, nullable=False)
    read = Column(Boolean, default=False)
    archived = Column(Boolean, default=False)

    email_account = relationship("EmailAccount", back_populates="messages")


class WhatsAppContact(Base):
    """WhatsApp contacts"""
    __tablename__ = "whatsapp_contacts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    phone = Column(String(20), nullable=False)
    name = Column(String(255))
    last_message_date = Column(DateTime)

    user = relationship("User", back_populates="whatsapp_contacts")
    messages = relationship("WhatsAppMessage", back_populates="contact")


class WhatsAppMessage(Base):
    """WhatsApp messages"""
    __tablename__ = "whatsapp_messages"

    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey("whatsapp_contacts.id"), nullable=False)
    sender = Column(String(50), nullable=False)  # user, contact
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)

    contact = relationship("WhatsAppContact", back_populates="messages")


class TelegramChat(Base):
    """Telegram chats"""
    __tablename__ = "telegram_chats"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chat_id = Column(String(100), nullable=False)
    chat_name = Column(String(255))
    last_sync = Column(DateTime)

    user = relationship("User", back_populates="telegram_chats")


# ==================== SCHEDULING DATA ====================

class CalendarEvent(Base):
    """Calendar events"""
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String(255))
    calendar_type = Column(String(50), default="personal")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="calendar_events")
    reminders = relationship("Reminder", back_populates="event")


class Reminder(Base):
    """Reminders for events"""
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("calendar_events.id"))
    reminder_text = Column(String(255))
    time_before = Column(Integer)  # minutes before
    notification_type = Column(String(50), default="email")
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)

    user = relationship("User", back_populates="reminders")
    event = relationship("CalendarEvent", back_populates="reminders")


class RecurringRule(Base):
    """Recurring event rules"""
    __tablename__ = "recurring_rules"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("calendar_events.id"), nullable=False)
    recurrence_pattern = Column(String(100), nullable=False)  # RRULE format
    until_date = Column(DateTime)


# ==================== TRAVEL & BOOKING ====================

class Booking(Base):
    """Travel bookings"""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    booking_type = Column(String(50), nullable=False)  # flight, hotel, restaurant
    booking_details = Column(JSON, nullable=False)
    confirmation_number = Column(String(100), unique=True)
    booking_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookings")


class Itinerary(Base):
    """Travel itineraries"""
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    destination = Column(String(255))
    activities_json = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="itineraries")


class HotelPreference(Base):
    """Hotel preferences"""
    __tablename__ = "hotel_preferences"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    city = Column(String(100))
    price_range = Column(String(50))
    amenities = Column(JSON, default=[])


class FlightPreference(Base):
    """Flight preferences"""
    __tablename__ = "flight_preferences"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    cabin_class = Column(String(50), default="economy")
    airlines = Column(JSON, default=[])
    departure_times = Column(JSON, default=[])


# ==================== LEARNING DATA ====================

class Course(Base):
    """Courses user is taking"""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_name = Column(String(255), nullable=False)
    provider = Column(String(100))
    progress = Column(Float, default=0.0)  # 0-100
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    completion_date = Column(DateTime)

    user = relationship("User", back_populates="courses")
    assignments = relationship("Assignment", back_populates="course")


class Assignment(Base):
    """Course assignments"""
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    due_date = Column(DateTime)
    status = Column(String(50), default="pending")  # pending, submitted, completed, graded
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="assignments")
    course = relationship("Course", back_populates="assignments")


class ExamPrep(Base):
    """Exam preparation"""
    __tablename__ = "exam_preps"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exam_name = Column(String(255), nullable=False)
    description = Column(Text)
    test_date = Column(DateTime)
    study_materials = Column(JSON, default=[])
    progress = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="exam_preps")


class LearningProgress(Base):
    """Learning progress tracking"""
    __tablename__ = "learning_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String(255), nullable=False)
    understanding_level = Column(Float, default=0.0)  # 0-1
    last_reviewed = Column(DateTime)


# ==================== BUSINESS DATA ====================

class Contact(Base):
    """Business contacts"""
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(20))
    company = Column(String(255))
    relationship_type = Column(String(50))  # client, supplier, partner, colleague
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="contacts")


class Deal(Base):
    """Sales deals"""
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    opportunity_name = Column(String(255), nullable=False)
    value = Column(Float)
    stage = Column(String(50))  # prospect, negotiation, won, lost
    expected_close_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="deals")


class Lead(Base):
    """Sales leads"""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    source = Column(String(100))  # website, referral, event, etc
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(20))
    score = Column(Float, default=0.0)
    status = Column(String(50), default="new")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="leads")


class TeamMember(Base):
    """Team members"""
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(20))
    role = Column(String(100), nullable=False)
    department = Column(String(100))
    joined_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="team_members")


class AgentTool(Base):
    """Tools available for agents"""
    __tablename__ = "agent_tools"

    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    input_schema = Column(JSON)
    output_schema = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="tools")


    created_at = Column(DateTime, default=datetime.utcnow)

    workflow = relationship("Workflow", back_populates="triggers")


class StepExecution(Base):
    """Execution records for workflow steps"""
    __tablename__ = "step_executions"

    id = Column(Integer, primary_key=True)
    workflow_execution_id = Column(Integer, ForeignKey("workflow_executions.id"), nullable=False)
    step_order = Column(Integer, nullable=False)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)

    execution = relationship("WorkflowExecution", back_populates="step_executions")


class IntegrationCredential(Base):
    """Credentials for integrations"""
    __tablename__ = "integration_credentials"

    id = Column(Integer, primary_key=True)
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=False)
    credential_key = Column(String(255), nullable=False)
    credential_value_encrypted = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    integration = relationship("Integration", back_populates="credentials")




class WebhookLog(Base):
    """Webhook event logs"""
    __tablename__ = "webhook_logs"

    id = Column(Integer, primary_key=True)
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=False)
    event_type = Column(String(100), nullable=False)
    payload = Column(JSON)
    received_at = Column(DateTime, default=datetime.utcnow)

    integration = relationship("Integration", back_populates="webhook_logs")




class IntegrationMetric(Base):
    """Metrics for integrations"""
    __tablename__ = "integration_metrics"

    id = Column(Integer, primary_key=True)
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)


class AdminAction(Base):
    """Admin action audit log"""
    __tablename__ = "admin_actions"

    id = Column(Integer, primary_key=True)
    admin_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(String(50), nullable=False)
    target_type = Column(String(50))
    target_id = Column(Integer)
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

    admin_user = relationship("User", foreign_keys=[admin_user_id])


class SystemConfig(Base):
    """System configuration"""
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SystemHealth(Base):
    """System health metrics"""
    __tablename__ = "system_health"

    id = Column(Integer, primary_key=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float)
    status = Column(String(50))
    recorded_at = Column(DateTime, default=datetime.utcnow)
