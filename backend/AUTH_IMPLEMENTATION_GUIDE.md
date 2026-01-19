# Backend JWT Authentication - Implementation Guide

## Quick Start

### 1. Environment Configuration

Ensure `.env` contains:
```bash
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=<minimum-32-character-secret>
```

**Security Note**: The secret must be at least 32 characters. Backend will refuse to start with shorter secrets.

### 2. Dependencies

Install required packages:
```bash
pip install -r requirements.txt
```

Key dependency: `pyjwt==2.8.0`

### 3. Running the Backend

```bash
cd backend
python main.py
```

Backend will validate environment on startup:
```
[OK] DATABASE_URL configured
[OK] BETTER_AUTH_SECRET configured (46 characters)
Database tables created successfully
```

---

## Architecture Overview

```
Frontend (Next.js)
    │
    │ Authorization: Bearer <JWT_TOKEN>
    ▼
┌──────────────────────────────────────┐
│         FastAPI Backend              │
│                                      │
│  ┌────────────────────────────────┐ │
│  │  get_current_user()            │ │
│  │  - Extracts Bearer token       │ │
│  │  - Verifies JWT signature      │ │
│  │  - Returns AuthenticatedUser   │ │
│  └──────────────┬─────────────────┘ │
│                 │                    │
│  ┌──────────────▼─────────────────┐ │
│  │  verify_path_user_id()         │ │
│  │  - Checks user_id in URL       │ │
│  │  - Matches against JWT user_id │ │
│  │  - Returns 403 if mismatch     │ │
│  └──────────────┬─────────────────┘ │
│                 │                    │
│  ┌──────────────▼─────────────────┐ │
│  │  Task Endpoints                │ │
│  │  - POST   /{user_id}/tasks     │ │
│  │  - GET    /{user_id}/tasks     │ │
│  │  - GET    /{user_id}/tasks/{id}│ │
│  │  - PUT    /{user_id}/tasks/{id}│ │
│  │  - DELETE /{user_id}/tasks/{id}│ │
│  │  - PATCH  /{user_id}/tasks/{id}│ │
│  └────────────────────────────────┘ │
└──────────────────────────────────────┘
```

---

## JWT Token Format

### Token Structure

```
Authorization: Bearer <JWT_TOKEN>
```

### JWT Claims (Payload)

```json
{
  "sub": "user123",                    // User ID (required)
  "email": "user@example.com",         // User email (optional)
  "exp": 1768259268,                   // Expiration timestamp (required)
  "iat": 1768255668                    // Issued at timestamp
}
```

### Creating Test Tokens

For testing, use this Python snippet:
```python
import jwt
import os
from datetime import datetime, timedelta

secret = os.getenv("BETTER_AUTH_SECRET")
payload = {
    "sub": "user1",
    "email": "user1@example.com",
    "exp": datetime.utcnow() + timedelta(hours=1),
    "iat": datetime.utcnow()
}
token = jwt.encode(payload, secret, algorithm="HS256")
print(f"Bearer {token}")
```

---

## Protected Endpoints

### All Task Endpoints Require Authentication

| Method | Endpoint | Auth Required | User Isolation |
|--------|----------|---------------|----------------|
| POST | `/api/{user_id}/tasks` | ✅ Yes | ✅ Enforced |
| GET | `/api/{user_id}/tasks` | ✅ Yes | ✅ Enforced |
| GET | `/api/{user_id}/tasks/{id}` | ✅ Yes | ✅ Enforced |
| PUT | `/api/{user_id}/tasks/{id}` | ✅ Yes | ✅ Enforced |
| DELETE | `/api/{user_id}/tasks/{id}` | ✅ Yes | ✅ Enforced |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | ✅ Yes | ✅ Enforced |

### Unprotected Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| GET | `/` | API info |
| GET | `/docs` | Swagger docs |

---

## Error Responses

### 401 Unauthorized

**When**: Missing, invalid, or expired JWT token

**Example**:
```json
{
  "detail": {
    "error": "Unauthorized",
    "message": "Authorization header is required"
  }
}
```

**Causes**:
- Missing `Authorization` header
- Malformed token (not "Bearer <token>" format)
- Invalid JWT signature
- Expired token (past `exp` claim)
- Missing `sub` claim in JWT

### 403 Forbidden

**When**: Valid JWT but user doesn't own the resource

**Example**:
```json
{
  "detail": {
    "error": "Forbidden",
    "message": "You are not authorized to access this user's resources"
  }
}
```

**Cause**: JWT `user_id` doesn't match `{user_id}` in URL path

---

## Adding Authentication to New Endpoints

### Step 1: Import Dependencies

```python
from src.auth.jwt_deps import verify_path_user_id
from src.auth.auth_context import AuthenticatedUser
```

### Step 2: Add Dependency to Route

```python
@router.post("/{user_id}/new-endpoint")
def new_endpoint(
    user_id: str,
    current_user: AuthenticatedUser = Depends(verify_path_user_id)
):
    # current_user.user_id is guaranteed to equal user_id
    # No additional validation needed
    ...
```

### Step 3: Access User Context

```python
def new_endpoint(..., current_user: AuthenticatedUser = Depends(...)):
    # Access authenticated user info
    authenticated_user_id = current_user.user_id
    user_email = current_user.email  # May be None

    # Filter data by user
    results = session.exec(
        select(MyModel).where(MyModel.user_id == authenticated_user_id)
    ).all()
    ...
```

