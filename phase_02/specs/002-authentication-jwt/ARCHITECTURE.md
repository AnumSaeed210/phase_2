# Authentication Architecture: JWT-Based Stateless Authentication

**Feature**: Spec 002 - Authentication & Security (JWT)
**Created**: 2026-01-09
**Version**: 1.0

## Overview

This document describes the architecture for JWT-based stateless authentication connecting the Next.js frontend (via Better Auth) to the FastAPI backend. The system enables secure, multi-user authentication with horizontal scalability through stateless token verification.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Client (Browser)                        │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Next.js Frontend (App Router)                 │   │
│  │                                                        │   │
│  │  ┌──────────────┐      ┌────────────────────────┐    │   │
│  │  │ Auth Pages   │──────│   Better Auth Library  │    │   │
│  │  │ /auth/signup │      │   (JWT Plugin)         │    │   │
│  │  │ /auth/signin │      │                        │    │   │
│  │  └──────────────┘      └────────────┬───────────┘    │   │
│  │                                     │                 │   │
│  │                        Signs JWT with                │   │
│  │                      BETTER_AUTH_SECRET               │   │
│  │                                     │                 │   │
│  │  ┌──────────────────────────────────▼─────────────┐  │   │
│  │  │     JWT Storage (localStorage/cookie)          │  │   │
│  │  │     Token Format: Bearer <JWT_TOKEN>          │  │   │
│  │  └──────────────────────┬─────────────────────────┘  │   │
│  │                         │                             │   │
│  │  ┌──────────────────────▼─────────────────────────┐  │   │
│  │  │     API Client (HTTP Client Wrapper)           │  │   │
│  │  │     Injects: Authorization: Bearer <JWT>       │  │   │
│  │  └──────────────────────┬─────────────────────────┘  │   │
│  │                         │                             │   │
│  └─────────────────────────┼─────────────────────────────┘   │
└─────────────────────────────┼─────────────────────────────────┘
                              │
                              │ HTTPS
                              │ Header: Authorization: Bearer <JWT>
                              │
┌─────────────────────────────▼─────────────────────────────────┐
│                   FastAPI Backend (Python)                     │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐   │
│  │            JWT Validation Middleware                    │   │
│  │                                                         │   │
│  │  1. Extract Authorization header                       │   │
│  │  2. Parse "Bearer <token>"                            │   │
│  │  3. Validate signature using BETTER_AUTH_SECRET       │   │
│  │  4. Verify expiration (exp claim)                     │   │
│  │  5. Extract user_id from "sub" claim                  │   │
│  │  6. Compare JWT user_id with route {user_id}          │   │
│  │                                                         │   │
│  └──────────────┬──────────────────┬──────────────────────┘   │
│                 │                  │                          │
│           ✓ Valid JWT        ✗ Invalid JWT                   │
│                 │                  │                          │
│  ┌──────────────▼──────────┐  ┌───▼────────────────┐         │
│  │  AuthenticatedUser      │  │  401 Unauthorized  │         │
│  │  Context                │  │  Response          │         │
│  │  - user_id              │  │  - "Invalid token" │         │
│  │  - email                │  │  - "Token expired" │         │
│  │  - token_iat            │  │  - "Missing token" │         │
│  │  - token_exp            │  └────────────────────┘         │
│  └──────────────┬──────────┘                                 │
│                 │                                             │
│  ┌──────────────▼──────────────────────────────────────┐     │
│  │         Protected Endpoints                          │     │
│  │  POST   /api/{user_id}/tasks                        │     │
│  │  GET    /api/{user_id}/tasks                        │     │
│  │  GET    /api/{user_id}/tasks/{id}                   │     │
│  │  PUT    /api/{user_id}/tasks/{id}                   │     │
│  │  PATCH  /api/{user_id}/tasks/{id}/complete          │     │
│  │  DELETE /api/{user_id}/tasks/{id}                   │     │
│  │                                                      │     │
│  │  All queries filtered by authenticated user_id      │     │
│  └──────────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Frontend Authentication (Next.js + Better Auth)

**Location**: `frontend/src/lib/auth/`

