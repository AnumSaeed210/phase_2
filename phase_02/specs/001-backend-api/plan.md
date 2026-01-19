# Implementation Plan: Backend API + Database

**Branch**: `001-backend-api` | **Date**: 2025-01-09 | **Spec**: [Backend API + Database](spec.md)
**Input**: Feature specification from `specs/001-backend-api/spec.md`

## Summary

Implement a fully specified backend service that manages user-scoped todo tasks with persistent storage in Neon Serverless PostgreSQL and RESTful API endpoints via Python FastAPI. The backend enforces user ownership at every layer, supports 6 CRUD endpoints, and is designed to accept JWT-based authentication via middleware without requiring code refactoring. This is the foundation for the full-stack Todo application and enables independent frontend and authentication development.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.104+, SQLModel 0.0.14+, psycopg2-binary (PostgreSQL driver), Pydantic v2
**Storage**: Neon Serverless PostgreSQL (DATABASE_URL environment variable)
**Testing**: pytest 7.4+, httpx (async HTTP client for FastAPI testing)
**Target Platform**: Linux/Unix server (cloud deployment via uvicorn ASGI server)
**Project Type**: Backend web API service (FastAPI application)
**Performance Goals**: Sub-200ms response times for single-task operations, sub-500ms for listing 100+ tasks
**Constraints**: Stateless authentication (no session storage), all queries scoped to authenticated user_id, persistent storage required
**Scale/Scope**: Multi-user SaaS application (unlimited users, unlimited tasks per user, extensible schema)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Spec-First Development
✅ **PASS**: Specification (spec.md) fully defines all API endpoints, user ownership enforcement, error codes, and validation rules. No implementation details in spec; all decisions captured before code generation.

### Agentic Workflow Integrity
✅ **PASS**: This plan is the input to `/sp.tasks` and `/sp.implement` phases. Code will be generated entirely via Claude Code agents (Backend Architect, Neon Postgres Expert) with no manual coding permitted.

### Security by Design
✅ **PASS**: User ownership enforced at API layer (FR-008) and database layer (WHERE user_id = $authenticated_user_id). JWT-based authentication assumed available via middleware. No hardcoded user IDs; all operations scoped to authenticated context.

### User Isolation (Data Ownership)
✅ **PASS**: Task model includes user_id foreign key. Every endpoint validates user ownership before returning/modifying data. FR-008 explicitly requires ownership check; database queries filtered by user_id.

### Deterministic Behavior
✅ **PASS**: All endpoints, status codes, error messages, and validation rules fully specified. No "reasonable assumptions" in implementation; every detail comes from spec.

### Reproducibility
✅ **PASS**: Same spec and plan will always produce equivalent API behavior. No non-deterministic decisions; technology stack fixed (Python 3.11, FastAPI, SQLModel, PostgreSQL).

**Gate Status**: ✅ **GATE PASSED** - Plan respects all constitutional principles. Spec is deterministic. Technology stack is fixed and justified. User isolation is architected at every layer.

## Project Structure

### Documentation (this feature)

```text
specs/001-backend-api/
├── spec.md                  # Feature specification (COMPLETE)
├── plan.md                  # This file
├── research.md              # Phase 0 research (generated below)
├── data-model.md            # Phase 1 data model & entities (generated below)
├── quickstart.md            # Phase 1 quickstart guide (generated below)
├── contracts/               # Phase 1 API contracts (generated below)
│   ├── openapi.yaml         # OpenAPI 3.1 schema
│   └── schemas.json         # Request/response models
└── checklists/
    └── requirements.md      # Quality validation (COMPLETE)
```

### Source Code Structure

```text
backend/
├── main.py                  # FastAPI application entry point
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── src/
│   ├── __init__.py
│   ├── database.py          # Database connection and session setup
│   ├── models.py            # SQLModel Task and User models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── services.py          # Business logic (task CRUD operations)
│   └── api/
│       ├── __init__.py
│       └── tasks.py         # Task endpoints (GET, POST, PUT, DELETE, PATCH)
└── tests/
    ├── __init__.py
    ├── conftest.py          # Pytest fixtures and test configuration
    ├── test_models.py       # Unit tests for models and validation
    ├── test_services.py     # Unit tests for business logic
    └── test_api.py          # Integration tests for API endpoints
```

**Structure Decision**: Backend-only structure (no frontend in this spec). All code under `backend/` directory. This enables parallel frontend development and clear separation of concerns.

## Phase 0: Research & Clarifications

**Status**: All technical details specified; no critical unknowns requiring research.

### Key Decisions (No Research Needed)

