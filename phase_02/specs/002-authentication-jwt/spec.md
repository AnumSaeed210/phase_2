# Feature Specification: Authentication & Security (JWT)

**Feature Branch**: `002-authentication-jwt`
**Created**: 2026-01-09
**Status**: Draft
**Input**: User description: "Todo Full-Stack Web Application — Spec 2: Authentication & Security (JWT)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Sign Up with Better Auth (Priority: P1)

A new user visits the application and needs to create an account to start managing tasks. They provide their email and password through a secure front-end sign-up form powered by Better Auth, receive authentication confirmation, and get issued a JWT token for subsequent API requests.

**Why this priority**: User sign-up is the critical first step for any authenticated application. Without this, users cannot access the system at all. This is the MVP foundation.

**Independent Test**: Can be fully tested by (1) visiting the sign-up page, (2) entering valid email and password, (3) submitting the form, (4) verifying JWT token is issued and stored on frontend, and delivers immediate value by enabling account creation.

**Acceptance Scenarios**:

1. **Given** a user visits the application for the first time, **When** they navigate to the sign-up page and enter valid email and password, **Then** Better Auth processes the request, creates a user account, and returns a JWT token that can be used for authenticated API calls.
2. **Given** a user attempts to sign up with an email that already exists, **When** they submit the sign-up form, **Then** the frontend displays an error message indicating the email is already registered.
3. **Given** a user enters a password that is too weak (less than 8 characters), **When** they submit the sign-up form, **Then** Better Auth validates and rejects the request with a clear error message on the frontend.

---

### User Story 2 - User Sign In with JWT Token Issuance (Priority: P1)

An existing user returns to the application and needs to authenticate themselves. They enter their credentials via Better Auth on the frontend, receive a valid JWT token upon successful authentication, and can immediately use that token to make authenticated requests to the backend API.

**Why this priority**: User sign-in is equally critical to sign-up. P1 because without working authentication, users cannot access their tasks or perform any operations on the backend.

**Independent Test**: Can be fully tested by (1) visiting the sign-in page, (2) entering valid email and password, (3) submitting credentials, (4) receiving JWT token from Better Auth, (5) confirming token is valid for API calls, and delivers immediate value by enabling existing users to access their data.

**Acceptance Scenarios**:

1. **Given** a user with a valid account signs in with correct credentials, **When** the frontend submits credentials to Better Auth, **Then** Better Auth returns a valid JWT token that includes the user's identity and can be used to authenticate API requests.
2. **Given** a user attempts to sign in with an incorrect password, **When** they submit the sign-in form, **Then** Better Auth rejects the request and the frontend displays an error message.
3. **Given** a user enters an email address that does not have an account, **When** they attempt to sign in, **Then** Better Auth returns an error indicating the user does not exist.

---

### User Story 3 - Protected API Endpoints Require JWT (Priority: P1)

After a user authenticates and receives a JWT token, they can make requests to the backend API. Every API request must include the JWT token in the Authorization header. The backend validates the token, extracts the user's identity, and ensures the request is authorized before processing.

**Why this priority**: This is the core of the authentication system. All 6 backend endpoints (from Spec 001) must be protected. P1 because without this, unauthenticated users could access protected resources.

**Independent Test**: Can be fully tested by (1) obtaining a valid JWT token, (2) making API requests with and without the token, (3) verifying that requests without the token receive 401 Unauthorized, (4) verifying that requests with valid token succeed, and delivers immediate value by securing all API endpoints.

**Acceptance Scenarios**:

1. **Given** a user has a valid JWT token, **When** they make a request to any protected endpoint with the token in the Authorization header (format: `Bearer <JWT>`), **Then** the backend validates the token and processes the request.
2. **Given** a user makes a request to a protected endpoint without an Authorization header, **When** the backend receives the request, **Then** it returns 401 Unauthorized with an error message.
3. **Given** a user provides an invalid or expired JWT token, **When** the backend validates the token, **Then** it returns 401 Unauthorized with an appropriate error message.