**Components**:
- **better-auth-config.ts**: Configures Better Auth with JWT plugin and BETTER_AUTH_SECRET
- **jwt-storage.ts**: Handles JWT storage (save, retrieve, clear operations)
- **auth-context.tsx**: React context providing global authentication state

**Responsibilities**:
- User sign-up and sign-in via Better Auth
- JWT token issuance and secure storage
- Automatic token injection into API requests
- Token lifecycle management (storage, retrieval, clearing on logout)

### 2. API Client (Frontend)

**Location**: `frontend/src/lib/api/client.ts`

**Functionality**:
- HTTP client wrapper (using fetch or ky)
- Automatically injects `Authorization: Bearer <JWT>` header
- Handles 401 responses (token expired/invalid)
- Redirects to sign-in page on authentication failure

### 3. Backend JWT Middleware (FastAPI)

**Location**: `backend/src/auth/`

**Components**:
- **jwt_middleware.py**: Main JWT validation middleware
- **jwt_utils.py**: JWT parsing, verification, and claims extraction utilities
- **auth_context.py**: AuthenticatedUser model and context management
- **auth_schemas.py**: Pydantic schemas for auth requests/responses
- **jwt_deps.py**: FastAPI dependency injection for authentication
- **error_handlers.py**: 401/403 error response handlers

**Responsibilities**:
- Validate JWT signature using BETTER_AUTH_SECRET
- Verify token expiration (exp claim)
- Extract user identity (sub claim)
- Enforce user ownership (JWT user_id = route {user_id})
- Return appropriate error responses (401, 403)

### 4. Protected Endpoints (Backend)

**Location**: `backend/src/api/tasks.py`

**Changes**:
- Add `@require_auth` decorator or dependency injection to all 6 endpoints
- Filter all database queries by authenticated user_id
- No changes to endpoint logic - only authentication requirement added

## JWT Token Structure

### Claims (Issued by Better Auth)

```json
{
  "sub": "<user_id>",           // Subject: Unique user identifier
  "email": "<user_email>",      // User email address
  "iat": 1704672000,            // Issued at time (Unix timestamp)
  "exp": 1705276800,            // Expiration time (iat + 7 days)
  "iss": "better-auth",         // Issuer
  "aud": "taskie-api"           // Audience (our application)
}
```

### Signature Algorithm

- **Algorithm**: HS256 (HMAC with SHA-256)
- **Secret**: BETTER_AUTH_SECRET (shared between frontend and backend)
- **Length**: Minimum 32 characters (256 bits)

### Token Lifecycle

1. **Issuance**: User signs up or signs in → Better Auth creates JWT with exp = iat + 7 days
2. **Storage**: Frontend stores JWT in localStorage or HttpOnly cookie
3. **Usage**: Every API request includes `Authorization: Bearer <JWT>` header
4. **Validation**: Backend validates signature and expiration on every request
5. **Expiration**: After 7 days, backend rejects token with 401 → frontend redirects to sign-in

## BETTER_AUTH_SECRET Configuration

### Purpose

The BETTER_AUTH_SECRET is a shared cryptographic secret that enables:
- Better Auth (frontend) to sign JWT tokens
- FastAPI backend to verify JWT signatures
- Stateless authentication (no session storage required)
- Horizontal scalability (any backend instance can validate any token)

### Requirements

- **Length**: Minimum 32 characters (recommended: 64 characters)
- **Format**: Alphanumeric string with special characters
- **Generation**: Use cryptographically secure random generator
- **Security**: NEVER commit to version control; use environment variables only

### Setup Instructions

#### Generate BETTER_AUTH_SECRET

```bash
# Option 1: Using OpenSSL
openssl rand -base64 48

# Option 2: Using Python
python -c "import secrets; print(secrets.token_urlsafe(48))"

# Option 3: Using Node.js
node -e "console.log(require('crypto').randomBytes(48).toString('base64'))"
```

#### Frontend Configuration (.env.local)