---

## Testing

### Unit Tests

Test JWT utilities:
```bash
pytest tests/test_jwt_validation.py -v
```

**Coverage**:
- JWT signature verification
- Token expiration
- User ID extraction
- AuthenticatedUser model

### Integration Tests

Test protected endpoints:
```bash
pytest tests/test_protected_endpoints.py -v
```

**Coverage**:
- Authentication required on all endpoints
- Invalid token handling
- User isolation enforcement
- Multi-user data separation

### Manual Testing

Run manual test script:
```bash
python test_auth_manual.py
```

**Tests**:
- Health check (no auth)
- Unauthenticated request (401)
- Valid authentication (200)
- User isolation (403)
- Invalid/expired tokens (401)

---

## Security Checklist

### Development

- [x] BETTER_AUTH_SECRET is at least 32 characters
- [x] .env file is in .gitignore
- [x] All task endpoints require authentication
- [x] User isolation enforced on all endpoints
- [x] Tests passing (30/30)

### Production Deployment

- [ ] HTTPS enforced (reverse proxy)
- [ ] BETTER_AUTH_SECRET is cryptographically random
- [ ] CORS origins restricted to actual frontend domain
- [ ] Rate limiting enabled (recommended)
- [ ] Authentication audit logging enabled (recommended)
- [ ] Monitoring/alerting configured

---

## Troubleshooting

### "BETTER_AUTH_SECRET environment variable is not configured"

**Problem**: Backend startup fails

**Solution**: Add to `.env`:
```bash
BETTER_AUTH_SECRET=<your-secret-minimum-32-characters-long>
```

### "401 Unauthorized" on valid request

**Problem**: Frontend JWT not accepted

**Causes**:
1. **Different secrets**: Frontend and backend using different BETTER_AUTH_SECRET
2. **Token expired**: Check `exp` claim
3. **Missing sub claim**: JWT must have `sub` or `user_id`

**Debug**:
```python
# Decode JWT to inspect claims
import jwt
token = "eyJ..."
decoded = jwt.decode(token, options={"verify_signature": False})
print(decoded)
```

### "403 Forbidden" on own resources

**Problem**: User gets 403 accessing their own tasks

**Cause**: `user_id` in URL doesn't match JWT `sub` claim

**Solution**: Ensure URL uses correct user ID:
```
Correct:   /api/user123/tasks  (JWT sub=user123)
Incorrect: /api/user456/tasks  (JWT sub=user123)
```

### Tests failing with "DATABASE_URL not set"

**Problem**: Pytest cannot import modules

**Solution**: Tests automatically load `.env` via `conftest.py`. Ensure `.env` exists in backend directory.

---

## Code Examples

### Example 1: Making Authenticated Request (Python)

```python
import requests
import jwt
import os
from datetime import datetime, timedelta

# Create JWT token
secret = os.getenv("BETTER_AUTH_SECRET")
token = jwt.encode({
    "sub": "user1",
    "email": "user1@example.com",
    "exp": datetime.utcnow() + timedelta(hours=1)
}, secret, algorithm="HS256")

# Make authenticated request
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/user1/tasks",
    headers=headers
)

print(response.json())
```

### Example 2: Making Authenticated Request (JavaScript)

```javascript
// Assume token is obtained from Better Auth
const token = "eyJ..."; // JWT from Better Auth

const response = await fetch("http://localhost:8000/api/user1/tasks", {
  headers: {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json"
  }
});

const tasks = await response.json();
console.log(tasks);
```

### Example 3: Creating Task

```javascript
const response = await fetch("http://localhost:8000/api/user1/tasks", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    title: "New Task",
    description: "Task description"
  })
});

const newTask = await response.json();
console.log(newTask);
```

---

## Module Reference

### `src/auth/jwt_utils.py`

**Functions**:
- `get_jwt_secret()`: Get BETTER_AUTH_SECRET from environment
- `verify_jwt_signature(token)`: Verify JWT signature and return claims
- `extract_user_id(claims)`: Extract user ID from JWT claims

### `src/auth/jwt_deps.py`

**Functions**:
- `get_current_user(authorization)`: FastAPI dependency for JWT auth
- `verify_path_user_id(user_id, current_user)`: Verify user owns resource

### `src/auth/auth_context.py`

**Classes**:
- `AuthenticatedUser`: Pydantic model for authenticated user context
  - `user_id: str` - User ID from JWT
  - `email: Optional[str]` - User email (if present)
  - `claims: Dict[str, Any]` - Full JWT payload

### `src/auth/error_handlers.py`

**Functions**:
- `unauthorized_handler(request, exc)`: Custom 401 error handler
- `forbidden_handler(request, exc)`: Custom 403 error handler

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ Yes | None | PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | ✅ Yes | None | JWT signing secret (32+ chars) |
| `CORS_ORIGINS` | No | `http://localhost:3000,...` | Allowed CORS origins |
| `SQLALCHEMY_ECHO` | No | `false` | Enable SQL query logging |

---

## Additional Resources

- **Security Report**: `BACKEND_AUTH_SECURITY_REPORT.md`
- **Specification**: `specs/002-authentication-jwt/spec.md`
- **Tasks**: `specs/002-authentication-jwt/tasks.md`
- **Plan**: `specs/002-authentication-jwt/plan.md`

---

**Last Updated**: 2026-01-13
**Version**: 1.0.0
