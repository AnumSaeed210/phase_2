# Testing Guide: Spec 002 Authentication & Security (JWT)

**Date**: 2026-01-09
**Status**: Ready for testing
**Backend**: FastAPI running on http://localhost:8000
**Database**: Neon PostgreSQL (live)

---

## Quick Start: Run All Tests

### Option 1: Run Full Test Suite (Recommended)
```bash
cd backend
pytest tests/test_api.py -v
```

**Expected Output**: All tests PASS with JWT authentication

### Option 2: Run Specific Test Class
```bash
# Test creating tasks with auth
pytest tests/test_api.py::TestCreateTask -v

# Test multi-user isolation
pytest tests/test_api.py::TestListTasks::test_list_tasks_multi_user_isolation -v

# Test authentication errors
pytest tests/test_api.py::TestErrorHandling -v
```

---

## Manual Testing with cURL

### Setup: Generate a Test Token

First, generate a valid JWT token using Python:

```bash
cd backend
python3 << 'EOF'
from src.auth.jwt_utils import create_test_jwt_token
from dotenv import load_dotenv
import os

load_dotenv()

# Create a test token for user "test-user-1"
token = create_test_jwt_token(
    user_id="test-user-1",
    email="test@example.com"
)
print("TEST TOKEN:")
print(token)
EOF
```

**Copy the token output** - you'll use it in the next commands.

---

## Test 1: Create a Task (With Authentication)

### ✅ **WITH Valid JWT Token**
```bash
curl -X POST http://localhost:8000/api/test-user-1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'
```

**Expected Response** (201 Created):
```json
{
  "id": 1,
  "user_id": "test-user-1",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "incomplete",
  "created_at": "2026-01-09T12:00:00",
  "updated_at": "2026-01-09T12:00:00"
}
```

### ❌ **WITHOUT Token (Should Fail)**
```bash
curl -X POST http://localhost:8000/api/test-user-1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries"}'
```

**Expected Response** (401 Unauthorized):
```json
{
  "detail": {
    "error": "Unauthorized"
  }
}
```

### ❌ **WITH Invalid Token (Should Fail)**
```bash
curl -X POST http://localhost:8000/api/test-user-1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer invalid.token.here" \
  -d '{"title": "Buy groceries"}'
```

**Expected Response** (401 Unauthorized):
```json
{
  "detail": {
    "error": "Unauthorized"
  }
}
```

---

## Test 2: Get All Tasks (List)

### ✅ **WITH Valid JWT Token**
```bash
curl -X GET http://localhost:8000/api/test-user-1/tasks \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected Response** (200 OK):
```json
[
  {
    "id": 1,
    "user_id": "test-user-1",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "status": "incomplete",
    "created_at": "2026-01-09T12:00:00",
    "updated_at": "2026-01-09T12:00:00"
  }
]
```

---

## Test 3: User Isolation (Multi-User Scenario)

### Setup: Create Tokens for Two Different Users

```bash
python3 << 'EOF'
from src.auth.jwt_utils import create_test_jwt_token

# Token for User 1
token1 = create_test_jwt_token(
    user_id="user-alice",
    email="alice@example.com"
)
print("USER 1 TOKEN (alice):")
print(token1)
print()

# Token for User 2
token2 = create_test_jwt_token(
    user_id="user-bob",
    email="bob@example.com"
)
print("USER 2 TOKEN (bob):")
print(token2)
EOF
```

### Test: User 1 Creates a Task
```bash
curl -X POST http://localhost:8000/api/user-alice/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN_1" \
  -d '{"title": "Alice task"}'
```

### Test: User 2 Lists Their Tasks (Should be empty)
```bash
curl -X GET http://localhost:8000/api/user-bob/tasks \
  -H "Authorization: Bearer TOKEN_2"
```

**Expected Response** (200 OK, empty list):
```json
[]
```

### Test: User 2 Tries to Access User 1's Task (Should Fail)
```bash
curl -X GET http://localhost:8000/api/user-bob/tasks/1 \
  -H "Authorization: Bearer TOKEN_2"
```

**Expected Response** (404 Not Found):
```json
{
  "detail": {
    "error": "Task not found"
  }
}
```

✅ **User isolation verified** - Bob cannot access Alice's task!

---

## Test 4: JWT Claims Validation

### Test: Wrong Issuer (Should Fail)

```bash
python3 << 'EOF'
import jwt
from datetime import datetime, timedelta

secret = "test_secret_minimum_32_characters_longggg"

# Create token with wrong issuer
payload = {
    "sub": "test-user-1",
    "email": "test@example.com",
    "iat": int(datetime.utcnow().timestamp()),
    "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
    "iss": "wrong-issuer",  # Should be "better-auth"
    "aud": "taskie-api"
}

