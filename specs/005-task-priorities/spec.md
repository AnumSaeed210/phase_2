# Feature Specification: Task Priorities

**Feature Branch**: `005-task-priorities`
**Created**: 2026-01-17
**Status**: Draft
**Input**: User description: "Todo Full-Stack Web Application — Spec 5: Task Priorities"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Set Task Priority on Creation (Priority: P1)

A user creates a new task and can immediately assign a priority level (Low, Medium, or High). If no priority is specified, the system defaults to Medium priority. The task is created with the selected priority stored in the database alongside other task metadata.

**Why this priority**: Task priority is fundamental to the feature. P1 because users expect to assign priority when creating tasks, and this is the primary way tasks gain priority metadata. Without this, the feature has no value.

**Independent Test**: Can be fully tested by calling the task creation endpoint with a priority field and verifying:
- Task is created with the specified priority (Low/Medium/High)
- Task is created with Medium priority when no priority is specified
- Priority is persisted in the database and retrievable via GET
- Only valid priority values (Low, Medium, High) are accepted

**Acceptance Scenarios**:

1. **Given** a user is creating a new task, **When** they POST `/api/{user_id}/tasks` with `{"title": "Deploy to production", "priority": "high"}`, **Then** return 201 Created with task priority = "high"
2. **Given** a user creates a task without specifying priority, **When** POST `/api/{user_id}/tasks` with `{"title": "Review code"}`, **Then** return 201 Created with default priority = "medium"
3. **Given** a user submits an invalid priority value, **When** POST `/api/{user_id}/tasks` with `{"title": "Task", "priority": "urgent"}`, **Then** return 400 Bad Request with error "Priority must be 'low', 'medium', or 'high'"
4. **Given** a task is created with priority "high", **When** GET `/api/{user_id}/tasks/{id}`, **Then** response includes `"priority": "high"`

---

### User Story 2 - Update Task Priority (Priority: P1)

A user can modify the priority of an existing task at any time. The backend validates the new priority value, updates the task, and returns the updated task with the new priority and updated timestamp.

**Why this priority**: Users frequently need to reprioritize tasks as circumstances change. P1 because priority management is core to the feature and enables dynamic task organization.

**Independent Test**: Can be fully tested by calling the task update endpoint with priority field and verifying:
- Task priority is updated to the new value
- Invalid priority values are rejected with 400 Bad Request
- User ownership is verified before update
- Updated_at timestamp is changed but created_at remains unchanged
- 404 is returned if task doesn't exist or belongs to another user

**Acceptance Scenarios**:

1. **Given** a task with priority "low", **When** PUT `/api/{user_id}/tasks/{id}` with `{"priority": "high"}`, **Then** return 200 OK with updated priority = "high"
2. **Given** a task exists, **When** PUT `/api/{user_id}/tasks/{id}` with `{"priority": "invalid"}`, **Then** return 400 Bad Request with error "Priority must be 'low', 'medium', or 'high'"
3. **Given** a task belongs to User A, **When** User B attempts PUT `/api/{user_id_b}/tasks/{id}`, **Then** return 404 Not Found
4. **Given** a task priority is updated, **When** GET `/api/{user_id}/tasks/{id}`, **Then** updated_at timestamp is newer but created_at unchanged

---

### User Story 3 - Retrieve Tasks Sorted by Priority (Priority: P1)

A user can request their task list sorted by priority level in descending order (High → Medium → Low). The backend returns tasks ordered by priority, with tasks of the same priority ordered by creation date (newest first). This helps users focus on their most important work.

**Why this priority**: Without sortable priorities, the priority metadata is decorative. P1 because sorting by priority is the core user-facing benefit of this feature—it enables better task organization and workflow focus.

**Independent Test**: Can be fully tested by calling the task list endpoint with sort parameter and verifying:
- Tasks are returned in order: High priority first, then Medium, then Low
- Tasks with the same priority are ordered by created_at (newest first)
- Sorting is deterministic and consistent across multiple requests
- Works correctly when user has 0 tasks, 1 task, or many tasks with mixed priorities

**Acceptance Scenarios**:

1. **Given** a user has 3 tasks with priorities [low, high, medium], **When** GET `/api/{user_id}/tasks?sort=priority`, **Then** return tasks in order [high, medium, low]
2. **Given** a user has 2 tasks both with priority "high" (created 2 minutes apart), **When** GET `/api/{user_id}/tasks?sort=priority`, **Then** return tasks ordered by created_at with newest first
3. **Given** a user has 0 tasks, **When** GET `/api/{user_id}/tasks?sort=priority`, **Then** return 200 OK with empty array `[]`
4. **Given** sorting by priority is requested, **When** GET `/api/{user_id}/tasks?sort=priority`, **Then** response includes all task fields including priority for each task

---

### User Story 4 - Visual Priority Indicators in Task UI (Priority: P1)

