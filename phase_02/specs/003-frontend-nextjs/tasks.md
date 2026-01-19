# Tasks: Frontend Application (Next.js)

**Input**: Design documents from `/specs/003-frontend-nextjs/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md (Phase 0), data-model.md (Phase 1), contracts/ (Phase 1)

**Organization**: Tasks are grouped by user story (P1 stories first, then P2 stories) to enable independent implementation and testing. Each story is independently testable and can be verified against the spec's acceptance scenarios.

**Total Tasks**: 52 tasks across 9 phases
**MVP Scope**: User Stories 1-4 (P1 stories: registration, sign-in, task list, create task)
**Extended Scope**: User Stories 5-8 (P2 stories: edit, complete, delete, sign-out) + 9-10 (responsiveness)

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no blocking dependencies)
- **[Story]**: Which user story this task belongs to (e.g., [US1], [US2])
- Include exact file paths in descriptions

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize Next.js project, configure dependencies, set up project structure

- [x] T001 Initialize Next.js 16+ project with TypeScript, TailwindCSS, ESLint, and App Router
- [x] T002 Initialize TypeScript configuration in `frontend/tsconfig.json` with strict mode enabled
- [x] T003 [P] Configure Tailwind CSS in `frontend/tailwind.config.ts` with custom theme and breakpoints
- [x] T004 [P] Configure Next.js in `frontend/next.config.ts` with App Router settings
- [x] T005 Create `.env.example` with required environment variables (NEXT_PUBLIC_API_BASE_URL, NEXT_PUBLIC_BETTER_AUTH_SECRET)
- [x] T006 [P] Create project folder structure: app/, components/, lib/, public/, styles/ per plan.md
- [x] T007 Initialize package.json dependencies (better-auth, tailwindcss, typescript)
- [x] T008 Create `frontend/README.md` with setup and running instructions

**Checkpoint**: Next.js project initialized and ready for foundational infrastructure

---

## Phase 2: Foundational (Core Infrastructure)

**Purpose**: Implement core infrastructure that blocks all user story work

**⚠️ CRITICAL**: All tasks in this phase must complete before any user story implementation begins

- [x] T009 [P] Create auth context in `frontend/src/lib/auth/auth-context.tsx` with AuthContext interface and provider
- [x] T010 [P] Create `frontend/src/lib/auth/useAuth.ts` custom hook to access auth context from components
- [x] T011 [P] Create `frontend/src/lib/api/types.ts` with TypeScript types for API responses (User, Task, AuthError)
- [x] T012 [P] Create centralized API client in `frontend/src/lib/api/client.ts` with:
  - Fetch wrapper with automatic Authorization header injection
  - 401 error handling (redirect to signin)
  - JSON parsing and error serialization
  - Base URL from NEXT_PUBLIC_API_BASE_URL
- [x] T013 Create `frontend/src/lib/auth/better-auth-config.ts` with Better Auth initialization and JWT configuration
- [x] T014 Create `frontend/src/lib/auth/jwt-storage.ts` with JWT token storage/retrieval functions (HttpOnly cookie strategy)
- [x] T015 [P] Create global error boundary in `frontend/src/app/error.tsx` for error handling
- [x] T016 [P] Create global styles in `frontend/src/styles/globals.css` with Tailwind directives and base styles
- [x] T017 [P] Create CSS variables in `frontend/src/styles/variables.css` for theme colors and spacing
- [x] T018 Create `frontend/src/middleware.ts` for Next.js route protection (redirect unauthenticated users to signin)
- [x] T019 [P] Create reusable UI components:
  - `frontend/src/components/common/Button.tsx` (responsive, accessible button)
  - `frontend/src/components/common/Input.tsx` (form input with validation feedback)
  - `frontend/src/components/common/ErrorAlert.tsx` (error message display)
  - `frontend/src/components/common/LoadingSpinner.tsx` (loading indicator)
- [x] T020 [P] Create layout components:
  - `frontend/src/components/layout/Container.tsx` (responsive container wrapper)
  - `frontend/src/components/layout/ResponsiveGrid.tsx` (grid layout)
- [x] T021 Create validation utilities in `frontend/src/lib/validation/auth.ts` (email, password validation rules)
- [x] T022 [P] Create validation utilities in `frontend/src/lib/validation/tasks.ts` (task title/description validation)
- [x] T023 [P] Create utility functions:
  - `frontend/src/utils/classnames.ts` (conditional CSS classes)
  - `frontend/src/utils/formatting.ts` (date formatting, text truncation)

**Checkpoint**: Foundation complete - all core infrastructure in place for user story implementation

---

## Phase 3: User Story 1 - User Registration via Sign-Up Form (Priority: P1) 🎯 MVP

**Goal**: Implement complete sign-up flow allowing new users to create accounts with email/password and receive JWT tokens

**Independent Test**: Can be fully verified by (1) visiting /auth/signup, (2) entering valid email and password, (3) confirming form submits to Better Auth, (4) verifying JWT token is stored, (5) confirming redirect to /tasks (US3), (6) confirming error handling for duplicate email and invalid password

- [x] T024 [P] [US1] Create sign-up form validation in `frontend/src/lib/validation/auth.ts`:
  - Email format validation
  - Password minimum 8 characters
  - Real-time error message display
- [x] T025 [US1] Create `frontend/src/components/auth/SignUpForm.tsx` component with:
  - Email and password inputs
  - Client-side validation with error messages
  - Submit button with loading state
  - "Already have an account?" link to signin
- [x] T026 [US1] Create `frontend/src/app/(auth)/layout.tsx` with centered form layout (no navbar)
- [x] T027 [US1] Create `frontend/src/app/(auth)/signup/page.tsx` page with:
  - SignUpForm component
  - Better Auth sign-up call on form submit
  - Error display from Better Auth
  - Redirect to /tasks on success
- [x] T028 [US1] Integrate Better Auth in `frontend/src/lib/auth/auth-context.tsx`:
  - signUp function calling Better Auth
  - JWT token storage after signup
  - Global loading state during signup
  - Error state with user-friendly messages

**Checkpoint**: User Story 1 complete - users can sign up with email/password and receive JWT tokens

---

## Phase 4: User Story 2 - User Sign-In via Login Form (Priority: P1) 🎯 MVP

**Goal**: Implement sign-in flow allowing existing users to authenticate and receive JWT tokens for API access

**Independent Test**: Can be fully verified by (1) visiting /auth/signin, (2) entering valid email and password, (3) confirming JWT token is stored, (4) confirming redirect to /tasks, (5) verifying token is included in subsequent API requests

- [x] T029 [P] [US2] Create `frontend/src/components/auth/SignInForm.tsx` component with:
  - Email and password inputs
  - Client-side validation with error messages
  - Submit button with loading state
  - "Don't have an account?" link to signup
- [x] T030 [US2] Create `frontend/src/app/(auth)/signin/page.tsx` page with:
  - SignInForm component
  - Better Auth sign-in call on form submit
  - Error display from Better Auth
  - Redirect to /tasks on success
  - Redirect to /auth/signup if accessing without account
- [x] T031 [US2] Extend Better Auth in auth context with:
  - signIn function calling Better Auth
  - JWT token storage after signin
  - Error handling for invalid credentials
- [x] T032 [US2] Create `frontend/src/lib/auth/useAuth.ts` to expose:
  - currentUser (from JWT)
  - isAuthenticated (boolean)
  - signIn/signUp/signOut functions
  - error state

**Checkpoint**: User Story 2 complete - users can sign in and receive JWT tokens for authenticated API access

---

## Phase 5: User Story 3 - View Task List with Real Backend State (Priority: P1) 🎯 MVP

**Goal**: Implement task list page that fetches and displays user's tasks from backend API with real data

**Independent Test**: Can be fully verified by (1) signing in successfully, (2) confirming redirect to /tasks, (3) confirming GET /api/{user_id}/tasks is called with JWT token, (4) displaying all user's tasks in UI, (5) showing empty state when no tasks, (6) verifying multi-user isolation (different users see different tasks)

- [x] T033 [P] [US3] Create `frontend/src/lib/hooks/useAsync.ts` custom hook for managing async state:
  - Loading state
  - Error state
  - Data state
  - Retry logic
- [x] T034 [P] [US3] Create `frontend/src/lib/hooks/useTasks.ts` custom hook with:
  - fetchTasks(userId) - GET /api/{user_id}/tasks
  - createTask(userId, data) - POST (for US4)
  - updateTask(userId, id, data) - PUT (for US5)
  - deleteTask(userId, id) - DELETE (for US7)
  - completeTask(userId, id) - PATCH (for US6)
- [x] T035 [P] [US3] Create task UI components:
  - `frontend/src/components/tasks/TaskList.tsx` - renders array of TaskItem components
  - `frontend/src/components/tasks/TaskItem.tsx` - single task display with title, status, date
  - `frontend/src/components/tasks/EmptyState.tsx` - "No tasks yet" message with create button
- [x] T036 [US3] Create `frontend/src/app/(dashboard)/layout.tsx` with:
  - Navbar component with user info and sign-out button
  - Main content area
  - Responsive layout
- [x] T037 [US3] Create `frontend/src/components/common/Navbar.tsx` with:
  - Current user info display
  - Sign-out button
  - Logo and branding
  - Responsive mobile menu (hamburger)
- [x] T038 [US3] Create `frontend/src/app/(dashboard)/tasks/page.tsx` with:
  - useTasks hook to fetch tasks
  - Display TaskList or EmptyState based on tasks array
  - Loading spinner while fetching
  - Error display with retry
  - Extract user_id from auth context for API call

**Checkpoint**: User Story 3 complete - users can view their task list populated from backend API

---

## Phase 6: User Story 4 - Create New Task via Form (Priority: P1) 🎯 MVP

**Goal**: Implement task creation allowing users to add new tasks to their list via form submission

**Independent Test**: Can be fully verified by (1) signing in, (2) visiting /tasks or /tasks/new, (3) accessing task creation form, (4) entering task title and submitting, (5) confirming POST request includes JWT token, (6) verifying new task appears in list, (7) validating empty title is rejected

- [x] T039 [P] [US4] Create `frontend/src/components/tasks/TaskForm.tsx` component with:
  - Title input (required)
  - Description textarea (optional)
  - Submit and cancel buttons
  - Loading state during submission
  - Error display
  - Pre-populated fields for editing (for US5)
- [x] T040 [US4] Create `frontend/src/app/(dashboard)/tasks/new/page.tsx` page with:
  - TaskForm component
  - useTasks.createTask on form submit
  - Redirect to /tasks on success
  - Show error if creation fails
- [x] T041 [US4] Extend task list page with:
  - "Create Task" button on task list page
  - Click opens modal or navigates to /tasks/new
  - After creation, task appears in list or list is refreshed
- [x] T042 [US4] Update useTasks hook to:
  - Implement createTask function
  - Handle optimistic UI update (show new task immediately)
  - Handle API response with created task ID

**Checkpoint**: User Story 4 complete - users can create new tasks via form and see them in list

---

## Phase 7: User Story 5 - Edit and Update Existing Tasks (Priority: P2)

**Goal**: Implement task editing allowing users to modify task title and description

**Independent Test**: Can be fully verified by (1) creating a task (US4), (2) clicking edit on task, (3) updating title/description, (4) confirming PUT request, (5) verifying task list updated without refresh

- [] T043 [P] [US5] Create `frontend/src/app/(dashboard)/tasks/[taskId]/page.tsx` with:
  - Fetch single task on load
  - TaskForm component in edit mode (populated with task data)
  - useTasks.updateTask on form submit
  - Redirect to /tasks on success
  - Show 404 if task not found
- [] T044 [US5] Update TaskItem component with:
  - Edit button that navigates to /tasks/{id}
  - Show error if task is deleted while editing
- [] T045 [US5] Extend useTasks hook with:
  - updateTask function (PUT /api/{user_id}/tasks/{id})
  - Handle 404 (task belongs to different user)
  - Optimistic UI update

**Checkpoint**: User Story 5 complete - users can edit tasks

---

## Phase 8: User Story 6 - Mark Tasks Complete/Incomplete (Priority: P2)

**Goal**: Implement task completion toggle allowing users to mark tasks as done

**Independent Test**: Can be fully verified by (1) creating a task (US4), (2) clicking completion checkbox, (3) confirming PATCH request, (4) verifying UI updates, (5) clicking again to mark incomplete

- [] T046 [P] [US6] Update TaskItem component with:
  - Completion checkbox/button
  - Visual styling for completed tasks (strikethrough)
  - Disable during request
- [] T047 [US6] Extend useTasks hook with:
  - completeTask function (PATCH /api/{user_id}/tasks/{id}/complete)
  - Optimistic UI update (toggle checkbox immediately)
  - Error rollback if API fails

**Checkpoint**: User Story 6 complete - users can mark tasks complete/incomplete

---

## Phase 9: User Story 7 - Delete Tasks (Priority: P2)

**Goal**: Implement task deletion allowing users to permanently remove tasks

**Independent Test**: Can be fully verified by (1) creating a task (US4), (2) clicking delete button, (3) confirming deletion, (4) verifying task removed from list, (5) verifying DELETE request sent

- [] T048 [P] [US7] Update TaskItem component with:
  - Delete button with confirmation dialog
  - Disable button during deletion
  - Show error if deletion fails
- [] T049 [US7] Extend useTasks hook with:
  - deleteTask function (DELETE /api/{user_id}/tasks/{id})
  - Remove task from list optimistically
  - Error rollback if API fails

**Checkpoint**: User Story 7 complete - users can delete tasks

---

## Phase 10: User Story 8 - Sign Out and Session Management (Priority: P1) 🎯 MVP

**Goal**: Implement sign-out flow allowing users to clear JWT tokens and end sessions

**Independent Test**: Can be fully verified by (1) signing in, (2) clicking sign-out button, (3) confirming JWT token cleared, (4) verifying redirect to /auth/signin, (5) confirming protected routes inaccessible without token

- [x] T050 [P] [US8] Create `frontend/src/app/(dashboard)/profile/page.tsx` page with:
  - User profile info display
  - Sign-out button
  - Simple layout
- [x] T051 [US8] Update Navbar component to:
  - Show "Sign Out" option (or link to profile)
  - Call signOut on click
  - Redirect to /auth/signin
- [x] T052 [US8] Extend auth context with:
  - signOut function that:
    - Calls Better Auth sign-out
    - Clears JWT token from storage
    - Resets auth state
    - Redirects to /auth/signin

**Checkpoint**: User Story 8 complete - users can sign out and sessions are terminated

---

## Phase 11: User Story 9 - Responsive Design and Mobile Compatibility (Priority: P2)

**Goal**: Ensure application is fully responsive on mobile, tablet, and desktop screens

**Independent Test**: Can be fully verified by (1) opening app on mobile (320px), (2) navigating all pages, (3) confirming touch targets ≥44px, (4) verifying no horizontal scrolling, (5) testing on tablet (768px) and desktop (1024px+)

- [ ] T053 [P] [US9] Update all pages for responsive design:
  - Mobile first layout (320px)
  - Single column for mobile
  - Two-column for tablet (768px)
  - Multi-column for desktop (1024px+)
- [ ] T054 [P] [US9] Update all components for touch-friendly sizing:
  - Buttons minimum 44px × 44px (mobile), 40px (tablet/desktop)
  - Input fields minimum 44px height
  - Form gaps 16px (mobile), 20px (tablet/desktop)
- [ ] T055 [P] [US9] Update Tailwind configuration with responsive utilities:
  - Mobile breakpoint: 320px (default)
  - Tablet breakpoint: 768px
  - Desktop breakpoint: 1024px
  - Apply `sm:`, `md:`, `lg:` prefixes to responsive classes
- [ ] T056 [US9] Test responsive design:
  - Browser dev tools at each breakpoint
  - Touch interaction on mobile devices (or emulator)
  - Verify no horizontal scrolling at any breakpoint

**Checkpoint**: User Story 9 complete - application is fully responsive

---

## Phase 12: User Story 10 - Unauthorized Access Redirects to Sign-In (Priority: P1) 🎯 MVP

**Goal**: Implement route protection and error handling for unauthorized access

**Independent Test**: Can be fully verified by (1) navigating to /tasks without signin, (2) confirming redirect to /auth/signin, (3) simulating 401 response, (4) verifying automatic redirect, (5) verifying 404 responses don't leak user data

- [x] T057 [P] [US10] Enhance middleware.ts to:
  - Check for JWT token on protected routes
  - Redirect to /auth/signin if missing
  - Redirect to /auth/signin if invalid
  - Allow public routes (/auth/\*)
- [x] T058 [P] [US10] Update API client to:
  - Detect 401 responses from backend
  - Clear JWT token on 401
  - Redirect to /auth/signin on 401
  - Show user-friendly error message
- [x] T059 [US10] Create `frontend/src/components/auth/ProtectedRoute.tsx` wrapper for protected pages
- [x] T060 [US10] Update auth context to:
  - Handle 401 responses globally
  - Clear auth state
  - Trigger redirect to signin

**Checkpoint**: User Story 10 complete - unauthorized access properly handled

---

## Phase 13: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements, documentation, and validation

- [ ] T061 [P] Run `npm run build` to verify TypeScript compilation with no errors
- [ ] T062 [P] Run ESLint and Prettier on all source files in frontend/src/
- [ ] T063 [P] Update `frontend/README.md` with:
  - Setup instructions
  - Environment variable configuration
  - Running development server
  - Building for production
  - Troubleshooting guide
- [ ] T064 [P] Create `frontend/ARCHITECTURE.md` documenting:
  - Project structure rationale
  - Authentication flow
  - API client pattern
  - Component hierarchy
  - State management approach
- [ ] T065 Test end-to-end user journey:
  - Sign up new user
  - Create multiple tasks
  - Edit a task
  - Mark tasks complete
  - Delete a task
  - Sign out
  - Sign in as same user
  - Verify tasks persist
  - Sign in as different user
  - Verify no cross-user data
- [ ] T066 [P] Run quickstart.md validation:
  - Follow setup steps exactly
  - Verify all commands work
  - Update docs if needed
- [ ] T067 Performance optimization:
  - Remove unused dependencies
  - Tree-shake unused code
  - Optimize bundle size
  - Verify page load <2s (desktop), <3s (mobile)
- [ ] T068 [P] Accessibility audit:
  - Verify keyboard navigation works
  - Check color contrast ratios
  - Test with screen reader
  - Verify form labels
- [ ] T069 Security validation:
  - Verify JWT token never in localStorage
  - Verify HttpOnly cookie strategy works
  - Verify no hardcoded credentials
  - Verify 401/404 error messages don't leak data

**Checkpoint**: Application complete, polished, and production-ready

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately ✅
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user story work**
- **User Stories (Phases 3-12)**: All depend on Foundational completion
  - P1 Stories (1, 2, 3, 4, 8, 10): Implement in order (critical for MVP)
  - P2 Stories (5, 6, 7, 9): Can follow after P1 stories or run in parallel
- **Polish (Phase 13)**: Depends on all user stories being complete

### User Story Completion Order (Sequential)

1. **US1 (Sign-Up)** - P1: Required for any user to access system
2. **US2 (Sign-In)** - P1: Required for returning users
3. **US3 (View Tasks)** - P1: Core value proposition
4. **US4 (Create Tasks)** - P1: MVP functionality
5. **US8 (Sign-Out)** - P1: Session management (can run parallel to 3/4)
6. **US10 (Auth Redirects)** - P1: Security (runs throughout)
7. **US5 (Edit Tasks)** - P2: Enhanced UX
8. **US6 (Complete Tasks)** - P2: Enhanced UX
9. **US7 (Delete Tasks)** - P2: Full CRUD
10. **US9 (Responsive)** - P2: Mobile support

### Parallel Opportunities Within Phases

**Phase 1 (Setup)**:

- T003, T004, T006, T007 can run in parallel (different files)

**Phase 2 (Foundational)**:

- T009-T023: Many tasks marked [P] can run in parallel
  - Auth infrastructure (T009-T014) parallel
  - UI components (T019) parallel
  - Utilities (T020-T022) parallel
  - After foundational complete, all user story implementation can proceed in parallel by different team members

**Within Each User Story**:

- Component creation tasks marked [P] can run in parallel
- Tests marked [P] can run in parallel before implementation

### Within-Phase Execution Example (Phase 3: US1)

```
Sequential Phase 3 (strict order):
  T024 → (validation rules ready)
  T025 → (form ready)
  T026 → (auth layout ready)
  T027 → (signup page ready)
  T028 → (auth context updated)

