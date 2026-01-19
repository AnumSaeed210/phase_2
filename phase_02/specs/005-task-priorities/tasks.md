# Tasks: Task Priorities Feature

**Input**: Design documents from `/specs/005-task-priorities/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅
**Branch**: `005-task-priorities`
**Status**: Ready for Implementation

**Tests**: Included (contract tests + integration tests for each user story)

**Organization**: Tasks organized by user story (US1-US5) to enable independent implementation and testing

---

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3, US4, US5)
- **ID**: Task identifier (T001, T002, etc.)
- Include exact file paths in descriptions

---

## Implementation Strategy

**MVP Scope**: User Stories 1-4 (P1 priority)
- ✅ Create task with priority (US1)
- ✅ Update task priority (US2)
- ✅ Sort tasks by priority (US3)
- ✅ Display priority indicators (US4)

**Phase 2 Enhancement**: User Story 5 (P2 priority)
- ✅ Priority selection UI in forms (US5)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare for backend and frontend development

- [ ] T001 Review planning artifacts (plan.md, research.md, data-model.md) and validate technical approach
- [ ] T002 Create feature branch `005-task-priorities` and ensure all team members have access

---

## Phase 2: Foundational (Backend Database & API)

**Purpose**: Implement database migration and extend existing API infrastructure

**⚠️ CRITICAL**: These must complete before ANY user story work begins

- [ ] T003 Create Alembic migration file `backend/alembic/versions/add_priority_to_tasks.py` to add priority column with CHECK constraint
- [ ] T004 Extend Task model in `backend/src/models.py` to add priority field (enum: low/medium/high, default: medium)
- [ ] T005 Extend TaskCreate and TaskUpdate schemas in `backend/src/schemas.py` to accept optional priority field with validation
- [ ] T006 Extend TaskResponse schema in `backend/src/schemas.py` to always include priority in responses
- [ ] T007 Add priority validation in Pydantic validators in `backend/src/schemas.py` (case-insensitive, lowercase normalization)
- [ ] T008 Update TaskService in `backend/src/services/tasks.py` to handle priority in create/update operations
- [ ] T009 Add query parameter support for `?sort=priority` in TaskService sorting logic in `backend/src/services/tasks.py`

**Checkpoint**: Database migration ready, model/schema extended, API service layer ready for endpoints

---

## Phase 3: User Story 1 - Set Task Priority on Creation (Priority: P1)

**Goal**: Users can create tasks with priority levels (Low/Medium/High) or accept default Medium

**Independent Test**: Create tasks via API with various priority values; verify persistence and default behavior

### Contract Tests for User Story 1

- [ ] T010 [P] [US1] Write contract test for POST `/api/{user_id}/tasks` with priority in `backend/tests/test_api_create_task_priority.py`
  - Test successful creation with priority
  - Test default priority (medium) when not specified
  - Test invalid priority rejection
  - Test case-insensitive input handling

### Implementation for User Story 1

- [ ] T011 [US1] Update POST `/api/{user_id}/tasks` endpoint in `backend/src/api/tasks.py` to accept priority parameter
- [ ] T012 [US1] Update `create_task()` method in TaskService in `backend/src/services/tasks.py` to handle priority parameter with default
- [ ] T013 [US1] Add priority validation error handling in `backend/src/api/tasks.py` (400 Bad Request for invalid values)
- [ ] T014 [US1] Test priority creation manually via curl commands from quickstart.md
- [ ] T015 [US1] Verify backward compatibility: tasks created before feature default to "medium"

**Checkpoint**: User Story 1 fully functional - users can create tasks with priority

---

## Phase 4: User Story 2 - Update Task Priority (Priority: P1)

**Goal**: Users can change task priority at any time; invalid values are rejected

**Independent Test**: Update existing tasks via API; verify new priority is saved and timestamps are updated correctly

### Contract Tests for User Story 2

- [ ] T016 [P] [US2] Write contract test for PUT `/api/{user_id}/tasks/{id}` with priority in `backend/tests/test_api_update_task_priority.py`
  - Test successful priority update
  - Test invalid priority rejection
  - Test user ownership enforcement (403 on cross-user update)
  - Test updated_at timestamp update

### Implementation for User Story 2

- [ ] T017 [US2] Update PUT `/api/{user_id}/tasks/{id}` endpoint in `backend/src/api/tasks.py` to accept optional priority field
- [ ] T018 [US2] Update `update_task()` method in TaskService in `backend/src/services/tasks.py` to handle priority updates
- [ ] T019 [US2] Add priority validation for updates in `backend/src/api/tasks.py` (same rules as creation)
- [ ] T020 [US2] Ensure updated_at timestamp is refreshed on priority changes in `backend/src/models.py`
- [ ] T021 [US2] Test priority updates manually via curl commands
- [ ] T022 [US2] Verify user ownership is enforced (another user cannot update a task's priority)

**Checkpoint**: User Story 2 fully functional - users can update task priority

---

## Phase 5: User Story 3 - Retrieve Tasks Sorted by Priority (Priority: P1)

**Goal**: Users can request task lists sorted by priority (High→Medium→Low); secondary sort by created_at

**Independent Test**: List tasks with `?sort=priority`; verify ordering is High then Medium then Low

### Contract Tests for User Story 3

- [ ] T023 [P] [US3] Write contract test for GET `/api/{user_id}/tasks?sort=priority` in `backend/tests/test_api_list_tasks_sorted.py`
  - Test sort order (high → medium → low)
  - Test secondary sort by created_at (newest first)
  - Test combination with status filter (`?status=incomplete&sort=priority`)
  - Test with 0 tasks, 1 task, and 5+ tasks

### Implementation for User Story 3

- [ ] T024 [US3] Extend TaskService `get_tasks_for_user()` method in `backend/src/services/tasks.py` to support sorting by priority
- [ ] T025 [US3] Add `sort` query parameter handling in GET `/api/{user_id}/tasks` endpoint in `backend/src/api/tasks.py`
- [ ] T026 [US3] Implement priority ordering logic: map priority strings to numeric values for descending sort
- [ ] T027 [US3] Implement secondary sort by created_at DESC (newest first within same priority)
- [ ] T028 [US3] Ensure sorting works with existing status filter (combinable: `?status=incomplete&sort=priority`)
- [ ] T029 [US3] Test sorting manually with multiple tasks of different priorities

**Checkpoint**: User Story 3 fully functional - users can sort tasks by priority

---

## Phase 6: User Story 4 - Visual Priority Indicators in Task UI (Priority: P1)

**Goal**: Frontend displays color-coded priority indicators with icons/text for accessibility

**Independent Test**: Sign in and view task list; verify high/medium/low priorities display distinct indicators

### Frontend Setup (Parallel with US1-3)

- [ ] T030 [P] [US4] Extend Task type in `frontend/src/lib/api/types.ts` to include priority field
- [ ] T031 [P] [US4] Create PriorityBadge component in `frontend/src/components/common/PriorityBadge.tsx`
  - Display color + icon + text label
  - Map: High=#ff6b6b (red), Medium=#c68dff (violet), Low=#3d444f (slate)
  - Use accessible combination (color + icon/text, not color-only)

- [ ] T032 [P] [US4] Add getPriorityColor() utility function in `frontend/src/lib/utils/priority.ts`
- [ ] T033 [P] [US4] Add getPriorityIcon() utility function in `frontend/src/lib/utils/priority.ts`
- [ ] T034 [P] [US4] Add getPriorityLabel() utility function in `frontend/src/lib/utils/priority.ts`

### Frontend Implementation for User Story 4

- [ ] T035 [US4] Update TaskItem component in `frontend/src/components/tasks/TaskItem.tsx` to display PriorityBadge
  - Show badge in list view
  - Show badge in detail view
  - Use responsive design (full badge on desktop, icon-only on mobile)

- [ ] T036 [US4] Update TaskList component in `frontend/src/components/tasks/TaskList.tsx` to handle tasks with priority field
- [ ] T037 [US4] Update task detail page in `frontend/src/app/(dashboard)/tasks/[taskId]/page.tsx` to show priority indicator
- [ ] T038 [US4] Test priority badges manually across devices (desktop, tablet, mobile)
- [ ] T039 [US4] Verify accessibility: color + icon + text work correctly in all browsers

**Checkpoint**: User Story 4 fully functional - users see visual priority indicators

---

## Phase 7: User Story 5 - Priority Selection UI in Task Forms (Priority: P2)

**Goal**: Task creation and edit forms include intuitive priority selector; defaults to Medium

**Independent Test**: Open task creation form; verify priority selector present with all options; test edit form pre-selection

### Frontend Implementation for User Story 5

- [ ] T040 [P] [US5] Create PrioritySelector component in `frontend/src/components/common/PrioritySelector.tsx`
  - Dropdown/radio button control
  - Show all three options: Low, Medium (default), High
  - Keyboard accessible
  - Mobile responsive

- [ ] T041 [US5] Update TaskForm component in `frontend/src/components/tasks/TaskForm.tsx` to include PrioritySelector
  - In create mode: default to "medium"
  - In edit mode: pre-select current priority
  - Validate priority selection before submit

- [ ] T042 [US5] Update task creation page in `frontend/src/app/(dashboard)/tasks/new/page.tsx` to use updated TaskForm
- [ ] T043 [US5] Update task edit page in `frontend/src/app/(dashboard)/tasks/[taskId]/page.tsx` to use updated TaskForm
- [ ] T044 [US5] Update API client in `frontend/src/lib/api/client.ts` to send priority in create/update requests
- [ ] T045 [US5] Update useTasks hook in `frontend/src/lib/hooks/useTasks.ts` to handle priority in create/update operations
- [ ] T046 [US5] Test form validation: verify can submit with/without priority selection
- [ ] T047 [US5] Test edit form: verify current priority is pre-selected and editable

**Checkpoint**: User Story 5 fully functional - users have intuitive priority selection in forms

---

## Phase 8: Integration & Cross-Story Testing

**Purpose**: Verify all user stories work together seamlessly

- [ ] T048 [P] Run end-to-end test: Create task with high priority → View in list with indicator → Update to low → Verify change
- [ ] T049 [P] Run end-to-end test: Create multiple tasks with mixed priorities → Sort by priority → Verify ordering (high→medium→low)
- [ ] T050 [P] Run end-to-end test: Sign in as User A → Create task with priority → Sign out → Sign in as User B → Verify cannot see User A's task
- [ ] T051 [P] Run end-to-end test: Create task without priority → Verify defaults to medium → Create with priority → Verify reflected

- [ ] T052 Test backward compatibility: Verify old tasks (created before feature) default to medium priority
- [ ] T053 Test database migration: Apply migration to dev database → Verify all existing tasks get priority="medium"
- [ ] T054 Test API contracts: Run all contract tests from Phase 3, 4, 5 together
- [ ] T055 Test frontend responsiveness: Open task list on desktop, tablet, mobile → Verify priority badges render correctly

---

## Phase 9: Polish & Final Validation

**Purpose**: Clean up, documentation, and production readiness

- [ ] T056 Add logging for priority operations in backend (create, update, sort with priority)
- [ ] T057 Add error handling for edge cases (concurrent priority updates, database failures)
- [ ] T058 Update API documentation/OpenAPI schema in `backend/src/api/tasks.py` docstrings
- [ ] T059 Update README or API docs with priority feature examples
- [ ] T060 Add JSDoc/TypeScript documentation for frontend PriorityBadge and PrioritySelector components
- [ ] T061 Run full test suite (backend pytest + frontend Jest/Vitest)
- [ ] T062 Code review: Backend changes (models, schemas, services, endpoints)
- [ ] T063 Code review: Frontend changes (components, pages, hooks)
- [ ] T064 Performance test: List 100+ tasks with `?sort=priority` → Verify <500ms response time
- [ ] T065 Accessibility audit: Run aWave or WAVE tool on task list → Verify priority indicators accessible

**Checkpoint**: Feature complete, tested, documented, and ready for production

---

## Dependency Graph

```
Phase 1: Setup
    ↓
