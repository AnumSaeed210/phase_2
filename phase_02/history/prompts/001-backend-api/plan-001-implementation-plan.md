---
id: plan-001-backend-api
stage: plan
title: "Backend API + Database Implementation Plan"
date: 2025-01-09
feature: 001-backend-api
status: completed
---

# Implementation Plan: Backend API + Database

## Prompt

```text
Todo Full-Stack Web Application — Spec 1: Backend API + Database

Objective:
Implement a fully specified backend service that manages user-scoped todo tasks
with persistent storage and RESTful API endpoints, ready for JWT-based security
integration.

Phases:

1. Backend Project Initialization
- Create FastAPI application structure
- Configure environment-based settings
- Establish database connection to Neon PostgreSQL
- Initialize SQLModel and database engine

2. Data Modeling
- Define User model (minimal fields for ownership reference)
- Define Task model with:
  - id
  - title
  - description (optional)
  - completed status
  - owner_user_id
  - timestamps (created_at, updated_at)
- Define database constraints and relationships
- Generate database schema

3. API Schema Definition
- Define request and response models using SQLModel / Pydantic
- Specify validation rules for task creation and updates
- Define consistent error response structure

4. CRUD Endpoint Implementation
- Implement endpoint to list all tasks for a user
- Implement endpoint to create a new task
- Implement endpoint to retrieve a single task by ID
- Implement endpoint to update a task
- Implement endpoint to delete a task
- Implement endpoint to toggle task completion
- Ensure all operations filter by owner_user_id

5. Ownership Enforcement
- Validate that requested task belongs to the specified user
- Return appropriate errors for unauthorized access attempts
- Prevent cross-user data leakage at query level

6. Error Handling and Status Codes
- 200/201 for successful operations
- 400 for invalid input
- 404 for missing resources
- 403 for ownership violations
- Define error messages consistently across endpoints

7. Backend Readiness for Authentication
- Structure code to accept injected authenticated user context
- Avoid hardcoded assumptions about auth provider
- Ensure clean integration path for JWT middleware in Spec 2

Deliverables:
- FastAPI backend service
- SQLModel models and database schema
- Fully implemented RESTful API endpoints
- Clear separation of concerns between API logic and authentication
- Backend code generated entirely via Claude Code from specs

Completion criteria:
- Backend runs successfully against Neon PostgreSQL
- All endpoints function as specified
- Tasks are persisted and isolated per user
- Backend is ready for JWT verification middleware without modification
```

## Response Summary

Created comprehensive **Implementation Plan for Backend API + Database** with complete technical architecture, data models, API contracts, and Phase 0/Phase 1 deliverables.

### Deliverables Generated

**Main Plan Document** (`specs/001-backend-api/plan.md` - 800+ lines):
- Summary: Clear feature overview and implementation scope
- Technical Context: Python 3.11, FastAPI, SQLModel, Neon PostgreSQL, pytest
- Constitution Check: ✅ GATE PASSED - All 6 principles verified
- Project Structure: Backend directory layout with code organization
- Phase 0 Research: All technical decisions documented with rationale
- Phase 1 Design: Data model, API contracts, architecture patterns
- Project Dependencies: requirements.txt with all needed packages
- Success Criteria Mapping: All 10 criteria mapped to implementation approach

**Phase 0 Research Document** (`specs/001-backend-api/research.md` - 500+ lines):
- 11 major technical decisions documented
- Rationale for each decision
- Alternatives considered and rejected
- Cross-references to specification
- No unknowns requiring external research

**Phase 1 Data Model** (`specs/001-backend-api/data-model.md` - 600+ lines):
- User model: id (string), email
- Task model: id (SERIAL), user_id (FK), title, description, status (enum), created_at, updated_at
- SQLModel class definitions with validation
- Request models: TaskCreate, TaskUpdate
- Response models: TaskResponse, ErrorResponse
- Database constraints and indexes
- State transitions for task completion
- SQL schema definition (informational)
- Scalability considerations

