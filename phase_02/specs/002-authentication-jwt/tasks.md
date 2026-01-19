# Implementation Tasks: Authentication & Security (JWT)

**Feature**: Spec 002 - Authentication & Security (JWT)
**Branch**: `002-authentication-jwt`
**Created**: 2026-01-09
**Plan**: [specs/002-authentication-jwt/plan.md](./plan.md)
**Spec**: [specs/002-authentication-jwt/spec.md](./spec.md)

**Total Tasks**: 52 | **Setup & Foundational**: 7 | **User Stories**: 35 | **Polish & Cross-Cutting**: 10

---

## Executive Summary

This task breakdown implements 7 implementation phases across 6 user stories (5 P1 core + 1 P2 enhancement) for JWT-based stateless authentication connecting Next.js frontend (Better Auth) to FastAPI backend.

**MVP Scope** (P1 Core - fully testable independently):
- User Story 1: Sign-up form + Better Auth integration (frontend)
- User Story 2: Sign-in form + Better Auth integration (frontend)
- User Story 3: Protected endpoints + 401 Unauthorized enforcement (backend)
- User Story 4: User identity extraction + multi-user isolation (backend)
- User Story 5: Stateless verification + shared secret configuration (backend)

**Enhancement** (P2):
- User Story 6: Token expiration + 7-day lifecycle

---

## Phase 1: Setup & Project Initialization

**Objective**: Initialize authentication architecture and configure shared infrastructure for all layers.

### Phase 1 Tasks (7 tasks)

- [X] T001 Create authentication architecture documentation and BETTER_AUTH_SECRET setup guide in `specs/002-authentication-jwt/ARCHITECTURE.md`
- [X] T002 Initialize backend authentication module structure: create `backend/src/auth/` directory with `__init__.py`
- [X] T003 Initialize frontend authentication module structure: create `frontend/src/lib/auth/` directory
- [X] T004 Add PyJWT to backend `requirements.txt` and document JWT library choice in plan.md
- [X] T005 Add python-dotenv to backend `requirements.txt` for environment variable loading
- [X] T006 Create `.env.template` files for frontend and backend with BETTER_AUTH_SECRET placeholder
- [X] T007 Update backend `.env.example` with BETTER_AUTH_SECRET configuration example

---

## Phase 2: Foundational Prerequisites

**Objective**: Implement cross-cutting concerns that enable all user stories.

### Phase 2 Tasks (5 tasks - blocking for all user stories)

- [X] T008 [P] Create JWT validation schema in `backend/src/auth/auth_schemas.py` (request/response models, error responses)
- [X] T009 [P] Create authentication context class in `backend/src/auth/auth_context.py` with AuthenticatedUser model
- [X] T010 [P] Implement JWT validation helper functions in `backend/src/auth/jwt_utils.py` (parse, verify, extract claims)
- [X] T011 Create API client for frontend in `frontend/src/lib/api/client.ts` with Authorization header injection capability
- [X] T012 Create auth context React hook in `frontend/src/lib/auth/auth-context.tsx` for global auth state management

---

## Phase 3: User Story 1 - User Sign Up with Better Auth

**Objective**: Enable new users to create accounts via Better Auth and receive JWT tokens (Frontend Implementation).

**Story Goal**: Users can sign up with email/password, Better Auth creates account, JWT token issued and stored.

**Independent Test Criteria**:
1. Can navigate to `/auth/signup` page without authentication
2. Can enter valid email (e.g., test@example.com) and password (8+ chars)
3. Form submission triggers Better Auth sign-up
4. On success: JWT token received from Better Auth
5. JWT token stored securely in frontend
6. Can verify token is present and contains user identity (sub, email claims)
7. Frontend redirects to app after successful sign-up

### Phase 3 Tasks (6 tasks - [US1] label)