token = jwt.encode(payload, secret, algorithm="HS256")
print("TOKEN WITH WRONG ISSUER:")
print(token)
EOF
```

```bash
curl -X GET http://localhost:8000/api/test-user-1/tasks \
  -H "Authorization: Bearer WRONG_ISSUER_TOKEN"
```

**Expected Response** (401 Unauthorized):
```json
{
  "detail": {
    "error": "Unauthorized"
  }
}
```

### Test: Wrong Audience (Should Fail)

```bash
python3 << 'EOF'
import jwt
from datetime import datetime, timedelta

secret = "test_secret_minimum_32_characters_longggg"

# Create token with wrong audience
payload = {
    "sub": "test-user-1",
    "email": "test@example.com",
    "iat": int(datetime.utcnow().timestamp()),
    "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
    "iss": "better-auth",
    "aud": "wrong-app"  # Should be "taskie-api"
}

token = jwt.encode(payload, secret, algorithm="HS256")
print("TOKEN WITH WRONG AUDIENCE:")
print(token)
EOF
```

```bash
curl -X GET http://localhost:8000/api/test-user-1/tasks \
  -H "Authorization: Bearer WRONG_AUDIENCE_TOKEN"
```

**Expected Response** (401 Unauthorized)

---

## Test 5: CORS Configuration

### Test: Allowed Origin (Should Succeed)
```bash
curl -X GET http://localhost:8000/api/test-user-1/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Origin: http://localhost:3000"
```

**Expected Response**: ✅ 200 OK with CORS headers

### Test: Unauthorized Origin (Should Fail)
```bash
curl -X GET http://localhost:8000/api/test-user-1/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Origin: https://evil.com"
```

**Expected Response**: ❌ CORS error (no CORS headers returned)

---

## Test 6: Token Expiration

### Create an Expired Token
```bash
python3 << 'EOF'
import jwt
from datetime import datetime, timedelta

secret = "test_secret_minimum_32_characters_longggg"

# Create token that expired 1 hour ago
payload = {
    "sub": "test-user-1",
    "email": "test@example.com",
    "iat": int((datetime.utcnow() - timedelta(hours=2)).timestamp()),
    "exp": int((datetime.utcnow() - timedelta(hours=1)).timestamp()),  # Expired 1 hour ago
    "iss": "better-auth",
    "aud": "taskie-api"
}

token = jwt.encode(payload, secret, algorithm="HS256")
print("EXPIRED TOKEN:")
print(token)
EOF
```

```bash
curl -X GET http://localhost:8000/api/test-user-1/tasks \
  -H "Authorization: Bearer EXPIRED_TOKEN"
```

**Expected Response** (401 Unauthorized):
```json
{
  "detail": {
    "error": "Unauthorized"
  }
}
```

---

## Test 7: User Ownership Enforcement (403)

### Setup: Create a Task and Try Different User Access

Create token for User A:
```bash
python3 << 'EOF'
from src.auth.jwt_utils import create_test_jwt_token
token_a = create_test_jwt_token("user-a", "a@example.com")
print(token_a)
EOF
```

Create token for User B:
```bash
python3 << 'EOF'
from src.auth.jwt_utils import create_test_jwt_token
token_b = create_test_jwt_token("user-b", "b@example.com")
print(token_b)
EOF
```

### User A creates a task:
```bash
curl -X POST http://localhost:8000/api/user-a/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN_A" \
  -d '{"title": "User A task"}'
```

Note the task ID from response (e.g., `"id": 5`)

### User B tries to get User A's task (Should fail with 403):
```bash
curl -X GET http://localhost:8000/api/user-b/tasks/5 \
  -H "Authorization: Bearer TOKEN_B"
```

**Expected Response** (404 Not Found - treated as "not found" for security):
```json
{
  "detail": {
    "error": "Task not found"
  }
}
```

---

## Test 8: All CRUD Operations

### CREATE
```bash
curl -X POST http://localhost:8000/api/test-user-1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"title": "New task"}'
```

### READ (Get single task)
```bash
curl -X GET http://localhost:8000/api/test-user-1/tasks/1 \
  -H "Authorization: Bearer TOKEN"
```

### UPDATE
```bash
curl -X PUT http://localhost:8000/api/test-user-1/tasks/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"title": "Updated title"}'
```

### DELETE
```bash
curl -X DELETE http://localhost:8000/api/test-user-1/tasks/1 \
  -H "Authorization: Bearer TOKEN"
```

### COMPLETE (Mark as done)
```bash
curl -X PATCH http://localhost:8000/api/test-user-1/tasks/1/complete \
  -H "Authorization: Bearer TOKEN"
