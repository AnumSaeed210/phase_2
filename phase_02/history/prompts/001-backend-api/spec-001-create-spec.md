---
id: spec-001-backend-api
stage: spec
title: "Create Backend API + Database Specification"
date: 2025-01-09
feature: 001-backend-api
status: completed
---

# Specification: Backend API + Database

## Prompt

```text
Todo Full-Stack Web Application — Spec 1: Backend API + Database

Target audience:
- Backend engineers
- API reviewers
- Claude Code agent responsible for implementation

Focus:
- Core task management domain logic
- RESTful API behavior and contracts
- Persistent data storage
- User-level data isolation enforced at the backend

Success criteria:
- All task-related CRUD operations exposed via RESTful API endpoints
- API behavior is fully deterministic and spec-defined
- All database queries are scoped to the authenticated user
- Task ownership is enforced on every operation (read/write/update/delete)
- API returns correct HTTP status codes for success and error cases
- Backend is ready to be secured by JWT middleware without refactoring
- Schema supports multi-user operation with persistent storage

Constraints:
- Backend framework: Python FastAPI
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Data persistence required (no in-memory or mock storage)
- RESTful endpoints must follow the defined URL structure:
  - GET    /api/{user_id}/tasks
  - POST   /api/{user_id}/tasks
  - GET    /api/{user_id}/tasks/{id}
  - PUT    /api/{user_id}/tasks/{id}
  - DELETE /api/{user_id}/tasks/{id}
  - PATCH  /api/{user_id}/tasks/{id}/complete
- All endpoints must assume an authenticated user context
- No frontend dependencies
- No authentication logic implementation in this spec

Not building:
- Frontend UI or client-side logic
- Better Auth configuration or JWT verification middleware
- User signup, login, or session handling
- Role-based access control beyond user ownership
- Admin or shared task features
- Background jobs, notifications, or analytics
```

## Response Summary

Created comprehensive **Backend API + Database specification (001-backend-api)** with full API contract, user ownership enforcement, and persistent storage design.

### Key Deliverables

**Feature Structure**:
- Branch: `001-backend-api`
- Spec file: `specs/001-backend-api/spec.md` (560 lines)
- Checklist: `specs/001-backend-api/checklists/requirements.md` (validation passed)

**Specification Contents**:

1. **User Scenarios (6 prioritized stories)**:
   - US1 (P1): Create a Task - POST /api/{user_id}/tasks with title/description
   - US2 (P1): View All Tasks - GET /api/{user_id}/tasks (user scoped)
   - US3 (P1): View Single Task - GET /api/{user_id}/tasks/{id} (ownership verified)
   - US4 (P2): Update Task - PUT /api/{user_id}/tasks/{id} (ownership verified)
   - US5 (P2): Delete Task - DELETE /api/{user_id}/tasks/{id} (ownership verified)
   - US6 (P3): Mark Complete - PATCH /api/{user_id}/tasks/{id}/complete (status transition)
   - Each story includes: rationale, independent test, 3-4 acceptance scenarios

2. **Functional Requirements (16 FRs)**:
   - API endpoints: FR-001 through FR-006 (all 6 RESTful endpoints specified)
   - Input validation: FR-007 (title required max 255, description max 5000)
   - User ownership enforcement: FR-008 (user_id from context matched against task.user_id)
   - Persistence: FR-009 (Neon PostgreSQL, persistent storage)
   - ORM/Framework: FR-010 (SQLModel), FR-011 (FastAPI)
   - Task metadata: FR-012 (id, user_id, title, description, status, created_at, updated_at)
   - HTTP status codes: FR-013 (201, 200, 204, 400, 401, 404, 500)
   - Error format: FR-014 (consistent JSON {"error": "message"})
   - Query parameters: FR-015 (status filter for future frontend)
   - Task ID validation: FR-016 (numeric validation before DB query)

3. **Key Entities**:
   - **Task**: id, user_id (FK), title, description (nullable), status (incomplete|complete), created_at, updated_at
   - **User**: id (from JWT), email (defined by Better Auth, FK relationship)