- [ ] T013 [US1] Create Better Auth configuration file in `frontend/src/lib/auth/better-auth-config.ts` with JWT plugin enabled
- [ ] T014 [US1] Create JWT storage utility in `frontend/src/lib/auth/jwt-storage.ts` (save, retrieve, clear functions)
- [ ] T015 [P] [US1] Create sign-up form component in `frontend/src/app/auth/signup/page.tsx` with email/password fields
- [ ] T016 [P] [US1] Implement sign-up form submission logic: call Better Auth, handle errors, store JWT on success
- [ ] T017 [US1] Create auth layout wrapper in `frontend/src/app/auth/layout.tsx` for sign-up/sign-in pages
- [ ] T018 [US1] Add route protection middleware in `frontend/src/middleware.ts` to verify JWT presence on protected routes

---

## Phase 4: User Story 2 - User Sign In with JWT Token Issuance

**Objective**: Enable existing users to authenticate and receive JWT tokens (Frontend Implementation).

**Story Goal**: Users can sign in with credentials, Better Auth validates, JWT token issued and stored for API calls.

**Independent Test Criteria**:
1. Can navigate to `/auth/signin` page without authentication
2. Can enter existing user email and correct password
3. Form submission triggers Better Auth sign-in
4. On success: JWT token received from Better Auth
5. JWT token stored securely in frontend
6. Can verify token is present and valid
7. Frontend redirects to app after successful sign-in
8. Invalid password shows error message
9. Non-existent email shows error message

### Phase 4 Tasks (5 tasks - [US2] label)

- [ ] T019 [P] [US2] Create sign-in form component in `frontend/src/app/auth/signin/page.tsx` with email/password fields
- [ ] T020 [P] [US2] Implement sign-in form submission logic: call Better Auth, validate credentials, store JWT on success
- [ ] T021 [US2] Add sign-in error handling in frontend (display error messages for invalid credentials)
- [ ] T022 [US2] Add sign-out functionality in `frontend/src/lib/auth/auth-context.tsx` (clear JWT and redirect to sign-in)
- [ ] T023 [US2] Create JWT refresh/renewal logic in auth context (handle token updates after sign-in)

---

## Phase 5: User Story 3 - Protected API Endpoints Require JWT

**Objective**: Protect all 6 backend API endpoints from Spec 001 with JWT validation (Backend Implementation).

**Story Goal**: All API requests without valid JWT receive 401 Unauthorized. Valid JWT requests are processed.

**Independent Test Criteria**:
1. POST /api/{user_id}/tasks without JWT → 401 Unauthorized
2. GET /api/{user_id}/tasks without JWT → 401 Unauthorized
3. GET /api/{user_id}/tasks/{id} without JWT → 401 Unauthorized
4. PUT /api/{user_id}/tasks/{id} without JWT → 401 Unauthorized
5. PATCH /api/{user_id}/tasks/{id}/complete without JWT → 401 Unauthorized
6. DELETE /api/{user_id}/tasks/{id} without JWT → 401 Unauthorized
7. All 6 endpoints with valid JWT → request processed (200/201/204 response)
8. Invalid JWT signature → 401 Unauthorized
9. Expired JWT token → 401 Unauthorized
10. Missing Authorization header → 401 Unauthorized

### Phase 5 Tasks (7 tasks - [US3] label)

- [X] T024 [P] [US3] Implement JWT validation middleware in `backend/src/auth/jwt_middleware.py` (extract, parse, verify JWT)
- [X] T025 [US3] Add middleware attachment to FastAPI app in `backend/main.py` (apply JWT middleware to all protected routes)
- [X] T026 [US3] Create dependency injection for JWT validation: `get_current_user()` dependency in `backend/src/auth/jwt_deps.py`
- [X] T027 [P] [US3] Update `/api/{user_id}/tasks` POST endpoint in `backend/src/api/tasks.py` to require JWT (add @require_auth decorator)
- [X] T028 [P] [US3] Update `/api/{user_id}/tasks` GET endpoint in `backend/src/api/tasks.py` to require JWT
- [X] T029 [P] [US3] Update `/api/{user_id}/tasks/{id}` endpoints (GET, PUT, DELETE, PATCH) to require JWT
- [X] T030 [US3] Add 401 Unauthorized response handler in `backend/src/auth/error_handlers.py` with appropriate error messages

---

## Phase 6: User Story 4 - JWT Token Contains User Identity

**Objective**: Extract user identity from JWT and enforce multi-user isolation (Backend Authorization).