---

### User Story 4 - JWT Token Contains User Identity (Priority: P1)

The JWT token issued by Better Auth contains the authenticated user's identity (email or user_id). When the backend receives a request with a valid JWT token, it can extract the user's identity from the token and use it to enforce data ownership (e.g., users can only access their own tasks).

**Why this priority**: User identity extraction from JWT is essential for enforcing multi-user isolation. P1 because without this, any authenticated user could access any other user's data.

**Independent Test**: Can be fully tested by (1) obtaining JWT tokens for multiple users, (2) making API requests with each token, (3) verifying the backend correctly identifies the user from the token, (4) confirming each user can only access their own data, and delivers immediate value by enforcing data ownership.

**Acceptance Scenarios**:

1. **Given** a valid JWT token is provided to the backend, **When** the backend decodes the token, **Then** it extracts the user's unique identifier (email or user_id) and can use this to filter requests.
2. **Given** User A authenticates and receives JWT token containing their identity, **When** User A makes a request to get their tasks, **Then** the backend returns only User A's tasks.
3. **Given** User B attempts to use User A's JWT token to access User A's tasks, **When** User B makes the request, **Then** the backend validates the token and identifies it as belonging to User B (not User A), preventing unauthorized access.

---

### User Story 5 - Stateless Authentication with Shared Secret (Priority: P1)

The backend does not maintain session state in a database or external store. Instead, JWT verification uses a shared secret (BETTER_AUTH_SECRET environment variable) that is configured in both the frontend (via Better Auth) and backend. This enables stateless, reproducible authentication across all deployments.

**Why this priority**: Stateless authentication is critical for horizontal scalability and production readiness. P1 because session-based approaches would create deployment and scaling challenges.

**Independent Test**: Can be fully tested by (1) configuring BETTER_AUTH_SECRET on both frontend and backend, (2) signing in a user and obtaining JWT, (3) restarting the backend, (4) verifying the same JWT still validates, and delivers immediate value by enabling seamless deployments and scaling.

**Acceptance Scenarios**:

1. **Given** BETTER_AUTH_SECRET is configured identically on frontend (Better Auth) and backend, **When** a user signs in and receives a JWT, **Then** the backend can validate the JWT without any database lookup.
2. **Given** a backend server instance is restarted, **When** a client submits a request with a valid JWT, **Then** the new instance validates the token successfully using the same shared secret.
3. **Given** BETTER_AUTH_SECRET is changed on the backend, **When** a client submits a request with a JWT signed with the old secret, **Then** the backend rejects the token as invalid.

---

### User Story 6 - Token Expiration for Security (Priority: P2)

JWT tokens issued by Better Auth have an expiration time (e.g., 7 days). When a token expires, users must authenticate again. The backend rejects expired tokens with 401 Unauthorized, and the frontend re-directs users to the sign-in page.

**Why this priority**: Token expiration is a security best practice to limit the window of compromise if a token is stolen. P2 because it enhances security but does not block core functionality (users can re-authenticate).

**Independent Test**: Can be fully tested by (1) obtaining a JWT token, (2) simulating token expiration, (3) making an API request with the expired token, (4) verifying the backend returns 401, (5) confirming frontend redirects to sign-in, and delivers value by enforcing token freshness.

**Acceptance Scenarios**:

1. **Given** a JWT token expires after 7 days, **When** a user attempts to make an API request with the expired token, **Then** the backend validates the token and rejects it with 401 Unauthorized.
2. **Given** a user submits an expired token, **When** the backend returns 401, **Then** the frontend detects this and redirects the user to the sign-in page.

---

### Edge Cases

