---
id: PHR-014
title: Fix API response mapping and verify full-stack data persistence
stage: green
date: 2026-01-13
surface: agent
model: claude-haiku-4-5-20251001
feature: 002-authentication-jwt
branch: 003-frontend-nextjs
user: ayeshaqadir
command: /sp.phr
labels: ["api-integration", "response-mapping", "database-verification", "frontend-fixes", "data-persistence", "type-mismatch", "full-stack-testing"]
links:
  spec: specs/002-authentication-jwt.md
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/lib/hooks/useTasks.ts
  - frontend/src/utils/formatting.ts
tests:
  - Task creation via browser (optimistic updates)
  - Task fetch from API (with JWT token)
  - Database query verification (Neon)
  - User isolation (multiple users, multiple tasks)
---

## Prompt

User reported two issues after successful login:
1. "After creating a task there's an error: Cannot read properties of undefined (reading 'getTime')" - from `formatRelativeTime()` in formatting utilities
2. "I can't see those on neon db's tables tasks" - concern that tasks weren't persisting to database after creation through browser UI

## Response snapshot

Fixed the API response mapping issue where backend returns snake_case fields but frontend expects camelCase. Verified all data IS correctly persisting to Neon database through direct query inspection.

## Outcome

- ✅ Impact:
  - Fixed TypeError in date formatting by adding null/undefined checks and a data transformation layer
  - Verified full end-to-end data flow: Frontend UI → API → Database
  - Confirmed user isolation is working (each user's tasks correctly linked via user_id)
  - Created 2 new tasks successfully via browser and verified they exist in database

- 🧪 Tests:
  - Manual task creation via browser form
  - API testing with curl/Python (POST /api/{user_id}/tasks)
  - Direct Neon database query: SELECT * FROM users; SELECT * FROM tasks;
  - Verified JWT token injection in Authorization header
  - Verified user authentication state persistence via localStorage

- 📁 Files:
  - frontend/src/lib/hooks/useTasks.ts (added transformTask function for snake_case ↔ camelCase conversion)
  - frontend/src/utils/formatting.ts (added safety checks for undefined dates)

- 🔁 Next prompts:
  - Test complete CRUD operations: edit task, mark complete, delete task
  - Test logout and sign in with different user
  - Test that unauthenticated access redirects to signin

- 🧠 Reflection: The "missing from database" concern was due to optimistic frontend updates - tasks displayed immediately even if POST hadn't confirmed. Direct database inspection revealed all data was correctly persisted, including user isolation via foreign keys and proper timestamp handling.

## Evaluation notes (flywheel)

- Failure modes observed:
  1. TypeError from `formatRelativeTime()` trying to call `.getTime()` on undefined - root cause was API response format mismatch (snake_case vs camelCase)
  2. User concern about data not persisting - actually a false alarm caused by optimistic UI updates masking successful backend transactions
  3. Date formatting assumed valid Date objects but backend returns ISO strings that could fail Date() constructor

- Graders run and results (PASS/FAIL):
  - PASS: Frontend displays tasks immediately after creation (optimistic update)
  - PASS: API POST /api/{user_id}/tasks succeeds with 200-201 status
  - PASS: Database query shows tasks with correct user_id, title, description, status
  - PASS: User isolation working (alice@example.com tasks separate from ayeshaabdulqadir07@gmail.com tasks)
  - PASS: Timestamps (created_at, updated_at) correctly formatted in database as ISO strings
  - PASS: JWT token validation working (Authorization header correctly injected)

- Prompt variant (if applicable): null

- Next experiment (smallest change to try):
  1. Test edit task endpoint: PUT /api/{user_id}/tasks/{id} with updated title/description
  2. Test complete task endpoint: PATCH /api/{user_id}/tasks/{id}/complete
  3. Test delete task endpoint: DELETE /api/{user_id}/tasks/{id}
  4. Test that deleted tasks no longer appear in frontend list

---

## Summary of Full-Stack Data Flow

**Working End-to-End Path:**

```
User creates task in browser
  ↓
TaskForm submits to CreateTaskPage
  ↓
useTasks.createTask(userId, {title, description})
  ↓
apiClient.post(/api/{userId}/tasks, data)
  ↓ JWT token injected in Authorization header
Backend POST /api/{userId}/tasks endpoint
  ↓
TaskService.create_task(user_id, title, description)
  ↓ SQL INSERT INTO tasks
Neon PostgreSQL tasks table
  ↓ Returns Task object (snake_case)
transformTask() converts to camelCase
  ↓
Frontend displays in TaskList (optimistic update already shown)
```

**Database Verification:**

Users table:
- alice@example.com (Alice Smith) - signed up successfully
- ayeshaabdulqadir07@gmail.com - separate user account

Tasks table (29 total):
- ID 30: "Buy groceries" (alice) - 2026-01-13 15:54:35
- ID 31: "task 2" (ayesha) - 2026-01-13 15:59:12
- ID 32: "Test task from API" (alice) - 2026-01-13 16:07:17
- Plus 26 previous test/development tasks

All records properly linked via user_id foreign key. Multi-user isolation confirmed working.
