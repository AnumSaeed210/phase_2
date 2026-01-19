# Research: Backend API + Database

**Purpose**: Phase 0 research for Backend API + Database specification
**Date**: 2025-01-09
**Status**: Complete - All technical decisions finalized; no critical unknowns

## Summary

All technical decisions for the Backend API + Database implementation are fully specified in `spec.md` and `plan.md`. No research tasks were required because the specification provides deterministic requirements for every component: API endpoints, data model, error handling, user ownership enforcement, and technology stack constraints.

This document records the architectural and technical decisions made during planning phase, with rationale and alternatives considered.

---

## Technical Decisions

### 1. Task ID Format: Auto-Incrementing Integer

**Decision**: Use SERIAL (auto-incrementing integer) as primary key for Task records

**Rationale**:
- Standard SQL pattern, well-supported by all databases including Neon PostgreSQL
- Numeric type matches API URL structure: `/api/{user_id}/tasks/{id}` expects numeric ID
- Specification FR-016 requires: "task ID validation: ensure task ID is numeric"
- Efficient for indexing, foreign keys, and query performance
- Simpler than UUID for small to medium scale applications

**Alternatives Considered**:
- **UUID (v4)**: Would be globally unique across systems; useful if tasks need to be shared across databases. Rejected because: spec doesn't require global uniqueness, adds bytes to every foreign key reference, slower than SERIAL for local database
- **String ID**: Could support custom IDs; rejected because numeric is simpler and spec assumes numeric validation

**Specification Reference**: FR-016 "ensure task ID is numeric and within valid range before querying database"

---

### 2. User ID Type: String/Varchar (Flexible for JWT Integration)

**Decision**: Store user_id as VARCHAR without transformation; accept any format from authenticated context

**Rationale**:
- Better Auth JWT tokens may use UUID, email, or custom format; backend shouldn't assume specific format
- Flexible for different auth providers (OAuth2, SAML, custom)
- Specification assumption states: "user_id is a string or UUID from the JWT token. Database will store it as provided without transformation"
- No validation or transformation needed at application layer; auth layer responsible for correct user_id

**Alternatives Considered**:
- **Enforce UUID format**: Would require validation and transformation. Rejected because spec explicitly avoids this; adds unnecessary coupling to auth provider
- **Use email as user_id**: More human-readable but not always available; couples domain logic to auth mechanism
- **Surrogate key (separate numeric ID for users)**: Would require User table in this backend; spec indicates User is defined by Better Auth, not this backend

**Specification Reference**: Assumption: "user_id is a string or UUID from JWT token. Database will store it as provided without transformation"

---

### 3. Task Status: Binary Enum (incomplete | complete)

**Decision**: Use PostgreSQL ENUM type with two values: "incomplete" and "complete"

**Rationale**:
- Specification defines status as enum with two values: "incomplete" | "complete"
- Binary state is appropriate for MVP todo application
- PostgreSQL ENUM enforces valid values at database layer
- SQLModel Python enum maps cleanly to database ENUM
- Extensible if future statuses needed (archived, delegated, etc.)

**Alternatives Considered**:
- **Boolean (is_complete)**: Simpler but less semantic; harder to extend to 3+ states later
- **String with CHECK constraint**: Would work but less efficient than ENUM type; ENUM checks constraints at database level
- **Numeric status codes (0=incomplete, 1=complete)**: Less readable than semantic strings

**Specification Reference**: Task metadata spec: "status (enum: incomplete | complete)"

---

### 4. Timestamps: UTC TIMESTAMP WITH TIME ZONE

**Decision**: Store created_at and updated_at as TIMESTAMP WITH TIME ZONE in PostgreSQL; return ISO 8601 format in API responses

**Rationale**:
- UTC is standard for system timestamps; avoids timezone conversion issues
- TIMESTAMP WITH TIME ZONE in PostgreSQL stores both value and timezone offset
- API returns ISO 8601 (e.g., "2025-01-09T12:34:56Z") per specification assumption
- created_at is immutable (set on creation, never updated)
- updated_at is auto-updated on any modification
- Specification assumes: "Timestamps stored in UTC. API returns them in ISO 8601 format"