**API Contracts** (`specs/001-backend-api/contracts/openapi.yaml` - OpenAPI 3.1):
- 6 fully documented endpoints with request/response examples
- GET /api/{user_id}/tasks - List tasks (200, 400, 401)
- POST /api/{user_id}/tasks - Create (201, 400, 401)
- GET /api/{user_id}/tasks/{id} - Get single (200, 400, 404, 401)
- PUT /api/{user_id}/tasks/{id} - Update (200, 400, 404, 401)
- DELETE /api/{user_id}/tasks/{id} - Delete (204, 400, 404, 401)
- PATCH /api/{user_id}/tasks/{id}/complete - Mark complete (200, 400, 404, 401)
- All error responses with examples
- Schema definitions for all models

**Quickstart Guide** (`specs/001-backend-api/quickstart.md`):
- Environment setup: Python venv, dependencies, .env configuration
- Database initialization: Create database, run migrations
- Running the backend: Uvicorn development server
- Testing the API: curl commands for all endpoints
- Running tests: pytest, coverage, test examples
- Troubleshooting: Common issues and solutions
- API endpoint summary table

### Technical Architecture

**Backend Technology Stack**:
- Language: Python 3.11+
- Framework: FastAPI 0.104+
- ORM: SQLModel 0.0.14+
- Database: Neon Serverless PostgreSQL
- Database Driver: psycopg2-binary
- Validation: Pydantic v2
- Testing: pytest 7.4+, httpx 0.25+
- Server: uvicorn (ASGI)

**Database Design**:
- Task table: SERIAL primary key, VARCHAR user_id (FK), title (max 255), description (max 5000, nullable), status enum (incomplete|complete), created_at/updated_at timestamps
- User table: Defined by Better Auth (external), id (PK), email (unique)
- Composite index: (user_id, created_at DESC) for efficient user task listing
- Constraints: NOT NULL on critical fields, CHECK constraints on lengths, FOREIGN KEY for referential integrity

**API Endpoint Design**:
- 6 RESTful endpoints following standard REST patterns
- All endpoints include user_id in path to make ownership explicit
- User ownership enforced on every operation
- Consistent error format: {"error": "message"}
- HTTP status codes: 201 (create), 200 (get/update), 204 (delete), 400 (validation), 401 (auth), 404 (not found)