- What happens when a user signs up with valid email but already has an account? (Better Auth should return an error, frontend should display it)
- How does the system handle concurrent sign-up requests from the same email? (Better Auth should prevent duplicates; database constraints enforce uniqueness)
- What happens if BETTER_AUTH_SECRET is not configured on the backend? (Startup should fail with clear error; backend cannot validate JWTs)
- What happens if a user signs out and then attempts to use their old JWT? (Token is still technically valid until expiration; this is expected stateless behavior)
- How does the system handle token refresh or renewal? (Not building refresh tokens in this spec; users re-authenticate when token expires)
- What happens if the frontend receives a JWT with an unexpected format or missing required fields? (Frontend validation via Better Auth should reject; backend also validates for defense-in-depth)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a sign-up endpoint on the frontend using Better Auth that accepts email and password as input.
- **FR-002**: System MUST provide a sign-in endpoint on the frontend using Better Auth that accepts email and password as input.
- **FR-003**: Better Auth MUST validate user credentials and return a JWT token upon successful authentication.
- **FR-004**: JWT token MUST be stored securely on the frontend (e.g., HttpOnly cookie or localStorage depending on Better Auth configuration).
- **FR-005**: Frontend MUST attach the JWT token to every API request in the Authorization header with format `Bearer <JWT>`.
- **FR-006**: Backend MUST validate the JWT token on every protected API request using the shared BETTER_AUTH_SECRET.
- **FR-007**: Backend MUST extract the user's unique identifier (email or user_id) from the validated JWT token.
- **FR-008**: Backend MUST enforce that the user_id in the JWT matches the user_id in the API route (e.g., `/api/{user_id}/tasks` enforces user_id from JWT = user_id in path).
- **FR-009**: Backend MUST reject requests without a valid Authorization header with 401 Unauthorized.
- **FR-010**: Backend MUST reject requests with invalid or expired JWT tokens with 401 Unauthorized.
- **FR-011**: Backend MUST return descriptive error messages for authentication failures (e.g., "Invalid token", "Token expired").
- **FR-012**: JWT token MUST include an expiration claim (exp) set to 7 days from issuance.
- **FR-013**: Backend MUST verify token expiration and reject expired tokens with 401 Unauthorized.
- **FR-014**: Backend MUST read BETTER_AUTH_SECRET from environment variable on startup and fail if not configured.
- **FR-015**: All 6 API endpoints from Spec 001 (POST/GET/PUT/DELETE/PATCH /api/{user_id}/tasks and GET /api/{user_id}/tasks/{id}) MUST require valid JWT authentication.

### Key Entities