Parallel Opportunities:
  T024 and T025 can start together (form component uses completed validation)
  T026 can start anytime (layout independent)
```

---

## MVP Scope & Incremental Delivery

### MVP (Minimum Viable Product)

Complete these user stories to have a working application:

- **Phase 1**: Setup ✅
- **Phase 2**: Foundational ✅
- **Phase 3**: US1 (Sign-Up) ✅
- **Phase 4**: US2 (Sign-In) ✅
- **Phase 5**: US3 (Task List) ✅
- **Phase 6**: US4 (Create Task) ✅
- **Phase 8**: US8 (Sign-Out) ✅
- **Phase 12**: US10 (Auth Redirects) ✅

**MVP Task Count**: 31 tasks (T001-T028 + T050-T060)

**MVP Deliverable**: Users can sign-up, sign-in, create tasks, view tasks, and sign-out. All API requests include JWT tokens. Unauthorized access is prevented.

### Phase 1 Enhancement

After MVP, add:

- **Phase 7**: US5 (Edit Tasks) - 3 tasks
- **Phase 8**: US6 (Complete Tasks) - 2 tasks
- **Phase 9**: US7 (Delete Tasks) - 2 tasks

**Task Count**: +7 tasks (total 38)

**Deliverable**: Full CRUD operations for task management

### Phase 2 Enhancement

After Phase 1, add:

- **Phase 11**: US9 (Responsive Design) - 4 tasks
- **Phase 13**: Polish - 9 tasks

**Task Count**: +13 tasks (total 51)

**Deliverable**: Fully responsive application ready for production

---

## Task Execution Summary

| Phase     | Focus          | Task Count   | Blocking? | Status             |
| --------- | -------------- | ------------ | --------- | ------------------ |
| 1         | Setup          | 8            | No        | Ready ✅           |
| 2         | Foundational   | 15           | **YES**   | Blocks all stories |
| 3         | US1 Sign-Up    | 5            | No        | After Phase 2      |
| 4         | US2 Sign-In    | 4            | No        | After Phase 2      |
| 5         | US3 Task List  | 6            | No        | After Phase 2      |
| 6         | US4 Create     | 4            | No        | After Phase 2      |
| 7         | US5 Edit       | 3            | No        | After Phase 2      |
| 8         | US6 Complete   | 2            | No        | After Phase 2      |
| 9         | US7 Delete     | 2            | No        | After Phase 2      |
| 10        | US8 Sign-Out   | 3            | No        | After Phase 2      |
| 11        | US9 Responsive | 4            | No        | After Phase 2      |
| 12        | US10 Auth      | 4            | No        | After Phase 2      |
| 13        | Polish         | 9            | No        | After stories      |
| **TOTAL** |                | **69 tasks** |           |                    |

---

## Checklist Format Validation

All tasks follow the strict format:

```
- [ ] [ID] [P?] [Story?] Description with file path
```

Examples from this task list:

✅ `- [ ] T001 Create Next.js 16+ project` (simple setup task)
✅ `- [ ] T009 [P] [US1] Create auth context in frontend/src/lib/auth/auth-context.tsx` (parallelizable story task)
✅ `- [ ] T024 [P] [US4] Create sign-up form validation in frontend/src/lib/validation/auth.ts` (parallelizable within story)

All tasks include:

1. Checkbox `- [ ]`
2. Task ID (T001-T069)
3. Parallelization marker [P] (where applicable)
4. Story label [US1]-[US10] (where applicable)
5. Clear description with file path