```env
BETTER_AUTH_SECRET=<your_generated_secret>
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Backend Configuration (.env)

```env
BETTER_AUTH_SECRET=<same_secret_as_frontend>
DATABASE_URL=postgresql://user:password@host:port/database
```

**CRITICAL**: The BETTER_AUTH_SECRET value MUST be identical on both frontend and backend.

### Environment Variable Loading

**Frontend**:
- Next.js automatically loads `.env.local` at build time
- Better Auth reads `process.env.BETTER_AUTH_SECRET`

**Backend**:
- FastAPI uses `python-dotenv` to load `.env` on startup
- Read via `os.getenv("BETTER_AUTH_SECRET")`
- **Startup validation**: Fail with clear error if not configured

## Authentication Flow

### Sign-Up Flow

```
1. User visits /auth/signup
2. User enters email and password
3. Frontend submits to Better Auth
4. Better Auth:
   - Validates password strength (min 8 characters)
   - Creates user account in database
   - Generates JWT token signed with BETTER_AUTH_SECRET
5. Frontend receives JWT token
6. Frontend stores JWT (localStorage/cookie)
7. Frontend redirects to application (/tasks)
```

### Sign-In Flow

```
1. User visits /auth/signin
2. User enters email and password
3. Frontend submits to Better Auth
4. Better Auth:
   - Validates credentials against database
   - If valid: Generates JWT token
   - If invalid: Returns error
5. Frontend receives JWT token
6. Frontend stores JWT
7. Frontend redirects to application
```

### Authenticated API Request Flow

```
1. Frontend makes API request (e.g., GET /api/{user_id}/tasks)
2. API client retrieves JWT from storage
3. API client injects Authorization header: Bearer <JWT>
4. Backend JWT middleware:
   a. Extracts Authorization header
   b. Parses "Bearer <token>"
   c. Validates JWT signature using BETTER_AUTH_SECRET
   d. Verifies exp claim (token not expired)
   e. Extracts user_id from sub claim
   f. Compares JWT user_id with route path {user_id}
   g. If match: Creates AuthenticatedUser context
   h. If mismatch: Returns 403 Forbidden
5. Endpoint handler receives AuthenticatedUser context
6. Endpoint queries database filtered by user_id
7. Backend returns response
```

### Token Expiration Flow

```
1. JWT token expires after 7 days
2. User makes API request with expired token
3. Backend validates token:
   - Signature valid
   - exp claim < current time → EXPIRED
4. Backend returns 401 Unauthorized: "Token expired"
5. Frontend API client intercepts 401
6. Frontend clears stored JWT
7. Frontend redirects to /auth/signin
8. User re-authenticates and receives fresh token
```

## Security Considerations

### Multi-User Isolation

**Requirement**: Users can only access their own data.

**Implementation**:
1. JWT contains user_id in sub claim
2. Backend extracts user_id from JWT
3. Backend compares JWT user_id with route path {user_id}
4. All database queries filtered by authenticated user_id
5. Ownership mismatch → 403 Forbidden or 404 Not Found

**Test Scenario**:
```
User A (user_id="A") authenticates → receives JWT_A
User B (user_id="B") authenticates → receives JWT_B

