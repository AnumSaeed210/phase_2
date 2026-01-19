# Implementation Plan: UI/UX Transformation & Landing Page

**Branch**: `004-ui-ux-polish` | **Date**: 2026-01-14 | **Spec**: [specs/004-ui-ux-polish/spec.md](spec.md)
**Input**: Feature specification from `/specs/004-ui-ux-polish/spec.md`

## Summary

Transform the Todo application from a functional MVP (Spec 3) into a production-quality application with two distinct user experiences:

1. **Public Landing Page** (new): Static, unauthenticated user discovery page at `/` that communicates product purpose, key features (3+), value proposition, and provides Sign Up/Sign In CTAs
2. **Polished Authenticated UI** (enhancement): Visual and interaction improvements to task management interface including better typography, spacing, color application per design guide, responsive layout, and accessibility compliance (WCAG AA)

**Technical Approach**: Client-side only. Leverage existing Next.js 16+ App Router structure from Spec 3. Create new public route at `/` with conditional rendering logic to redirect authenticated users to `/tasks` dashboard. Enhance existing component styling and navigation using Tailwind CSS and design-guide.md palette (Midnight Slate, Focus Violet, Momentum Lime, Paper White). No backend changes, API contract changes, or database schema changes required.

---

## Technical Context

**Language/Version**: TypeScript + Next.js 16+ (App Router), Node.js 18+

**Primary Dependencies**:
- Frontend framework: Next.js 16+ with App Router
- Styling: Tailwind CSS (already in project)
- Authentication: Better Auth (already integrated, JWT-based)
- Component library: Custom React components (no external component library)

**Storage**: N/A (frontend-only changes)

**Testing**: React Testing Library + Vitest or Jest (existing test setup from Spec 3)

**Target Platform**: Web (desktop, tablet, mobile - 320px+)

**Project Type**: Single web application (Next.js frontend + existing Python FastAPI backend)

**Performance Goals**:
- Landing page: Static HTML rendering, <1s load time on 4G
- Page transitions: Smooth without layout shifts (CLS < 0.1)
- Interactive elements: Responsive within 200ms

**Constraints**:
- No backend API changes
- No authentication logic changes
- No task data model changes
- Landing page must be statically renderable
- Must strictly follow `frontend/design-guide.md` color palette and spacing
- WCAG AA accessibility compliance required
- Responsive design: 320px (mobile), 768px (tablet), 1024px+ (desktop)

**Scale/Scope**:
- 2 new/modified page routes: `/` (landing) and improved `/tasks` (dashboard)
- 5 existing pages to enhance: `/signin`, `/signup`, `/tasks`, `/tasks/[taskId]`, `/tasks/new`
- ~10-15 component updates for styling/spacing/accessibility
- No new data models or API endpoints

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Constitutional Principles Alignment

| Principle | Assessment | Status |
|-----------|-----------|--------|
| **I. Spec-First Development** | Spec 4 comprehensively defines landing page and UI polish requirements with 5 user stories, 26 functional requirements, and 20 success criteria. All behavior is deterministically specified. | ✅ PASS |
| **II. Agentic Workflow Integrity** | Implementation will proceed through Claude Code agents (Next.js UI Optimizer, Auth Security Reviewer). No manual coding. | ✅ PASS |
| **III. Security by Design** | No authentication changes required. Existing JWT-based auth from Spec 3 remains. Landing page is public (no auth required). Authenticated pages remain protected. User isolation already enforced. | ✅ PASS |
| **IV. User Isolation** | Feature does not affect data access patterns. Existing user isolation from Spec 3 persists unchanged. | ✅ PASS |
| **V. Deterministic Behavior** | Spec defines exact routing behavior (redirect to `/tasks` for auth users), color usage, spacing scale, typography hierarchy, focus states, loading states, and error states. All behaviors are deterministic and measurable. | ✅ PASS |
| **VI. Reproducibility** | Same spec and plan will consistently produce the same UI/UX. Technology stack is fixed (Next.js, Tailwind, design-guide.md). No non-deterministic decisions required. | ✅ PASS |

### Technology Stack Validation