4. **Success Criteria (10 measurable outcomes)**:
   - SC-001: All 6 endpoints implemented and testable
   - SC-002: 100% user ownership enforcement verified via contract tests
   - SC-003: Correct HTTP status codes for all cases
   - SC-004: Data persists in PostgreSQL across API restarts
   - SC-005: Multi-user operation verified (each user sees only their tasks)
   - SC-006: Input validation rejects invalid data with 400 errors
   - SC-007: Backend ready for JWT middleware without refactoring
   - SC-008: All task metadata correctly returned and stored
   - SC-009: Default status set to "incomplete", timestamps auto-generated
   - SC-010: API response times under 200-500ms

5. **Assumptions & Dependencies**:
   - Authentication context (user_id) assumed available via middleware
   - DATABASE_URL environment variable configured
   - Database schema (Task table) created before API startup
   - Timestamps stored in UTC, returned in ISO 8601
   - Empty list returns `[]` not null
   - Last-write-wins for concurrent updates (no optimistic locking)
   - Cascading deletes handled separately or by database

6. **Edge Cases (5 identified)**:
   - Null/undefined title → 400 Bad Request
   - Invalid task ID format → 400 or 404
   - Concurrent updates → Last write wins
   - Stale task view → 404 on next GET (acceptable)
   - Database connection failure → 500 with logging

**Quality Validation**: ✅ **PASSED**
- All mandatory sections completed
- No [NEEDS CLARIFICATION] markers
- 6 prioritized user stories with independent tests
- 16 concrete functional requirements
- 10 measurable success criteria
- Scope tightly bounded (backend API + database only)
- Checklist: 22/22 items passing

### Specification Highlights

**API Contract Definition**:
- 6 endpoints with exact URL structure, HTTP methods, request/response formats
- Every operation includes explicit HTTP status codes for success and error cases
- 22 total acceptance scenarios covering happy path and error cases

**User Ownership Enforcement**:
- FR-008: "user_id from authenticated context must match task.user_id before returning/modifying"
- Enforced on: GET list (filter), GET single (403/404), PUT (403/404), DELETE (403/404), PATCH (403/404)
- Clear rule: "Requests for records owned by other users return 404 or 403, never 200"

**Persistent Storage Requirement**:
- FR-009: "Neon Serverless PostgreSQL with persistent storage"
- SC-004: "Data persists and survives API restart"
- No in-memory storage, file-based storage, or mock data

**Ready for Authentication Layer**:
- SC-007: "Backend ready for JWT middleware without refactoring"
- Assumption: "API assumes authenticated user context is available (via JWT middleware)"
- All endpoints expect user_id to be injected by auth layer; no changes needed when middleware added

### Architectural Decisions

1. **User ID in URL Path**: `/api/{user_id}/tasks` - Makes ownership explicit in API contract
2. **6 Separate Endpoints**: Rather than `/tasks?action=complete`, explicit PATCH endpoint for clarity
3. **Status Enum**: "incomplete" | "complete" (simple binary, extensible for future statuses)
4. **Idempotent Complete**: PATCH /tasks/{id}/complete idempotent (safe to retry)
5. **Consistent Error Format**: All errors return `{"error": "message"}` JSON
6. **No Pagination Specified**: List endpoint assumes reasonable task counts; pagination can be added later without breaking contract

### Files Created

1. `specs/001-backend-api/spec.md` - Full specification (560 lines)
2. `specs/001-backend-api/checklists/requirements.md` - Quality validation checklist (PASSED)

### Next Steps

1. Run `/sp.plan` to generate implementation plan:
   - Detail database schema (Task table DDL)
   - Outline API endpoint implementations
   - Define middleware integration points
   - Establish project structure (FastAPI app layout)

2. Plan will perform Constitution Check:
   - Verify spec-first discipline met
   - Confirm tech stack constraints respected
   - Validate security/ownership architecture
   - Identify any spec gaps before code generation

3. Then `/sp.tasks` to break plan into ordered implementation tasks
4. Finally `/sp.implement` to generate backend code via Backend Architect and Neon Postgres Expert agents

---

## Context References

- **Specification File**: `specs/001-backend-api/spec.md`
- **Quality Checklist**: `specs/001-backend-api/checklists/requirements.md`
- **Constitution**: `.specify/memory/constitution.md` (v1.1.0)
- **Project Guidance**: `CLAUDE.md`

## Stage

`spec` - Backend API and database specification for core task management CRUD operations
