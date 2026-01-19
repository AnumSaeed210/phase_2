# Implementation Plan: Task Priorities

**Branch**: `005-task-priorities` | **Date**: 2026-01-17 | **Spec**: [specs/005-task-priorities/spec.md](spec.md)
**Input**: Feature specification from `/specs/005-task-priorities/spec.md`

## Summary

Add task priority levels (Low/Medium/High) to the Taskie todo application. This feature extends the existing Task model with a priority field, updates API endpoints to accept/return priority data, implements server-side priority sorting, and adds UI components for priority selection and visual indicators. The implementation preserves backward compatibility with existing tasks (defaulting to "medium" priority) and integrates seamlessly with the existing design system.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend), Node.js 18+
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, Alembic (migrations)
- Frontend: Next.js 16+, React 18+, TypeScript, Tailwind CSS
**Storage**: Neon Serverless PostgreSQL (add `priority` column to tasks table)
**Testing**: pytest (backend), Vitest/Jest (frontend)
**Target Platform**: Web application (Linux server backend, modern browsers frontend)
**Project Type**: Web application (backend + frontend)
**Performance Goals**: <200ms for single task operations, <500ms for listing 100+ tasks
**Constraints**: No breaking changes to existing API; backward compatible with existing tasks
**Scale/Scope**: Extends existing 5-user-story MVP with additional user story (priority management)

## Constitution Check

✅ **Project Structure**: Maintains existing web application structure (backend + frontend separation)
✅ **Technology Stack**: Uses established stack (FastAPI, Next.js, SQLModel, Tailwind CSS)
✅ **Authentication**: Leverages existing Better Auth + JWT implementation (no changes needed)
✅ **Database**: Extends existing Neon PostgreSQL schema with single new column
✅ **API Design**: Follows existing RESTful patterns from Spec 001
✅ **UI Patterns**: Integrates with existing component system and design tokens from Spec 004
✅ **No Architectural Changes**: Feature is purely additive, no refactoring required

**Gate Status**: ✅ PASS - Feature aligns with project constitution and existing architecture

## Project Structure

### Documentation (this feature)

```text
specs/005-task-priorities/
├── spec.md                  # Feature specification (complete)
├── plan.md                  # This file (in-progress)
├── research.md              # Phase 0 output (TBD)
├── data-model.md           # Phase 1 output (TBD)
├── quickstart.md           # Phase 1 output (TBD)
├── contracts/              # Phase 1 output (TBD)
│   ├── task-creation-priority.md
│   ├── task-update-priority.md
│   ├── task-list-sorting.md
│   └── task-response-schema.md
└── tasks.md                # Phase 2 output (TBD)
```

### Source Code Structure (Web Application)

```text
backend/
├── src/
│   ├── models/
│   │   └── Task.py (extend with priority field)
│   ├── schemas/
│   │   └── TaskSchema.py (update request/response)
│   ├── api/
│   │   └── tasks.py (extend endpoints for priority)
│   ├── services/
│   │   └── TaskService (add sorting logic)
│   └── database.py
├── alembic/
│   ├── versions/
│   │   └── add_priority_to_tasks.py (new migration)
│   └── env.py
└── tests/
    ├── test_task_priorities.py (new)
    └── test_api_priority_endpoints.py (new)

frontend/
├── src/
│   ├── components/
│   │   ├── tasks/
│   │   │   ├── TaskItem.tsx (update with priority indicator)
│   │   │   └── TaskList.tsx (update sorting)
│   │   ├── common/
│   │   │   └── PrioritySelector.tsx (new)
│   │   │   └── PriorityBadge.tsx (new)
│   ├── pages/
│   │   ├── tasks/new/page.tsx (update with priority field)
│   │   └── tasks/[taskId]/page.tsx (update with priority indicator)
│   ├── lib/
│   │   ├── api/types.ts (extend Task type with priority)
│   │   └── hooks/useTasks.ts (add sort logic)
│   └── styles/
│       └── priority-colors.css (or Tailwind config)
└── tests/
    ├── components/PrioritySelector.test.tsx (new)
    └── components/PriorityBadge.test.tsx (new)
```

**Structure Decision**: Web application with clear backend/frontend separation. Priority feature extends existing models and components without architectural changes. New migrations, API endpoints, and UI components added alongside existing implementations.

## Implementation Phases

### Phase 0: Research & Design Validation

**Objectives**:
- Validate priority field design choices
- Confirm color scheme for visual indicators
- Review database migration approach
- Document API contract patterns

**Research Topics**:
1. **Priority Color Scheme**: Confirm High=Red, Medium=Slate, Low=Muted matches design system (Spec 004)
2. **Database Migration Strategy**: Alembic migration approach for adding priority column with default
3. **API Sorting Parameter**: Confirm `?sort=priority` pattern aligns with existing API conventions
4. **Case Handling**: Confirm lowercase normalization of priority values acceptable
5. **Backward Compatibility**: Validate that treating existing null priorities as "medium" is correct approach

**Deliverables**: research.md with all design decisions documented

### Phase 1: Data Model & API Contracts

**Objectives**:
- Extend Task model with priority field
- Define API request/response schemas
- Document database migration
- Create API contracts