- ✅ Frontend: Next.js 16+ (App Router) - matches constitution
- ✅ Styling: Tailwind CSS - appropriate for responsive design and design system compliance
- ✅ Authentication: Better Auth (JWT) - existing, unchanged
- ✅ No backend/database changes required
- ✅ No new external dependencies needed

### Compliance Summary

**Gate Status**: ✅ **PASS** - Feature fully complies with constitution. No deviations, no justifications required. Spec-first process adhered to, agentic workflow will be followed, security by design is maintained, and reproducibility is ensured.

---

## Project Structure

### Documentation (this feature)

```text
specs/004-ui-ux-polish/
├── spec.md                  # Feature specification (complete)
├── plan.md                  # This file (implementation plan)
├── research.md              # Phase 0 output (if research needed)
├── data-model.md            # Phase 1 output (routes, components, styling system)
├── quickstart.md            # Phase 1 output (setup guide for developers)
├── contracts/               # Phase 1 output (routing, component contracts)
│   ├── pages.md
│   ├── components.md
│   └── styling.md
└── checklists/
    └── requirements.md      # Specification validation checklist
```

### Source Code (repository)

```text
# Existing structure from Spec 3 (unchanged backend)
backend/
└── [unchanged]

# Frontend structure (Spec 4 enhancements)
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx                    # Enhanced navbar with navigation state
│   │   ├── page.tsx                      # NEW: Landing page for unauth users
│   │   ├── error.tsx                     # Enhanced error handling
│   │   ├── (auth)/
│   │   │   ├── signin/
│   │   │   │   └── page.tsx              # Enhanced styling/accessibility
│   │   │   └── signup/
│   │   │       └── page.tsx              # Enhanced styling/accessibility
│   │   └── (dashboard)/
│   │       ├── layout.tsx                # Enhanced with design system
│   │       ├── tasks/
│   │       │   ├── page.tsx              # Polished task list
│   │       │   ├── [taskId]/
│   │       │   │   └── page.tsx          # Enhanced task detail
│   │       │   └── new/
│   │       │       └── page.tsx          # Enhanced form styling
│   │       └── profile/
│   │           └── page.tsx              # Styling enhancements
│   ├── components/
│   │   ├── auth/
│   │   │   ├── SignInForm.tsx            # Enhanced styling
│   │   │   └── SignUpForm.tsx            # Enhanced styling
│   │   ├── common/
│   │   │   ├── Navbar.tsx                # Enhanced navigation, active state
│   │   │   ├── Button.tsx                # NEW: Reusable button component
│   │   │   ├── Card.tsx                  # NEW: Reusable card component
│   │   │   └── LoadingSpinner.tsx        # NEW: Loading state component
│   │   ├── tasks/
│   │   │   ├── TaskList.tsx              # Enhanced layout and spacing
│   │   │   ├── TaskItem.tsx              # Enhanced visual state
│   │   │   ├── TaskForm.tsx              # Enhanced form styling
│   │   │   └── EmptyState.tsx            # Enhanced messaging
│   │   └── landing/
│   │       ├── Hero.tsx                  # NEW: Landing page hero section
│   │       ├── Features.tsx              # NEW: Features section (3+ benefits)
│   │       ├── ValueProp.tsx             # NEW: Value proposition section
│   │       └── CTA.tsx                   # NEW: Call-to-action section
│   ├── lib/
│   │   ├── auth/                         # Unchanged
│   │   ├── api/                          # Unchanged
│   │   ├── hooks/                        # Unchanged
│   │   ├── styles/
│   │   │   ├── design-tokens.ts          # NEW: Color, spacing, typography tokens
│   │   │   └── globals.css               # Enhanced with design system
│   │   └── utils/
│   │       └── formatting.ts             # Existing, enhanced if needed
│   ├── middleware.ts                     # Enhanced auth state routing
│   └── app/globals.css                   # Updated with design system tokens
├── public/
│   └── [no changes]
├── tailwind.config.ts                    # Enhanced with design-guide.md colors
└── tsconfig.json                         # Existing
```

**Structure Decision**: Web application with Next.js App Router frontend. Existing backend from Spec 3 remains unchanged. Frontend enhancements are isolated to client-side pages, components, and styling. No changes to API layer, database layer, or authentication mechanism.