- **User (from Spec 001)**: id (string), email (string). Authentication adds: user must have valid JWT token to access API.
- **JWT Token**: Issued by Better Auth on the frontend. Contains: user identity, exp (expiration time in seconds), iat (issued at time), potentially email and other claims. Signed using BETTER_AUTH_SECRET.
- **Authorization Header**: HTTP request header on every API call. Format: `Authorization: Bearer <JWT_TOKEN>`. Backend must extract, validate, and use token for user identification.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: New users can complete sign-up via Better Auth in under 1 minute (measure time from page load to JWT token issued).
- **SC-002**: Existing users can sign in and receive JWT token in under 30 seconds.
- **SC-003**: 100% of unauthenticated API requests return 401 Unauthorized (zero unauthenticated access to protected endpoints).
- **SC-004**: 100% of requests with invalid JWT tokens return 401 Unauthorized.
- **SC-005**: 100% of requests with valid JWT token from correct user are processed successfully (verified by testing all 6 endpoints with valid JWT).
- **SC-006**: Backend correctly identifies user from JWT token with 100% accuracy (verified by multi-user scenario testing).
- **SC-007**: Users can only access their own tasks (zero instances of user being able to access another user's data via valid but mismatched JWT).
- **SC-008**: JWT token expiration is enforced: tokens expire exactly 7 days after issuance, and expired tokens are rejected by backend.
- **SC-009**: All 6 API endpoints (POST/GET/PUT/DELETE/PATCH /tasks endpoints) require authentication; zero endpoints allow unauthenticated access.
- **SC-010**: Backend validates BETTER_AUTH_SECRET on startup; if not configured, startup fails with clear error message.
- **SC-011**: Token validation latency is under 50ms per request (stateless verification has minimal overhead).
- **SC-012**: Multi-user scenario: Users A, B, C can authenticate independently, receive separate JWT tokens, and each can access only their own tasks (100% isolation).

## Assumptions *(if applicable)*

- Better Auth is already integrated or will be integrated into the Next.js frontend as part of Spec 2 implementation.
- BETTER_AUTH_SECRET is a cryptographically secure string (minimum 32 characters) shared between frontend and backend via environment variables.
- JWT tokens are Bearer tokens as per RFC 6750 (Authorization: Bearer <token>).
- Token expiration is set to 7 days (168 hours). This can be adjusted by frontend/Better Auth configuration; backend simply verifies the exp claim.
- User identity in JWT is the user's unique identifier (e.g., email or user_id); Spec 001 already uses user_id in API routes, so JWT must include user_id.
- Frontend handles token refresh (user must re-authenticate after expiration); no refresh token mechanism in this spec.
- CORS (Cross-Origin Resource Sharing) between frontend and backend is already configured or will be configured separately.
- Backend database (Neon PostgreSQL from Spec 001) stores users; authentication does not require new database tables, only validation logic.

## Out of Scope

The following are explicitly **NOT** building in this specification:

- Custom password hashing or storage logic (Better Auth handles this)
- OAuth, OpenID Connect, or third-party identity providers
- Role-based access control (RBAC) or permission levels (all authenticated users have equal access to their own tasks)
- Refresh tokens or token rotation mechanisms
- Session management or server-side session storage
- Password reset, email verification, or multi-factor authentication (future enhancements)
- Frontend UI styling for authentication screens (handled in Spec 3)
- Rate limiting or brute-force protection on authentication endpoints (may be added later)
- Token revocation or blacklisting
- User management endpoints (create/delete/update user operations beyond sign-up)

---

## Implementation Notes for Development

### Frontend (Next.js + Better Auth)

1. Integrate Better Auth library with Next.js app
2. Create sign-up page: form with email/password → submit to Better Auth → receive JWT → store securely
3. Create sign-in page: form with email/password → submit to Better Auth → receive JWT → store securely
4. Add middleware or utility to attach JWT to all outgoing API requests in Authorization header
5. Handle 401 responses by redirecting to sign-in page and clearing stored token
6. Configure Better Auth with BETTER_AUTH_SECRET from environment

### Backend (Python FastAPI)

1. Add JWT validation middleware or dependency to FastAPI
2. Read BETTER_AUTH_SECRET from environment variable (fail startup if missing)
3. On every request to protected endpoints:
   - Extract Authorization header
   - Parse Bearer token
   - Validate JWT signature using BETTER_AUTH_SECRET and PyJWT library (or equivalent)
   - Verify token is not expired (check exp claim)
   - Extract user_id or email from token claims
   - Verify user_id matches the one in the API route path
   - Pass user context to endpoint handler
4. Add test fixtures for valid/invalid/expired JWT tokens
5. Update all 6 endpoints from Spec 001 to require valid JWT (no changes to endpoint logic, just add authentication requirement)

### Verification Strategy

1. **Unit Tests**: JWT validation logic, token parsing, expiration verification
2. **Integration Tests**: End-to-end flow (sign-up → get JWT → make API call → verify user context)
3. **Security Tests**:
   - Unauthenticated requests return 401
   - Invalid tokens return 401
   - Expired tokens return 401
   - User B cannot use User A's token to access User A's data
4. **Multi-User Tests**: Users A, B, C authenticate independently and can only access their own tasks
5. **Environment Tests**: Missing BETTER_AUTH_SECRET causes startup failure
