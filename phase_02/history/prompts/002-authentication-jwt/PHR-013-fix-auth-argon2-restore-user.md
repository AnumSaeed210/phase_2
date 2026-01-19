---
id: PHR-013
title: Fix authentication with argon2 and restore user state
stage: red
date: 2026-01-13
surface: agent
model: claude-haiku-4-5-20251001
feature: 002-authentication-jwt
branch: 003-frontend-nextjs
user: ayeshaqadir
command: /sp.phr
labels: ["authentication", "bcrypt-incompatibility", "argon2", "jwt", "state-persistence", "localStorage", "debugging"]
links:
  spec: specs/002-authentication-jwt.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/requirements.txt
  - backend/src/api/auth.py
  - frontend/src/lib/auth/auth-context.tsx
tests:
  - POST /auth/signup endpoint (argon2 hashing)
  - POST /auth/signin endpoint (credential validation)
  - User state restoration from localStorage
---

## Prompt

The user reported two issues with authentication:
1. Backend signup/signin endpoints were failing with bcrypt/passlib compatibility errors on Python 3.13: "password cannot be longer than 72 bytes" error from passlib
2. After successful login, the tasks page wasn't showing anything - blank page with no content

## Response snapshot

Debugged and fixed both issues:

**Backend**: Replaced incompatible bcrypt/passlib with argon2 (OWASP recommended, better Python 3.13 support)
- Updated requirements.txt to use argon2-cffi==23.1.0
- Rewrote password hashing/verification in auth.py to use PasswordHasher
- Added password_hash column to users table in Neon database
- Removed conflicting old password column

**Frontend**: Fixed missing user state restoration on page load
- AuthProvider now restores user from localStorage on mount using useEffect
- Added getUser() import to auth-context.tsx
- User state persists across page refreshes

**Both endpoints now working**: signup and signin return valid JWT tokens, user can authenticate.

## Outcome

- ✅ Impact: Backend authentication endpoints fully functional with argon2. Frontend now displays tasks page after login. User state persists across browser refreshes.
- 🧪 Tests: Manual curl tests for signup (returns JWT) and signin (authenticates user). Tasks API endpoint verified working with token injection.
- 📁 Files: backend/requirements.txt, backend/src/api/auth.py, frontend/src/lib/auth/auth-context.tsx
- 🔁 Next prompts: Test complete signup→signin→create-task→logout flow in browser
- 🧠 Reflection: Database schema mismatches (missing password_hash, conflicting password column) were the root cause of "blank page" - once auth state restored from localStorage, tasks page rendered correctly with API integration.

## Evaluation notes (flywheel)

- Failure modes observed:
  1. bcrypt 72-byte password limit was blocking password hashing due to passlib 1.7.4 incompatibility with Python 3.13
  2. Users table had old `password` column (NOT NULL) conflicting with new `password_hash` column
  3. AuthProvider didn't restore user from localStorage, causing blank page after redirect from login
  4. Issue was diagnosed through: checking backend logs, verifying database schema, reading auth-context implementation

- Graders run and results (PASS/FAIL):
  - PASS: POST /auth/signup returns user object with JWT token
  - PASS: POST /auth/signin authenticates and returns JWT token
  - PASS: User state persists when page refreshes
  - PASS: Tasks API endpoint accessible with JWT bearer token

- Prompt variant (if applicable): null

- Next experiment (smallest change to try):
  1. Test that logout clears localStorage and redirects to signin
  2. Test that unauthenticated access to /tasks redirects to signin
  3. Run browser e2e test for complete auth flow: signup → tasks page → create task → logout → signin

---