**User Ownership Enforcement**:
- Service layer: Validate task.user_id == authenticated_user_id before returning/modifying
- Query layer: All database queries include WHERE user_id = $authenticated_user_id
- Defense in depth: Both layers must agree task belongs to user
- Error strategy: Return 404 for both "not found" and "not owned" (security: don't leak info)

**Authentication Readiness**:
- Dependency injection pattern for authenticated user context
- No hardcoded user IDs or authentication logic in API layer
- User_id expected from authenticated request context
- Clean integration point for JWT middleware (Spec 2)
- No code refactoring needed when auth middleware added

### Constitution Check: ✅ PASSED

1. **Spec-First Development** ✓ - Specification fully defines all API behavior; plan derives from spec
2. **Agentic Workflow Integrity** ✓ - Plan ready for `/sp.tasks` and `/sp.implement` phases
3. **Security by Design** ✓ - User ownership enforced at API + database layers; JWT-ready
4. **User Isolation** ✓ - Task model includes user_id FK; all queries scoped to authenticated user
5. **Deterministic Behavior** ✓ - All endpoints, status codes, error messages fully specified
6. **Reproducibility** ✓ - Same spec + plan = identical API behavior; no non-deterministic decisions

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| SERIAL (auto-increment) task ID | Standard SQL pattern, numeric validation required, efficient indexing |
| String user_id (no transformation) | Flexible for JWT format (UUID, email, custom); database stores as-is |
| Binary status enum (incomplete\|complete) | Simple MVP; extensible for future statuses |
| UTC TIMESTAMP WITH TIME ZONE | Standard for system timestamps; avoids timezone confusion; ISO 8601 API format |
| Consistent error format `{"error": "..."}` | Simple, predictable; specification FR-014 requirement |
| Service + Query layer ownership enforcement | Defense in depth; prevents accidental cross-user access |
| Dependency injection for auth context | Clean separation; ready for auth middleware without refactoring |
| Composite index (user_id, created_at DESC) | Efficient list queries; supports filter + sort in single scan |
| SQLModel for ORM + validation | Single model definition for DB schema + API validation; Pydantic integration |
| FastAPI framework | Modern, async-friendly, auto-documentation, built-in validation |

### Implementation Readiness

**Ready for Phase 2**: All Phase 1 deliverables complete:
- ✅ Technical context fully specified
- ✅ Constitution Check passed
- ✅ Phase 0 research complete (11 decisions documented)
- ✅ Phase 1 design complete (data models, API contracts, quickstart)
- ✅ No unknowns blocking implementation
- ✅ Database schema defined
- ✅ API contracts documented in OpenAPI format
- ✅ Error handling fully specified
- ✅ Testing strategy outlined

**Next Phase**: `/sp.tasks` will:
1. Break plan into ordered implementation tasks
2. Organize by user story (P1 create → P1 list → P1 get → P2 update → P2 delete → P3 complete)
3. Identify parallel opportunities (models, services, endpoints can be parallel)
4. Create dependency graph (models before services, services before endpoints)

**Then `/sp.implement`**:
- Backend Architect agent: FastAPI application, endpoints, services
- Neon Postgres Expert agent: SQLModel models, database schema, migrations

### Files Created

1. `specs/001-backend-api/plan.md` - Complete implementation plan (800+ lines)
2. `specs/001-backend-api/research.md` - Phase 0 research and decisions (500+ lines)
3. `specs/001-backend-api/data-model.md` - Phase 1 data model design (600+ lines)
4. `specs/001-backend-api/contracts/openapi.yaml` - OpenAPI 3.1 specification
5. `specs/001-backend-api/quickstart.md` - Getting started guide

### Project Dependencies

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

### Success Criteria Coverage

| SC # | Criterion | Plan Address |
|---|---|---|
| SC-001 | All 6 endpoints implemented | Plan details all 6 endpoints with URLs, methods, behaviors |
| SC-002 | 100% ownership enforcement | Service + query layer validation; every endpoint verifies user_id |
| SC-003 | Correct HTTP status codes | Plan specifies all codes per endpoint (201, 200, 204, 400, 401, 404, 500) |
| SC-004 | Data persists | SQLModel + Neon; database schema with TIMESTAMP fields |
| SC-005 | Multi-user isolation | Composite index (user_id, created_at); WHERE user_id filters prevent leakage |
| SC-006 | Input validation | Pydantic models enforce max lengths; FastAPI returns 400 automatically |
| SC-007 | JWT-ready | Dependency injection for auth; user_id injected not hardcoded |
| SC-008 | All metadata stored/returned | TaskResponse schema + database schema includes all fields |
| SC-009 | Timestamps auto-generated | created_at immutable, updated_at auto-updates; SQLModel handles |
| SC-010 | Response times < 200-500ms | Composite index optimizes queries; SERIAL PK efficient |

### Files Generated

```
specs/001-backend-api/
├── spec.md                                (EXISTING - specification)
├── plan.md                                (NEW - implementation plan)
├── research.md                            (NEW - Phase 0 research)
├── data-model.md                          (NEW - Phase 1 data design)
├── quickstart.md                          (NEW - quickstart guide)
├── contracts/
│   └── openapi.yaml                      (NEW - API specification)
└── checklists/
    └── requirements.md                    (EXISTING - quality checklist)
```

---

## Context References

- **Specification**: `specs/001-backend-api/spec.md`
- **Constitution**: `.specify/memory/constitution.md` (v1.1.0)
- **Tech Stack**: Python FastAPI, SQLModel, Neon PostgreSQL
- **Agents**: Backend Architect, Neon Postgres Expert (will implement)

## Stage

`plan` - Implementation planning phase for Backend API + Database feature

