# Data Model: Task Priorities

**Feature**: 005-task-priorities
**Date**: 2026-01-17
**Based on**: research.md + spec.md requirements

## Overview

The Task data model is extended with a `priority` field to support task prioritization. This document defines the entity structure, fields, relationships, validation rules, and state transitions.

---

## Entity Definition: Task

### Full Entity Structure

```
Task {
  id: integer (primary key, auto-increment)
  user_id: string/UUID (foreign key → User)
  title: string (max 255 characters)
  description: string (max 5000 characters, nullable)
  status: enum ("incomplete" | "complete")
  priority: enum ("low" | "medium" | "high")    ← NEW FIELD
  created_at: timestamp (UTC, set on create)
  updated_at: timestamp (UTC, set on create/update)
}
```

### Field Specifications

| Field | Type | Constraints | Default | Description |
|-------|------|-----------|---------|-------------|
| `id` | Integer | NOT NULL, PRIMARY KEY, AUTO_INCREMENT | N/A | Unique task identifier |
| `user_id` | String/UUID | NOT NULL, FOREIGN KEY | N/A | Owner of the task (from JWT) |
| `title` | String(255) | NOT NULL, MIN_LENGTH=1, MAX_LENGTH=255 | N/A | Task title/summary |
| `description` | String(5000) | NULLABLE, MAX_LENGTH=5000 | NULL | Detailed task description |
| `status` | Enum | NOT NULL, IN ('incomplete','complete') | 'incomplete' | Current task state |
| `priority` | Enum | NOT NULL, IN ('low','medium','high') | 'medium' | Task importance level |
| `created_at` | Timestamp | NOT NULL, SET ON CREATE | CURRENT_TIMESTAMP | Task creation time (UTC) |
| `updated_at` | Timestamp | NOT NULL, SET ON CREATE/UPDATE | CURRENT_TIMESTAMP | Last modification time (UTC) |

### Priority Field Details

**Type**: String Enum (stored as VARCHAR(10) with CHECK constraint)

**Allowed Values**:
- `"low"` - Lower priority task
- `"medium"` - Standard/normal priority (default)
- `"high"` - Higher priority task

**Default Value**: `"medium"`

**Storage**: Database column with CHECK constraint:
```sql
ALTER TABLE tasks ADD COLUMN priority VARCHAR(10) DEFAULT 'medium' NOT NULL;
ALTER TABLE tasks ADD CONSTRAINT check_priority
  CHECK (priority IN ('low', 'medium', 'high'));
```

**Input Validation**: Case-insensitive (normalized to lowercase)
- Input "HIGH" → Stored as "high"
- Input "High" → Stored as "high"
- Input "high" → Stored as "high"
- Invalid input "urgent" → 400 Bad Request error

---

## Relationships

```
User (1) ──→ (*) Task
  ↑
  └─── one-to-many relationship
       enforced via user_id foreign key
       all task operations verified against user ownership
```

**User → Task Relationship**:
- One user has many tasks
- Enforced at API layer: users can only access their own tasks
- Foreign key constraint in database: `FOREIGN KEY (user_id) REFERENCES users(id)`
- Cascade delete: when user is deleted, all their tasks are deleted

---

## Validation Rules

### Input Validation (Task Creation/Update)

| Field | Rule | Error Response |
|-------|------|----------------|
| `title` | Required, 1-255 chars | 400 Bad Request: "Title is required" / "Title must be 255 characters or less" |
| `description` | Optional, max 5000 chars | 400 Bad Request: "Description must be 5000 characters or less" |
| `priority` | Optional, must be low/medium/high | 400 Bad Request: "Priority must be 'low', 'medium', or 'high'" |
| `user_id` | Must match authenticated user | 403 Forbidden (auth layer enforces) |

### Database Constraints

| Constraint | Purpose |
|-----------|---------|
| PRIMARY KEY (id) | Ensure unique task IDs |
| FOREIGN KEY (user_id) | Enforce user ownership |
| CHECK (priority IN (...)) | Enforce valid priority values |
| NOT NULL (title, status, priority) | Ensure required fields present |
| NOT NULL (created_at, updated_at) | Audit trail completeness |

---

## State Transitions

### Task Status States (unchanged)

```
┌─────────────┐
│  INCOMPLETE │ ← Default on creation
└────────┬────┘
         │
         │ Mark Complete (PATCH)
         ↓
┌─────────────┐
│  COMPLETE   │
└────────┬────┘
         │
         │ Mark Incomplete (via PUT) [Note: not explicitly in spec, but reasonable]
         ↓
       INCOMPLETE
```

### Priority States (NEW)

```
Priority state is independent of status state.
A task can be:
- incomplete + high priority
- complete + high priority
- incomplete + low priority
- complete + low priority

Priority can change at any time:
- low ←→ medium ←→ high
- Can be updated during task creation
- Can be updated independently via PUT endpoint
```

---

## Backward Compatibility

### Handling Existing Tasks

