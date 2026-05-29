# Database Quick Reference - Buddy AI OS

## TL;DR - Get Started in 5 Minutes

```bash
# 1. Environment setup
cp backend/.env.example backend/.env

# 2. Create PostgreSQL user and database
sudo -u postgres psql
CREATE USER buddy_user WITH PASSWORD 'buddy_password';
CREATE DATABASE buddy_ai_db OWNER buddy_user;
GRANT ALL PRIVILEGES ON DATABASE buddy_ai_db TO buddy_user;
\q

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Run migrations
cd backend
python -m alembic upgrade head

# 5. Seed initial data (optional)
python db/seed_data.py

# Done! Database is ready.
```

---

## Common Tasks

### Query a User

```python
from db.database import AsyncSessionLocal
from db.models import User
from sqlalchemy import select

async with AsyncSessionLocal() as session:
    stmt = select(User).where(User.email == "user@example.com")
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
```

### Create a New User

```python
from db.models import User, UserProfile
import bcrypt

async with AsyncSessionLocal() as session:
    # Create user
    user = User(
        email="newuser@example.com",
        username="newuser",
        password_hash=bcrypt.hashpw(b"password", bcrypt.gensalt()).decode(),
        full_name="New User"
    )
    session.add(user)
    await session.flush()  # Get user.id
    
    # Create profile
    profile = UserProfile(user_id=user.id)
    session.add(profile)
    
    await session.commit()
```

### Register an Agent for a User

```python
from db.models import AgentRegistration, Agent
from sqlalchemy import select

async with AsyncSessionLocal() as session:
    # Get agent
    stmt = select(Agent).where(Agent.agent_id == "email_agent")
    result = await session.execute(stmt)
    agent = result.scalar_one()
    
    # Register for user
    registration = AgentRegistration(
        user_id=user_id,
        agent_id=agent.id,
        enabled=True,
        permissions=["send_email", "receive_email"]
    )
    session.add(registration)
    await session.commit()
```

### Save a Memory

```python
from db.models import Memory

async with AsyncSessionLocal() as session:
    memory = Memory(
        user_id=user_id,
        content="User prefers morning meetings",
        memory_type="preference",
        tags=["meeting", "schedule"],
    )
    session.add(memory)
    await session.commit()
```

### Create a Workflow

```python
from db.models import Workflow, WorkflowStep, Trigger
import json

async with AsyncSessionLocal() as session:
    workflow = Workflow(
        user_id=user_id,
        name="Daily Standup",
        description="Generate daily standup",
        definition_json=json.dumps({
            "steps": [
                {"agent": "researcher_agent", "action": "get_news"},
                {"agent": "email_agent", "action": "send_email"}
            ]
        }),
        status="active"
    )
    session.add(workflow)
    await session.flush()
    
    # Add step
    step = WorkflowStep(
        workflow_id=workflow.id,
        step_order=1,
        agent_id="researcher_agent",
        action="get_news"
    )
    session.add(step)
    
    # Add trigger
    trigger = Trigger(
        workflow_id=workflow.id,
        trigger_type="schedule",
        condition_json=json.dumps({"cron": "0 9 * * *"})  # 9 AM daily
    )
    session.add(trigger)
    
    await session.commit()
```

### Connect a Third-Party Integration

```python
from db.models import Integration
from utils.security import encrypt_key

async with AsyncSessionLocal() as session:
    integration = Integration(
        user_id=user_id,
        service="gmail",
        api_key_encrypted=encrypt_key("encrypted_refresh_token"),
        config={"scopes": ["gmail.send", "gmail.modify"]},
        status="connected"
    )
    session.add(integration)
    await session.commit()
```

### Track User Activity

```python
from db.models import UserActivity

async with AsyncSessionLocal() as session:
    activity = UserActivity(
        user_id=user_id,
        action="email_sent",
        details={"recipient": "boss@company.com", "subject": "Report"}
    )
    session.add(activity)
    await session.commit()
```

### Create Financial Transaction

```python
from db.models import Transaction
from datetime import datetime

async with AsyncSessionLocal() as session:
    transaction = Transaction(
        user_id=user_id,
        amount=100.50,
        transaction_type="expense",
        category="software",
        description="ChatGPT subscription",
        date=datetime.utcnow()
    )
    session.add(transaction)
    await session.commit()
```

### Track Course Assignment