---

## Complexity Tracking

No violations. Feature fully adheres to constitution. Spec-first development maintained, agentic workflow will be followed, no security deviations, no technology stack changes.

---

## Implementation Strategy

### Phase 0: Research & Setup

**Objective**: Validate assumptions and establish foundation

**Research Topics** (if needed):
1. Next.js 16 App Router routing patterns for public vs authenticated pages
2. Tailwind CSS design token implementation for consistent branding
3. WCAG AA accessibility best practices for form focus states and keyboard navigation
4. Responsive design patterns for 320px-1024px+ viewports
5. Next.js middleware for conditional routing based on auth state

**Outputs**:
- `research.md`: Document findings, best practices, and implementation patterns
- Updated `tailwind.config.ts` with design-guide.md color palette as design tokens
- Enhanced `globals.css` with typography scale and spacing utilities

### Phase 1: Design & Architecture

**Objective**: Define component contracts, routing structure, and styling system

**1a. Data Model & Contracts**:
- Document routing structure: `/` (public landing), `/signin`, `/signup`, `/tasks` (protected), `/tasks/[taskId]` (protected), `/tasks/new` (protected)
- Define component contracts (props, state, behavior)
- Establish design token mapping (colors, spacing, typography, breakpoints)
- Document middleware routing logic for auth redirect

**Outputs**:
- `data-model.md`: Routes, components, design tokens, middleware logic
- `contracts/pages.md`: Page route definitions and auth requirements
- `contracts/components.md`: Component API contracts
- `contracts/styling.md`: Design token system and Tailwind configuration

**1b. Styling System**:
- Extract color palette from `frontend/design-guide.md` as Tailwind design tokens
- Define spacing scale (4px, 8px, 12px, 16px, 24px, 32px, 48px)
- Define typography scale (heading hierarchy: h1, h2, h3; body text sizes)
- Define component base styles (buttons, inputs, forms, cards)
- Define responsive breakpoints: `sm` (320px), `md` (768px), `lg` (1024px+)

**Outputs**:
- Enhanced `tailwind.config.ts` with design tokens
- New `frontend/src/lib/styles/design-tokens.ts` with token constants
- Updated `frontend/src/app/globals.css` with utility classes and base styles

**1c. Component Architecture**:
- Identify reusable components: Button, Card, LoadingSpinner, Form inputs
- Define landing page component structure: Hero, Features, ValueProp, CTA sections
- Document component composition patterns

**Outputs**:
- `contracts/components.md` with component API specs

**1d. Routing & Middleware**:
- Define public routes: `/`, `/signin`, `/signup` (no auth required)
- Define protected routes: `/tasks`, `/tasks/[taskId]`, `/tasks/new`, `/profile` (auth required)
- Document middleware logic: Check `Better Auth` session, redirect unauthenticated users from protected routes to signin, redirect authenticated users from landing page to `/tasks`
- Define sign-out flow: Redirect to landing page (`/`)

**Outputs**:
- Enhanced `frontend/src/middleware.ts` with routing logic
- `contracts/pages.md` with route definitions

**1e. Accessibility & Responsive Design**:
- Define focus management patterns for forms and navigation
- Define keyboard navigation order
- Define color contrast requirements (4.5:1 for text, 3:1 for graphics)
- Define responsive typography and spacing scales
- Define ARIA patterns for dynamic content (loading states, error messages)

**Outputs**:
- `quickstart.md` with accessibility requirements and patterns
- Documented in component contracts

### Phase 2: Task Breakdown

**Objective**: Convert design into ordered, parallel-safe implementation tasks (handled by `/sp.tasks` command)

Tasks will be organized by:
1. **Foundation Tasks** (prerequisite): Design tokens, Tailwind config, globals.css
2. **Landing Page Tasks** (can run in parallel): Hero section, Features, ValueProp, CTA, responsive layout
3. **Routing & Middleware Tasks** (can run in parallel with landing page): Middleware auth routing, public/protected route structure
4. **UI Component Tasks** (can run in parallel): Button, Card, LoadingSpinner, Form inputs
5. **Page Enhancement Tasks** (depend on components): Auth pages (signin/signup), Task pages (list, detail, new), Profile page
6. **Navigation Enhancement Tasks**: Enhanced Navbar with active state, user info
7. **Integration & Testing Tasks**: Full-flow testing, accessibility audit, responsive design verification