#### Task ID Format
- **Decision**: Integer auto-incrementing primary key
- **Rationale**: Standard SQL pattern, compatible with Neon PostgreSQL SERIAL type, matches URL structure `{id}` (numeric), efficient for indexing and foreign keys
- **Spec Reference**: FR-012 defines metadata; task ID should be numeric (inferred from FR-016: "ensure task ID is numeric")

#### User ID Field Type
- **Decision**: String (UUID or varchar) - store as provided from authenticated context
- **Rationale**: JWT tokens may use UUID, email, or custom format depending on Better Auth configuration. Database stores as-is without transformation. Spec assumption: "user_id is a string or UUID from JWT token"
- **Spec Reference**: Assumption documented in spec.md: "user_id is stored as provided without transformation"

#### Status Enum Values
- **Decision**: Enum type in database; "incomplete" and "complete" strings in API responses
- **Rationale**: Simple binary state, matches spec (US6: "change status from incomplete to complete"). PostgreSQL ENUM type enforces values at DB level. SQLModel uses Python enum with string values
- **Spec Reference**: Task metadata spec includes "status (enum: incomplete | complete)"

#### Timestamp Format
- **Decision**: UTC timestamps stored as TIMESTAMP WITH TIME ZONE in PostgreSQL. API returns ISO 8601 format (e.g., "2025-01-09T12:34:56Z")
- **Rationale**: Spec assumption: "Timestamps stored in UTC. API returns them in ISO 8601 format"
- **Spec Reference**: FR-012 includes created_at and updated_at; SC-009 requires auto-generation and preservation

#### Error Response Format
- **Decision**: Consistent JSON error format: `{"error": "Human-readable message"}`
- **Rationale**: Simple, readable, matches FR-014 requirement
- **Spec Reference**: FR-014: "System MUST return error responses in consistent JSON format: `{"error": \"Human-readable error message\"}`"

#### Input Validation Library
- **Decision**: Pydantic v2 (via FastAPI) for request validation; SQLModel for database model validation
- **Rationale**: FastAPI integrates Pydantic; provides automatic 400 Bad Request responses; SQLModel extends Pydantic. No additional validation library needed
- **Spec Reference**: FR-007 validation rules (title required, max 255; description max 5000)

### Identified Design Decisions (Completed in Phase 1 Below)

No research tasks required. All technical decisions are captured in Phase 1 design (data model, API contracts, database schema).

---

## Phase 1: Design & Contracts

### 1. Data Model (data-model.md)

#### User Model
```plaintext
Entity: User
Purpose: Represents an authenticated user; minimal data for task ownership reference
Attributes:
  - id (String, PK): From Better Auth JWT token (UUID or custom format)
  - email (String, unique): User email from Better Auth
Relationships:
  - has_many Tasks (via task.user_id foreign key)
Notes:
  - User model is NOT created by this backend; defined by Better Auth
  - This backend only reads user_id from authenticated request context
  - No user creation/deletion in this spec (handled by auth service in Spec 2)
```

#### Task Model
```plaintext
Entity: Task
Purpose: Represents a single to-do item owned by a user
Attributes:
  - id (Integer, PK): Auto-incrementing primary key, SERIAL type
  - user_id (String, FK -> User.id): Owner of the task (from authenticated context)
  - title (String, max 255): Task description; required
  - description (String, max 5000, nullable): Extended task details
  - status (Enum[incomplete|complete]): Task completion state; default: "incomplete"
  - created_at (Timestamp, UTC): Auto-set on creation, never updated
  - updated_at (Timestamp, UTC): Auto-set on creation, updated on any modification
Relationships:
  - belongs_to User (via user_id foreign key)
Indexes:
  - PRIMARY KEY (id)
  - FOREIGN KEY (user_id) REFERENCES users(id)
  - Composite index (user_id, created_at DESC) for efficient "list tasks by user" queries
Constraints:
  - NOT NULL: id, user_id, title, status, created_at, updated_at
  - UNIQUE constraint on: None (multiple tasks can have same title)
  - CHECK constraints: title length > 0 AND <= 255; description length <= 5000
Validation Rules (from FR-007):
  - title: required, string, max 255 characters
  - description: optional, string, max 5000 characters
  - status: enum (incomplete | complete), default: "incomplete"
```

#### Database Schema (SQL DDL - Informational)
```sql
-- Generated by SQLModel migrations (not manually written for this spec)
-- This schema will be created by Alembic migrations

CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description VARCHAR(5000),
    status VARCHAR CHECK (status IN ('incomplete', 'complete')) DEFAULT 'incomplete',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_user_id_created_at ON tasks(user_id, created_at DESC);
```