**Tasks**:
1. **data-model.md**: Task entity with priority field (type: enum, default: medium)
2. **contracts/**: OpenAPI schemas for:
   - POST /api/{user_id}/tasks (with priority field)
   - PUT /api/{user_id}/tasks/{id} (update priority)
   - GET /api/{user_id}/tasks?sort=priority (sorted response)
3. **quickstart.md**: API usage examples showing priority in action

**Deliverables**: data-model.md, contracts/*, quickstart.md

### Phase 2: Task Breakdown

**Objectives**:
- Create detailed task list for implementation
- Define dependencies between backend and frontend work
- Establish testing strategy
- Identify integration points

**Deliverables**: tasks.md with ordered implementation sequence

---

## Implementation Sequence (High Level)

### Backend Implementation Order

1. **Database Migration** - Add priority column to tasks table
2. **Model Update** - Add priority field to Task model
3. **Schema Update** - Update TaskCreate/TaskUpdate schemas with priority
4. **API Endpoints** - Update POST /tasks and PUT /tasks/{id} to handle priority
5. **Sorting Logic** - Implement ?sort=priority query parameter support
6. **Backend Testing** - Unit and integration tests for priority feature

### Frontend Implementation Order

1. **Type Updates** - Extend Task type with priority field
2. **API Client** - Update API client to send/receive priority
3. **Priority Components** - Create PrioritySelector and PriorityBadge components
4. **Task Forms** - Update task creation/edit forms with priority selector
5. **Task Display** - Update TaskItem and TaskList to show priority indicators
6. **Sorting UI** - Add option to sort tasks by priority
7. **Frontend Testing** - Component and integration tests

### Integration & Validation

1. **End-to-end Testing** - Create task with priority, update, sort, display
2. **Backward Compatibility** - Verify existing tasks work with new field
3. **Responsive Design** - Test priority indicators on mobile
4. **Accessibility** - Verify color + icon/text indicators meet WCAG standards

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Priority Values | Enum: low, medium, high | Simple, constrained, standard in task apps |
| Default Priority | "medium" | Neutral middle value, sensible for most tasks |
| Storage Type | Database column (string enum or int) | Simple, performant, supports sorting |
| Sorting Order | High → Medium → Low (descending) | Matches user mental model (important first) |
| API Pattern | ?sort=priority query parameter | Consistent with Spec 001 filtering patterns |
| Visual Indicators | Color + Icon/Text | Accessible (not relying on color alone) |
| Case Handling | Lowercase normalization | Consistent with other enum fields |
| Backward Compat | Existing tasks → "medium" | Maintains consistency, no data loss |

---

## Risk & Mitigation

| Risk | Mitigation |
|------|-----------|
| Database migration fails on large task tables | Test migration on staging DB first; use Alembic's built-in safety features |
| Breaking change to API consumers | Priority is optional in requests; gracefully defaults if not provided |
| Visual indicators don't meet accessibility standards | Use color + icon/text; test with accessibility audits |
| Priority sorting impacts performance | Ensure priority column is indexed; test with 1000+ tasks |
| Mobile display issues with priority badges | Responsive design testing across device sizes |

---

## Success Criteria for Implementation

1. ✅ Task model includes priority field (low/medium/high)
2. ✅ All task CRUD endpoints accept/return priority
3. ✅ Tasks default to "medium" priority
4. ✅ ?sort=priority returns tasks ordered High→Medium→Low
5. ✅ Task forms include priority selection (defaults to medium)
6. ✅ Task list displays color-coded priority indicators (Red/Slate/Muted)
7. ✅ Priority indicators are accessible (color + icon/text)
8. ✅ Existing tasks work with priority feature (backward compatible)
9. ✅ No performance degradation (API response times maintained)
10. ✅ No regressions in existing task features

---

## Dependency Map

```
Phase 0: Research
    ↓
Phase 1: Design (Data Model, API Contracts)
    ↓
Phase 2: Task Breakdown
    ↓
Backend Track          |  Frontend Track
├─ Migration          |  ├─ Type Updates
├─ Model Update       |  ├─ API Client
├─ Schema Update      |  ├─ Components (NEW)
├─ API Endpoints      |  ├─ Forms Update
├─ Sorting Logic      |  ├─ Task Display
└─ Backend Tests      |  └─ Frontend Tests
    ↓                 |      ↓
Integration & E2E Testing
    ↓
Validation & Sign-Off
```

Backend and frontend can be developed in parallel after Phase 1 design is complete.

---

## Next Steps

1. **Phase 0**: Execute `/sp.plan` research tasks (resolve technical unknowns)
2. **Phase 1**: Generate data-model.md, contracts/, and quickstart.md
3. **Phase 2**: Execute `/sp.tasks` to create detailed task breakdown in tasks.md
4. **Implementation**: Execute `/sp.implement` to run tasks and complete feature

---

## Notes

- Feature integrates cleanly with existing code; no architectural changes required
- All changes are backward compatible (existing tasks work unchanged)
- Visual design leverages existing Spec 004 design system
- API patterns follow established Spec 001 conventions
- Database migration is low-risk single-column addition

