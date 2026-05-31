# Phase 7: Search & Discovery - Quick Reference

## API Endpoints Overview

### Global Search
```bash
curl -X POST http://localhost:8000/api/v1/search/global \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "workflow automation",
    "entity_types": ["workflow", "agent"],
    "filters": [],
    "sort_by": "relevance",
    "skip": 0,
    "limit": 20
  }'
```

### Advanced Search with Filters
```bash
curl -X POST http://localhost:8000/api/v1/search/advanced \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "email",
    "entity_types": ["workflow"],
    "filters": [
      {
        "field": "status",
        "operator": "equals",
        "value": "active"
      }
    ],
    "date_from": "2024-01-01",
    "date_to": "2024-12-31",
    "skip": 0,
    "limit": 20
  }'
```

### Save Search
```bash
curl -X POST http://localhost:8000/api/v1/search/saved \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Active Workflows",
    "description": "All active workflow automations",
    "query": "automation",
    "entity_types": ["workflow"],
    "is_public": false
  }'
```

### List Saved Searches
```bash
curl -X GET "http://localhost:8000/api/v1/search/saved?skip=0&limit=20" \
  -H "Authorization: Bearer {token}"
```

### Delete Saved Search
```bash
curl -X DELETE http://localhost:8000/api/v1/search/saved/123 \
  -H "Authorization: Bearer {token}"
```

### Get Search Suggestions
```bash
curl -X POST http://localhost:8000/api/v1/search/suggestions \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "work",
    "entity_types": ["workflow"],
    "limit": 10
  }'
```

### Get Recommendations
```bash
curl -X POST http://localhost:8000/api/v1/search/discover \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "agent",
    "limit": 10,
    "include_trending": true
  }'
```

### Get Search History
```bash
curl -X GET "http://localhost:8000/api/v1/search/history?limit=20" \
  -H "Authorization: Bearer {token}"
```

### Get Trending Searches
```bash
curl -X GET "http://localhost:8000/api/v1/search/trending?limit=10" \
  -H "Authorization: Bearer {token}"
```

### Get Search Analytics
```bash
curl -X GET http://localhost:8000/api/v1/search/analytics \
  -H "Authorization: Bearer {token}"
```

### Get Popular Searches
```bash
curl -X GET "http://localhost:8000/api/v1/search/popular?limit=10" \
  -H "Authorization: Bearer {token}"
```

---

## Filter Operators

| Operator | Example |
|----------|---------|
| `equals` | Status equals "active" |
| `not_equals` | Status not equals "deleted" |
| `greater_than` | Created date > "2024-01-01" |
| `less_than` | Score < 100 |
| `in` | Status in ["active", "pending"] |
| `contains` | Title contains "workflow" |
| `starts_with` | Name starts with "my_" |
| `ends_with` | Filename ends with ".pdf" |

---

## Entity Types

```
- user: Users and profiles
- agent: AI agents
- workflow: Automation workflows
- integration: Third-party integrations
- file: Uploaded files
- notification: User notifications
- document: Documents and content
```

---

## Python Client Example

```python
import httpx

async def search_globally(client: httpx.AsyncClient, token: str, query: str):
    response = await client.post(
        "http://localhost:8000/api/v1/search/global",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "query": query,
            "entity_types": ["workflow", "agent"],
            "filters": [],
            "skip": 0,
            "limit": 20
        }
    )
    return response.json()

async def save_search(client: httpx.AsyncClient, token: str, name: str, query: str):
    response = await client.post(
        "http://localhost:8000/api/v1/search/saved",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": name,
            "description": f"Searching for {query}",
            "query": query,
            "entity_types": ["workflow"],
            "is_public": False
        }
    )
    return response.json()

async def get_recommendations(client: httpx.AsyncClient, token: str):
    response = await client.post(
        "http://localhost:8000/api/v1/search/discover",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "entity_type": "agent",
            "limit": 10,
            "include_trending": True
        }
    )
    return response.json()
```

---

## TypeScript/JavaScript Example

```typescript
async function globalSearch(token: string, query: string) {
  const response = await fetch('http://localhost:8000/api/v1/search/global', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query,
      entity_types: ['workflow', 'agent'],
      filters: [],
      skip: 0,
      limit: 20
    })
  });
  return response.json();
}

async function advancedSearch(token: string, params: any) {
  const response = await fetch('http://localhost:8000/api/v1/search/advanced', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(params)
  });
  return response.json();
}

async function saveSearch(token: string, search: any) {
  const response = await fetch('http://localhost:8000/api/v1/search/saved', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(search)
  });
  return response.json();
}

async function getRecommendations(token: string, entityType: string) {
  const response = await fetch('http://localhost:8000/api/v1/search/discover', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      entity_type: entityType,
      limit: 10,
      include_trending: true
    })
  });
  return response.json();
}

async function getSuggestions(token: string, query: string) {
  const response = await fetch('http://localhost:8000/api/v1/search/suggestions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query,
      entity_types: ['workflow', 'agent'],
      limit: 10
    })
  });
  return response.json();
}

async function getSearchHistory(token: string) {
  const response = await fetch('http://localhost:8000/api/v1/search/history?limit=20', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}

async function getTrendingSearches(token: string) {
  const response = await fetch('http://localhost:8000/api/v1/search/trending?limit=10', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}
```

---

## Response Examples

### Global Search Response
```json
{
  "query": "workflow automation",
  "total_results": 150,
  "page": 1,
  "per_page": 20,
  "execution_time_ms": 245.5,
  "results": [
    {
      "id": 1,
      "entity_type": "workflow",
      "title": "Email Automation Workflow",
      "description": "Automates email sending",
      "relevance_score": 0.95,
      "matched_fields": ["title", "description"],
      "url": "/workflows/1",
      "created_at": "2024-05-30T10:00:00Z",
      "updated_at": "2024-05-30T15:30:00Z",
      "metadata": { "status": "active" }
    }
  ],
  "facets": {
    "entity_type": {
      "workflow": 45,
      "agent": 32,
      "file": 28
    }
  }
}
```

### Saved Search Response
```json
{
  "id": 123,
  "user_id": 456,
  "name": "Active Workflows",
  "description": "All active workflow automations",
  "query": "automation",
  "entity_types": ["workflow"],
  "filters": [],
  "is_public": false,
  "execution_count": 5,
  "created_at": "2024-05-30T10:00:00Z",
  "updated_at": "2024-05-30T15:30:00Z"
}
```

### Recommendations Response
```json
{
  "recommendations": [
    {
      "id": 1,
      "entity_type": "agent",
      "title": "Email Agent",
      "description": "Popular email handling agent",
      "popularity_score": 0.92,
      "recommendation_reason": "Trending in your industry",
      "url": "/agents/1",
      "created_at": "2024-05-30T10:00:00Z"
    }
  ],
  "generated_at": "2024-05-30T16:00:00Z"
}
```

---

## Performance Tips

1. **Use Facets:** Filter results before requesting details
2. **Pagination:** Always use skip/limit for large result sets
3. **Entity Types:** Narrow search scope to specific types
4. **Saved Searches:** Use for repeated queries
5. **Caching:** Cache suggestions and trending searches
6. **History:** Track searches for recommendations

---

## Status: Phase 7 Complete ✅