**Story Goal**: Backend correctly identifies user from JWT token and ensures users can only access their own data.

**Independent Test Criteria**:
1. Valid JWT with user_id="user-001" → backend extracts user_id="user-001"
2. Valid JWT with user_id="user-002" → backend extracts user_id="user-002"
3. User A (with JWT user_id="A") requests GET /api/A/tasks → receives their tasks (200 OK)
4. User A (with JWT user_id="A") requests GET /api/B/tasks → receives 403 Forbidden or 404 Not Found
5. User B attempts to use User A's JWT to GET /api/A/tasks → gets 404 Not Found (JWT identifies User B, not A)
6. Multi-user scenario: Users A, B, C authenticate independently, each accesses only their own data
7. Task ownership validation: user_id from JWT must match {user_id} in request path

### Phase 6 Tasks (8 tasks - [US4] label)

- [X] T031 [US4] Implement user identity extraction from JWT claims in `backend/src/auth/auth_context.py` (extract "sub" or "user_id" claim)
- [X] T032 [P] [US4] Create route parameter validation function in `backend/src/auth/jwt_deps.py` (verify JWT user_id matches route path {user_id})
- [X] T033 [P] [US4] Update all task endpoints to extract authenticated user context and validate ownership
- [X] T034 [US4] Add query filters for all GET/PUT/DELETE/PATCH endpoints: filter tasks by authenticated user_id
- [X] T035 [US4] Implement 403 Forbidden response for ownership mismatch (JWT user_id ≠ route path user_id)
- [X] T036 [US4] Add logging for authorization decisions (log successful authorizations and rejections for debugging)
- [ ] T037 [P] [US4] Add test fixtures for multi-user JWT tokens in `backend/tests/conftest.py`
- [ ] T038 [US4] Create integration tests for multi-user scenarios in `backend/tests/test_multi_user_isolation.py`

---

## Phase 7: User Story 5 - Stateless Authentication with Shared Secret

**Objective**: Implement stateless JWT verification using BETTER_AUTH_SECRET (Infrastructure & Validation).

**Story Goal**: Backend validates JWT using shared secret without database lookups. Same secret enables frontend/backend trust.

**Independent Test Criteria**:
1. BETTER_AUTH_SECRET configured on backend (environment variable)
2. BETTER_AUTH_SECRET configured on frontend (Better Auth configuration)
3. User signs in → receives JWT signed with BETTER_AUTH_SECRET
4. Backend validates JWT signature using BETTER_AUTH_SECRET → succeeds
5. Backend instance restarted → validates same JWT → succeeds (no session lookup)
6. BETTER_AUTH_SECRET changed on backend → same JWT validation fails (403/401)
7. No database queries for JWT validation (stateless verification)
8. BETTER_AUTH_SECRET missing on backend startup → application fails with clear error message

### Phase 7 Tasks (7 tasks - [US5] label)

- [X] T039 [US5] Read BETTER_AUTH_SECRET from environment in `backend/main.py` on startup
- [X] T040 [US5] Add startup validation: fail with clear error message if BETTER_AUTH_SECRET is not configured
- [X] T041 [P] [US5] Implement JWT signature verification using BETTER_AUTH_SECRET in `backend/src/auth/jwt_utils.py`
- [ ] T042 [P] [US5] Configure Better Auth in frontend with BETTER_AUTH_SECRET from environment in `frontend/src/lib/auth/better-auth-config.ts`
- [ ] T043 [US5] Add integration test for stateless verification in `backend/tests/test_stateless_auth.py`
- [ ] T044 [US5] Add integration test: backend restart → same JWT validates successfully
- [ ] T045 [US5] Add integration test: BETTER_AUTH_SECRET mismatch → JWT validation fails

---

## Phase 8: User Story 6 - Token Expiration for Security

**Objective**: Enforce 7-day token expiration and re-authentication (P2 Enhancement).

**Story Goal**: JWT tokens expire after 7 days. Backend rejects expired tokens. Frontend redirects to sign-in.