Tasks displayed in the frontend UI show visual indicators for their priority level. High priority tasks display a red/urgent color indicator, Medium priority displays a neutral color, and Low priority displays a muted color. Icons or badge labels accompany color indicators for accessibility and clarity.

**Why this priority**: Visual differentiation is the primary user benefit of priorities in the UI. P1 because users need to quickly scan their task list and identify what matters most at a glance.

**Independent Test**: Can be fully tested by signing in, viewing the task list, and verifying:
- High priority tasks display a distinct red/urgent visual indicator
- Medium priority tasks display a neutral indicator
- Low priority tasks display a muted/subtle indicator
- Visual indicators are clear and accessible (color + icon/text, not just color)
- Indicators are present in both list view and task detail view
- Visual styling matches the design system from Spec 4 (colors, spacing, typography)

**Acceptance Scenarios**:

1. **Given** a task with priority "high" is displayed in the list, **When** user views the task list, **Then** the task shows a red indicator with "High" label or high-priority icon
2. **Given** a task with priority "medium" is displayed, **When** user views the task, **Then** it shows a neutral gray/slate indicator
3. **Given** a task with priority "low" is displayed, **When** user views the task, **Then** it shows a muted/subtle indicator
4. **Given** a user has a mix of priority levels, **When** user scans the task list, **Then** they can quickly identify high-priority items without reading the text

---

### User Story 5 - Priority Selection UI in Task Forms (Priority: P2)

When creating or editing a task, the user interface provides a clear way to select priority (Low, Medium, High). The selection interface is intuitive, accessible, and clearly shows the current priority. Creating tasks defaults to Medium priority if the user doesn't explicitly select.

**Why this priority**: P2 because while the priority selection UI enhances usability, the core backend functionality (P1) can work without a polished UI. However, without good UI affordances, users won't easily discover or use the feature.

**Independent Test**: Can be fully tested by opening task creation and edit forms and verifying:
- Priority selection control is present and visible
- All three options (Low, Medium, High) are available to select
- Creating a task without selecting priority defaults to Medium
- Editing a task shows the current priority as pre-selected
- Selection is keyboard accessible (no mouse required)
- Visual style matches the design system (Spec 4)

**Acceptance Scenarios**:

1. **Given** a user opens the task creation form, **When** they look for priority options, **Then** they see a selection control with Low/Medium/High options
2. **Given** a user creates a task without selecting priority, **When** the task is saved, **Then** priority defaults to "medium" without requiring explicit selection
3. **Given** a user opens the edit form for an existing task with priority "high", **When** the form loads, **Then** "high" is pre-selected in the priority control
4. **Given** a user is on a mobile device, **When** they interact with the priority selection, **Then** the control is appropriately sized and touchable (responsive design)

---

### Edge Cases

- What happens when a user tries to set priority on a task that has already been deleted? Return 404 Not Found (task not found)
- What happens if two concurrent requests update the same task's priority simultaneously? Last write wins (acceptable for this feature's scope)
- What happens when filtering/sorting by priority and the user has tasks with null/undefined priority? Treat as "medium" priority (consistent default)
- What happens when the database connection fails during priority update? Return 500 Internal Server Error with appropriate logging
- What happens if a user accidentally sends a lowercase priority value (e.g., "HIGH" instead of "high")? Accept it case-insensitively and normalize to lowercase in storage
- What happens when displaying priority on a small mobile screen? Priority indicator is compact and doesn't break layout (responsive design requirement)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST add a `priority` field to the Task model with allowed values: "low", "medium", "high" (stored as enum or constrained string)
- **FR-002**: System MUST set default priority to "medium" when a task is created without an explicit priority value
- **FR-003**: System MUST expose a POST `/api/{user_id}/tasks` endpoint that accepts an optional `priority` field and validates it against allowed values (low/medium/high)
- **FR-004**: System MUST expose a PUT `/api/{user_id}/tasks/{id}` endpoint that accepts an optional `priority` field for updating task priority
- **FR-005**: System MUST validate all priority values: only "low", "medium", "high" are accepted; return 400 Bad Request if invalid
- **FR-006**: System MUST expose a GET `/api/{user_id}/tasks` endpoint that accepts a `sort=priority` query parameter to return tasks ordered by priority (high → medium → low)
- **FR-007**: System MUST ensure user ownership is enforced on priority updates: users can only update priority on tasks they own
- **FR-008**: System MUST persist priority in the database and return it in all task API responses (GET single task, GET list, POST create, PUT update)
- **FR-009**: System MUST support case-insensitive priority input (accept "HIGH", "High", "high") and normalize to lowercase for storage
- **FR-010**: Frontend MUST display visual priority indicators for all tasks in the task list view (color + icon/label, not just color alone)
- **FR-011**: Frontend MUST display visual priority indicators in task detail/edit views
- **FR-012**: Frontend MUST provide a priority selection control in the task creation form (dropdown, radio buttons, or similar) with Low/Medium/High options
- **FR-013**: Frontend MUST provide a priority selection control in the task edit form with current priority pre-selected
- **FR-014**: Frontend MUST use color-coded visual indicators that match the design system: High = red/urgent color, Medium = neutral/slate color, Low = muted/subtle color
- **FR-015**: Frontend MUST include text labels or icons alongside color indicators for accessibility (not relying on color alone)
- **FR-016**: System MUST maintain backward compatibility: existing tasks created before this feature are assigned default priority "medium"
- **FR-017**: System MUST include priority in all task responses: `{"id": 1, "title": "...", "priority": "high", ...}`
- **FR-018**: System MUST support sorting tasks by priority in descending order (high → medium → low) with consistent secondary sort by created_at (newest first)

