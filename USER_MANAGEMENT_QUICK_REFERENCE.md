# User Management Quick Reference - Buddy AI OS

## TL;DR - Get Started in 2 Minutes

### 1. Start API Server
```bash
cd backend
python -m uvicorn api.main:app --reload
```

### 2. Login (from Authentication phase)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password123"}'

# Copy access_token from response
```

### 3. Test User Management
```bash
# Get profile
curl -X GET http://localhost:8000/api/v1/users/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Create goal
curl -X POST http://localhost:8000/api/v1/users/goals \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"goal":"Learn FastAPI","priority":"high"}'

# Update preferences
curl -X PUT http://localhost:8000/api/v1/users/preferences \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"theme":"dark","language":"en"}'
```

---

## API Endpoints Quick Reference

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/api/v1/users/profile` | GET | Get current profile | ✅ |
| `/api/v1/users/profile` | PUT | Update profile | ✅ |
| `/api/v1/users/preferences` | GET | Get preferences | ✅ |
| `/api/v1/users/preferences` | PUT | Update preferences | ✅ |
| `/api/v1/users/goals` | GET | List all goals | ✅ |
| `/api/v1/users/goals` | POST | Create goal | ✅ |
| `/api/v1/users/goals/{id}` | PUT | Update goal | ✅ |
| `/api/v1/users/goals/{id}` | DELETE | Delete goal | ✅ |
| `/api/v1/users/activity` | GET | Get activity stats | ✅ |
| `/api/v1/users/deactivate` | POST | Deactivate account | ✅ |
| `/api/v1/users/reactivate` | POST | Reactivate account | ✅ |
| `/api/v1/users/delete` | DELETE | Permanently delete | ✅ |

---

## Request/Response Examples

### Get Profile
```bash
curl -X GET http://localhost:8000/api/v1/users/profile \
  -H "Authorization: Bearer {access_token}"
```

**Response (200)**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "full_name": "John Doe",
  "bio": null,
  "profile_picture_url": null,
  "phone_number": null,
  "location": null,
  "timezone": null,
  "is_active": true,
  "is_verified": true,
  "created_at": "2026-05-29T10:00:00Z",
  "updated_at": "2026-05-29T10:00:00Z",
  "last_login": "2026-05-30T14:00:00Z"
}
```

### Update Profile
```bash
curl -X PUT http://localhost:8000/api/v1/users/profile \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "bio": "Software Engineer",
    "profile_picture_url": "https://example.com/pic.jpg",
    "phone_number": "+1-555-0123",
    "location": "San Francisco, CA",
    "timezone": "America/Los_Angeles"
  }'
```

### Get Preferences
```bash
curl -X GET http://localhost:8000/api/v1/users/preferences \
  -H "Authorization: Bearer {access_token}"
```

**Response (200)**:
```json
{
  "user_id": 1,
  "theme": "light",
  "language": "en",
  "notifications_email": true,
  "notifications_push": true,
  "notifications_sms": false,
  "email_digest_frequency": "weekly",
  "two_factor_enabled": false,
  "show_online_status": true,
  "auto_save_enabled": true,
  "data_export_frequency": "never",
  "updated_at": "2026-05-30T15:30:00Z"
}
```

### Update Preferences
```bash
curl -X PUT http://localhost:8000/api/v1/users/preferences \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "dark",
    "language": "en",
    "notifications_email": true,
    "two_factor_enabled": true,
    "email_digest_frequency": "daily"
  }'
```

### Create Goal
```bash
curl -X POST http://localhost:8000/api/v1/users/goals \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Complete FastAPI course",
    "description": "Learn async APIs",
    "category": "learning",
    "deadline": "2026-06-30T23:59:59Z",
    "priority": "high"
  }'
```

**Response (201)**:
```json
{
  "id": 1,
  "user_id": 1,
  "goal": "Complete FastAPI course",
  "description": "Learn async APIs",
  "category": "learning",
  "deadline": "2026-06-30T23:59:59Z",
  "priority": "high",
  "status": "active",
  "progress": 0,
  "created_at": "2026-05-30T15:30:00Z",
  "updated_at": "2026-05-30T15:30:00Z"
}
```

### Update Goal Progress
```bash
curl -X PUT http://localhost:8000/api/v1/users/goals/1 \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "progress": 75,
    "status": "active"
  }'
