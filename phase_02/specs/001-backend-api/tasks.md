---

description: "Task list for Backend API + Database feature implementation"

---

# Tasks: Backend API + Database

**Input**: Design documents from `specs/001-backend-api/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: NOT INCLUDED - Test tasks optional per spec. Focus on implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[ID]**: Sequential task ID (T001, T002, etc.)
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1, US2, US3, etc.) or PHASE label
- Include exact file paths in descriptions

## Path Conventions

- **Backend structure**: `backend/src/`, `backend/tests/` at repository root
- Paths shown below use this structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure - MUST complete first

- [X] T001 Create backend project structure (directory layout, __init__.py files) in `backend/`
- [X] T002 Initialize Python requirements.txt with dependencies: fastapi, uvicorn, sqlmodel, psycopg2-binary, pydantic, python-dotenv, pytest, httpx in `backend/requirements.txt`
- [X] T003 [P] Create `.env.example` template with DATABASE_URL and BETTER_AUTH_SECRET placeholders in `backend/.env.example`
- [X] T004 [P] Create `backend/src/database.py` with SQLModel engine initialization and session factory (DATABASE_URL from environment)
- [X] T005 [P] Create `backend/src/models.py` with Task and User SQLModel class definitions (id, user_id, title, description, status, created_at, updated_at)
- [X] T006 [P] Create `backend/src/schemas.py` with Pydantic request/response models (TaskCreate, TaskUpdate, TaskResponse, ErrorResponse)
- [X] T007 [P] Create `backend/main.py` FastAPI application with database initialization and CORS configuration

**Checkpoint**: Setup complete - backend project structure ready with models and schemas

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 [P] Create database schema and migrations framework in `backend/` (Alembic setup or SQLModel migrations)
- [X] T009 [P] Implement `backend/src/services.py` with TaskService class containing core CRUD business logic:
  - get_tasks_for_user(user_id) - query filtered by user_id
  - get_task_by_id(task_id, user_id) - retrieve single task with ownership check
  - create_task(user_id, title, description) - create and return new task
  - update_task(task_id, user_id, title, description) - update and return updated task
  - delete_task(task_id, user_id) - delete task (ownership checked)
  - mark_complete(task_id, user_id) - mark task complete (ownership checked)
- [X] T010 [P] Create `backend/src/api/__init__.py` (API package initialization)
- [X] T011 Implement request validation and error handling middleware in `backend/src/api/tasks.py` (placeholder structure)
- [X] T012 [P] Create `backend/tests/conftest.py` with pytest fixtures for test database, test client, and test data
- [X] T013 [P] Configure test database connection (separate test database or in-memory for speed)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create a Task (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks via POST endpoint with title and optional description; tasks stored in database with auto-generated IDs and timestamps

**Independent Test**: `POST /api/{user_id}/tasks` creates task, returns 201 with full task metadata, task persisted in database

### Implementation for User Story 1

- [X] T014 [P] [US1] Create request model for task creation in `backend/src/schemas.py` (TaskCreate: title required max 255, description optional max 5000)
- [X] T015 [P] [US1] Create response model in `backend/src/schemas.py` (TaskResponse with all fields: id, user_id, title, description, status, created_at, updated_at)
- [X] T016 [US1] Implement POST endpoint in `backend/src/api/tasks.py`:
  - `@app.post("/api/{user_id}/tasks", status_code=201)`
  - Validate request (title required, max lengths)
  - Call TaskService.create_task(user_id, title, description)
  - Return 201 Created with TaskResponse
  - Return 400 Bad Request for validation errors
- [X] T017 [US1] Implement input validation in TaskCreate schema with Pydantic validators (title: min 1, max 255; description: max 5000)
- [X] T018 [US1] Test POST /api/{user_id}/tasks locally with curl (create task with title + description, verify 201 response includes id and timestamps)

**Checkpoint**: User Story 1 complete - tasks can be created and persisted. Application has basic MVP functionality.

---

## Phase 4: User Story 2 - View All Tasks (Priority: P1)

**Goal**: Users can retrieve all their tasks via GET endpoint; no tasks from other users visible; empty array if no tasks

**Independent Test**: `GET /api/{user_id}/tasks` returns 200 with array of TaskResponse objects; multi-user isolation verified (User A cannot see User B's tasks)

### Implementation for User Story 2

- [X] T019 [P] [US2] Implement GET /api/{user_id}/tasks endpoint in `backend/src/api/tasks.py`:
  - `@app.get("/api/{user_id}/tasks")`
  - Call TaskService.get_tasks_for_user(user_id)
  - Return 200 OK with array of TaskResponse (may be empty [])
  - Database query filters WHERE user_id = authenticated_user_id
- [X] T020 [US2] Add optional status query parameter support to GET endpoint (e.g., `?status=complete`)
- [X] T021 [US2] Test GET /api/{user_id}/tasks locally (verify empty list, add tasks, verify list contains created tasks)
- [X] T022 [US2] Test multi-user isolation: create tasks for User A, verify User B's GET returns empty list (not User A's tasks)

**Checkpoint**: User Story 1 + 2 complete - users can create and list tasks independently

---

## Phase 5: User Story 3 - View a Single Task (Priority: P1)

**Goal**: Users can retrieve individual task details; ownership enforced; 404 if task doesn't exist or belongs to another user

**Independent Test**: `GET /api/{user_id}/tasks/{id}` returns 200 with task details if owned by user; returns 404 if not owned or missing

### Implementation for User Story 3

- [X] T023 [P] [US3] Implement GET /api/{user_id}/tasks/{id} endpoint in `backend/src/api/tasks.py`:
  - `@app.get("/api/{user_id}/tasks/{id}")`
  - Validate task_id is numeric (FR-016)
  - Call TaskService.get_task_by_id(task_id, user_id) with ownership check
  - Return 200 OK with TaskResponse if owned
  - Return 404 Not Found if task doesn't exist or belongs to different user
  - Return 400 Bad Request if task_id format invalid
- [X] T024 [US3] Implement task_id numeric validation in endpoint (before database query)
- [X] T025 [US3] Test GET /api/{user_id}/tasks/{id} locally (verify successful retrieval, ownership check, 404 for missing task)
- [X] T026 [US3] Test ownership enforcement: User A retrieves own task (200), User B attempts same task (404)

**Checkpoint**: User Stories 1, 2, 3 complete - full read-side functionality working. Users can create, list, and view tasks.

---

## Phase 6: User Story 4 - Update a Task (Priority: P2)

**Goal**: Users can update task title and/or description; ownership enforced; updated_at timestamp changes; 404 if not owned

**Independent Test**: `PUT /api/{user_id}/tasks/{id}` updates task, returns 200 with updated task; ownership enforced; old values in database replaced

### Implementation for User Story 4

- [X] T027 [P] [US4] Create TaskUpdate request model in `backend/src/schemas.py` (title and description both optional, but at least one required)
- [X] T028 [US4] Implement PUT /api/{user_id}/tasks/{id} endpoint in `backend/src/api/tasks.py`:
  - `@app.put("/api/{user_id}/tasks/{id}")`
  - Validate task_id is numeric
  - Validate at least one field provided (title or description)
  - Call TaskService.update_task(task_id, user_id, title, description) with ownership check
  - Return 200 OK with updated TaskResponse
  - Return 404 Not Found if task not owned or missing
  - Return 400 Bad Request for validation errors (empty title, length limits)
  - Verify updated_at timestamp is automatically updated by database
- [X] T029 [US4] Implement validation for update: at least one field, title min 1 char if provided, length limits
- [X] T030 [US4] Test PUT /api/{user_id}/tasks/{id} locally (update title, update description, update both, verify 200 with changes, verify updated_at changed, verify created_at unchanged)
- [X] T031 [US4] Test ownership enforcement on update (User A updates own task success, User B attempts same task gets 404)

**Checkpoint**: User Stories 1-4 complete - full CRUD read + update working. Users can modify existing tasks.

---

## Phase 7: User Story 5 - Delete a Task (Priority: P2)

**Goal**: Users can delete tasks; ownership enforced; returns 204 No Content; subsequent GET returns 404

**Independent Test**: `DELETE /api/{user_id}/tasks/{id}` removes task from database; ownership enforced; task no longer retrievable

### Implementation for User Story 5

- [X] T032 [P] [US5] Implement DELETE /api/{user_id}/tasks/{id} endpoint in `backend/src/api/tasks.py`:
  - `@app.delete("/api/{user_id}/tasks/{id}", status_code=204)`
  - Validate task_id is numeric
  - Call TaskService.delete_task(task_id, user_id) with ownership check
  - Return 204 No Content on success (empty response body)
  - Return 404 Not Found if task not owned or missing
  - Return 400 Bad Request if task_id format invalid
- [X] T033 [US5] Verify task is actually removed from database (not soft-deleted)
- [X] T034 [US5] Test DELETE /api/{user_id}/tasks/{id} locally (delete task, verify 204 response, verify subsequent GET returns 404)
- [X] T035 [US5] Test ownership enforcement on delete (User A deletes own task success, User B attempts same task gets 404)

**Checkpoint**: User Stories 1-5 complete - full CRUD operations working. Users can create, read, update, and delete tasks.

---

## Phase 8: User Story 6 - Mark Task as Complete (Priority: P3)

**Goal**: Users can mark tasks complete via PATCH endpoint; status changes from incomplete to complete; idempotent (safe to call multiple times)

**Independent Test**: `PATCH /api/{user_id}/tasks/{id}/complete` changes status to "complete"; ownership enforced; idempotent operation

### Implementation for User Story 6

- [X] T036 [P] [US6] Implement PATCH /api/{user_id}/tasks/{id}/complete endpoint in `backend/src/api/tasks.py`:
  - `@app.patch("/api/{user_id}/tasks/{id}/complete")`
  - Validate task_id is numeric
  - Call TaskService.mark_complete(task_id, user_id) with ownership check
  - Return 200 OK with updated TaskResponse (status = "complete")
  - Return 404 Not Found if task not owned or missing
  - Return 400 Bad Request if task_id format invalid
  - Ensure operation is idempotent (calling multiple times is safe)
- [X] T037 [US6] Verify updated_at timestamp changes when status updated
- [X] T038 [US6] Test PATCH /api/{user_id}/tasks/{id}/complete locally (mark incomplete task complete, verify status change, verify 200 with updated task)
- [X] T039 [US6] Test idempotence: mark complete twice, verify second call returns 200 with status = "complete" (not error)
- [X] T040 [US6] Test ownership enforcement on complete (User A completes own task success, User B attempts same task gets 404)

**Checkpoint**: All 6 user stories complete - full task management API operational. All CRUD operations working, all endpoints functional.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T041 [P] Write integration tests in `backend/tests/test_api.py` for all 6 endpoints:
  - Test creation, listing, retrieval, update, deletion, completion
  - Test validation error cases (400 responses)
  - Test ownership enforcement (404 for cross-user access)
  - Test multi-user isolation
- [X] T042 [P] Write unit tests in `backend/tests/test_services.py` for TaskService methods
- [X] T043 [P] Write model tests in `backend/tests/test_models.py` for validation and constraints
- [X] T044 Verify all HTTP status codes correct (201, 200, 204, 400, 401, 404)
- [X] T045 Verify consistent error response format: `{"error": "message"}`
- [X] T046 Test error cases: validation errors (400), not found (404), database connection failure (500)
- [X] T047 Verify timestamps (created_at immutable, updated_at auto-updated, ISO 8601 format)
- [X] T048 Run full test suite: `pytest tests/ -v --cov=src`
- [X] T049 Verify response times (single task < 200ms, list 100+ tasks < 500ms)
- [X] T050 Document quickstart.md with curl examples for all 6 endpoints
- [X] T051 Run backend against live Neon PostgreSQL database and verify persistence
- [X] T052 Verify OpenAPI documentation auto-generates correctly (http://localhost:8000/docs)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately ✓
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories ✓
- **User Stories (Phase 3-8)**: All depend on Foundational completion ✓
  - All user stories can then proceed in parallel (if staffed) or sequentially
  - User story order: P1 stories first (Phases 3-5), then P2 (Phases 6-7), then P3 (Phase 8)
- **Polish (Phase 9)**: Depends on all user stories being complete ✓

### User Story Dependencies

**CRITICAL**: User stories are INDEPENDENT (can be done in any order after Foundational phase)

- **User Story 1 (Create)** (Phase 3): Depends on Foundational only - No dependencies on other stories
  - Can be completed alone for MVP
  - Enables all other stories (no update/delete/list without create)
- **User Story 2 (List)** (Phase 4): Depends on Foundational only - Independent of US1 (but uses US1 data)
- **User Story 3 (Get)** (Phase 5): Depends on Foundational only - Independent of US1/US2
- **User Story 4 (Update)** (Phase 6): Depends on Foundational only - Can start after US1 created data
- **User Story 5 (Delete)** (Phase 7): Depends on Foundational only - Can start after US1 created data
- **User Story 6 (Complete)** (Phase 8): Depends on Foundational only - Can start after US1 created data

### Parallel Opportunities

**Phase 1 (Setup)**: All [P] tasks can run in parallel
- T003, T004, T005, T006, T007 can all run simultaneously (different files, no dependencies)

**Phase 2 (Foundational)**: All [P] tasks can run in parallel
- T008, T009, T010, T012, T013 can all run simultaneously (different files)

**Phase 3+ (User Stories)**: All 6 user stories can run in PARALLEL once Foundational complete
- User Story 1 tasks (T014-T018): Parallel within story, independent of other stories
- User Story 2 tasks (T019-T022): Parallel within story, can run simultaneously with US1, US3, US4, US5, US6
- User Story 3 tasks (T023-T026): Parallel within story, independent of other stories
- User Story 4 tasks (T027-T031): Parallel within story, independent of other stories
- User Story 5 tasks (T032-T035): Parallel within story, independent of other stories
- User Story 6 tasks (T036-T040): Parallel within story, independent of other stories

**Phase 9 (Polish)**: Testing and documentation tasks (T041-T052) mostly parallel
- T041, T042, T043 (different test files): [P] can run in parallel
- T044-T052: Sequential validation and testing

### Parallel Example: All 6 User Stories Simultaneously

If team has 6+ developers after Foundational phase:

```
Developer 1: User Story 1 (T014-T018) → Create
Developer 2: User Story 2 (T019-T022) → List
Developer 3: User Story 3 (T023-T026) → Get Single
Developer 4: User Story 4 (T027-T031) → Update
Developer 5: User Story 5 (T032-T035) → Delete
Developer 6: User Story 6 (T036-T040) → Complete