```python
from db.models import Course, Assignment
from datetime import datetime, timedelta

async with AsyncSessionLocal() as session:
    # Get or create course
    course = Course(
        user_id=user_id,
        course_name="Advanced Python",
        provider="Coursera",
        progress=45.5
    )
    session.add(course)
    await session.flush()
    
    # Add assignment
    assignment = Assignment(
        user_id=user_id,
        course_id=course.id,
        title="Final Project",
        due_date=datetime.utcnow() + timedelta(days=14),
        status="in_progress"
    )
    session.add(assignment)
    
    await session.commit()
```

### Log Security Event

```python
from db.models import SecurityEvent

async with AsyncSessionLocal() as session:
    event = SecurityEvent(
        user_id=user_id,
        event_type="login_from_new_device",
        severity="medium",
        details={"ip": "192.168.1.1", "device": "iPhone"}
    )
    session.add(event)
    await session.commit()
```

---

## Relationship Cheat Sheet

```python
# User → Profile (1:1)
user.profile  # Get profile
profile.user  # Get user

# User → Agents (many:many through AgentRegistration)
user.agent_registrations  # Get registrations
agent.registrations  # Get users

# User → Workflows (1:many)
user.workflows
workflow.user

# Workflow → Steps (1:many)
workflow.steps
step.workflow

# User → Conversations (1:many)
user.conversations
thread.user
thread.messages

# User → Integrations (1:many)
user.integrations
integration.connection_logs

# Course → Assignments (1:many)
course.assignments
assignment.course
```

---

## Database Connection Patterns

### Async Context Manager (Recommended)

```python
async with AsyncSessionLocal() as session:
    # Your queries here
    user = await session.get(User, user_id)
    # Auto-rollback on exception, auto-close
```

### Dependency Injection (FastAPI)

```python
from fastapi import Depends
from db.database import get_db_session

@app.get("/users/{user_id}")
async def get_user(user_id: int, session = Depends(get_db_session)):
    user = await session.get(User, user_id)
    return user
```

### Explicit Session Management

```python
from db.database import AsyncSessionLocal

session = AsyncSessionLocal()
try:
    user = await session.get(User, user_id)
    session.add(new_record)
    await session.commit()
finally:
    await session.close()
```

---

## Migration Commands

```bash
# Show current revision
python -m alembic current

# Show all revisions
python -m alembic history

# Upgrade to latest
python -m alembic upgrade head

# Downgrade one version
python -m alembic downgrade -1

# Upgrade to specific version
python -m alembic upgrade abc123def

# Create new migration
python -m alembic revision --autogenerate -m "Add new table"

# Show migration SQL
python -m alembic upgrade head --sql
```

---

## Performance Tips

### Use Indexes

All frequently queried fields have indexes:
- user.email
- user.created_at
- memory.user_id + memory.memory_type
- integration.user_id + service

### Lazy Load Relationships

```python
# Instead of loading all relationships
user = await session.get(User, user_id)
print(user.workflows)  # Triggers query if not loaded

# Use joinedload for eager loading
from sqlalchemy.orm import joinedload
stmt = select(User).options(joinedload(User.workflows))
result = await session.execute(stmt)
user = result.unique().scalar_one()
```

### Batch Operations

```python
# Instead of loop
for user_id in user_ids:
    session.add(Transaction(...))

# Use bulk_insert_mappings
session.bulk_insert_mappings(
    Transaction,
    [{"user_id": id, "amount": amt} for id, amt in data]
)
```

---

## Debugging

### Check Database Connection

```python
from db.database import engine
print(engine)
```

### View Generated SQL

```python
# Set in .env: SQL_ECHO=true
# All queries will be printed

# Or manually:
from sqlalchemy import event
@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    print(statement, params)
```

### Common Errors

| Error | Solution |
|-------|----------|
| `no such table: users` | Run migrations: `alembic upgrade head` |
| `foreign key violation` | Create parent record first |
| `unique constraint violation` | Check for duplicates |
| `connection refused` | Check PostgreSQL is running |
| `authentication failed` | Check credentials in .env |

---

## File Locations

| Component | Location |
|-----------|----------|
| Models | `backend/db/models.py` |
| Database config | `backend/db/database.py` |
| Migrations | `backend/migrations/versions/` |
| Environment | `backend/.env` |
| Seed data | `backend/db/seed_data.py` |
| Documentation | `backend/DATABASE_README.md` |

---

## Useful Links

- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Alembic Docs](https://alembic.sqlalchemy.org/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [AsyncPG Docs](https://magicstack.github.io/asyncpg/)

---

**Database Version**: 1.0.0  
**Last Updated**: 2026-05-29  
**Status**: Production Ready