**Independent Test Criteria**:
1. JWT token with valid exp claim (not expired) → backend accepts (200 OK)
2. JWT token with exp claim in past (expired) → backend rejects (401 Unauthorized)
3. Expired token response includes "Token expired" message
4. Frontend receives 401 with expired token → clears stored JWT
5. Frontend receives 401 with expired token → redirects to /auth/signin
6. New sign-in after expiration → user receives fresh JWT with updated exp
7. Token exp claim set to iat + 7 days (604,800 seconds)
8. Better Auth configured with 7-day expiration policy

### Phase 8 Tasks (5 tasks - [US6] label)

- [X] T046 [P] [US6] Implement JWT expiration validation in `backend/src/auth/jwt_utils.py` (check exp claim)
- [ ] T047 [US6] Configure Better Auth in frontend with 7-day token expiration in `frontend/src/lib/auth/better-auth-config.ts`
- [ ] T048 [US6] Add 401 error handler in frontend auth context: detect expired token and clear JWT
- [ ] T049 [US6] Add 401 error handler in frontend API client: redirect to /auth/signin on expired token
- [ ] T050 [US6] Add integration tests for token expiration in `backend/tests/test_token_expiration.py`

---

## Phase 9: Polish & Cross-Cutting Concerns

**Objective**: Comprehensive testing, documentation, and production readiness.

### Phase 9 Tasks (10 tasks)

- [ ] T051 [P] Create comprehensive JWT validation test suite in `backend/tests/test_jwt_validation.py` (valid/invalid/expired tokens, signature verification)
- [ ] T052 [P] Create protected endpoint test suite in `backend/tests/test_protected_endpoints.py` (401 responses, token injection)
- [ ] T053 Create frontend JWT storage tests in `frontend/tests/auth.test.ts` (save, retrieve, clear JWT)
- [ ] T054 Create frontend API client tests in `frontend/tests/api-client.test.ts` (Authorization header injection)
- [ ] T055 [P] Create multi-user isolation test suite in `backend/tests/test_user_isolation.py` (users A, B, C scenarios)
- [ ] T056 Create Spec 002 implementation documentation in `specs/002-authentication-jwt/IMPLEMENTATION_COMPLETE.md` (completed features, tested endpoints, known limitations)
- [ ] T057 Add error message documentation to backend in `backend/AUTH_ERRORS.md` (401, 403, 422 error codes and messages)
- [ ] T058 Update backend README in `backend/README.md` with authentication requirements for new users
- [ ] T059 Create frontend authentication guide in `frontend/AUTH_SETUP.md` (Better Auth setup, JWT storage, environment configuration)
- [ ] T060 Verify all 15 functional requirements from Spec 002 are implemented (FR-001 through FR-015 checklist)

---

## Task Dependencies & Execution Order

### Critical Path (Blocking Dependencies)

```
Phase 1 Setup (T001-T007)
    ↓
Phase 2 Foundational (T008-T012) [blocks all user stories]
    ↓
Parallel User Story Implementation:
├─ US1 Sign-Up (T013-T018)
├─ US2 Sign-In (T019-T023)
├─ US3 Protected Endpoints (T024-T030)
├─ US4 User Identity (T031-T038)
├─ US5 Stateless Auth (T039-T045)
└─ US6 Token Expiration (T046-T050)
    ↓
Phase 9 Polish & Testing (T051-T060)
```

### Parallel Execution Opportunities

**After Phase 2 (Foundational)**:
- US1 (sign-up) and US2 (sign-in) can develop in parallel (both frontend, shared auth context)
- US3, US4, US5 can develop in parallel (all backend, share JWT middleware infrastructure)

**Within User Stories**:
- US1: T015-T016 can develop in parallel (form component + form logic)
- US1: T015-T017-T018 can develop in parallel (form, layout, middleware)
- US3: T027-T029 can develop in parallel (different endpoint updates)
- US4: T032-T033-T034 can develop in parallel (validation, extraction, filtering)
- US5: T041-T042 can develop in parallel (backend secret reading, frontend config)
- US6: T046-T048-T049 can develop in parallel (validation, handlers, redirects)

**Phase 9 (Testing)**:
- T051, T052, T053, T054, T055 can develop in parallel (different test modules)

---

## MVP Scope (Minimum Viable Product)

