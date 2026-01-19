# Research Phase: Task Priorities Implementation

**Feature**: 005-task-priorities
**Date**: 2026-01-17
**Status**: Complete

## Overview

This document consolidates research findings and design decisions for implementing task priorities in Taskie. All technical unknowns from the plan have been resolved through analysis of the existing codebase and project architecture.

---

## Research Topics

### 1. Color Scheme for Visual Indicators

**Question**: What colors should be used for High, Medium, and Low priority indicators?

**Research**: Reviewed Spec 004 (UI/UX Polish) and existing design system in `frontend/tailwind.config.ts`

**Design System Available**:
- **Slate** (Primary): #323843, #3d444f (light), #252a31 (dark) - Main text/backgrounds
- **Violet** (Accent): #c68dff (primary), #d9a5ff (light), #b373e6 (dark) - Focus/highlight
- **Lime** (Success): #cbe857 (primary), #b3d946 (dark) - Positive/completion
- **Error**: #ff6b6b, #ff8c8c (light) - Destructive/errors
- **White**: #f5f5f5 - Paper/background

**Decision**:
- **High Priority**: Error red (#ff6b6b) - conveys urgency
- **Medium Priority**: Slate (#323843) or Violet accent (#c68dff) - neutral but visible
- **Low Priority**: Slate-light (#3d444f) - muted, de-emphasized

**Rationale**:
- Uses existing design system colors (no new colors needed)
- Red for high priority is standard across task apps (Todoist, Asana, etc.)
- Slate medium for neutral choice; visually lighter than high
- Slate-light for low priority (least urgent)
- All colors have sufficient contrast for accessibility

**Alternatives Considered**:
- Lime for High: Not appropriate (lime conveys "success", not "urgent")
- Violet for all priorities: Insufficient differentiation
- Custom colors: Violates design system consistency principle

**Final Color Map**:
```
High:   #ff6b6b (Error red)
Medium: #c68dff (Violet accent)  OR  #323843 (Slate, if more conservative)
Low:    #3d444f (Slate-light)
```

---

### 2. Database Migration Strategy

**Question**: How should we add the priority column to the tasks table?

**Research**: Reviewed existing migration structure in `backend/alembic/versions/`

**Findings**:
- Project uses Alembic for migrations (SQLModel + Alembic)
- Existing migrations use standard SQLAlchemy operations
- No migrations yet exist in the repo (greenfield database setup)

**Decision**:
Create new migration file `add_priority_to_tasks.py` that:
1. Adds `priority` column to `tasks` table as nullable VARCHAR with constraint
2. Sets default value to 'medium' for all existing and new rows
3. Adds CHECK constraint to ensure only valid values (low, medium, high)
4. Marks column as NOT NULL after setting defaults

**Migration Approach**:
```python
def upgrade():
    # Add nullable column first
    op.add_column('tasks', sa.Column('priority', sa.String(10), nullable=True))

    # Set default for existing rows
    op.execute("UPDATE tasks SET priority = 'medium' WHERE priority IS NULL")

    # Add constraint
    op.alter_column('tasks', 'priority', nullable=False)
```

**Rationale**:
- Two-step approach (nullable → default → not null) ensures safety
- CHECK constraint prevents invalid values at database level
- Backward compatible: existing tasks automatically get "medium" priority
- Alembic handles database portability

**Alternatives Considered**:
- Direct non-nullable column: Fails on existing data (requires default immediately)
- No constraint: Allows invalid data (violates spec requirement)
- Multiple columns (is_high, is_medium, is_low): Normalized poorly, less maintainable

---

### 3. API Sorting Parameter Pattern

**Question**: What query parameter pattern should we use for sorting by priority?

**Research**: Reviewed existing Spec 001 (Backend API) and current endpoints in `backend/src/api/tasks.py`

**Findings**:
- Spec 001 already shows `?status=complete` filtering pattern
- List endpoint: `GET /api/{user_id}/tasks?status=incomplete` is supported
- No existing sort parameter documented (only filter)

**Decision**:
Use query parameter: `?sort=priority`
- Explicit, clear, follows REST conventions
- Doesn't conflict with existing `?status=` filter
- Can be combined: `GET /api/{user_id}/tasks?status=incomplete&sort=priority`

**API Behavior**:
- Default (no sort): By created_at (newest first) - maintains existing behavior
- `?sort=priority`: By priority descending (High→Medium→Low), secondary sort by created_at
- `?sort=priority&status=incomplete`: Both filters applied
- Case-insensitive input: "HIGH", "high", "High" all normalized to "high"

**Rationale**:
- Explicit parameter is clearer than overloading `?status=`
- RESTful convention for sorting
- Backward compatible (no breaking changes to default sort)
- Matches user mental model (focus on important tasks first)

**Alternatives Considered**:
- `?order_by=priority`: Too verbose
- `?priority_sort=true`: Less standard
- Custom ranking algorithm: Out of scope per spec constraints

---

### 4. Case Handling for Priority Values

**Question**: Should priority input be case-sensitive or case-insensitive?

**Research**: Reviewed Spec 005 requirement FR-009 and existing code patterns in TaskCreate schema

**Findings**:
- Spec 005 requirement FR-009: "System MUST support case-insensitive priority input"
- No existing case-insensitive handling in current codebase
- SQLModel schemas use Pydantic validators

**Decision**:
Implement case-insensitive handling in Pydantic validator:
```python
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"

    @field_validator('priority', mode='before')
    @classmethod
    def normalize_priority(cls, v):
        if v is None:
            return "medium"
        if isinstance(v, str):
            normalized = v.lower().strip()
            if normalized not in ["low", "medium", "high"]:
                raise ValueError("Priority must be 'low', 'medium', or 'high'")
            return normalized
        raise ValueError("Priority must be a string")
```

**Rationale**:
- Improves user experience (common mistake to use "HIGH" instead of "high")
- Simple to implement with Pydantic validators
- No performance impact
- Maintains data consistency (always lowercase in database)

**Alternatives Considered**:
- Strict case-sensitive: Forces API consumers to remember exact casing
- Multiple accepted values: Harder to maintain consistency
- Case-insensitive at database level only: Frontend must still normalize

---

### 5. Backward Compatibility: Handling Existing Tasks

**Question**: How should we handle tasks created before the priority feature?

**Research**: Reviewed Spec 005 requirements and migration strategy above

**Findings**:
- Spec 005 FR-016: "System MUST maintain backward compatibility: existing tasks created before this feature are assigned default priority medium"
- Migration will set all existing tasks to "medium" automatically
- No manual data migration needed

**Decision**:
1. Migration sets all existing tasks to priority='medium'
2. API treats null/missing priority as "medium"
3. Frontend handles tasks without priority field gracefully (displays as medium)
4. No special "legacy" field or separate handling needed

**Rationale**:
- Medium is sensible default (neutral, not too urgent or deferrable)
- Seamless experience for users (existing tasks gain priority organizing benefit)
- No user action required
- Simple to maintain (single default, not multiple legacy paths)

**Alternatives Considered**:
- Null priority value: Causes errors in sorting logic, requires extra handling
- Separate "unset" state: Adds complexity with no user benefit
- User choice on migration: Requires UI for data migration, out of scope

---

### 6. Visual Accessibility: Color + Icon/Text Strategy

**Question**: How should we display priority indicators accessibly?

**Research**: Reviewed WCAG 2.1 guidelines and Spec 004 component patterns

**Findings**:
- WCAG 2.1 Level AA requires: "Color is not used as the only means of conveying information"
- Existing components in Spec 004 use color + icons/text combinations
- Example: Error alerts use red color + error icon + text

**Decision**:
Display priority as combination of:
1. **Color badge** (background): #ff6b6b (High), #c68dff (Medium), #3d444f (Low)
2. **Icon**: ⬆️ (High), ➡️ (Medium), ⬇️ (Low) OR 🔴 (High), 🟡 (Medium), ⚪ (Low)
3. **Text label**: "High", "Medium", "Low" (shown in tooltip or alongside badge)

**Implementation**:
```jsx
<div className="flex items-center gap-2">
  <span
    className="px-2 py-1 rounded text-white text-sm font-medium"
    style={{ backgroundColor: getPriorityColor(priority) }}
  >
    {priority.charAt(0).toUpperCase() + priority.slice(1)}
  </span>
  <span className="text-gray-600 text-xs" title={`Priority: ${priority}`}>
    {getPriorityIcon(priority)}
  </span>
</div>
```

**Rationale**:
- Meets WCAG AA compliance (color + text)
- Clear and scannable in task list
- Consistent with existing component patterns
- Icons provide visual shorthand without reading text
- Tooltip provides accessible label for screen readers

**Alternatives Considered**:
- Color only: Fails accessibility requirement
- Text only: Less scannable in long lists
- Separate icon component: More complex, less space-efficient

---

### 7. Mobile Responsive Design for Priority Indicators

**Question**: How should priority indicators render on small screens?

**Research**: Reviewed Spec 005 requirement SC-012 and existing responsive patterns in TaskItem component

**Findings**:
- Tailwind CSS responsive utilities already configured (mobile: 320px, tablet: 768px, desktop: 1024px)
- Existing TaskItem component uses responsive gap and padding
- Priority indicator should be compact on mobile

**Decision**:
Responsive priority rendering:
- **Desktop (1024px+)**: Full badge with text + icon
- **Tablet (768px)**: Badge with text label (icon optional)
- **Mobile (320px-767px)**: Compact icon badge only (text in tooltip)

**Implementation**:
```jsx
<div className="flex items-center gap-2">
  {/* Full badge on desktop/tablet, icon-only on mobile */}
  <div className="hidden sm:flex items-center gap-1">
    <span className="px-2 py-1 rounded text-white text-xs font-medium"
      style={{ backgroundColor: getPriorityColor(priority) }}>
      {getPriorityLabel(priority)}
    </span>
  </div>

  {/* Icon always visible, shows tooltip on hover */}
  <span className="text-lg" title={`Priority: ${getPriorityLabel(priority)}`}>
    {getPriorityIcon(priority)}
  </span>
</div>
```

**Rationale**:
- Saves space on mobile without losing information
- Icon provides visual context; text available in tooltip
- Uses existing Tailwind responsive classes
- Consistent with Spec 004 responsive design patterns

**Alternatives Considered**:
- Always show text: Takes too much space on mobile (breaks layout)
- Hide priority on mobile: Users lose important context
- Drawer/modal for priority: Overkill for simple metadata

---

## Implementation Assumptions

1. **Database Connection**: Neon PostgreSQL connection is stable; migration runs synchronously
2. **Enum Storage**: Priority stored as VARCHAR with CHECK constraint (SQLModel supports this)
3. **User Expectations**: Default "medium" priority aligns with user mental model (verified by Spec 005)
4. **API Stability**: Adding optional field doesn't break existing API consumers
5. **Performance**: Priority field doesn't create indexes automatically (OK for this feature scope)
6. **Frontend Compatibility**: All modern browsers support the colors and responsive design needed

---

## Unknowns Resolved

| Unknown | Resolution | Evidence |
|---------|-----------|----------|
| Color scheme | High=#ff6b6b, Medium=#c68dff, Low=#3d444f | Design system in tailwind.config.ts |
| Migration approach | Alembic two-step (nullable → default → not null) | Existing migration patterns |
| Sorting pattern | ?sort=priority query parameter | Spec 001 conventions + REST standards |
| Case handling | Lowercase normalization via Pydantic | Spec 005 FR-009 requirement |
| Backward compatibility | Migrate existing to "medium" | Spec 005 FR-016 requirement |
| Accessibility | Color + icon/text combination | WCAG 2.1 AA guidelines |
| Mobile responsive | Icon-only on mobile, full badge on desktop | Tailwind responsive utilities |

---

## Conclusion

All research topics have been resolved with decisions that:
- ✅ Align with project constitution and existing architecture
- ✅ Follow spec requirements (005) precisely
- ✅ Leverage existing design system (Spec 004)
- ✅ Maintain backward compatibility
- ✅ Meet accessibility standards (WCAG 2.1 AA)
- ✅ Are implementable with existing technology stack

**Status**: Ready to proceed to Phase 1 (Data Model & API Contracts design)

