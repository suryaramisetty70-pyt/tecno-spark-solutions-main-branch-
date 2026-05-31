# Agent Management Quick Reference - Buddy AI OS

## TL;DR - Get Started in 2 Minutes

### 1. Register New Agent (Admin)
```bash
curl -X POST http://localhost:8000/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name":"Email Agent",
    "description":"Handle email operations",
    "version":"1.0.0",
    "capabilities":["email","messaging"],
    "author":"Team"
  }'
```

### 2. List Available Agents
```bash
curl -X GET "http://localhost:8000/api/v1/agents?skip=0&limit=50"
```

### 3. Enable Agent for User
```bash
curl -X POST http://localhost:8000/api/v1/agents/1/enable \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled":true,
    "permissions":["send_email","read_email"]
  }'
```

### 4. Get User's Agents
```bash
curl -X GET http://localhost:8000/api/v1/agents/user/agents \
  -H "Authorization: Bearer {access_token}"
```

---

## API Endpoints Quick Reference

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/api/v1/agents` | GET | List agents | ❌ |
| `/api/v1/agents` | POST | Register agent | ✅ |
| `/api/v1/agents/{id}` | GET | Get agent details | ❌ |
| `/api/v1/agents/{id}/status` | GET | Get status | ❌ |
| `/api/v1/agents/{id}/metrics` | GET | Get metrics | ❌ |
| `/api/v1/agents/{id}/config` | PUT | Update config | ✅ |
| `/api/v1/agents/{id}/enable` | POST | Enable for user | ✅ |
| `/api/v1/agents/{id}/disable` | POST | Disable for user | ✅ |
| `/api/v1/agents/user/agents` | GET | List user's agents | ✅ |
| `/api/v1/agents/{id}/tools` | POST | Register tool | ❌ |
| `/api/v1/agents/{id}/tools` | GET | List tools | ❌ |

---

## Request/Response Examples

### Register Agent
```bash
curl -X POST http://localhost:8000/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Research Agent",
    "description": "Web research and information gathering",
    "version": "1.0.0",
    "capabilities": ["research", "integration"],
    "enabled_by_default": true,
    "requires_authentication": true,
    "author": "Buddy AI Team",
    "documentation_url": "https://docs.example.com/research",
    "config": {"timeout": 30}
  }'
```

**Response (201)**:
```json
{
  "id": 1,
  "name": "Research Agent",
  "version": "1.0.0",
  "capabilities": ["research", "integration"],
  "status": "active",
  "downloads": 0,
  "rating": 0,
  "total_reviews": 0,
  "created_at": "2026-05-30T15:30:00Z",
  "updated_at": "2026-05-30T15:30:00Z"
}
```

### List Agents
```bash
curl -X GET "http://localhost:8000/api/v1/agents?skip=0&limit=10"
```

**Response (200)**:
```json
{
  "total": 50,
  "page": 1,
  "per_page": 10,
  "agents": [
    {
      "id": 1,
      "name": "Email Agent",
      "description": "Email operations",
      "version": "1.0.0",
      "capabilities": ["email", "messaging"],
      "status": "active",
      "downloads": 1000,
      "rating": 4.5,
      "total_reviews": 250
    }
  ]
}
```

### Get Agent Details
```bash
curl -X GET http://localhost:8000/api/v1/agents/1
```

### Get Agent Status
```bash
curl -X GET http://localhost:8000/api/v1/agents/1/status
```

**Response (200)**:
```json
{
  "agent_id": 1,
  "agent_name": "Email Agent",
  "status": "active",
  "uptime_percentage": 99.9,
  "last_health_check": "2026-05-30T15:30:00Z",
  "error_count_24h": 2,
  "execution_count_24h": 1000,
  "average_execution_time_ms": 250.5
}
```

### Get Agent Metrics
```bash
curl -X GET http://localhost:8000/api/v1/agents/1/metrics
```

**Response (200)**:
```json
{
  "agent_id": 1,
  "agent_name": "Email Agent",
  "total_executions": 5000,
  "successful_executions": 4950,
  "failed_executions": 50,
  "average_execution_time_ms": 245.3,
  "success_rate": 99.0,
  "most_common_error": "timeout",
  "last_executed": "2026-05-30T15:30:00Z"
}
```

### Enable Agent for User
```bash
curl -X POST http://localhost:8000/api/v1/agents/1/enable \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "permissions": ["send_email", "read_email", "archive"]
  }'
```

**Response (200)**:
```json
{
  "id": 1,
  "user_id": 1,
  "agent_id": 1,
  "agent_name": "Email Agent",
  "status": "active",
  "enabled": true,
  "permissions": ["send_email", "read_email", "archive"],
  "usage_count": 0,
  "last_used": null,
  "created_at": "2026-05-30T15:30:00Z",
  "updated_at": "2026-05-30T15:30:00Z"
}
```

### Disable Agent for User
```bash
curl -X POST http://localhost:8000/api/v1/agents/1/disable \
  -H "Authorization: Bearer {access_token}"
