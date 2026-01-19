<!--
SYNC IMPACT REPORT (v1.0.0 → v1.1.0)
- Version bump: MINOR (added Security by Design principle + comprehensive Authentication Architecture section)
- Modified principles: None renamed (all 6 principles from user input incorporated as new foundational set)
- Added sections: None (Authentication Architecture was expanded in CLAUDE.md, principles embedded here)
- Removed sections: None
- Templates to update:
  ✅ spec-template.md - Already includes functional requirements (FR-XXX format aligned with principles)
  ✅ plan-template.md - Already includes Constitution Check gate
  ✅ tasks-template.md - Already organizes by user story and includes test-first mandate
- Follow-up TODOs: None
-->

# Todo Full-Stack Web Application Constitution

## Core Principles

### I. Spec-First Development

All functionality must be explicitly defined in specifications before any implementation begins. No code is written, no database schema is designed, no API endpoint is built until the corresponding specification has been approved. Specifications are the source of truth; implementation is merely the physical manifestation of an approved spec. This discipline ensures deterministic behavior and enables reproducible system construction from the same specifications.

**Rationale**: Spec-first prevents wasted effort on feature creep, unverified assumptions, and rework. It creates a clear handoff between design and implementation and makes the project auditable.

### II. Agentic Workflow Integrity

All implementation must be generated through Claude Code and its agent infrastructure. No manual coding is permitted. The Agentic Dev Stack workflow (Spec → Plan → Tasks → Implementation) is the only legitimate path to code generation. Each agent in the system performs its designated function without human code authoring. This ensures consistency, auditability, and adherence to the constitution through automated patterns.

**Rationale**: Removing manual coding enforces discipline, captures all decisions in specs and plans, and makes the development process fully reviewable and repeatable.

### III. Security by Design

Authentication and authorization must be enforced at every layer—database, API, and frontend. User isolation is non-negotiable: each user can only access and modify their own data. JWT-based authentication via Better Auth is the mechanism; the principle is that security is not added after the fact but designed into the initial specification and enforced throughout implementation. All API endpoints require valid JWT tokens; stateless verification is the only acceptable pattern.

**Rationale**: Layered security prevents accidental data leaks and privilege escalation. JWT-based design enables the backend to verify requests without session storage, matching the serverless database architecture.

### IV. User Isolation (Data Ownership)

Every data record (task, preference, etc.) must be owned by an authenticated user. API endpoints must validate that the requesting user owns the resource before returning or modifying it. User IDs are extracted from JWT tokens and matched against record ownership. Queries must always filter by the authenticated user's ID. This principle ensures multi-tenancy without data leakage and supports the business model of a truly multi-user application.

**Rationale**: User isolation is the foundation of a multi-user SaaS application. Enforcing it in specs and verifying it in API contracts prevents the most common class of security bugs.

### V. Deterministic Behavior

All API behavior, error handling, status codes, and response formats must be fully defined in specifications before implementation. There is no "reasonable assumption"—if it is not in the spec, it does not exist in the code. This includes response structure for success and failure cases, exact HTTP status codes (e.g., 401 for unauthorized, 404 for not found), and validation rules. Deterministic behavior enables testing against specifications and guarantees consistency across all agents.

**Rationale**: Determinism makes the system testable, predictable, and auditable. It eliminates ambiguity during implementation and review.

### VI. Reproducibility

The same specification and plan, executed by the agentic workflow, must always produce equivalent system behavior. No non-deterministic decisions are permitted during implementation (no "developer preference" logic). Technology choices are fixed; architectural decisions are captured in the plan; implementation patterns are derived from specifications. Any two independent runs of the Agentic Dev Stack on the same specs must yield systems with identical behavior.

**Rationale**: Reproducibility enables teams to evaluate and trust the development process. It also allows specs to be the single source of truth for project behavior.

## Technology Stack (Fixed)

The technology stack is non-negotiable and must remain constant throughout the project:

- **Frontend**: Next.js 16+ (App Router), TypeScript, Tailwind CSS
- **Backend**: Python FastAPI
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth (JWT-based)
- **Development Workflow**: Claude Code + Spec-Kit Plus (Agentic Dev Stack)

