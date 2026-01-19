# Quickstart Guide: Backend API + Database

**Feature**: Backend API + Database (001-backend-api)
**Purpose**: Get the backend running locally for development and testing
**Prerequisites**: Python 3.11+, pip, PostgreSQL (Neon or local)

---

## 1. Environment Setup

### 1.1 Create Python Virtual Environment

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 1.2 Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt** contains:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlmodel==0.0.14
psycopg2-binary==2.9.9
pydantic==2.5.0
python-dotenv==1.0.0
pytest==7.4.3
httpx==0.25.2
pytest-asyncio==0.21.1
```

### 1.3 Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/taskie_dev
BETTER_AUTH_SECRET=your-test-secret-key-min-32-chars
```

**Important**:
- Never commit `.env` to version control
- Use `.env.example` as template for new developers
- For Neon database: get DATABASE_URL from Neon dashboard
- BETTER_AUTH_SECRET is used for JWT verification (added in Spec 2)

---

## 2. Database Initialization

### 2.1 Create Database

```bash
# Using Neon (recommended for cloud)
# Database URL provided by Neon dashboard

# OR using local PostgreSQL
psql -U postgres -c "CREATE DATABASE taskie_dev;"
```

### 2.2 Run Database Migrations

```bash
# Using Alembic (SQLModel migrations)
alembic upgrade head

# OR manually create schema (for initial setup)
# SQL schema in specs/001-backend-api/data-model.md
```

### 2.3 Verify Database Connection

```bash
python -c "
from src.database import engine
from sqlmodel import Session
try:
    with Session(engine) as session:
        print('✓ Database connection successful')
except Exception as e:
    print(f'✗ Database connection failed: {e}')
"
```

---

## 3. Running the Backend

### 3.1 Start the Development Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 3.2 View API Documentation

Open in browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 4. Testing the API

### 4.1 Create Test User Session

For testing without auth middleware, add test user_id to requests:

```bash
# Export test user ID
TEST_USER_ID="test-user-001"
```

### 4.2 Create a Task

```bash
curl -X POST "http://localhost:8000/api/${TEST_USER_ID}/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'
```

**Response** (201 Created):
```json
{
  "id": 1,
  "user_id": "test-user-001",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "incomplete",
  "created_at": "2025-01-09T12:34:56Z",
  "updated_at": "2025-01-09T12:34:56Z"
}
```

### 4.3 List All Tasks

```bash
curl -X GET "http://localhost:8000/api/${TEST_USER_ID}/tasks" \
  -H "Content-Type: application/json"
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "user_id": "test-user-001",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "status": "incomplete",
    "created_at": "2025-01-09T12:34:56Z",
    "updated_at": "2025-01-09T12:34:56Z"
  }
]
```

### 4.4 Get Single Task

```bash
curl -X GET "http://localhost:8000/api/${TEST_USER_ID}/tasks/1" \
  -H "Content-Type: application/json"
```

### 4.5 Update a Task

```bash
curl -X PUT "http://localhost:8000/api/${TEST_USER_ID}/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries (updated)"
  }'
```

### 4.6 Mark Task Complete

```bash
curl -X PATCH "http://localhost:8000/api/${TEST_USER_ID}/tasks/1/complete" \
  -H "Content-Type: application/json"
```

### 4.7 Delete a Task

```bash
curl -X DELETE "http://localhost:8000/api/${TEST_USER_ID}/tasks/1" \
  -H "Content-Type: application/json"
```

**Response** (204 No Content):
```
(empty response body)
```

---

## 5. Running Tests

### 5.1 Run All Tests

```bash
pytest tests/ -v
```

### 5.2 Run Specific Test File

```bash
pytest tests/test_api.py -v
```

### 5.3 Run Tests with Coverage

```bash
pytest tests/ --cov=src --cov-report=html
# View coverage report: open htmlcov/index.html
```

### 5.4 Test Database Isolation (Multi-User)

```python
# tests/test_api.py - example test

def test_user_isolation():
    """Verify User A cannot see User B's tasks"""

    # User A creates task
    response_a = client.post(
        "/api/user-a/tasks",
        json={"title": "User A task"}
    )
    assert response_a.status_code == 201
    task_id = response_a.json()["id"]

    # User B attempts to view User A's task
    response_b = client.get(f"/api/user-b/tasks/{task_id}")
    assert response_b.status_code == 404  # User B cannot see User A's task

    # User B list returns empty (no tasks created by User B)
    response_b_list = client.get("/api/user-b/tasks")
    assert response_b_list.json() == []
```

