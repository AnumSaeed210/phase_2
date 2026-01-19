# API Contracts: Task Priorities

**Feature**: 005-task-priorities
**Date**: 2026-01-17
**Based on**: data-model.md + spec.md requirements

## Overview

This document defines the API contracts (request/response schemas) for task priority endpoints. All endpoints follow RESTful conventions established in Spec 001.

---

## Endpoint Summary

| Method | Endpoint | Purpose | Change |
|--------|----------|---------|--------|
| POST | `/api/{user_id}/tasks` | Create task with priority | **UPDATED** - accept optional priority |
| PUT | `/api/{user_id}/tasks/{id}` | Update task (including priority) | **UPDATED** - accept optional priority |
| GET | `/api/{user_id}/tasks/{id}` | Get single task | **UPDATED** - returns priority |
| GET | `/api/{user_id}/tasks` | List all tasks (optional sort) | **UPDATED** - support ?sort=priority |

---

## 1. POST /api/{user_id}/tasks - Create Task with Priority

### Request

**Method**: POST
**Path**: `/api/{user_id}/tasks`
**Auth**: Required (JWT token in Authorization header)

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Body** (application/json):
```json
{
  "title": "string (required, 1-255 chars)",
  "description": "string (optional, max 5000 chars)",
  "priority": "string (optional: 'low'|'medium'|'high', default: 'medium')"
}
```

**Examples**:

With priority specified:
```json
{
  "title": "Deploy to production",
  "description": "Deploy latest release to production environment",
  "priority": "high"
}
```

Without priority (defaults to medium):
```json
{
  "title": "Review PR #1234",
  "description": null
}
```

Case-insensitive priority:
```json
{
  "title": "Update documentation",
  "priority": "HIGH"  ← Will be normalized to "high"
}
```

### Response

**Status Code**: 201 Created

**Body** (application/json):
```json
{
  "id": 123,
  "user_id": "user_abc123",
  "title": "Deploy to production",
  "description": "Deploy latest release to production environment",
  "status": "incomplete",
  "priority": "high",
  "created_at": "2026-01-17T14:30:00Z",
  "updated_at": "2026-01-17T14:30:00Z"
}
```

### Error Responses

**400 Bad Request** - Invalid input:
```json
{
  "error": "Title is required"
}
```
or
```json
{
  "error": "Priority must be 'low', 'medium', or 'high'"
}
```

**401 Unauthorized** - Missing/invalid auth token:
```json
{
  "error": "Unauthorized"
}
```

**403 Forbidden** - User mismatch (authenticated user ≠ path user_id):
```json
{
  "error": "Forbidden"
}
```

---

## 2. PUT /api/{user_id}/tasks/{id} - Update Task Priority

### Request

**Method**: PUT
**Path**: `/api/{user_id}/tasks/{id}`
**Auth**: Required (JWT token)

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Body** (application/json):
```json
{
  "title": "string (optional, 1-255 chars)",
  "description": "string (optional, max 5000 chars)",
  "priority": "string (optional: 'low'|'medium'|'high')"
}
```

**Examples**:

Update only priority:
```json
{
  "priority": "high"
}
```

Update priority and title:
```json
{
  "title": "Updated task title",
  "priority": "medium"
}
```

### Response

**Status Code**: 200 OK

**Body** (application/json):
```json
{
  "id": 123,
  "user_id": "user_abc123",
  "title": "Updated task title",
  "description": "Task description",
  "status": "incomplete",
  "priority": "medium",
  "created_at": "2026-01-17T14:30:00Z",
  "updated_at": "2026-01-17T15:45:30Z"
}
```

### Error Responses

**400 Bad Request** - Invalid input:
```json
{
  "error": "Priority must be 'low', 'medium', or 'high'"
}
```

**404 Not Found** - Task doesn't exist or belongs to another user:
```json
{
  "error": "Task not found"
}
```

**401/403** - Same as POST endpoint

---

## 3. GET /api/{user_id}/tasks/{id} - Get Single Task

### Request

**Method**: GET
**Path**: `/api/{user_id}/tasks/{id}`
**Auth**: Required

### Response

**Status Code**: 200 OK

**Body** (application/json):
```json
{
  "id": 123,
  "user_id": "user_abc123",
  "title": "Task title",
  "description": "Task description",
  "status": "incomplete",
  "priority": "high",
  "created_at": "2026-01-17T14:30:00Z",
  "updated_at": "2026-01-17T14:30:00Z"
}
```