**Alternatives Considered**:
- **TIMESTAMP WITHOUT TIME ZONE**: Would require explicit timezone handling in application; UTC WITH TIME ZONE is clearer
- **Unix timestamp (epoch seconds)**: Machine-readable but less human-friendly for debugging; ISO 8601 better for API

**Specification Reference**: Assumption: "Timestamps stored in UTC. API returns them in ISO 8601 format (e.g., '2025-01-09T12:34:56Z')"

---

### 5. Error Response Format: Consistent JSON Structure

**Decision**: All error responses use consistent format: `{"error": "Human-readable message"}`

**Rationale**:
- Simple, easy to parse for frontend
- Specification requirement FR-014: "System MUST return error responses in consistent JSON format: `{"error": \"Human-readable error message\"}`"
- Single field makes response structure predictable
- Human-readable messages help with debugging and user communication

**Alternatives Considered**:
- **Detailed error objects**: Could include error_code, details, stack_trace. Rejected because spec specifies simple format only
- **Error arrays**: Could handle multiple validation errors. Rejected because simple format sufficient for initial MVP

**Specification Reference**: FR-014 "System MUST return error responses in consistent JSON format"

---

### 6. Ownership Enforcement: Service + Query Layer

**Decision**: Enforce user ownership at both service layer (application logic) and query layer (database filters)

**Rationale**:
- **Service layer**: Application code validates task.user_id == authenticated_user_id before returning/modifying
- **Query layer**: All database queries include WHERE user_id = $authenticated_user_id to prevent accidental cross-user data access
- Defense in depth: both layers must agree task belongs to user
- Specification FR-008: "System MUST enforce user ownership on every task operation: user_id from the authenticated context must match task.user_id"

**Implementation Pattern**:
```
1. Extract authenticated user_id from request context (dependency injection)
2. For GET list: query WHERE user_id = authenticated_user_id
3. For GET single/PUT/DELETE/PATCH:
   a. Query task by ID
   b. Verify task.user_id == authenticated_user_id
   c. Return 404 if ownership check fails (same error as "not found")
4. For POST: Auto-associate new task with authenticated_user_id
```

**Specification Reference**: FR-008 "System MUST enforce user ownership on every task operation"

---

### 7. Database Connection: Neon Serverless PostgreSQL

**Decision**: Use Neon Serverless PostgreSQL as specified; connection via DATABASE_URL environment variable

**Rationale**:
- Specification constraint: "Database: Neon Serverless PostgreSQL"
- Serverless model matches scalability needs of SaaS application
- Connection pooling handled by Neon; backend uses psycopg2 driver
- DATABASE_URL environment variable configures connection without hardcoding credentials

**Configuration**:
```
DATABASE_URL=postgresql://user:password@host.neon.tech:5432/database?sslmode=require
(provided externally; never committed to version control)
```

**Specification Reference**: FR-009 "System MUST store all tasks in Neon Serverless PostgreSQL with persistent storage"

---

### 8. ORM: SQLModel (Pydantic + SQLAlchemy)

**Decision**: Use SQLModel for both database models and API request/response validation

**Rationale**:
- Specification requirement: "ORM: SQLModel"
- SQLModel combines SQLAlchemy models with Pydantic validation
- Single model definition covers database schema + API schema
- Automatic OpenAPI documentation generation via FastAPI
- Type hints throughout improve code clarity and IDE support

**Model Pattern**:
```python
from sqlmodel import SQLModel, Field

class Task(SQLModel, table=True):
    # Both database schema and API response definition
    id: int | None = Field(default=None, primary_key=True)
    user_id: str
    title: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    status: str = "incomplete"
    created_at: datetime
    updated_at: datetime
```

**Specification Reference**: FR-010 "System MUST use SQLModel as the ORM"

---

### 9. Web Framework: Python FastAPI

**Decision**: Use FastAPI as specified for REST API implementation

**Rationale**:
- Specification requirement: "Backend framework: Python FastAPI"
- Modern, high-performance async framework
- Automatic OpenAPI/Swagger documentation
- Built-in request validation (Pydantic)
- Dependency injection for middleware and auth
- Excellent for RESTful APIs