All complete simultaneously, then merge and run Phase 9 Polish tests
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T013)
3. Complete Phase 3: User Story 1 (T014-T018)
4. **STOP and VALIDATE**:
   - Run `pytest tests/` for User Story 1 tests
   - Test `POST /api/{user_id}/tasks` manually with curl
   - Verify task created in database
   - Deploy/demo if ready
5. Application has basic MVP: users can create tasks ✓

### Incremental Delivery

```
Phase 1 + 2 + US1 → MVP ready (create tasks)
Add US2 → Users can list tasks
Add US3 → Users can view individual tasks
Add US4 → Users can edit tasks
Add US5 → Users can delete tasks
Add US6 → Users can mark complete
```

Each story adds value; previous stories still work perfectly.

### Parallel Team Strategy (6+ developers)

1. **Sprint 1**: Phase 1 + 2 (whole team, 1-2 days)
2. **Sprint 2**: All 6 user stories in parallel (each dev takes one story, 2-3 days)
3. **Sprint 3**: Phase 9 Polish + integration (1-2 days)

---

## Task Execution Checklist

- [X] Phase 1 Setup: All tasks complete (T001-T007)
- [X] Phase 2 Foundational: All tasks complete (T008-T013) - **GATE: No user stories start until this is done**
- [X] Phase 3 US1: All tasks complete (T014-T018) - MVP functionality
- [X] Phase 4 US2: All tasks complete (T019-T022)
- [X] Phase 5 US3: All tasks complete (T023-T026)
- [X] Phase 6 US4: All tasks complete (T027-T031)
- [X] Phase 7 US5: All tasks complete (T032-T035)
- [X] Phase 8 US6: All tasks complete (T036-T040)
- [X] Phase 9 Polish: All tasks complete (T041-T052)
- [X] All tests passing: `pytest tests/ -v`
- [X] All endpoints verified: curl tests for all 6 endpoints
- [X] Persistence verified: Data survives API restart
- [X] Multi-user isolation verified: User A cannot access User B's tasks

---

## Notes

- [P] tasks = different files, no interdependencies, safe to run in parallel
- [Story] label = maps task to specific user story (US1, US2, etc.)
- Each user story should be independently completable and testable
- Verify tests pass before implementing next story (or run all parallel then test together)
- Stop at Phase 3 checkpoint for MVP validation before continuing to Phase 4+
- Each phase builds on previous; phases cannot be skipped (Setup → Foundational → User Stories)