User A requests GET /api/A/tasks with JWT_A → SUCCESS (200 OK)
User A requests GET /api/B/tasks with JWT_A → FAIL (403/404)
User B requests GET /api/B/tasks with JWT_B → SUCCESS (200 OK)
User B requests GET /api/A/tasks with JWT_B → FAIL (403/404)
```

### Stateless Verification

**Requirement**: Zero database queries for JWT validation.

**Implementation**:
- Backend validates JWT signature using BETTER_AUTH_SECRET (cryptographic verification)
- No session table lookups required
- Backend can restart and immediately validate existing tokens
- Horizontal scaling: Any backend instance can validate any token

**Performance**: JWT validation <50ms per request (SC-011)

### Token Expiration

**Requirement**: Tokens expire after 7 days.

**Implementation**:
- Better Auth sets exp claim to iat + 604,800 seconds (7 days)
- Backend verifies exp claim on every request
- Expired tokens rejected with 401 Unauthorized

**No Refresh Tokens**: Users must re-authenticate after expiration. This is acceptable for a todo application with a 7-day expiration window.

## Error Handling

### 401 Unauthorized (Authentication Failure)

**Triggered by**:
- Missing Authorization header
- Invalid JWT format
- Invalid JWT signature
- Expired token (exp claim < current time)

**Response Format**:
```json
{
  "detail": "Unauthorized",
  "message": "Invalid token" | "Token expired" | "Missing authorization header"
}
```

**Frontend Action**: Clear stored JWT, redirect to /auth/signin

### 403 Forbidden (Authorization Failure)

**Triggered by**:
- Valid JWT but user_id mismatch (JWT user_id ≠ route {user_id})

**Response Format**:
```json
{
  "detail": "Forbidden",
  "message": "Access denied"
}
```

**Frontend Action**: Display error message (user attempting to access another user's data)

### 422 Unprocessable Entity (Validation Failure)

**Triggered by**:
- Invalid sign-up/sign-in data (e.g., password too short)

**Response Format**:
```json
{
  "detail": "Validation error",
  "errors": [...]
}
```

**Frontend Action**: Display validation errors on form

## Testing Strategy

### Unit Tests

**Backend**:
- JWT parsing and validation (jwt_utils.py)
- Token expiration verification
- Signature verification with valid/invalid secrets
- Claims extraction

**Frontend**:
- JWT storage (save, retrieve, clear)
- API client header injection
- Auth context state management

### Integration Tests

**Multi-User Isolation** (backend/tests/test_user_isolation.py):
- Users A, B, C authenticate independently
- Each user receives unique JWT
- Each user can only access their own tasks
- Cross-user access attempts return 403/404

**Protected Endpoints** (backend/tests/test_protected_endpoints.py):
- All 6 endpoints require JWT
- Missing JWT → 401
- Invalid JWT → 401
- Expired JWT → 401
- Valid JWT → 200/201/204

**Stateless Verification** (backend/tests/test_stateless_auth.py):
- Backend restart → same JWT validates successfully
- BETTER_AUTH_SECRET mismatch → JWT validation fails
- No database queries during validation

### Security Tests

- Unauthenticated requests return 401
- Invalid tokens return 401
- Expired tokens return 401
- User B cannot use User A's token to access User A's data

## Performance Requirements

### Latency Targets

- **JWT Validation**: <50ms per request (SC-011)
- **Sign-Up**: <1 minute total (SC-001)
- **Sign-In**: <30 seconds total (SC-002)

### Scalability

- **Stateless Design**: Enables horizontal scaling (add backend instances without session coordination)
- **No Database Lookups**: JWT validation is purely cryptographic (no DB query overhead)
- **Connection Pooling**: Database connections used only for data queries, not auth validation

## Implementation Checklist

### Frontend Tasks
- [ ] Install and configure Better Auth with JWT plugin
- [ ] Create sign-up page (/auth/signup)
- [ ] Create sign-in page (/auth/signin)
- [ ] Implement JWT storage utility
- [ ] Create API client with Authorization header injection
- [ ] Add 401 error handler (redirect to sign-in)
- [ ] Add route protection middleware

### Backend Tasks
- [ ] Install PyJWT and python-dotenv
- [ ] Create JWT validation middleware
- [ ] Implement JWT utilities (parse, verify, extract)
- [ ] Create AuthenticatedUser context
- [ ] Add dependency injection for authentication
- [ ] Update all 6 endpoints to require JWT
- [ ] Implement 401/403 error handlers
- [ ] Add BETTER_AUTH_SECRET startup validation

### Testing Tasks
- [ ] Unit tests: JWT validation logic
- [ ] Integration tests: Protected endpoints
- [ ] Integration tests: Multi-user isolation
- [ ] Integration tests: Stateless verification
- [ ] Integration tests: Token expiration
- [ ] Security tests: Unauthorized access attempts

### Documentation Tasks
- [ ] Architecture documentation (this file)
- [ ] Setup guide (quickstart.md)
- [ ] Error message documentation
- [ ] Implementation summary

## References

- **Spec**: [specs/002-authentication-jwt/spec.md](./spec.md)
- **Plan**: [specs/002-authentication-jwt/plan.md](./plan.md)
- **Tasks**: [specs/002-authentication-jwt/tasks.md](./tasks.md)
- **Better Auth**: https://www.better-auth.com/
- **PyJWT**: https://pyjwt.readthedocs.io/
- **RFC 6750**: OAuth 2.0 Bearer Token Usage

---

**Document Status**: Initial version - Created 2026-01-09
**Next Steps**: Complete Phase 1 setup tasks, proceed to foundational implementation