**Minimum Viable Implementation** = Phases 1-7, User Stories 1-5 (P1 core)

This MVP enables:
- ✅ Users can sign up and sign in via Better Auth
- ✅ JWT tokens issued and stored on frontend
- ✅ All 6 API endpoints protected with JWT requirement
- ✅ User identity extracted and enforced (multi-user isolation)
- ✅ Stateless verification with BETTER_AUTH_SECRET
- ✅ 401 Unauthorized responses for missing/invalid tokens

**NOT included in MVP**:
- ❌ Token expiration enforcement (User Story 6/Phase 8)
- ❌ Comprehensive testing suite (Phase 9)
- ❌ Production documentation (Phase 9)

---

## Implementation Strategy

### Frontend Development (Next.js + Better Auth)

1. **Dependencies** (Phase 2): API client, auth context
2. **Sign-Up** (Phase 3): Form + Better Auth integration
3. **Sign-In** (Phase 4): Form + token storage
4. **Token Expiration** (Phase 8): Redirect on 401
5. **Testing** (Phase 9): Storage + API client tests

### Backend Development (Python + FastAPI)

1. **Dependencies** (Phase 2): JWT schemas, auth context
2. **Middleware** (Phase 5): JWT validation on all endpoints
3. **Authorization** (Phase 6): User identity extraction + ownership enforcement
4. **Stateless Verification** (Phase 7): BETTER_AUTH_SECRET configuration
5. **Expiration** (Phase 8): Expired token rejection
6. **Testing** (Phase 9): JWT validation, multi-user, protected endpoints

### Cross-Team Integration Points

- **Phase 2**: Frontend + Backend must align on JWT claims structure (sub, email, exp, iat)
- **Phase 5**: Backend JWT middleware ready before frontend attaches tokens
- **Phase 7**: BETTER_AUTH_SECRET must be identical on frontend + backend
- **Phase 9**: Multi-user integration test verifies frontend JWT → backend validation → data isolation

---

## Success Criteria Mapping

| Success Criterion | Implemented in Phase | Task IDs |
|-------------------|---------------------|----------|
| SC-001: Sign-up <1 min | Phase 3 | T013-T018 |
| SC-002: Sign-in <30 sec | Phase 4 | T019-T023 |
| SC-003: 100% unauthenticated → 401 | Phase 5 | T024-T030 |
| SC-004: 100% invalid JWT → 401 | Phase 5 | T024-T030 |
| SC-005: Valid JWT succeeds | Phase 5 | T024-T030 |
| SC-006: Correct user identification | Phase 6 | T031-T038 |
| SC-007: User isolation enforced | Phase 6 | T031-T038, Phase 9: T055 |
| SC-008: Token expiration enforced | Phase 8 | T046-T050 |
| SC-009: All endpoints authenticated | Phase 5 | T024-T030 |
| SC-010: BETTER_AUTH_SECRET required | Phase 7 | T039-T040 |
| SC-011: <50ms validation latency | Phase 7 | T041-T042 |
| SC-012: Multi-user isolation | Phase 6 & 9 | T031-T038, T055 |

---

## Checklist Format Validation

✅ All 60 tasks follow strict format:
- ✅ Checkbox: `- [ ]`
- ✅ Task ID: T001-T060 (sequential)
- ✅ [P] parallelization markers: Applied to independent tasks
- ✅ [US#] story labels: Applied to Phase 3-8 tasks only
- ✅ Description: Clear action with exact file paths

---

## Notes for Implementation

1. **JWT Claims**: Coordinate with Better Auth on JWT structure (sub, email, iat, exp claims)
2. **BETTER_AUTH_SECRET**: Minimum 32 characters, must be identical frontend + backend
3. **Error Messages**: All 401/403 responses must be deterministic (same message format every time)
4. **Stateless Design**: Zero database queries for JWT validation (use PyJWT library)
5. **User Ownership**: All Task operations filtered by authenticated user_id (WHERE user_id = $user_id)
6. **Integration Points**: Frontend API client + backend middleware must exchange tokens in Authorization header

---

**Generated**: 2026-01-09
**Status**: Ready for `/sp.implement` command
**Next Phase**: Agent execution of tasks in dependency order