### 2. API Contracts (contracts/openapi.yaml)

#### Endpoint Summary
```plaintext
GET    /api/{user_id}/tasks              → List all tasks for user
POST   /api/{user_id}/tasks              → Create new task for user
GET    /api/{user_id}/tasks/{id}         → Get single task (ownership verified)
PUT    /api/{user_id}/tasks/{id}         → Update task (ownership verified)
DELETE /api/{user_id}/tasks/{id}         → Delete task (ownership verified)
PATCH  /api/{user_id}/tasks/{id}/complete → Mark task complete (ownership verified)
```

#### Request/Response Models

**CreateTaskRequest** (POST /api/{user_id}/tasks)
```plaintext
{
  "title": "string (required, 1-255 chars)",
  "description": "string (optional, max 5000 chars)"
}
```

**TaskResponse** (all GET endpoints, POST create, PUT update)
```plaintext
{
  "id": "integer",
  "user_id": "string",
  "title": "string",
  "description": "string | null",
  "status": "incomplete | complete",
  "created_at": "ISO8601 timestamp",
  "updated_at": "ISO8601 timestamp"
}
```

**TaskListResponse** (GET /api/{user_id}/tasks)
```plaintext
[
  TaskResponse,
  TaskResponse,
  ...
]
(empty array [] if no tasks)
```

**UpdateTaskRequest** (PUT /api/{user_id}/tasks/{id})
```plaintext
{
  "title": "string (optional, 1-255 chars if provided)",
  "description": "string (optional, max 5000 chars if provided)"
}
(at least one field must be provided)
```

**ErrorResponse** (all error cases)
```plaintext
{
  "error": "Human-readable error message"
}
```

#### HTTP Status Codes & Behaviors

**CREATE (POST /api/{user_id}/tasks)**
- 201 Created: Task created successfully, full TaskResponse returned
- 400 Bad Request: Title is required, title > 255 chars, description > 5000 chars
- 401 Unauthorized: (middleware will enforce)

**LIST (GET /api/{user_id}/tasks)**
- 200 OK: Array of TaskResponse (may be empty [])
- 400 Bad Request: Invalid status query parameter (if provided)
- 401 Unauthorized: (middleware will enforce)

**GET SINGLE (GET /api/{user_id}/tasks/{id})**
- 200 OK: TaskResponse with full task data
- 400 Bad Request: Invalid task ID format (non-numeric)
- 404 Not Found: Task doesn't exist OR belongs to different user
- 401 Unauthorized: (middleware will enforce)

**UPDATE (PUT /api/{user_id}/tasks/{id})**
- 200 OK: Updated TaskResponse with new updated_at timestamp
- 400 Bad Request: Empty title, title > 255 chars, description > 5000 chars, no fields provided
- 404 Not Found: Task doesn't exist OR belongs to different user
- 401 Unauthorized: (middleware will enforce)

**DELETE (DELETE /api/{user_id}/tasks/{id})**
- 204 No Content: Task deleted successfully, no response body
- 400 Bad Request: Invalid task ID format (non-numeric)
- 404 Not Found: Task doesn't exist OR belongs to different user
- 401 Unauthorized: (middleware will enforce)

**COMPLETE (PATCH /api/{user_id}/tasks/{id}/complete)**
- 200 OK: Updated TaskResponse with status = "complete"
- 400 Bad Request: Invalid task ID format (non-numeric)
- 404 Not Found: Task doesn't exist OR belongs to different user
- 401 Unauthorized: (middleware will enforce)

### 3. Implementation Architecture

#### Authentication Layer (Boundary)
```plaintext
Purpose: Inject authenticated user_id into every request
Pattern: FastAPI dependency injection with custom Depends()
Approach:
  - Expect JWT token in Authorization: Bearer <token> header
  - Extract user_id from JWT payload (BETTER_AUTH_SECRET used to verify)
  - Inject user_id into request context (kwargs or request state)
  - Return 401 if token missing or invalid

NOT IMPLEMENTED IN THIS SPEC:
  - JWT token verification logic
  - Better Auth integration
  - User signup/login endpoints

READY FOR AUTH MIDDLEWARE (Spec 2):
  - All endpoints expect user_id to be available
  - Clean dependency injection point for auth middleware
  - No changes needed when auth is added
```