```

**Response (200)**:
```json
{
  "message": "Agent disabled successfully"
}
```

### Get User's Agents
```bash
curl -X GET http://localhost:8000/api/v1/agents/user/agents \
  -H "Authorization: Bearer {access_token}"
```

**Response (200)**:
```json
{
  "total": 15,
  "enabled_count": 12,
  "disabled_count": 3,
  "agents": [
    {
      "id": 1,
      "user_id": 1,
      "agent_id": 1,
      "agent_name": "Email Agent",
      "status": "active",
      "enabled": true,
      "usage_count": 42,
      "last_used": "2026-05-30T14:00:00Z"
    }
  ]
}
```

### Register Tool for Agent
```bash
curl -X POST http://localhost:8000/api/v1/agents/1/tools \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "send_email",
    "description": "Send an email message",
    "requires_auth": true,
    "input_schema": {
      "type": "object",
      "properties": {
        "to": {"type": "string"},
        "subject": {"type": "string"},
        "body": {"type": "string"}
      },
      "required": ["to", "subject", "body"]
    },
    "output_schema": {
      "type": "object",
      "properties": {
        "message_id": {"type": "string"},
        "sent_at": {"type": "string"}
      }
    }
  }'
```

**Response (201)**:
```json
{
  "id": 1,
  "agent_id": 1,
  "tool_name": "send_email",
  "description": "Send an email message",
  "requires_auth": true,
  "created_at": "2026-05-30T15:30:00Z"
}
```

### Get Agent Tools
```bash
curl -X GET http://localhost:8000/api/v1/agents/1/tools
```

**Response (200)**:
```json
[
  {
    "id": 1,
    "agent_id": 1,
    "tool_name": "send_email",
    "description": "Send an email message",
    "input_schema": {...},
    "output_schema": {...},
    "requires_auth": true,
    "created_at": "2026-05-30T15:30:00Z"
  }
]
```

---

## Agent Capabilities

| Capability | Purpose |
|-----------|---------|
| `email` | Email operations |
| `messaging` | Messaging platforms |
| `scheduling` | Calendar/schedule |
| `research` | Web research |
| `automation` | Task automation |
| `analytics` | Data analysis |
| `integration` | API integrations |
| `personalization` | User customization |
| `learning` | Educational content |
| `content` | Content creation |

---

## Python Client Example

```python
import httpx

async with httpx.AsyncClient() as client:
    # Get all agents
    response = await client.get("http://localhost:8000/api/v1/agents")
    agents = response.json()
    
    # Get specific agent
    response = await client.get("http://localhost:8000/api/v1/agents/1")
    agent = response.json()
    
    # Enable agent for user
    response = await client.post(
        "http://localhost:8000/api/v1/agents/1/enable",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"enabled": True, "permissions": ["send_email", "read_email"]}
    )
    instance = response.json()
    
    # Get user's agents
    response = await client.get(
        "http://localhost:8000/api/v1/agents/user/agents",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_agents = response.json()
    
    # Get agent metrics
    response = await client.get("http://localhost:8000/api/v1/agents/1/metrics")
    metrics = response.json()
    
    # Register tool
    response = await client.post(
        "http://localhost:8000/api/v1/agents/1/tools",
        json={
            "tool_name": "send_email",
            "description": "Send email",
            "requires_auth": True,
            "input_schema": {...},
            "output_schema": {...}
        }
    )
    tool = response.json()
```

---

## Common Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `skip` | int | Pagination offset (default: 0) |
| `limit` | int | Results per page (default: 50, max: 100) |
| `enabled_only` | bool | Filter enabled agents (default: false) |

---

## Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad request |
| 401 | Unauthorized |
| 404 | Not found |
| 500 | Server error |

---

## Common Headers

```
Content-Type: application/json
Authorization: Bearer {access_token}  (for user-specific endpoints)
```

---

## Error Examples

### 404 Not Found
```json
{
  "status_code": 404,
  "message": "Not Found",
  "detail": "Agent not found"
}
```

### 400 Bad Request
```json
{
  "status_code": 400,
  "message": "Bad Request",
  "detail": "Agent with this name already exists"
}
```

---

## Tips & Best Practices

1. **List agents** before enabling to get IDs
2. **Register tools** for agents before use
3. **Track metrics** to monitor performance
4. **Use permissions** to limit agent capabilities
5. **Check status** regularly for health
6. **Store agent IDs** in user preferences
7. **Version agents** for rollback capability
8. **Test tools** before enabling in production

---

## Files Location

| File | Purpose |
|------|---------|
| `api/schemas/agent_schemas.py` | Agent request/response models |
| `services/agent_service.py` | Agent business logic |
| `api/v1/agents.py` | Agent API endpoints |
| `db/models.py` | Agent database models |
| `api/main.py` | FastAPI application |

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: 2026-05-30
