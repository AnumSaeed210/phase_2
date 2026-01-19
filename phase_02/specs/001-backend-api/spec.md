# Feature Specification: Backend API + Database

**Feature Branch**: `001-backend-api`
**Created**: 2025-01-09
**Status**: Draft
**Input**: User description: "Todo Full-Stack Web Application — Spec 1: Backend API + Database"

## User Scenarios & Testing

### User Story 1 - Create a Task (Priority: P1)

A backend service receives a POST request from an authenticated user to create a new task with a title and optional description. The service validates the input, stores the task in the database associated with the user's ID, and returns the created task with a generated ID and metadata (created_at, updated_at).

**Why this priority**: Creating tasks is the core MVP feature. Without the ability to create tasks, the entire application has no purpose. This is the foundation for all other task operations.

**Independent Test**: Can be fully tested by calling `POST /api/{user_id}/tasks` with valid task data and verifying:
- Task is created in the database
- Response includes task ID, title, description, status (default: incomplete), and timestamps
- Task is correctly associated with the authenticated user

**Acceptance Scenarios**:

1. **Given** a user is authenticated, **When** POST `/api/{user_id}/tasks` with `{"title": "Buy groceries", "description": "Milk, eggs, bread"}`, **Then** return 201 Created with task ID, timestamps, and status = "incomplete"
2. **Given** a user is authenticated, **When** POST `/api/{user_id}/tasks` with only `{"title": "Review PR"}`, **Then** return 201 Created with description = null and status = "incomplete"
3. **Given** a user is authenticated, **When** POST `/api/{user_id}/tasks` with empty title, **Then** return 400 Bad Request with error message "Title is required"
4. **Given** a user is authenticated, **When** POST `/api/{user_id}/tasks` with title longer than 255 characters, **Then** return 400 Bad Request with error message "Title must be 255 characters or less"

---

### User Story 2 - View All Tasks (Priority: P1)

A user calls the API to list all their tasks. The backend queries the database filtered by the authenticated user's ID and returns a list of tasks with complete metadata (ID, title, description, status, created_at, updated_at).

**Why this priority**: Users must be able to see their tasks to verify creation and plan work. Without listing, the application is not functional.

**Independent Test**: Can be fully tested by calling `GET /api/{user_id}/tasks` and verifying:
- All tasks belonging to the user are returned
- No tasks from other users are visible
- Response includes all task fields (ID, title, description, status, timestamps)
- Empty list is returned if user has no tasks

**Acceptance Scenarios**:

1. **Given** a user has 3 tasks, **When** GET `/api/{user_id}/tasks`, **Then** return 200 OK with array of 3 tasks, each with complete metadata
2. **Given** a user has 0 tasks, **When** GET `/api/{user_id}/tasks`, **Then** return 200 OK with empty array `[]`
3. **Given** User A and User B both exist, **When** User A calls GET `/api/{user_id_a}/tasks`, **Then** return only User A's tasks, not User B's
4. **Given** a user calls the API without proper authentication, **When** GET `/api/{user_id}/tasks`, **Then** return 401 Unauthorized (middleware will enforce this)

---

### User Story 3 - View a Single Task (Priority: P1)

A user calls the API to retrieve details of a specific task by its ID. The backend verifies the task is owned by the authenticated user, retrieves it from the database, and returns the full task object.

**Why this priority**: Users need to view individual task details (especially important when tasks have long descriptions that might be truncated in list view).

