# Todo Backend API

A FastAPI-based backend service for multi-user todo task management with persistent storage in Neon Serverless PostgreSQL.

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL or Neon serverless database
- Virtual environment (optional but recommended)

### Setup

1. **Create virtual environment**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and set:
# - DATABASE_URL (your PostgreSQL connection string)
# - BETTER_AUTH_SECRET (shared JWT secret)
```

4. **Run migrations** (if using Alembic):
```bash
alembic upgrade head
```

5. **Start the server**:
```bash
python -m uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Endpoints

### Create Task
POST /api/{user_id}/tasks

### List All Tasks
GET /api/{user_id}/tasks
GET /api/{user_id}/tasks?status=incomplete

### Get Single Task
GET /api/{user_id}/tasks/{id}

### Update Task
PUT /api/{user_id}/tasks/{id}

### Delete Task
DELETE /api/{user_id}/tasks/{id}

### Mark Task Complete
PATCH /api/{user_id}/tasks/{id}/complete

## Task Priorities

The API supports task prioritization with three levels: **low**, **medium**, and **high**. All tasks default to **medium** priority.

### Create Task with Priority
```bash
curl -X POST http://localhost:8000/api/user123/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fix critical bug",
    "description": "Production issue",
    "priority": "high"
  }'
```

Response:
```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Fix critical bug",
  "status": "incomplete",
  "priority": "high",
  "created_at": "2026-01-17T15:30:00Z",
  "updated_at": "2026-01-17T15:30:00Z"
}
```

### Update Task Priority
```bash
curl -X PUT http://localhost:8000/api/user123/tasks/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"priority": "medium"}'
```

### List Tasks Sorted by Priority
```bash
curl -X GET "http://localhost:8000/api/user123/tasks?sort=priority" \
  -H "Authorization: Bearer <token>"
```

Returns tasks in priority order: High → Medium → Low, with secondary sort by creation date (newest first).

### Priority Features
- **Case-insensitive input**: `"HIGH"`, `"high"`, `"High"` all normalize to `"high"`
- **Default value**: Tasks created without priority default to `"medium"`
- **Validation**: Invalid priority values (e.g., `"urgent"`) return 400 Bad Request
- **Backward compatible**: Existing tasks automatically default to `"medium"` priority
- **Sorting**: Use `?sort=priority` query parameter to sort tasks by priority (high→medium→low)

## Testing

```bash
pytest tests/ -v
pytest tests/ --cov=src
```

## Project Structure

```
backend/
├── main.py                  # FastAPI application
├── requirements.txt         # Dependencies
├── .env.example            # Environment template
├── alembic.ini             # Alembic config
├── alembic/                # Database migrations
├── src/
│   ├── database.py         # Database connection
│   ├── models.py           # SQLModel definitions
│   ├── schemas.py          # Pydantic models
│   ├── services.py         # Business logic
│   └── api/tasks.py        # Endpoints
└── tests/                   # Test suite
```

## Features

- **Task Management**: Create, read, update, delete tasks with full ownership enforcement
- **Task Priorities**: Assign priority levels (low/medium/high) to tasks with default to medium
- **Priority Sorting**: Retrieve tasks sorted by priority (high → medium → low) with secondary sort by creation date
- **Input Validation**: Title (1-255 chars), description (max 5000 chars), priority (case-insensitive)
- **Timestamps**: created_at (immutable), updated_at (auto-updated on changes)
- **User Isolation**: Multi-user support with strict ownership enforcement on all operations
- **Logging**: Info-level logging for priority operations (create, update, sort)
- **Error Handling**: Consistent error responses with JSON format and appropriate HTTP status codes
- **Backward Compatibility**: Existing tasks automatically default to "medium" priority

## Authentication

User ID is passed in the URL path. JWT middleware will be added in a future release.

## License

MIT