Phase 2: Foundation (Database + API Infrastructure)
    ↓
Phase 3: US1 (Create with Priority) ←─┐
Phase 4: US2 (Update Priority)       │ Can run in parallel
Phase 5: US3 (Sort by Priority)      ├─→ Phase 7: US5 (Forms)
Phase 6: US4 (Visual Indicators) ←───┘
    ↓
Phase 8: Integration Testing
    ↓
Phase 9: Polish & Validation
    ↓
READY FOR PRODUCTION DEPLOYMENT
```

---

## Parallel Execution Plan

### Batch 1 (Foundation - Sequential)
- Execute T001-T009 sequentially (database setup)

### Batch 2 (User Stories 1-4 Backend - Can parallelize)
After T009 complete:
- **Track A**: T010-T015 (US1 - Create with Priority)
- **Track B**: T016-T022 (US2 - Update Priority)
- **Track C**: T023-T029 (US3 - Sort by Priority)

### Batch 3 (User Story 4 Frontend - Starts after Batch 2 Backend)
Can parallelize:
- T030-T034 (Priority components) in parallel with T035-T039 (TaskItem integration)

### Batch 4 (User Story 5 Frontend - After US1-US4 Backend)
- T040-T047 sequentially (depends on working US1-US4 backend)

### Batch 5 (Integration - After all stories)
- T048-T055 can run in parallel (independent test scenarios)

### Batch 6 (Polish - After integration)
- T056-T065 sequentially (final touches)

---

## Task Tracking Checklist

Use this to track progress:

### Phase 1 ✓
- [ ] T001 ✓
- [ ] T002 ✓

### Phase 2 (Foundation)
- [ ] T003 - Database migration
- [ ] T004 - Task model
- [ ] T005 - TaskCreate/Update schemas
- [ ] T006 - TaskResponse schema
- [ ] T007 - Priority validation
- [ ] T008 - TaskService create/update
- [ ] T009 - TaskService sorting

### Phase 3 (US1)
- [ ] T010 - Contract tests
- [ ] T011 - POST endpoint
- [ ] T012 - Service create logic
- [ ] T013 - Error handling
- [ ] T014 - Manual testing
- [ ] T015 - Backward compat

### Phase 4 (US2)
- [ ] T016 - Contract tests
- [ ] T017 - PUT endpoint
- [ ] T018 - Service update logic
- [ ] T019 - Validation
- [ ] T020 - Timestamps
- [ ] T021 - Manual testing
- [ ] T022 - User ownership

### Phase 5 (US3)
- [ ] T023 - Contract tests
- [ ] T024 - Sorting logic
- [ ] T025 - Query parameter
- [ ] T026 - Priority ordering
- [ ] T027 - Secondary sort
- [ ] T028 - Filter combination
- [ ] T029 - Manual testing

### Phase 6 (US4)
- [ ] T030 - Task type
- [ ] T031 - PriorityBadge component
- [ ] T032 - Color utility
- [ ] T033 - Icon utility
- [ ] T034 - Label utility
- [ ] T035 - TaskItem integration
- [ ] T036 - TaskList
- [ ] T037 - Detail page
- [ ] T038 - Responsive testing
- [ ] T039 - Accessibility

### Phase 7 (US5)
- [ ] T040 - PrioritySelector component
- [ ] T041 - TaskForm integration
- [ ] T042 - Create page
- [ ] T043 - Edit page
- [ ] T044 - API client
- [ ] T045 - useTasks hook
- [ ] T046 - Form validation
- [ ] T047 - Edit form testing

### Phase 8 (Integration)
- [ ] T048 - E2E create + display
- [ ] T049 - E2E sort + verify
- [ ] T050 - E2E user isolation
- [ ] T051 - E2E default priority
- [ ] T052 - Backward compat
- [ ] T053 - Migration testing
- [ ] T054 - Contract test suite
- [ ] T055 - Responsive test

### Phase 9 (Polish)
- [ ] T056 - Logging
- [ ] T057 - Error handling
- [ ] T058 - API docs
- [ ] T059 - README
- [ ] T060 - Component docs
- [ ] T061 - Test suite
- [ ] T062 - Code review (backend)
- [ ] T063 - Code review (frontend)
- [ ] T064 - Performance test
- [ ] T065 - Accessibility audit

---

## Notes

- **Total Tasks**: 65 tasks across 9 phases
- **MVP Scope**: Complete Phases 1-6 (Tasks T001-T047)
- **Full Scope**: Complete all 65 tasks through Phase 9
- **Parallel Opportunities**: Identified in Parallel Execution Plan above
- **Database Migration**: Critical path item (T003 blocks everything)
- **Frontend Blocked By**: Backend API endpoints (wait for US1-US4 backend to complete)
- **Test First**: Contract tests written BEFORE implementation for each user story
- **Production Ready**: Complete Phase 9 before deploying to production

---

*Generated for Spec 005: Task Priorities on 2026-01-17. Ready for implementation execution via `/sp.implement`*

