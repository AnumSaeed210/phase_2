---
id: 001
title: Write CLAUDE.md project instructions
stage: general
date: 2026-01-08
surface: agent
model: claude-haiku-4-5-20251001
feature: none
branch: master
user: user
command: write CLAUDE.md
labels: ["project-setup", "documentation", "claude-md"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - CLAUDE.md
tests:
  - none
---

## Prompt

write a CLAUDE.md file in the root:
# Takie - Todo app
## Project Overview
Full-stack multi-user todo application using spec-driven development.

## Tech Stack
- Frontend: Next.js 16+ (App Router), TypeScript, Tailwind CSS
- Backend: Python FastAPI, SQLModel
- Database: Neon Serverless PostgreSQL
- Auth: Better Auth with JWT


## Agent Structure
- Main Orchestrator (@agents/orchestrator.md)
- Database Agent (@agents/database.md)
- Backend Agent (@agents/backend.md)
- Frontend Agent (@agents/frontend.md)
- Integration Agent (@agents/integration.md)

## Development Workflow
1. Read spec: @specs/features/[feature].md
2. Orchestrator creates plan
3. Database Agent implements models
4. Backend Agent implements API
5. Frontend Agent implements UI
6. Integration Agent verifies auth & connectivity


## Environment Variables
Required in both frontend and backend:
- BETTER_AUTH_SECRET (shared secret for JWT)
- DATABASE_URL (Neon PostgreSQL connection)

## Response snapshot

Created CLAUDE.md file in the root directory with project overview, tech stack details, agent structure, development workflow, and environment variable requirements for the Takie todo app.

## Outcome

- ✅ Impact: Project documentation established with clear tech stack, agent roles, and development workflow
- 🧪 Tests: File creation validated; content matches specification
- 📁 Files: CLAUDE.md created at root
- 🔁 Next prompts: Create agent definition files (@agents/*.md), establish specs directory, configure environment
- 🧠 Reflection: Project structure and documentation foundation established for spec-driven development workflow

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): File creation PASS
- Prompt variant (if applicable): null
- Next experiment: Create supporting documentation and agent files