**Before Migration**: Tasks created without priority field

**After Migration**: All existing tasks receive `priority = "medium"` via:
1. **Database Migration**: UPDATE statement sets all null priorities to 'medium'
2. **API Handling**: If priority is null (shouldn't happen), treat as "medium"
3. **Frontend**: Displays all existing tasks with medium priority indicator

**Example**:
```
Before:  task { id: 1, title: "Buy milk", status: "incomplete" }
After:   task { id: 1, title: "Buy milk", status: "incomplete", priority: "medium" }
```

---

## Query Patterns

### Sorting by Priority

**Default Sort** (no sort parameter):
- Primary: created_at DESC (newest first)
- Priority field ignored unless explicitly requested

**Priority Sort** (?sort=priority):
- Primary: priority DESC (High → Medium → Low)
  - High: sort_order = 3
  - Medium: sort_order = 2
  - Low: sort_order = 1
- Secondary: created_at DESC (newest first within same priority)

**Implementation Pseudocode**:
```python
if sort == "priority":
    # Map priority strings to sortable integers
    priority_order = {"high": 3, "medium": 2, "low": 1}
    tasks = tasks.order_by(
        lambda t: (-priority_order[t.priority], -t.created_at.timestamp())
    )
else:
    tasks = tasks.order_by(-created_at)
```

### Filtering (Existing Pattern)

```
GET /api/{user_id}/tasks?status=incomplete
  → Returns only incomplete tasks (regardless of priority)

GET /api/{user_id}/tasks?status=incomplete&sort=priority
  → Returns incomplete tasks sorted by priority
```

---

## SQLModel Implementation

### Python Model Definition

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime

class PriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str  # From JWT token
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)
    status: str = Field(default="incomplete")  # "incomplete" or "complete"
    priority: PriorityEnum = Field(
        default=PriorityEnum.MEDIUM,
        sa_column_kwargs={"nullable": False}
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Add database constraints
    __table_args__ = (
        # No need to explicitly define foreign key here; handled by ORM relationship
    )
```

### Pydantic Schema Definitions

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)
    priority: Optional[str] = Field(default="medium")

    @field_validator('priority', mode='before')
    @classmethod
    def normalize_priority(cls, v):
        if v is None:
            return "medium"
        if isinstance(v, str):
            normalized = v.lower().strip()
            if normalized not in ["low", "medium", "high"]:
                raise ValueError(
                    "Priority must be 'low', 'medium', or 'high'"
                )
            return normalized
        raise ValueError("Priority must be a string")

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)
    priority: Optional[str] = None

    @field_validator('priority', mode='before')
    @classmethod
    def normalize_priority(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            normalized = v.lower().strip()
            if normalized not in ["low", "medium", "high"]:
                raise ValueError(
                    "Priority must be 'low', 'medium', or 'high'"
                )
            return normalized
        raise ValueError("Priority must be a string")

class TaskResponse(BaseModel):
    id: int
    user_id: str
    title: str
    description: Optional[str]
    status: str
    priority: str  ← NEW FIELD
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

---

## Database Migration

### Alembic Migration File

**File**: `backend/alembic/versions/add_priority_to_tasks.py`

```python
"""Add priority field to tasks table

Revision ID: 002_add_priority
Revises: 001_create_tasks
Create Date: 2026-01-17

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '002_add_priority'
down_revision = '001_create_tasks'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Step 1: Add nullable column
    op.add_column('tasks', sa.Column('priority', sa.String(10), nullable=True))

    # Step 2: Set default for existing rows
    op.execute("UPDATE tasks SET priority = 'medium' WHERE priority IS NULL")

    # Step 3: Make non-nullable
    op.alter_column('tasks', 'priority', nullable=False)

    # Step 4: Add check constraint
    op.create_check_constraint(
        'check_priority',
        'tasks',
        "priority IN ('low', 'medium', 'high')"
    )

def downgrade() -> None:
    # Remove check constraint
    op.drop_constraint('check_priority', 'tasks', type_='check')

    # Drop column
    op.drop_column('tasks', 'priority')
```

---

## Summary of Changes

| Aspect | Before | After | Change Type |
|--------|--------|-------|------------|
| Task fields | 7 fields | 8 fields | Addition |
| Default sort | created_at DESC | created_at DESC | Unchanged |
| Priority sort | N/A | priority DESC + created_at DESC | New capability |
| API contracts | No priority field | Includes priority | Extension |
| Database schema | 7 columns | 8 columns (+ check constraint) | Additive |
| Validation | title, description | + priority field | Extended |
| Backward compat | N/A | All existing tasks → "medium" | Preserved |

---

## Notes

- Priority field is **independent** of status field (task can be completed high priority or incomplete low priority)
- Default priority "medium" is sensible neutral choice
- All changes are **backward compatible** (optional in requests, populated by default)
- No breaking changes to existing code (priority is additive)
- Database migration is **safe** (two-step approach handles existing data)