#### Ownership Enforcement Layer
```plaintext
Purpose: Verify every task belongs to authenticated user before operation
Pattern: Service-layer validation + query-layer filtering
Implementation:
  1. Extract authenticated user_id from request context
  2. For GET operations: Query only tasks WHERE user_id = authenticated_user_id
  3. For GET single/PUT/DELETE/PATCH: Retrieve task, validate task.user_id == authenticated_user_id, return 404 if mismatch
  4. For POST: Auto-associate task with authenticated user_id
Enforcement Points:
  - API layer: Receive user_id from URL; match against authenticated context
  - Service layer: All queries filtered by user_id
  - Database layer: Composite index (user_id, created_at) ensures efficient scoping
```

#### Error Handling
```plaintext
Pattern: Consistent error responses with descriptive messages
Validation Errors (400):
  - Title is required
  - Title must be between 1 and 255 characters
  - Description must be 5000 characters or less
Resource Not Found (404):
  - Task not found (if task doesn't exist)
  - Task not found (if task exists but belongs to different user - same message for security)
Ownership/Authorization (404):
  - Treated as "not found" to avoid leaking information (user can't see that they don't own resource)
Database Errors (500):
  - "Internal server error" - don't expose database details
```

#### Testing Strategy
```plaintext
Unit Tests (test_models.py):
  - Task model validation (title required, length constraints)
  - Status enum enforcement
  - Timestamp handling

Unit Tests (test_services.py):
  - CRUD operations with mocked database
  - Ownership validation logic
  - Error cases

Integration Tests (test_api.py):
  - All 6 endpoints with real database (test database)
  - Happy path scenarios for each endpoint
  - Error cases (invalid input, not found, ownership violations)
  - Multi-user isolation (user A cannot see/modify user B's tasks)
  - Timestamp validation (created_at immutable, updated_at changes)
```

---

## Phase 1 Deliverables (Generated Below)

### research.md
All Phase 0 decisions documented in "Phase 0: Research & Clarifications" section above. No research tasks required; all technical decisions specified.

### data-model.md
Comprehensive entity definitions, database schema, validation rules, and relationships documented above in "Phase 1: Design & Contracts" > "1. Data Model" section.

### contracts/openapi.yaml
Full OpenAPI 3.1 specification generated below with all endpoints, request/response models, and status codes.

### quickstart.md
Getting started guide generated below with environment setup, project initialization, running the backend, and testing endpoints.

---

## Project Dependencies

### Python Requirements
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

### Environment Variables
```
DATABASE_URL=postgresql://user:password@host:port/database
BETTER_AUTH_SECRET=<shared-secret-from-env>
```

---

## Complexity Tracking

No violations of Constitution Check. Implementation follows all principles:
- Spec-first: All endpoints defined in spec; no design decisions during coding
- Agentic: Code generated via Claude Code agents only
- Security: User ownership enforced at every layer
- User isolation: Queries filtered by authenticated user_id
- Deterministic: All behavior defined in spec
- Reproducible: Same plan + spec = identical behavior

---

## Next Steps

1. **Phase 0 Research Complete**: All technical decisions finalized; proceed to Phase 1
2. **Phase 1 Design Complete**: Data model, API contracts, and architecture documented
3. **Phase 2**: Run `/sp.tasks` to break this plan into ordered implementation tasks
4. **Phase 3**: Run `/sp.implement` to generate backend code via Backend Architect and Neon Postgres Expert agents
5. **Phase 4**: Test backend independently against spec; manual testing validates all endpoints

---

## Success Criteria Mapping

| Success Criterion | Implementation Approach |
|---|---|
| SC-001: All 6 endpoints implemented | Plan details all 6 endpoints (GET list, POST create, GET single, PUT update, DELETE, PATCH complete) |
| SC-002: 100% user ownership enforcement | Ownership validation in service layer + query filtering; every endpoint verifies user_id |
| SC-003: Correct HTTP status codes | Plan specifies all status codes (201, 200, 204, 400, 401, 404, 500) for each endpoint |
| SC-004: Data persists in PostgreSQL | SQLModel + Neon connection; database schema includes CREATE TABLE with TIMESTAMP fields |
| SC-005: Multi-user operation | Composite index (user_id, created_at); queries filtered by user_id prevent cross-user data leakage |
| SC-006: Input validation rejects invalid data | Pydantic request models enforce max lengths; FastAPI returns 400 automatically |
| SC-007: Ready for JWT middleware | Dependency injection point for auth; user_id injected, not hardcoded; no refactoring needed |
| SC-008: All metadata correctly stored/returned | TaskResponse schema includes all fields; updated_at auto-updated on modification |
| SC-009: Timestamps auto-generated and preserved | Database schema: created_at immutable, updated_at auto-updated; SQLModel handles this |
| SC-010: Response times < 200-500ms | Composite index on (user_id, created_at) optimizes list queries; SERIAL primary key efficient |