---

## Implementation Details

### Core Components to Build/Enhance

#### New Components

1. **Button** (`frontend/src/components/common/Button.tsx`):
   - Props: variant (primary/secondary), size (sm/md/lg), disabled state, loading state
   - Styling: Focus Violet for primary, responsive sizing, clear focus indicator
   - States: hover, active, disabled, loading

2. **Card** (`frontend/src/components/common/Card.tsx`):
   - Props: children, padding, className
   - Styling: Midnight Slate background, subtle shadow, responsive spacing
   - Usage: Task items, form containers, landing page sections

3. **LoadingSpinner** (`frontend/src/components/common/LoadingSpinner.tsx`):
   - Props: size, color
   - Animation: Smooth rotation, disrespect prefers-reduced-motion
   - Usage: Form submission, page transitions

4. **Hero** (`frontend/src/components/landing/Hero.tsx`):
   - Content: Headline, subheading, product description
   - Design: Full-width, Midnight Slate background, Paper White text
   - Responsive: Stack vertically on mobile, flex layout on desktop
   - CTA: "Get Started" button (Focus Violet)

5. **Features** (`frontend/src/components/landing/Features.tsx`):
   - Content: 3+ key benefits with icons/descriptions
   - Design: Card grid layout, responsive columns
   - Responsive: 1 column (mobile), 2 columns (tablet), 3 columns (desktop)

6. **ValueProp** (`frontend/src/components/landing/ValueProp.tsx`):
   - Content: Why users should use the product, key differentiators
   - Design: Highlight important text with Focus Violet
   - Responsive: Flex layout adapting to screen size

7. **LandingCTA** (`frontend/src/components/landing/CTA.tsx`):
   - Content: Call-to-action section with Sign Up and Sign In buttons
   - Design: Both buttons visible and accessible
   - Links: Sign Up → `/signup`, Sign In → `/signin`

#### Enhanced Components

1. **Navbar** (`frontend/src/components/common/Navbar.tsx`):
   - Add active state indicator (Focus Violet underline/highlight for current page)
   - Display user email/info
   - Add Sign Out button (redirects to landing page)
   - Responsive: Hamburger menu on mobile if needed

2. **TaskList** (`frontend/src/components/tasks/TaskList.tsx`):
   - Layout: Improved spacing and typography
   - Styling: Midnight Slate background, Paper White text, Focus Violet accents
   - Task items: Clear completed state (strikethrough + Momentum Lime accent)
   - Empty state: Motivating message with CTA

3. **TaskItem** (`frontend/src/components/tasks/TaskItem.tsx`):
   - Visual state: Clear pending vs completed distinction
   - Styling: Card layout with hover effects
   - Actions: Edit/delete affordances with clear icons
   - Responsive: Adapt layout for mobile

4. **TaskForm** (`frontend/src/components/tasks/TaskForm.tsx`):
   - Focus states: Clear Focus Violet border on input focus
   - Loading state: Submit button shows loading indicator
   - Error states: Inline error messages with warning color
   - Responsive: Full-width on mobile, flex layout on desktop

5. **SignInForm** & **SignUpForm** (`frontend/src/components/auth/*.tsx`):
   - Styling: Match design system (colors, spacing, typography)
   - Focus states: Clear focus indicators on inputs
   - Error messages: Inline, clear, actionable
   - Responsive: Full-width forms on mobile

#### Design Tokens

New file: `frontend/src/lib/styles/design-tokens.ts`

```typescript
export const colors = {
  slate: '#323843',      // Midnight Slate
  violet: '#c68dff',     // Focus Violet
  lime: '#cbe857',       // Momentum Lime
  white: '#f5f5f5',      // Paper White
  error: '#ff6b6b',      // Error red (for accessibility)
}

export const spacing = [4, 8, 12, 16, 24, 32, 48] // px values

export const typography = {
  h1: { size: '32px', weight: '600' },
  h2: { size: '24px', weight: '600' },
  h3: { size: '18px', weight: '600' },
  body: { size: '16px', weight: '400' },
  small: { size: '14px', weight: '400' },
}

export const breakpoints = {
  sm: '320px',
  md: '768px',
  lg: '1024px',
}
```