**Change**: Response now includes `"priority"` field

### Error Responses

**404 Not Found** - Task doesn't exist:
```json
{
  "error": "Task not found"
}
```

---

## 4. GET /api/{user_id}/tasks - List Tasks (with optional priority sort)

### Request

**Method**: GET
**Path**: `/api/{user_id}/tasks`
**Auth**: Required

**Query Parameters**:
```
?status=incomplete          (existing, filters by status)
&sort=priority              (NEW, sorts by priority)
```

**Examples**:

List all tasks (default sort by created_at):
```
GET /api/{user_id}/tasks
```

List tasks sorted by priority (High → Medium → Low):
```
GET /api/{user_id}/tasks?sort=priority
```

List incomplete tasks sorted by priority:
```
GET /api/{user_id}/tasks?status=incomplete&sort=priority
```

### Response

**Status Code**: 200 OK

**Body** (application/json):
```json
[
  {
    "id": 456,
    "user_id": "user_abc123",
    "title": "Urgent task",
    "description": null,
    "status": "incomplete",
    "priority": "high",
    "created_at": "2026-01-17T14:00:00Z",
    "updated_at": "2026-01-17T14:00:00Z"
  },
  {
    "id": 789,
    "user_id": "user_abc123",
    "title": "Medium priority task",
    "description": "Description here",
    "status": "incomplete",
    "priority": "medium",
    "created_at": "2026-01-17T13:00:00Z",
    "updated_at": "2026-01-17T13:00:00Z"
  },
  {
    "id": 101,
    "user_id": "user_abc123",
    "title": "Low priority task",
    "description": null,
    "status": "incomplete",
    "priority": "low",
    "created_at": "2026-01-17T12:00:00Z",
    "updated_at": "2026-01-17T12:00:00Z"
  }
]
```

**Sorting Behavior** (?sort=priority):
- Primary sort: `priority DESC` (High → Medium → Low)
- Secondary sort: `created_at DESC` (newest first within same priority)

**Result when requesting /api/{user_id}/tasks?sort=priority**:
- All tasks with priority="high" (ordered by created_at DESC)
- Then all tasks with priority="medium" (ordered by created_at DESC)
- Then all tasks with priority="low" (ordered by created_at DESC)

### Backward Compatibility

**Default (no sort parameter)**:
```
GET /api/{user_id}/tasks
```
Returns tasks sorted by `created_at DESC` (unchanged behavior)

**With sort parameter**:
```
GET /api/{user_id}/tasks?sort=priority
```
Returns tasks sorted by priority descending, then created_at (new behavior)

### Error Responses

**401 Unauthorized** - Missing/invalid token:
```json
{
  "error": "Unauthorized"
}
```

**403 Forbidden** - User mismatch:
```json
{
  "error": "Forbidden"
}
```

---

## Summary of Schema Changes

### Task Response Object

**Before** (Spec 001):
```json
{
  "id": integer,
  "user_id": string,
  "title": string,
  "description": string|null,
  "status": "incomplete"|"complete",
  "created_at": datetime,
  "updated_at": datetime
}
```

**After** (Spec 005):
```json
{
  "id": integer,
  "user_id": string,
  "title": string,
  "description": string|null,
  "status": "incomplete"|"complete",
  "priority": "low"|"medium"|"high",  ← NEW FIELD
  "created_at": datetime,
  "updated_at": datetime
}
```

### Validation Rules Summary

| Field | Create | Update | Values | Default |
|-------|--------|--------|--------|---------|
| title | Required | Optional | 1-255 chars | N/A |
| description | Optional | Optional | 0-5000 chars | null |
| status | Auto-set | Not via this endpoint | incomplete/complete | incomplete |
| priority | Optional | Optional | low/medium/high | medium |
| priority (input) | Case-insensitive | Case-insensitive | Normalized to lowercase | - |

---

## Notes

- All endpoints require authentication (JWT token in Authorization header)
- User ownership is enforced: can only access/modify own tasks
- Priority field is always present in responses (defaults to "medium" if not set)
- Case-insensitive priority input is normalized to lowercase
- Backward compatible: existing code continues to work without changes
- No breaking changes to API contracts (priority is optional/additive)