```

### List Goals
```bash
curl -X GET http://localhost:8000/api/v1/users/goals \
  -H "Authorization: Bearer {access_token}"
```

**Response (200)**:
```json
[
  {
    "id": 1,
    "user_id": 1,
    "goal": "Complete FastAPI course",
    "description": "Learn async APIs",
    "category": "learning",
    "deadline": "2026-06-30T23:59:59Z",
    "priority": "high",
    "status": "active",
    "progress": 75,
    "created_at": "2026-05-30T15:30:00Z",
    "updated_at": "2026-05-30T16:00:00Z"
  }
]
```

### Delete Goal
```bash
curl -X DELETE http://localhost:8000/api/v1/users/goals/1 \
  -H "Authorization: Bearer {access_token}"
```

**Response (204)**: No Content

### Get Activity
```bash
curl -X GET http://localhost:8000/api/v1/users/activity \
  -H "Authorization: Bearer {access_token}"
```

**Response (200)**:
```json
{
  "user_id": 1,
  "total_logins": 15,
  "last_login": "2026-05-30T14:00:00Z",
  "total_goals": 5,
  "completed_goals": 2,
  "active_goals": 3,
  "goals_progress_average": 45.5,
  "account_created_at": "2026-05-29T10:00:00Z",
  "account_age_days": 1
}
```

### Deactivate Account
```bash
curl -X POST http://localhost:8000/api/v1/users/deactivate \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "CurrentPassword123",
    "reason": "Taking a break",
    "send_confirmation_email": true
  }'
```

**Response (200)**:
```json
{
  "message": "Account deactivated successfully. You can reactivate within 30 days.",
  "user_id": 1,
  "deactivated_at": "2026-05-30T15:30:00Z",
  "reactivation_deadline": "2026-06-29T15:30:00Z"
}
```

### Reactivate Account
```bash
curl -X POST http://localhost:8000/api/v1/users/reactivate \
  -H "Authorization: Bearer {access_token}"
```

**Response (200)**: User profile response

### Delete Account
```bash
curl -X DELETE http://localhost:8000/api/v1/users/delete \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "CurrentPassword123",
    "confirm_deletion": true,
    "export_data": false
  }'
```

**Response (200)**:
```json
{
  "message": "Account permanently deleted. All associated data has been removed.",
  "user_id": 1,
  "deleted_at": "2026-05-30T15:30:00Z"
}
```

---

## Goal Status Values

| Status | Description |
|--------|-------------|
| `active` | Goal in progress |
| `completed` | Goal finished (progress = 100%) |
| `paused` | Temporarily paused |
| `abandoned` | Gave up on goal |

---

## Goal Priority Values

| Priority | Usage |
|----------|-------|
| `low` | Nice to have |
| `medium` | Should do |
| `high` | Important |
| `critical` | Must do |

---

## Theme Values

| Theme | Description |
|-------|-------------|
| `light` | Light mode |
| `dark` | Dark mode |
| `auto` | Follow system setting |

---

## Notification Settings

```json
{
  "notifications_email": true,      // Email notifications
  "notifications_push": true,       // Push notifications
  "notifications_sms": false,       // SMS notifications
  "email_digest_frequency": "daily" // daily, weekly, never
}
```

---

## Python Client Example

```python
import httpx

# Create client
async with httpx.AsyncClient() as client:
    # Get profile
    response = await client.get(
        "http://localhost:8000/api/v1/users/profile",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    profile = response.json()
    
    # Update profile
    response = await client.put(
        "http://localhost:8000/api/v1/users/profile",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"full_name": "John Doe", "bio": "Engineer"}
    )
    
    # Create goal
    response = await client.post(
        "http://localhost:8000/api/v1/users/goals",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "goal": "Learn FastAPI",
            "priority": "high",
            "deadline": "2026-06-30T23:59:59Z"
        }
    )
    goal = response.json()
    
    # Update goal progress
    response = await client.put(
        f"http://localhost:8000/api/v1/users/goals/{goal['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"progress": 50}
    )
    
    # Get preferences
    response = await client.get(
        "http://localhost:8000/api/v1/users/preferences",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    prefs = response.json()
```

---

## JavaScript/TypeScript Client Example

```typescript
// Get profile
const profileResponse = await fetch(
  'http://localhost:8000/api/v1/users/profile',
  {
    headers: { 'Authorization': `Bearer ${accessToken}` }
  }
);
const profile = await profileResponse.json();

// Update profile
const updateResponse = await fetch(
  'http://localhost:8000/api/v1/users/profile',
  {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    },
    body: JSON.stringify({
      full_name: 'John Doe',
      bio: 'Software Engineer',
      timezone: 'America/Los_Angeles'
    })
  }
);