### Routing & Middleware

**Updated `frontend/src/middleware.ts`**:
- Check Better Auth session
- If authenticated and path is `/`: redirect to `/tasks`
- If unauthenticated and path starts with `/tasks`: redirect to `/signin`
- Pass through public routes: `/`, `/signin`, `/signup`

**Updated `frontend/src/app/layout.tsx`**:
- Check auth state
- Render Navbar with Sign Out option for authenticated users
- Render landing page nav for unauthenticated users
- Enhanced styling with design system

**New `frontend/src/app/page.tsx`** (Landing Page):
- Check auth state (if authenticated, middleware will redirect)
- Render: Hero + Features + ValueProp + CTA sections
- Responsive layout

### Styling System

**Enhanced `frontend/tailwind.config.ts`**:
- Add design colors from design-guide.md as custom colors
- Add custom spacing scale
- Add custom typography scale
- Add custom breakpoints (if not using defaults)
- Configure responsive prefixes

**Enhanced `frontend/src/app/globals.css`**:
- Base styles: reset, typography defaults, body background
- Utility classes: flex layouts, spacing utilities, typography utilities
- Component base styles: button, input, form, card
- Focus/hover states for accessibility
- Responsive utilities

### Accessibility Patterns

1. **Keyboard Navigation**:
   - Tab order follows visual flow
   - All interactive elements have clear focus indicators (Focus Violet border/outline)
   - Skip links if needed for landing page

2. **Form Focus States**:
   - Input focus: Focus Violet border + outline
   - Submit button focus: Clear indicator
   - Error states have `aria-invalid="true"` and error message has `role="alert"`

3. **Color Contrast**:
   - Text: 4.5:1 contrast ratio (Paper White on Midnight Slate = high contrast)
   - Graphics: 3:1 contrast ratio for icons/accents
   - Error states: Don't rely on color alone; use icons + text

4. **ARIA Patterns**:
   - Loading states: Spinner has `aria-label="Loading"`
   - Error messages: `role="alert"` for instant announcement
   - Navigation state: Current page link has `aria-current="page"`

5. **Responsive Design**:
   - Mobile-first approach (base styles for mobile, enhance with media queries)
   - Touch targets: Minimum 44px on mobile
   - Typography scales with viewport
   - No horizontal scrolling

---

## Deliverables

### Phase 0 Output
- `research.md` (if needed): Best practices and implementation patterns

### Phase 1 Output
- `data-model.md`: Routes, components, design tokens, styling system
- `contracts/pages.md`: Page route definitions and auth requirements
- `contracts/components.md`: Component API contracts
- `contracts/styling.md`: Design token system and Tailwind configuration
- `quickstart.md`: Developer setup and accessibility requirements guide
- Enhanced `tailwind.config.ts` with design tokens
- New `frontend/src/lib/styles/design-tokens.ts`
- Updated `frontend/src/app/globals.css`

### Phase 2 Output (from `/sp.tasks`)
- `tasks.md`: Ordered, parallel-safe implementation tasks organized by user story

### Implementation Output (from `/sp.implement`)
- Landing page: `frontend/src/app/page.tsx` + landing page components
- Enhanced components: Navbar, TaskList, TaskItem, TaskForm, Auth forms
- Enhanced styling: globals.css, tailwind.config.ts, design tokens
- Updated middleware: Auth routing and redirect logic
- Updated layout: Enhanced Navbar with navigation state

---

## Success Criteria Mapping