---

## 6. Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template (commit this)
├── .env                    # Environment variables (DO NOT commit)
├── venv/                   # Python virtual environment (DO NOT commit)
├── src/
│   ├── __init__.py
│   ├── database.py         # Database connection setup
│   ├── models.py           # SQLModel Task and User definitions
│   ├── schemas.py          # Pydantic request/response schemas
│   ├── services.py         # Business logic (CRUD operations)
│   └── api/
│       ├── __init__.py
│       └── tasks.py        # Task endpoints
└── tests/
    ├── __init__.py
    ├── conftest.py         # Pytest fixtures
    ├── test_models.py      # Unit tests for models
    ├── test_services.py    # Unit tests for services
    └── test_api.py         # Integration tests for endpoints
```

---

## 7. Common Tasks

### 7.1 Reset Database

```bash
# Drop all tables and recreate schema
alembic downgrade base
alembic upgrade head
```

### 7.2 View Database Records (psql)

```bash
# Connect to database
psql postgresql://user:password@localhost:5432/taskie_dev

# List tasks
SELECT * FROM tasks;

# List by user
SELECT * FROM tasks WHERE user_id = 'test-user-001';

# Delete all tasks (development only)
DELETE FROM tasks;
```

### 7.3 Debug SQL Queries

Set `SQLALCHEMY_ECHO=true` in `.env` to see all SQL queries:

```bash
# .env
SQLALCHEMY_ECHO=true
```

Queries will print to console:

```
SELECT tasks.id, tasks.user_id, tasks.title, ...
FROM tasks
WHERE tasks.user_id = 'test-user-001'
```

### 7.4 Reload Dependencies

```bash
pip install -r requirements.txt --upgrade
```

---

## 8. Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'sqlmodel'"

**Solution**: Ensure virtual environment is activated and dependencies installed:
```bash
source venv/bin/activate  # Activate venv
pip install -r requirements.txt
```

### Issue: "psycopg2.OperationalError: could not connect to server"

**Solution**: Verify DATABASE_URL in `.env`:
```bash
# For Neon:
DATABASE_URL=postgresql://user:password@host.neon.tech:5432/database?sslmode=require

# For local PostgreSQL:
DATABASE_URL=postgresql://user:password@localhost:5432/taskie_dev
```

### Issue: "401 Unauthorized" on all endpoints (before auth middleware)

**Solution**: Auth middleware is not yet implemented. For testing, use test user_id in URL:
```bash
# ✓ Correct (test mode)
GET /api/test-user-001/tasks

# ✗ Won't work until Spec 2 auth implemented
GET /api/tasks  # Missing user_id
```

### Issue: Tests fail with "No such table: tasks"

**Solution**: Run migrations before tests:
```bash
alembic upgrade head
pytest tests/
```

---

## 9. Next Steps

1. **Run Backend Locally**: Follow section 3 to start development server
2. **Test Endpoints**: Use Swagger UI (http://localhost:8000/docs) or curl commands in section 4
3. **Run Tests**: Execute `pytest tests/ -v` to verify all endpoints
4. **Implement Frontend**: Once backend is running, Spec 2 will build frontend (Next.js)
5. **Add Authentication**: Spec 2 will add JWT middleware; no backend code changes needed

---

## 10. API Endpoint Summary

| Method | Endpoint | Purpose | Status Code |
|--------|----------|---------|-------------|
| POST | `/api/{user_id}/tasks` | Create task | 201 Created |
| GET | `/api/{user_id}/tasks` | List tasks | 200 OK |
| GET | `/api/{user_id}/tasks/{id}` | Get task | 200 OK |
| PUT | `/api/{user_id}/tasks/{id}` | Update task | 200 OK |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task | 204 No Content |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Mark complete | 200 OK |

**Error Codes**: 400 (validation), 401 (auth), 404 (not found), 500 (server error)

---

## 11. Useful Links

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLModel Docs**: https://sqlmodel.tiangolo.com/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **Neon Docs**: https://neon.tech/docs/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