```

---

## Test 9: Run Full Pytest Suite

### Run all tests with JWT authentication:
```bash
cd backend
pytest tests/test_api.py -v --tb=short
```

### Run with detailed output:
```bash
pytest tests/test_api.py -vv --tb=long
```

### Run specific test:
```bash
pytest tests/test_api.py::TestCreateTask::test_create_task_with_title_only -v
```

### Run with coverage:
```bash
pytest tests/test_api.py --cov=src/auth --cov-report=html
```

---

## Checklist: What to Verify

### ✅ Authentication
- [ ] Valid JWT token allows access
- [ ] Missing token → 401 Unauthorized
- [ ] Invalid token → 401 Unauthorized
- [ ] Expired token → 401 Unauthorized
- [ ] Wrong issuer → 401 Unauthorized
- [ ] Wrong audience → 401 Unauthorized

### ✅ Authorization
- [ ] User can access own tasks
- [ ] User cannot access other user's tasks → 404
- [ ] User cannot modify other user's tasks → 404
- [ ] User cannot delete other user's tasks → 404

### ✅ CRUD Operations
- [ ] Create task (POST) → 201
- [ ] List tasks (GET) → 200
- [ ] Get single task (GET) → 200
- [ ] Update task (PUT) → 200
- [ ] Delete task (DELETE) → 204
- [ ] Complete task (PATCH) → 200

### ✅ Security
- [ ] CORS allows localhost:3000
- [ ] CORS blocks unauthorized origins
- [ ] Generic error messages (no info disclosure)
- [ ] Timestamps preserved (created_at immutable, updated_at changes)

### ✅ Multi-User Isolation
- [ ] User A's tasks not visible to User B
- [ ] User B cannot modify User A's tasks
- [ ] List endpoints filter by authenticated user
- [ ] All endpoints enforce user ownership

---

## Environment Setup

### Before Running Tests

1. **Set environment variables**:
```bash
export BETTER_AUTH_SECRET="test_secret_minimum_32_characters_longggg"
export DATABASE_URL="postgresql://..."  # Your Neon URL
export CORS_ORIGINS="http://localhost:3000"
```

2. **Start backend** (if not running):
```bash
cd backend
python -m uvicorn main:app --reload
```

3. **Run tests** (in separate terminal):
```bash
cd backend
pytest tests/test_api.py -v
```

---

## Quick Command Reference

### Generate Test Token
```bash
cd backend && python3 -c "from src.auth.jwt_utils import create_test_jwt_token; print(create_test_jwt_token('test-user-1', 'test@example.com'))"
```

### Test with cURL (Create Task)
```bash
curl -X POST http://localhost:8000/api/test-user-1/tasks \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test"}'
```

### Run All Tests
```bash
cd backend && pytest tests/test_api.py -v
```

### Run Specific Test Class
```bash
cd backend && pytest tests/test_api.py::TestCreateTask -v
```

---

## Expected Test Results

When you run `pytest tests/test_api.py -v`, you should see:

```
test_api.py::TestCreateTask::test_create_task_with_title_only PASSED
test_api.py::TestCreateTask::test_create_task_with_description PASSED
test_api.py::TestCreateTask::test_create_task_missing_title PASSED
test_api.py::TestCreateTask::test_create_task_empty_title PASSED
...
test_api.py::TestListTasks::test_list_tasks_multi_user_isolation PASSED
test_api.py::TestGetTask::test_get_task_ownership_check PASSED
test_api.py::TestUpdateTask::test_update_task_ownership_check PASSED
test_api.py::TestDeleteTask::test_delete_task_ownership_check PASSED
...
======================== X passed in Y.XXs ========================
```

**All tests should PASS** with the JWT authentication now in place.

---

## Troubleshooting

### Issue: "Token expired"
- Generate a fresh token (they expire after 7 days by default)

### Issue: "Unauthorized" for valid token
- Check `BETTER_AUTH_SECRET` matches between token generation and server
- Verify token includes `iss: "better-auth"` and `aud: "taskie-api"`

### Issue: CORS error
- Ensure `CORS_ORIGINS` includes your frontend origin
- Check `Origin` header matches allowed origins

### Issue: "Task not found" for valid ID
- Might be ownership enforcement (user_id mismatch)
- Try with correct user_id in URL path

---

## Success Criteria

✅ **Spec 002 Authentication Tests PASS** when:
1. All pytest tests pass (X/X)
2. Valid JWT tokens access protected endpoints
3. Invalid tokens get 401 Unauthorized
4. Wrong user gets 404 (cannot access other users' tasks)
5. CORS only allows specified origins
6. All CRUD operations work with authentication

**You're done when all tests pass!** 🎉
