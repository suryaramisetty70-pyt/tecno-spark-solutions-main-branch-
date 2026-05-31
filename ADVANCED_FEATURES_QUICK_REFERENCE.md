# Advanced Features - Quick Reference & API Examples

## Admin Management API Examples

### Create Admin
```bash
curl -X POST http://localhost:8000/api/v1/admin/admins \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "newadmin",
    "full_name": "Admin User",
    "role": "admin",
    "permissions": ["user_manage", "system_config"]
  }'
```

### Suspend User
```bash
curl -X POST http://localhost:8000/api/v1/admin/users/suspend \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "status": "suspended",
    "reason": "Suspicious activity detected"
  }'
```

### Get Dashboard
```bash
curl -X GET "http://localhost:8000/api/v1/admin/dashboard" \
  -H "Authorization: Bearer {token}"
```

### Audit Logs
```bash
curl -X GET "http://localhost:8000/api/v1/admin/audit-logs?skip=0&limit=20" \
  -H "Authorization: Bearer {token}"
```

### System Config
```bash
curl -X POST http://localhost:8000/api/v1/admin/config \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "config_key": "max_upload_size",
    "config_value": 104857600,
    "description": "Maximum file upload size in bytes"
  }'
```

---

## File Management API Examples

### Upload File
```bash
curl -X POST http://localhost:8000/api/v1/files/upload \
  -H "Authorization: Bearer {token}" \
  -F "file=@/path/to/document.pdf" \
  -F "description=Important document" \
  -F "is_public=false"
```

### List Files
```bash
curl -X GET "http://localhost:8000/api/v1/files?skip=0&limit=20" \
  -H "Authorization: Bearer {token}"
```

### Get File Details
```bash
curl -X GET http://localhost:8000/api/v1/files/123 \
  -H "Authorization: Bearer {token}"
```

### Share File
```bash
curl -X POST http://localhost:8000/api/v1/files/123/share \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": 123,
    "share_with_user_id": 456,
    "permission": "view"
  }'
```

### Search Files
```bash
curl -X POST http://localhost:8000/api/v1/files/search \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "quarterly report",
    "file_type": "document",
    "skip": 0,
    "limit": 20
  }'
```

### Get File Metadata
```bash
curl -X GET http://localhost:8000/api/v1/files/123/metadata \
  -H "Authorization: Bearer {token}"
```

### Create File Version
```bash
curl -X POST http://localhost:8000/api/v1/files/123/versions \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated with corrections"
  }'
```

---

## Analytics API Examples

### User Analytics
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/user?time_range=30d" \
  -H "Authorization: Bearer {token}"
```

### Workflow Analytics
```bash
curl -X GET http://localhost:8000/api/v1/analytics/workflows/1 \
  -H "Authorization: Bearer {token}"
```

### Agent Analytics
```bash
curl -X GET http://localhost:8000/api/v1/analytics/agents/1 \
  -H "Authorization: Bearer {token}"
```

### API Performance
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/api?endpoint=/api/v1/workflows" \
  -H "Authorization: Bearer {token}"
```

### Dashboard
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/dashboard?time_range=30d" \
  -H "Authorization: Bearer {token}"
```

### Generate Report
```bash
curl -X POST http://localhost:8000/api/v1/analytics/reports \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "monthly_summary",
    "time_range": "30d",
    "metrics": ["user_activity", "workflow_execution"],
    "format": "json"
  }'
```

### System Health
```bash
curl -X GET http://localhost:8000/api/v1/analytics/health \
  -H "Authorization: Bearer {token}"
```

### Time Series Data
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/timeseries?metric_type=user_activity&start_date=2024-01-01&end_date=2024-01-31&granularity=daily" \
  -H "Authorization: Bearer {token}"
```

---

## Python Client Examples

### Admin Management
```python
import httpx

async def create_admin(client: httpx.AsyncClient, token: str):
    response = await client.post(
        "http://localhost:8000/api/v1/admin/admins",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "admin@example.com",
            "username": "admin1",
            "full_name": "Admin User",
            "role": "admin"
        }
    )
    return response.json()

async def get_dashboard(client: httpx.AsyncClient, token: str):
    response = await client.get(
        "http://localhost:8000/api/v1/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()
```

### File Management
```python
async def upload_file(client: httpx.AsyncClient, token: str, file_path: str):
    with open(file_path, 'rb') as f:
        response = await client.post(
            "http://localhost:8000/api/v1/files/upload",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": f}
        )
    return response.json()

async def search_files(client: httpx.AsyncClient, token: str, query: str):
    response = await client.post(
        "http://localhost:8000/api/v1/files/search",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "query": query,
            "skip": 0,
            "limit": 20
        }
    )
    return response.json()
```

### Analytics
```python
async def get_analytics(client: httpx.AsyncClient, token: str):
    response = await client.get(
        "http://localhost:8000/api/v1/analytics/user?time_range=30d",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()

async def generate_report(client: httpx.AsyncClient, token: str):
    response = await client.post(
        "http://localhost:8000/api/v1/analytics/reports",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "report_type": "monthly",
            "time_range": "30d",
            "metrics": ["user_activity", "workflow_execution"]
        }
    )
    return response.json()
```

---

## TypeScript/JavaScript Client Examples

### Admin Management
```typescript
async function createAdmin(token: string) {
  const response = await fetch('http://localhost:8000/api/v1/admin/admins', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      email: 'admin@example.com',
      username: 'admin1',
      full_name: 'Admin User',
      role: 'admin'
    })
  });
  return response.json();
}

async function getDashboard(token: string) {
  const response = await fetch('http://localhost:8000/api/v1/admin/dashboard', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}
```

### File Management
```typescript
async function uploadFile(token: string, file: File) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('description', 'My document');
  
  const response = await fetch('http://localhost:8000/api/v1/files/upload', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  });
  return response.json();
}

async function searchFiles(token: string, query: string) {
  const response = await fetch('http://localhost:8000/api/v1/files/search', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ query, skip: 0, limit: 20 })
  });
  return response.json();
}
```

### Analytics
```typescript
async function getUserAnalytics(token: string, timeRange: string = '30d') {
  const response = await fetch(
    `http://localhost:8000/api/v1/analytics/user?time_range=${timeRange}`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  return response.json();
}

async function generateReport(token: string) {
  const response = await fetch('http://localhost:8000/api/v1/analytics/reports', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      report_type: 'monthly',
      time_range: '30d',
      metrics: ['user_activity', 'workflow_execution']
    })
  });
  return response.json();
}
```

---

## Endpoint Statistics

### Admin Endpoints: 10
- Create, List Admins
- Suspend, Ban Users
- Dashboard, Audit Logs
- Configuration Management
- Report Generation

### File Endpoints: 12
- Upload, List, Get Files
- Delete, Share Files
- Search, Metadata
- Tagging, Versioning

### Analytics Endpoints: 9
- User, Workflow, Agent Analytics
- Integration, API Performance
- Dashboard, Reports
- Health Metrics, Time Series

**Total: 31+ Advanced Endpoints**

---

## Status: Advanced Features Complete ✅

All systems implemented and tested. Ready for Phase 7!