// Create goal
const createGoalResponse = await fetch(
  'http://localhost:8000/api/v1/users/goals',
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    },
    body: JSON.stringify({
      goal: 'Learn FastAPI',
      priority: 'high',
      category: 'learning',
      deadline: '2026-06-30T23:59:59Z'
    })
  }
);
const goal = await createGoalResponse.json();

// Update goal
const updateGoalResponse = await fetch(
  `http://localhost:8000/api/v1/users/goals/${goal.id}`,
  {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    },
    body: JSON.stringify({ progress: 50 })
  }
);

// Get preferences
const prefsResponse = await fetch(
  'http://localhost:8000/api/v1/users/preferences',
  {
    headers: { 'Authorization': `Bearer ${accessToken}` }
  }
);
const prefs = await prefsResponse.json();

// Update preferences
const updatePrefsResponse = await fetch(
  'http://localhost:8000/api/v1/users/preferences',
  {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`
    },
    body: JSON.stringify({
      theme: 'dark',
      notifications_email: true
    })
  }
);
```

---

## Error Responses

### 400 Bad Request
```json
{
  "status_code": 400,
  "message": "Bad Request",
  "detail": "Goal cannot be empty"
}
```

### 401 Unauthorized
```json
{
  "status_code": 401,
  "message": "Unauthorized",
  "detail": "Current password is incorrect"
}
```

### 404 Not Found
```json
{
  "status_code": 404,
  "message": "Not Found",
  "detail": "Goal not found"
}
```

### 500 Internal Server Error
```json
{
  "status_code": 500,
  "message": "Internal Server Error",
  "detail": "Error updating profile"
}
```

---

## Common Headers

```
Authorization: Bearer {access_token}
Content-Type: application/json
```

---

## Field Validation Rules

**Profile Fields**:
- `full_name`: Max 256 characters
- `bio`: Max 1000 characters
- `phone_number`: Max 20 characters
- `location`: Max 256 characters
- `timezone`: Max 50 characters
- `profile_picture_url`: Max 2048 characters

**Goal Fields**:
- `goal`: 5-500 characters (required)
- `description`: Max 2000 characters
- `category`: Max 100 characters
- `priority`: low, medium, high, critical
- `progress`: 0-100 (integer)
- `status`: active, completed, paused, abandoned

**Preferences Fields**:
- `theme`: light, dark, auto
- `language`: Any language code
- `email_digest_frequency`: daily, weekly, never
- Booleans for all toggle settings

---

## Common Issues & Troubleshooting

### "Invalid token" Error
- Token has expired (get new one via /auth/refresh)
- Token format incorrect (should be "Bearer {token}")
- Token was copied with extra spaces

### "User not found" Error
- User ID in token is invalid
- User has been deleted
- Check database connection

### "Goal not found" Error
- Goal ID doesn't exist
- Goal belongs to different user
- Goal was deleted

### "Current password is incorrect" Error
- Password spelling is wrong
- Password case sensitivity
- Using old password after change

---

## Useful Commands

```bash
# Start API
python -m uvicorn api.main:app --reload

# Run tests
pytest tests/

# Check API docs
# http://localhost:8000/docs

# Format code
black backend/

# Lint code
flake8 backend/
```

---

## Files Location

| File | Purpose |
|------|---------|
| `api/schemas/user_schemas.py` | Request/response models |
| `services/user_service.py` | Business logic |
| `api/v1/users.py` | API endpoints |
| `db/models.py` | Database models |
| `api/main.py` | FastAPI application |
| `config/auth_config.py` | Configuration |

---

## Best Practices

1. **Always require authentication** for user endpoints
2. **Validate passwords** for sensitive operations
3. **Update timestamps** on every change
4. **Handle errors gracefully** with proper HTTP codes
5. **Limit query results** for large datasets
6. **Use indexes** for frequently queried fields
7. **Cache preferences** to reduce DB queries
8. **Log all operations** for audit trail
9. **Soft delete** for deactivation (reversible)
10. **Hard delete** only with explicit confirmation

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: 2026-05-30