| Success Criterion | Implementation Task | Verification |
|-------------------|-------------------|--------------|
| **SC-LP-001**: Unauthenticated users see landing page at `/` | Create public `page.tsx` at `/`, update middleware | Test: Navigate to `/` without auth, see landing page |
| **SC-LP-002**: 3+ key product benefits visible | Create Features component with 3+ sections | Review: Check features section content |
| **SC-LP-003**: Sign Up/Sign In buttons in header + body | Add buttons to Hero and CTA sections | Test: Verify button placement and functionality |
| **SC-LP-004**: Landing page responsive (320px-1024px+) | Responsive component layouts with Tailwind | Test: Verify layout on mobile/tablet/desktop |
| **SC-LP-005**: Static rendering (no API calls) | Use static content, no API calls | Review: Check page.tsx for API calls |
| **SC-LP-006**: Auth users redirect to `/tasks` within 1s | Update middleware auth routing | Test: Login, verify redirect to `/tasks` |
| **SC-LP-007**: WCAG AA accessibility | Semantic HTML, focus states, color contrast | Audit: Run accessibility checker |
| **SC-UI-001**: WCAG AA on authenticated pages | Semantic HTML, focus states, ARIA patterns | Audit: Run accessibility checker |
| **SC-UI-002**: Task list responsive | Enhance TaskList with responsive layout | Test: Verify layout on mobile/tablet/desktop |
| **SC-UI-003**: Task form completable in 30s | Enhance form with clear focus states | Test: Create task, time interaction |
| **SC-UI-004**: Loading states within 200ms | Add LoadingSpinner component | Review: Check loading state timing |
| **SC-UI-005**: Focus indicators & 3:1 contrast | Add focus Violet focus states | Audit: Verify contrast and focus states |
| **SC-UI-006**: Form errors inline | TaskForm error state display | Test: Submit invalid form, check error display |
| **SC-UI-007**: Task state distinct (not color alone) | Use strikethrough + Momentum Lime | Review: Verify completion indicator |
| **SC-UI-008**: Navigation active state | Enhance Navbar with active page indicator | Test: Navigate between pages, check highlighting |
| **SC-UI-009**: Empty state visible | Enhance EmptyState component | Review: Check empty state messaging |
| **SC-UI-010**: Design colors consistent | Apply design-guide.md colors to all components | Review: Verify color usage |
| **SC-UI-011**: Text readable 4.5:1 contrast | Apply Paper White on Midnight Slate | Audit: Verify contrast ratios |
| **SC-UI-012**: Sign out → landing page | Update sign-out handler to redirect to `/` | Test: Sign out, verify landing page |
| **SC-UI-013**: Smooth page transitions | Use CSS transitions and Tailwind | Test: Navigate between pages, observe smoothness |

---

## Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Auth state routing bugs | Medium | Medium | Thorough testing of middleware logic; test auth and unauth flows |
| Responsive layout breaks on edge cases | Medium | Low | Test on actual devices; use mobile-first approach |
| Accessibility issues (focus, contrast) | Low | High | Use accessibility tools (axe, WAVE); follow ARIA patterns |
| Design token inconsistency | Low | Medium | Centralize tokens in design-tokens.ts; reference in components |
| Component prop API complexity | Low | Medium | Keep components simple; document props; use TypeScript |

---

## Dependencies & Blockers

- ✅ **No blockers**: Feature requires no backend changes, no new dependencies, no database schema changes
- ✅ **Spec 3 completion**: Assumes Spec 3 (auth, task CRUD) is complete and working
- ✅ **design-guide.md**: Must be available and finalized (already exists)
- ✅ **Tailwind CSS**: Already in project from Spec 3

---

## Timeline & Resource Allocation

*Note: This plan is resource-ordered, not time-ordered. Implementation will be concurrent where possible.*

- **Phase 0 Research**: 1-2 research tasks (if needed) - parallel with Phase 1 design
- **Phase 1 Design**: 4 parallel work streams:
  1. Design tokens + styling system
  2. Routing & middleware
  3. Component contracts
  4. Accessibility patterns
- **Phase 2 Task Breakdown**: 1 task to organize Phase 2 into `/sp.tasks` format
- **Phase 3+ Implementation**: Organized by `/sp.tasks` command (estimated 12-20 tasks, many parallelizable)

---

**Status**: ✅ Plan complete and ready for Phase 2 task breakdown. Constitution check passed. No research required (tech stack and patterns are well-established). Proceed to `/sp.tasks` for task breakdown.