### Key Entities

- **Task**: Extended to include priority field. Attributes: id (integer or UUID), user_id (foreign key), title (string, max 255), description (string, max 5000, nullable), status (enum: incomplete | complete), priority (enum: low | medium | high, default: medium), created_at (timestamp), updated_at (timestamp). Relationships: belongs_to User (enforced via user_id).

## Success Criteria

### Measurable Outcomes

- **SC-001**: All task CRUD endpoints (POST create, GET list, GET single, PUT update, DELETE) accept and persist the priority field without errors
- **SC-002**: Priority defaults to "medium" for 100% of tasks created without explicit priority specification
- **SC-003**: Invalid priority values are rejected with 400 Bad Request for 100% of invalid requests
- **SC-004**: Tasks are returned from GET `/api/{user_id}/tasks?sort=priority` in consistent priority order (High first, then Medium, then Low) for all test scenarios
- **SC-005**: Tasks with the same priority are sorted by created_at with newest first (secondary sort is deterministic)
- **SC-006**: All task list API responses include priority field for every task returned
- **SC-007**: User ownership is enforced on priority updates: attempts by User B to update User A's task priority returns 404 Not Found for 100% of cross-user scenarios
- **SC-008**: Frontend displays visual priority indicators for all tasks (list view and detail view) without missing any tasks
- **SC-009**: Visual priority indicators use color + icon/text (not color alone) for accessibility compliance
- **SC-010**: Task creation and edit forms include intuitive priority selection controls that are keyboard accessible
- **SC-011**: Priority selection forms default to "medium" when creating new tasks without explicit selection
- **SC-012**: Frontend mobile responsive design: priority indicators render correctly on screens 320px and up
- **SC-013**: Backward compatibility: tasks created before this feature are automatically treated as priority "medium" when retrieved
- **SC-014**: Database migration succeeds for 100% of existing task records without data loss
- **SC-015**: API response times remain under 200ms for single-task operations and under 500ms for listing 100+ tasks (performance not degraded by priority field)

## Assumptions

- **Priority Semantics**: Priority is a task property only; it does NOT trigger automated actions (alerts, notifications, deadline changes). Priority is purely metadata for user organization.
- **Sorting Direction**: "High" priority is more important than "Low"; API sorts descending (High first). This is the standard convention for task management systems.
- **Default Priority**: Reasonable default is "medium" because it's neither too urgent nor too deferrable. Systems typically default to middle values.
- **Case Handling**: Input priority values are case-insensitive (standard practice for enum-like fields); system normalizes to lowercase for consistency.
- **Backward Compatibility**: Existing tasks in the database are treated as "medium" priority to maintain consistent behavior across old and new tasks.
- **Visual Design**: Color indicators and styling follow the design system defined in Spec 4 (colors: red for high, slate for medium, muted for low). Exact colors will be confirmed during UI implementation.
- **User Ownership**: Priority updates are subject to the same user ownership checks as other task updates (user can only change priority on their own tasks).
- **Database Schema**: The Task table can be extended with a new `priority` column via migration; this won't break existing API consumers if priority is optional in requests (defaults applied server-side).
- **Sorting Performance**: When sorting by priority, the backend assumes the `priority` column is indexed for efficient queries on large task lists.
- **No Complex Priority Rules**: This spec does NOT include auto-prioritization, priority inheritance, or context-based priority changes. Priority is set and maintained by the user explicitly.

## Notes & Dependencies

- **Depends on Spec 1**: This feature extends the Task model defined in Spec 1 (Backend API). All existing CRUD endpoints and data persistence remain functional.
- **Depends on Spec 2**: Authentication and user ownership checks from Spec 2 (Authentication) apply to priority operations. Priority updates must be authorized via the same JWT mechanism.
- **Depends on Spec 3 & 4**: Frontend implementation follows patterns and styles defined in Spec 3 (Frontend) and Spec 4 (UI/UX Polish). Visual indicators use the design system colors and typography.
- **No Breaking Changes**: This feature is additive. Existing API consumers (frontend or third-party) are not broken; priority field is optional in requests and included in responses.
- **Database Migration Required**: A schema migration must add the `priority` column to the Task table. This can be done via SQLModel migrations or Alembic (existing migration tools in the project).
- **Future Enhancements**: This spec enables future features like priority-based filtering, priority history/audit logs, or automated priority suggestions, but those are out of scope here.

