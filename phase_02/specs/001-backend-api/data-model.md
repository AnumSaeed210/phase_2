# Data Model & Entity Design

**Feature**: Backend API + Database
**Date**: 2025-01-09
**Specification Reference**: `spec.md` (Key Entities section)

---

## Entity: User

**Purpose**: Represent an authenticated user; provides ownership reference for tasks

**Source**: Defined by Better Auth (external to this backend)

**Attributes**:

| Attribute | Type | Constraints | Purpose |
|-----------|------|-------------|---------|
| `id` | String (VARCHAR) | Primary Key, Required | Unique user identifier from JWT token (UUID or custom format) |
| `email` | String (VARCHAR) | Unique, Required | User email address from Better Auth |

**Relationships**:
- `has_many` Tasks (via Task.user_id foreign key)
  - One user can own many tasks
  - Task creation auto-associates with user_id
  - Implicit relationship; no explicit foreign key table needed in this backend

**Notes**:
- User creation/deletion is NOT handled by this backend (auth service responsibility in Spec 2)
- This backend only reads user_id from authenticated request context
- No user API endpoints in this specification
- User model is imported from Better Auth integration layer

**Database Assumption**:
- Users table created by Better Auth migration or external process
- Tasks table has foreign key constraint: `FOREIGN KEY (user_id) REFERENCES users(id)`

---

## Entity: Task

**Purpose**: Represent a single to-do item owned by a user

**Source**: Defined in this specification; stored in Neon PostgreSQL

**Attributes**:

| Attribute | Type | Constraints | Purpose | Spec Reference |
|-----------|------|-------------|---------|-----------------|
| `id` | Integer (SERIAL) | Primary Key, Auto-increment, Required | Unique task identifier; auto-generated on creation | FR-012 |
| `user_id` | String (VARCHAR) | Foreign Key (users.id), Required | Owner of task; from authenticated context | FR-008, FR-012 |
| `title` | String (VARCHAR) | Max 255 chars, Required, NOT NULL | Task description/title | FR-012, FR-007 |
| `description` | String (VARCHAR) | Max 5000 chars, Optional, NULL | Extended task details | FR-012 |
| `status` | Enum (VARCHAR) | Enum{incomplete, complete}, Required, Default: incomplete | Task completion state | FR-012, US6 |
| `created_at` | Timestamp (TIMESTAMP WITH TIME ZONE) | UTC, Required, Immutable, Auto-set | Creation timestamp; never updated | FR-012, SC-009 |
| `updated_at` | Timestamp (TIMESTAMP WITH TIME ZONE) | UTC, Required, Auto-set, Auto-updated | Last modification timestamp; updates on any change | FR-012, SC-009 |

**Relationships**:
- `belongs_to` User (via user_id foreign key)
  - Many tasks can belong to one user
  - Task always owned by exactly one user
  - Task cannot exist without associated user

**Primary Key**:
```sql
PRIMARY KEY (id)
```

**Foreign Key**:
```sql
FOREIGN KEY (user_id) REFERENCES users(id)
  ON DELETE CASCADE  -- When user deleted, delete their tasks
```

**Indexes**:
```sql
-- Automatic index on primary key
INDEX idx_pk_tasks ON tasks(id)

-- Composite index for efficient user task listing
INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC)
  -- Supports: GET /api/{user_id}/tasks sorted by creation time
  -- Satisfies filter (user_id) + sort (created_at DESC) in single scan

-- Optional index for status filtering (future frontend feature)
INDEX idx_tasks_user_status ON tasks(user_id, status)
  -- Supports: GET /api/{user_id}/tasks?status=complete
```

**Check Constraints**:
```sql
CHECK (LENGTH(title) > 0 AND LENGTH(title) <= 255)
  -- Title must be non-empty and <= 255 characters (FR-007)

CHECK (description IS NULL OR LENGTH(description) <= 5000)
  -- Description must be null or <= 5000 characters (FR-007)

CHECK (status IN ('incomplete', 'complete'))
  -- Status must be one of the enum values
```

**Default Values**:
```sql
status DEFAULT 'incomplete'
  -- New tasks always start as incomplete (FR-012, US1)

created_at DEFAULT CURRENT_TIMESTAMP AT TIME ZONE 'UTC'
  -- Auto-set to current UTC time on creation

updated_at DEFAULT CURRENT_TIMESTAMP AT TIME ZONE 'UTC'
  -- Auto-set to current UTC time on creation; updated on modification
```

**Validation Rules** (from Specification):

| Field | Validation | Error Message | Spec Reference |
|-------|-----------|---|---|
| title | Required | "Title is required" | FR-007, US1 |
| title | Min 1 character | "Title cannot be empty" | FR-007, US4 |
| title | Max 255 characters | "Title must be 255 characters or less" | FR-007, US1 |
| description | Max 5000 characters | "Description must be 5000 characters or less" | FR-007, US4 |
| description | Optional | Can be null | FR-007, US1 |
| status | Enum validation | (enforced at DB level) | FR-012 |
| user_id | Required | (enforced at API layer) | FR-008 |

---

## SQLModel Class Definitions

**Purpose**: SQLModel classes define both database schema and API request/response models

### User Model (Read-Only Reference)

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    """User model - imported from Better Auth; minimal fields for task ownership"""
    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