No substitutions, experimental technologies, or workarounds are permitted. If a constraint of the chosen stack is discovered to be insufficient, the solution is to enhance the specification and plan, not to bypass the stack.

## Security & Authentication Requirements

### JWT-Based Stateless Authentication

- All API endpoints MUST require a valid JWT token in the `Authorization: Bearer <token>` header
- JWT tokens are issued by Better Auth on successful user signup/signin
- Backend verification uses the shared `BETTER_AUTH_SECRET` environment variable
- User identity is extracted from the JWT token payload (user ID, email)
- No session storage on backend; each request is independently verified
- Invalid or missing tokens return HTTP 401 Unauthorized

### User Ownership Enforcement

- Every API endpoint that returns or modifies data MUST verify user ownership
- User ID from token is matched against record's user ownership field
- Requests for records owned by other users return HTTP 404 (not found) or 403 (forbidden), never 200
- Database queries must include `WHERE user_id = $authenticated_user_id` filters
- API contracts must explicitly document the ownership check behavior

### Environment Variable Management

- `BETTER_AUTH_SECRET` must be identical on frontend and backend for token verification to succeed
- `DATABASE_URL` must be set in both frontend and backend environments
- Secrets are never committed to version control; they are managed externally (CI/CD, deployment platform)

## Development Workflow

1. **Specification Phase** (`/sp.specify`): Write feature specification with user stories, requirements, success criteria, and edge cases
2. **Planning Phase** (`/sp.plan`): Orchestrator Agent reviews spec, researches tech stack, produces implementation plan with Constitution Check
3. **Task Breakdown** (`/sp.tasks`): Plan is decomposed into ordered, parallel-safe tasks organized by user story
4. **Implementation Phase** (`/sp.implement`): Designated agents (Backend Architect, Neon Postgres Expert, Next.js UI Optimizer, Auth Security Reviewer) execute tasks in dependency order
5. **Verification Phase**: Auth Security Reviewer confirms authentication enforcement and API contracts; manual testing validates spec compliance

## Governance

### Constitution Supremacy

This constitution supersedes all other practices, guidelines, and preferences. In case of conflict between the constitution and any other document (README, agent guidance, developer preference), the constitution prevails.

### Compliance Review & Gate

Before implementation, the Orchestrator Agent MUST perform a **Constitution Check**:
- Does the specification define all required behavior deterministically?
- Does the plan respect the fixed technology stack?
- Does the implementation strategy enforce spec-first development?
- Are authentication and user isolation mechanisms explicitly designed?
- Can the implementation be fully traced back to specifications and plans?

If any check fails, the spec or plan is returned for revision before implementation proceeds.

### Amendment Procedure

Amendments to this constitution require:
1. Clear rationale: what violation or ambiguity triggered the amendment
2. Explicit description of the change (principle added, removed, or redefined; constraint adjusted)
3. Impact analysis: which specs, plans, and implementations are affected
4. Version bump: MAJOR for backward-incompatible changes (principle removals), MINOR for additions or clarifications, PATCH for wording-only fixes
5. Documentation: update CLAUDE.md and all downstream templates

Amendments are recorded in the version line and a Sync Impact Report is prepended as an HTML comment.

### Complexity Justification

If an implementation deviates from the constitution (e.g., using an unapproved technology, bypassing JWT verification, adding manual code), the plan must explicitly document:
- Why the deviation is necessary
- What simpler alternative was considered and rejected
- Explicit approval from the project lead

Such deviations are exceptions, not the norm, and must be recorded in the plan's "Complexity Tracking" section.

### Agent Guidance

Each agent has its own detailed guidance file in `.claude/agents/`:
- **Orchestrator Agent** (`orchestrator-agent.md`): Coordinates specs, plans, and implementation
- **Backend Architect** (`backend-architect.md`): Implements FastAPI endpoints and models
- **Neon Postgres Expert** (`neon-postgres-expert.md`): Designs and manages database schema
- **Auth Security Reviewer** (`auth-security-reviewer.md`): Reviews and implements authentication
- **Next.js UI Optimizer** (`nextjs-ui-optimizer.md`): Builds frontend components and pages

These guidance files are subordinate to this constitution and must not contradict its principles.

---

**Version**: 1.1.0 | **Ratified**: 2025-01-08 | **Last Amended**: 2025-01-09