**Endpoint Structure**:
```python
@app.post("/api/{user_id}/tasks", status_code=201)
async def create_task(user_id: str, task: TaskCreate):
    # Implementation
    pass
```

**Specification Reference**: FR-011 "System MUST use Python FastAPI to implement all REST endpoints"

---

### 10. Input Validation: Pydantic v2 + FastAPI

**Decision**: Use Pydantic v2 (integrated with FastAPI) for all input validation

**Rationale**:
- FastAPI automatically uses Pydantic for request body validation
- Returns 400 Bad Request with validation errors automatically
- Specification FR-007 requirements:
  - Title: required, max 255 characters
  - Description: optional, max 5000 characters
- Pydantic v2 field validators provide clear error messages

**Validation Rules** (mapped to Pydantic):
```python
from pydantic import Field

class TaskCreate(SQLModel):
    title: str = Field(..., min_length=1, max_length=255)  # required
    description: str | None = Field(None, max_length=5000)  # optional
```

**Specification Reference**: FR-007 "System MUST validate all input: title is required, max 255 characters; description is optional, max 5000 characters"

---

### 11. Testing Framework: pytest + httpx

**Decision**: Use pytest for unit/integration tests; httpx for async HTTP client testing

**Rationale**:
- pytest is standard Python testing framework
- httpx supports async/await syntax needed for FastAPI testing
- Test database (separate PostgreSQL database) for integration tests
- Fixtures for setup/teardown and test data

**Test Categories**:
- **Unit**: Model validation, service logic
- **Integration**: Full API endpoint testing with real database
- **Contract**: Verify API responses match specification

**Specification Reference**: SC testing requirements across all success criteria

---

## Architecture Decisions

### Authentication Layer Boundary

**Decision**: API expects authenticated user_id to be injected via dependency injection; no JWT verification in this backend

**Rationale**:
- Specification explicitly states: "No authentication logic implementation in this spec"
- Specification assumption: "API assumes an authenticated user context is available in each request (e.g., via JWT middleware)"
- Enables clean separation: Auth spec (Spec 2) adds middleware without modifying task endpoints
- Specification SC-007: "Backend is ready for JWT verification middleware without refactoring"

**Integration Pattern**:
```python
from fastapi import Depends

async def get_authenticated_user_id(request: Request) -> str:
    # Will be implemented by auth middleware in Spec 2
    # For now, accept user_id from path or header injection
    user_id = request.state.user_id  # set by middleware
    if not user_id:
        raise HTTPException(status_code=401)
    return user_id

@app.get("/api/{user_id}/tasks")
async def list_tasks(user_id: str, authenticated_user_id: str = Depends(get_authenticated_user_id)):
    # Verify user_id matches authenticated_user_id
    pass
```

**Specification Reference**: SC-007 "Backend is ready for JWT middleware without refactoring"

---

## Database Design Decisions

### Composite Index Strategy

**Decision**: Create composite index on (user_id, created_at DESC) for efficient task listing queries

**Rationale**:
- Most common query: "Get all tasks for a user ordered by creation time"
- Composite index allows database to satisfy filter + sort in single index scan
- DESC sort improves common UX pattern: newest tasks first
- Reduces database load; improves response time (SC-010)

**Alternative**: Separate indexes on user_id and created_at. Would work but less efficient for combined queries.

**Specification Reference**: SC-010 "Response times under 200ms for single-task operations and under 500ms for listing 100+ tasks"

### Foreign Key Constraint

**Decision**: Create foreign key constraint: tasks.user_id REFERENCES users(id)

**Rationale**:
- Enforces referential integrity: task can only exist if user exists
- Database-level validation prevents orphaned tasks
- Important for long-term data consistency as users are created/deleted (future spec)

**Note**: User table is defined by Better Auth (not in this backend). Migration must create users table or handle this constraint appropriately.

---

## No Research Unknowns

All technical decisions are fully specified in `spec.md` and documented above. Phase 0 research is complete without requiring external research tasks. The specification provides sufficient detail to proceed directly to Phase 1 design and Phase 2 task breakdown.

**Decision Confidence**: High - All constraints from specification mapped to concrete technology choices.