**Independent Test**: Can be fully tested by calling `GET /api/{user_id}/tasks/{id}` and verifying:
- Correct task is returned with all metadata
- User ownership is enforced (user cannot view another user's task)
- 404 is returned if task does not exist or belongs to another user

**Acceptance Scenarios**:

1. **Given** a task belongs to User A, **When** User A calls GET `/api/{user_id_a}/tasks/{task_id}`, **Then** return 200 OK with full task object
2. **Given** a task belongs to User A, **When** User B calls GET `/api/{user_id_b}/tasks/{task_id}`, **Then** return 404 Not Found (user ownership enforced)
3. **Given** a task ID does not exist, **When** GET `/api/{user_id}/tasks/{invalid_id}`, **Then** return 404 Not Found with error message "Task not found"

---

### User Story 4 - Update a Task (Priority: P2)

A user calls the API to update an existing task (title, description, or both). The backend validates the updated data, verifies the user owns the task, updates the database record, and returns the updated task.

**Why this priority**: Users frequently need to refine task details. High priority but not critical for MVP if only read + delete are supported.

**Independent Test**: Can be fully tested by calling `PUT /api/{user_id}/tasks/{id}` with updated fields and verifying:
- Task is updated in the database
- Updated timestamp is changed
- User ownership is verified before update
- 404 is returned if task doesn't exist or belongs to another user

**Acceptance Scenarios**:

1. **Given** User A owns a task with title "Old Title", **When** PUT `/api/{user_id_a}/tasks/{id}` with `{"title": "New Title"}`, **Then** return 200 OK with updated task
2. **Given** a task belongs to User A, **When** User B attempts PUT `/api/{user_id_b}/tasks/{id}`, **Then** return 404 Not Found
3. **Given** a task exists, **When** PUT `/api/{user_id}/tasks/{id}` with empty title, **Then** return 400 Bad Request with error "Title cannot be empty"
4. **Given** a task exists, **When** PUT `/api/{user_id}/tasks/{id}` with description longer than 5000 characters, **Then** return 400 Bad Request with error "Description must be 5000 characters or less"

---

### User Story 5 - Delete a Task (Priority: P2)

A user calls the API to delete a task. The backend verifies user ownership, removes the task from the database, and returns a 204 No Content response to confirm successful deletion.

**Why this priority**: Users need to remove completed or erroneous tasks. High priority but not critical for initial MVP if all 5 basic features are required.

**Independent Test**: Can be fully tested by calling `DELETE /api/{user_id}/tasks/{id}` and verifying:
- Task is removed from the database
- Subsequent GET request returns 404 for the deleted task
- User ownership is verified before deletion
- 404 is returned if task doesn't exist or belongs to another user

**Acceptance Scenarios**:

1. **Given** User A owns a task, **When** User A calls DELETE `/api/{user_id_a}/tasks/{id}`, **Then** return 204 No Content and task is deleted
2. **Given** User A owns a task, **When** User B attempts DELETE `/api/{user_id_b}/tasks/{id}`, **Then** return 404 Not Found and task remains in database
3. **Given** a task does not exist, **When** DELETE `/api/{user_id}/tasks/{invalid_id}`, **Then** return 404 Not Found with error "Task not found"
4. **Given** a task is deleted, **When** GET `/api/{user_id}/tasks/{id}` is called, **Then** return 404 Not Found

---

### User Story 6 - Mark Task as Complete (Priority: P3)

A user calls the API to change a task's status from "incomplete" to "complete". The backend verifies ownership, updates the task status and updated_at timestamp, and returns the updated task.

**Why this priority**: Marking completion is valuable for task tracking but can be achieved via PUT /tasks/{id} in early MVP. Separate endpoint provides cleaner API surface.

**Independent Test**: Can be fully tested by calling `PATCH /api/{user_id}/tasks/{id}/complete` and verifying:
- Task status changes to "complete"
- Updated_at timestamp is changed
- User ownership is verified before update
- Task cannot be marked complete if already complete (idempotent)

**Acceptance Scenarios**:

1. **Given** a user has an incomplete task, **When** PATCH `/api/{user_id}/tasks/{id}/complete`, **Then** return 200 OK with task status = "complete"
2. **Given** a task is already complete, **When** PATCH `/api/{user_id}/tasks/{id}/complete`, **Then** return 200 OK (idempotent) with status = "complete"
3. **Given** a task belongs to another user, **When** PATCH `/api/{user_id}/tasks/{id}/complete`, **Then** return 404 Not Found

---

### Edge Cases

- What happens when a user attempts to create a task with null/undefined title? Return 400 Bad Request with "Title is required"
- What happens when a user attempts to update a task with invalid task ID (e.g., non-numeric string)? Return 400 Bad Request or 404 Not Found as appropriate
- What happens when two concurrent requests attempt to update the same task? Last write wins (no optimistic locking for this spec)
- What happens when a task is deleted while a user is viewing it? Subsequent GET returns 404 Not Found (acceptable stale state)
- What happens when database connection fails? Return 500 Internal Server Error with appropriate error logging (auth layer must provide user context)

## Requirements

### Functional Requirements

- **FR-001**: System MUST expose a RESTful API endpoint GET `/api/{user_id}/tasks` that returns all tasks belonging to the authenticated user
- **FR-002**: System MUST expose a RESTful API endpoint POST `/api/{user_id}/tasks` that creates a new task with title (required), description (optional), and returns 201 Created with task ID and timestamps
- **FR-003**: System MUST expose a RESTful API endpoint GET `/api/{user_id}/tasks/{id}` that returns a single task only if owned by the authenticated user
- **FR-004**: System MUST expose a RESTful API endpoint PUT `/api/{user_id}/tasks/{id}` that updates task title and/or description only if owned by the authenticated user
- **FR-005**: System MUST expose a RESTful API endpoint DELETE `/api/{user_id}/tasks/{id}` that removes a task only if owned by the authenticated user and returns 204 No Content
- **FR-006**: System MUST expose a RESTful API endpoint PATCH `/api/{user_id}/tasks/{id}/complete` that marks a task as complete only if owned by the authenticated user
- **FR-007**: System MUST validate all input: title is required, max 255 characters; description is optional, max 5000 characters; both must be strings
- **FR-008**: System MUST enforce user ownership on every task operation: user_id from the authenticated context must match task.user_id in the database before returning/modifying the record
- **FR-009**: System MUST store all tasks in Neon Serverless PostgreSQL with persistent storage and support multi-user operation
- **FR-010**: System MUST use SQLModel as the ORM to define Task model and execute database queries
- **FR-011**: System MUST use Python FastAPI to implement all REST endpoints
- **FR-012**: System MUST track task metadata: id (primary key), user_id (foreign key to user), title, description (nullable), status (enum: "incomplete" or "complete"), created_at (UTC), updated_at (UTC)
- **FR-013**: System MUST return appropriate HTTP status codes: 201 Created, 200 OK, 204 No Content, 400 Bad Request (validation error), 401 Unauthorized (missing/invalid auth), 404 Not Found (resource not owned or doesn't exist), 500 Internal Server Error
- **FR-014**: System MUST return error responses in consistent JSON format: `{"error": "Human-readable error message"}`
- **FR-015**: System MUST support task status filter in query parameters (e.g., GET `/api/{user_id}/tasks?status=complete`) for future frontend use
- **FR-016**: System MUST include task ID validation: ensure task ID is numeric and within valid range before querying database

### Key Entities

- **Task**: Represents a to-do item owned by a user. Attributes: id (UUID or integer), user_id (foreign key), title (string, max 255), description (string, max 5000, nullable), status (enum: incomplete | complete), created_at (timestamp), updated_at (timestamp). Relationships: belongs_to User (enforced at API layer via user ownership checks)
- **User**: Represents an authenticated user (defined by Better Auth, not in this spec's responsibility to create). Attributes: id (from JWT token), email. Relationship: has_many Tasks (via user_id foreign key)

## Success Criteria

### Measurable Outcomes

- **SC-001**: All 6 task CRUD endpoints (GET list, POST create, GET single, PUT update, DELETE, PATCH complete) are implemented and fully testable without frontend code
- **SC-002**: API enforces user ownership on 100% of task operations: every endpoint verified to reject access to tasks not owned by the authenticated user (measured by API contract tests)
- **SC-003**: API returns correct HTTP status codes for success (201, 200, 204) and error cases (400 for validation, 401 for auth, 404 for not found): verified via contract tests
- **SC-004**: Task data persists in Neon PostgreSQL and survives API restart (verified by creating a task, restarting server, and confirming task still exists via GET)
- **SC-005**: Database schema supports multi-user operation: confirmed by creating tasks for 2+ users simultaneously and verifying each user sees only their own tasks
- **SC-006**: API input validation rejects invalid data: titles longer than 255 chars, descriptions longer than 5000 chars, empty titles all return 400 Bad Request with clear error messages
- **SC-007**: Backend is ready for JWT middleware without refactoring: all endpoints assume authenticated user_id is available in request context; no refactoring needed when middleware is added
- **SC-008**: All task metadata (id, user_id, title, description, status, created_at, updated_at) is correctly returned in API responses and stored in database
- **SC-009**: Task creation sets default status to "incomplete" and auto-generates timestamps; subsequent updates preserve created_at and update updated_at only
- **SC-010**: API response times are under 200ms for single-task operations and under 500ms for listing 100+ tasks (measured on typical Neon connection)

## Assumptions

- **Authentication Context**: The API assumes an authenticated user context is available in each request (e.g., via JWT middleware). This spec does NOT implement authentication; the middleware that extracts user_id from JWT tokens will be added in a separate auth spec.
- **User ID Type**: user_id is a string or UUID from the JWT token (exact format will be determined by Better Auth integration). Database will store it as provided without transformation.
- **Database URL**: DATABASE_URL environment variable is set and points to a valid Neon PostgreSQL database. API assumes the database schema (Task table with user_id, title, etc.) is created before API startup (via migrations).
- **Timestamps**: created_at and updated_at are stored in UTC. API returns them in ISO 8601 format (e.g., "2025-01-09T12:34:56Z").
- **Empty Responses**: When no tasks exist, GET `/api/{user_id}/tasks` returns `[]` (empty array), not null.
- **Concurrent Writes**: No optimistic locking or versioning is implemented. Last write wins if two users attempt simultaneous updates to the same task (unlikely given user ownership, but included for clarity).
- **Cascading Deletes**: When a user account is deleted (out of scope for this spec), their tasks are assumed to be deleted via database cascade rules or a separate cleanup process.

## Notes & Dependencies

- **No Frontend Dependencies**: This spec defines backend behavior only. Frontend (Next.js) will consume these endpoints; backend does NOT depend on frontend code.
- **No Authentication Implementation**: Better Auth JWT middleware is NOT implemented in this spec. The assumption is that middleware will inject authenticated user_id into request context. API endpoints assume the user_id is already available.
- **No Authorization Beyond Ownership**: This spec enforces user ownership of tasks only. No role-based access control, admin access, or shared tasks are supported.
- **Schema Migration**: Database schema (Task table creation) is assumed to be handled separately (via SQLModel migrations, Alembic, or manual DDL). This spec focuses on API behavior, not schema setup.