```

**Note**: User model is defined by Better Auth. This definition is informational.

### Task Model (Database + API)

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    """Task model - database schema and API response"""
    __tablename__ = "tasks"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign Key
    user_id: str = Field(foreign_key="users.id", index=True)

    # Content
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)

    # State
    status: str = Field(default="incomplete")  # Enum: incomplete | complete

    # Timestamps (UTC)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### Request Model: CreateTask

```python
from sqlmodel import SQLModel
from typing import Optional

class TaskCreate(SQLModel):
    """Request model for POST /api/{user_id}/tasks"""

    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)
```

### Request Model: UpdateTask

```python
from sqlmodel import SQLModel
from typing import Optional

class TaskUpdate(SQLModel):
    """Request model for PUT /api/{user_id}/tasks/{id}"""

    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)

    # Validation: at least one field must be provided
    # Handled in API endpoint logic
```

### Response Model: TaskResponse

```python
from sqlmodel import SQLModel
from datetime import datetime

class TaskResponse(SQLModel):
    """Response model for all GET/POST/PUT/PATCH endpoints"""

    id: int
    user_id: str
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
```

### Error Response Model

```python
from sqlmodel import SQLModel

class ErrorResponse(SQLModel):
    """Standard error response for all error cases"""

    error: str
```

---

## State Transitions

### Task Status Lifecycle

```
User creates task
    ↓
Status = "incomplete"
    ↓
User marks task complete (PATCH /api/{user_id}/tasks/{id}/complete)
    ↓
Status = "complete"
    ↓
User can update/delete completed task
User can delete at any status
```

**Valid Transitions**:
- `incomplete` → `complete` (via PATCH /complete)
- `incomplete` → `incomplete` (via PUT update with no status change)
- `complete` → `complete` (via PATCH /complete - idempotent)
- Any status → deleted (via DELETE)

**Invalid Transitions**:
- `complete` → `incomplete` (not supported in spec; could add via future enhancement)

**Implementation Note**: PATCH /complete is idempotent (safe to call multiple times on same task).

---

## Database Relationships Diagram

```
┌─────────────────────────────────────┐
│           User (users)              │
├─────────────────────────────────────┤
│ id (PK, VARCHAR)                    │
│ email (UNIQUE)                      │
└──────────────┬──────────────────────┘
               │
         (1 : N)
               │
               │ user_id (FK)
               │
┌──────────────▼──────────────────────┐
│          Task (tasks)               │
├─────────────────────────────────────┤
│ id (PK, SERIAL)                     │
│ user_id (FK, VARCHAR)               │
│ title (VARCHAR 255)                 │
│ description (VARCHAR 5000, NULL)    │
│ status (ENUM[incomplete|complete])  │
│ created_at (TIMESTAMP UTC)          │
│ updated_at (TIMESTAMP UTC)          │
└─────────────────────────────────────┘
```

---

## SQL Schema Definition

**Generated by SQLModel migrations** (not manually written):

```sql
-- User table (created by Better Auth migration)
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL
);

-- Task table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(5000),
    status VARCHAR NOT NULL DEFAULT 'incomplete',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_tasks_user_id_created_at ON tasks(user_id, created_at DESC);
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
```

---

## Data Constraints & Validation

### Database-Level Constraints

| Constraint | Type | Enforcement | Purpose |
|-----------|------|------------|---------|
| `PRIMARY KEY (id)` | Uniqueness | Database | Ensure each task has unique ID |
| `FOREIGN KEY (user_id)` | Referential integrity | Database | Task must belong to existing user |
| `NOT NULL: user_id, title, status, created_at, updated_at` | Required fields | Database | Ensure critical fields always present |
| `LENGTH(title) > 0 AND <= 255` | Check constraint | Database | Enforce title length limits |
| `LENGTH(description) <= 5000` | Check constraint | Database | Enforce description length limit |
| `status IN (incomplete, complete)` | Check constraint | Database | Enforce valid status values |

### Application-Level Validation (Pydantic)

| Field | Validation | Purpose | Spec Reference |
|-------|-----------|---------|---|
| title | Required, min_length=1, max_length=255 | Pre-database validation | FR-007 |
| description | Optional, max_length=5000 | Pre-database validation | FR-007 |
| TaskUpdate: at least one field | Custom validation | Ensure PUT has something to update | FR-004 |

---

## Uniqueness & Cardinality

| Relationship | Cardinality | Enforced By | Notes |
|------------|---|---|---|
| User → Task | 1 : N | Foreign key constraint | One user owns many tasks |
| Task → User | N : 1 | Foreign key constraint | Many tasks owned by one user |
| Task.id uniqueness | 1 : 1 | Primary key | Each task has unique ID |
| Task.title uniqueness | N : N | None | Multiple tasks can have same title |

---

## Scalability Considerations

**Current Design**:
- SERIAL (32-bit integer) supports ~2 billion tasks per user
- User-scoped queries use composite index (user_id, created_at)
- Timestamps indexed for efficient sorting

**Future Enhancements**:
- Pagination: Add LIMIT/OFFSET to list endpoint (index already supports)
- Full-text search: Add full-text index on title + description if needed
- Tags/Categories: Add junction table tasks_tags(task_id, tag_id)
- Sharing: Add tasks_shared(task_id, shared_with_user_id) table

**No Changes Required to Current Schema** if these features are added later.

