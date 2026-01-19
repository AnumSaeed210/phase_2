# Task Breakdown: UI/UX Transformation & Landing Page

**Feature**: Spec 4: UI/UX Transformation & Landing Page
**Branch**: `004-ui-ux-polish`
**Date**: 2026-01-14
**Plan**: [specs/004-ui-ux-polish/plan.md](plan.md)
**Spec**: [specs/004-ui-ux-polish/spec.md](spec.md)

---

## Executive Summary

This task breakdown converts the implementation plan into **38 ordered, parallel-safe tasks** organized by user story and implementation phase. The feature introduces a public landing page and enhances the authenticated UI with design system compliance, responsiveness, and accessibility (WCAG AA).

**Total Tasks**: 38
- **Phase 1 (Setup & Foundation)**: 7 tasks
- **Phase 2 (Design System & Routing)**: 8 tasks
- **User Story 1 (Landing Page)**: 8 tasks
- **User Story 2 (Task List Display)**: 6 tasks
- **User Story 3 (Form Interactions)**: 5 tasks
- **User Story 4 (Navigation & Feedback)**: 2 tasks
- **User Story 5 (Accessibility & Responsiveness)**: 2 tasks

**MVP Scope**: Phase 1 + Phase 2 + User Story 1 (landing page creation)
**Full Scope**: All phases and user stories (production-quality application)

---

## Task Dependencies & Parallelization

### Dependency Chain
```
Phase 1 (Setup)
    ↓
Phase 2 (Design System & Routing)
    ↓ (blocks all user stories)
    ├→ [P] User Story 1 (Landing Page) - independent
    ├→ [P] User Story 2 (Task List) - independent
    ├→ [P] User Story 3 (Forms) - independent
    ├→ [P] User Story 4 (Navigation) - depends on US2 & US3 (can start after)
    └→ [P] User Story 5 (Accessibility) - spans all (runs in parallel)
```

### Parallel Execution Groups

**After Phase 2 (all can run in parallel)**:
1. **Group A**: User Story 1 (Landing Page) - 8 tasks, fully independent
2. **Group B**: User Story 2 (Task List) - 6 tasks, independent from US1
3. **Group C**: User Story 3 (Forms) - 5 tasks, independent from US1 & US2
4. **Group D**: User Story 4 (Navigation) - 2 tasks, can run after US2 & US3 start
5. **Group E**: User Story 5 (Accessibility) - 2 tasks, validation across all stories

### Estimated Task Duration

- **Phase 1**: ~1-2 hours (setup)
- **Phase 2**: ~2-3 hours (design system)
- **User Story 1**: ~2-3 hours (landing page)
- **User Story 2**: ~2-3 hours (task list styling)
- **User Story 3**: ~1-2 hours (form states)
- **User Story 4**: ~1 hour (navigation)
- **User Story 5**: ~2-3 hours (accessibility audit & fixes)

**Total**: ~12-17 hours of implementation work

---

## Phase 1: Setup & Foundation

**Goal**: Initialize project structure, dependencies, and base configuration for design system implementation.

**Independent Test**:
- Project compiles without errors
- Tailwind CSS processes correctly
- design-guide.md colors are documented

### Tasks

- [ ] T001 Create design-tokens.ts file with color, spacing, and typography constants in `frontend/src/lib/styles/design-tokens.ts`
- [ ] T002 Update `frontend/tailwind.config.ts` to add design-guide.md colors as custom color palette (slate, violet, lime, white)
- [ ] T003 Add design token spacing scale to `tailwind.config.ts` (4px, 8px, 12px, 16px, 24px, 32px, 48px)
- [ ] T004 Create or update `frontend/src/app/globals.css` with base styles: reset, typography defaults, body background (Midnight Slate)
- [ ] T005 Add utility classes to `globals.css`: flex layouts, spacing utilities, typography helpers
- [ ] T006 Add focus/hover states and accessibility utilities to `globals.css`
- [ ] T007 Verify Tailwind CSS build and styles output in browser console

---

## Phase 2: Design System & Routing Foundation

**Goal**: Establish design system components and routing architecture to support all user stories.

**Independent Test**:
- Common components render with correct styling
- Routes are structured and accessible
- Middleware auth logic works for public/protected routes
- Color palette is consistently applied

### Tasks

- [ ] T008 [P] Create Button component in `frontend/src/components/common/Button.tsx` with variants (primary/secondary), sizes (sm/md/lg), and states (hover, active, disabled, loading)
- [ ] T009 [P] Create Card component in `frontend/src/components/common/Card.tsx` with Midnight Slate background, responsive padding, and subtle shadow
- [ ] T010 [P] Create LoadingSpinner component in `frontend/src/components/common/LoadingSpinner.tsx` with smooth animation and prefers-reduced-motion support
- [ ] T011 Update `frontend/src/middleware.ts` to implement auth routing logic: redirect unauthenticated from protected routes to signin, redirect authenticated from `/` to `/tasks`, pass through public routes
- [ ] T012 Enhance `frontend/src/app/layout.tsx` to check auth state, conditionally render Navbar with user info for authenticated users, apply design system styling
- [ ] T013 [P] Create reusable FormInput component in `frontend/src/components/common/FormInput.tsx` with Focus Violet focus states, error display, and helper text
- [ ] T014 [P] Create reusable ErrorDisplay component in `frontend/src/components/common/ErrorDisplay.tsx` with alert styling and icon
- [ ] T015 Create or update `frontend/src/components/common/index.ts` to export all common components for easy imports

---

## Phase 3: User Story 1 - Public Landing Page Discovery

**Story Goal**: Create a static, unauthenticated landing page that clearly communicates product purpose, key features, and value proposition with prominent Sign Up/Sign In CTAs.

**Independent Test Criteria**:
- Unauthenticated user visits `/` and sees landing page (not redirect to signin)
- Landing page loads as static HTML (no API calls)
- Product purpose visible above the fold (first 100 pixels)
- 3+ key product benefits clearly displayed
- Sign Up button in header navigates to `/signup`
- Sign In button in header navigates to `/signin`
- Additional CTA button in page body redirects to Sign Up
- Layout is responsive (320px, 768px, 1024px+) with no horizontal scrolling
- Authenticated user visits `/` and is redirected to `/tasks`

### Tasks

- [ ] T016 [US1] Create Hero component in `frontend/src/components/landing/Hero.tsx` with headline, subheading, description, and "Get Started" CTA button
- [ ] T017 [US1] Create Features component in `frontend/src/components/landing/Features.tsx` displaying 3+ key benefits (e.g., "Simple Task Management", "Track Progress", "Stay Organized") in responsive grid layout
- [ ] T018 [US1] Create ValueProp component in `frontend/src/components/landing/ValueProp.tsx` highlighting why users should use the product with Focus Violet text highlights
- [ ] T019 [US1] Create LandingCTA component in `frontend/src/components/landing/CTA.tsx` with "Sign Up" and "Sign In" buttons, both accessible and responsive
- [ ] T020 [US1] Create landing page route in `frontend/src/app/page.tsx` that composes Hero, Features, ValueProp, and CTA components into a complete static page
- [ ] T021 [US1] [P] Create landing page navbar (header) component in `frontend/src/components/landing/Header.tsx` with logo/branding and prominent "Sign Up" + "Sign In" buttons
- [ ] T022 [US1] Test landing page responsive layout on mobile (320px), tablet (768px), desktop (1024px+) viewports without horizontal scrolling
- [ ] T023 [US1] Test auth redirect: log in, navigate to `/`, verify redirect to `/tasks` within 1 second

---

## Phase 4: User Story 2 - Polished Task List Display

**Story Goal**: Enhance task list UI to clearly communicate task state (pending vs completed) through visual design with proper spacing, typography, and color application.

**Independent Test Criteria**:
- Task list displays with improved spacing and typography
- Pending tasks use Midnight Slate background, Paper White text
- Completed tasks have strikethrough text and Momentum Lime accent
- Task items are card-based layout with consistent spacing
- Layout is responsive (320px, 768px, 1024px+)
- Touch targets are minimum 44px on mobile
- Empty state displays with motivating message and CTA

### Tasks

- [ ] T024 [US2] Enhance TaskList component in `frontend/src/components/tasks/TaskList.tsx` with improved layout, spacing using design tokens, Paper White text on Midnight Slate background
- [ ] T025 [US2] [P] Enhance TaskItem component in `frontend/src/components/tasks/TaskItem.tsx` to use Card component, add hover effects, visually distinguish completed tasks (strikethrough + Momentum Lime color)
- [ ] T026 [US2] [P] Enhance EmptyState component in `frontend/src/components/tasks/EmptyState.tsx` with motivating messaging, add "Create Task" CTA button using Button component
- [ ] T027 [US2] Enhance task list page in `frontend/src/app/(dashboard)/tasks/page.tsx` to apply responsive layout and design system styling
- [ ] T028 [US2] Test task list responsive layout on mobile (320px), tablet (768px), desktop (1024px+) viewports
- [ ] T029 [US2] Test task state distinction: create task, mark complete, verify strikethrough and Momentum Lime styling visible, verify completed/pending states are distinct

---

## Phase 5: User Story 3 - Enhanced Form & Input Interactions

**Story Goal**: Improve form inputs and submission experience with clear focus states, loading feedback, and error messaging.

**Independent Test Criteria**:
- Form inputs have clear Focus Violet border on focus
- Submit button shows loading state (disabled, loading spinner)
- Success feedback displays before redirect
- Error messages appear inline with clear guidance
- Form is responsive (320px, 768px, 1024px+)

### Tasks

- [ ] T030 [US3] Enhance TaskForm component in `frontend/src/components/tasks/TaskForm.tsx` with FormInput components, Focus Violet focus states, loading state on submit, inline error display
- [ ] T031 [US3] [P] Enhance SignInForm component in `frontend/src/components/auth/SignInForm.tsx` to use FormInput components, apply design system colors/spacing, add error display with ErrorDisplay component
- [ ] T032 [US3] [P] Enhance SignUpForm component in `frontend/src/components/auth/SignUpForm.tsx` to use FormInput components, apply design system colors/spacing, add error display with ErrorDisplay component
- [ ] T033 [US3] Test form focus states: click form inputs, verify Focus Violet border and clear focus indicator
- [ ] T034 [US3] Test form submission: submit task form, verify loading state visible, verify error messages display inline with clear guidance

---

## Phase 6: User Story 4 - Clear Navigation & System Feedback

**Story Goal**: Enhance navigation bar and system feedback to clearly indicate current page and loading states.

**Independent Test Criteria**:
- Active page is highlighted in navbar with Focus Violet accent
- User email/info is displayed in navbar
- Loading indicators appear during page transitions
- Sign out button exists and redirects to landing page (`/`)

### Tasks

- [ ] T035 [US4] Enhance Navbar component in `frontend/src/components/common/Navbar.tsx` to display active page indicator (Focus Violet underline/highlight), show user email, add Sign Out button
- [ ] T036 [US4] Implement sign-out handler to redirect to `/` (landing page) instead of signin, update auth context or hook to support this flow

---

## Phase 7: User Story 5 - Accessible & Responsive Design

**Story Goal**: Ensure WCAG AA compliance across all pages and components with proper keyboard navigation, focus management, color contrast, and responsive typography.

**Independent Test Criteria**:
- All pages pass WCAG AA color contrast check (4.5:1 for text, 3:1 for graphics)
- Keyboard navigation works on all pages (Tab through elements in logical order)
- Focus indicators are visible on all interactive elements
- Responsive typography and spacing scales correctly across viewports (320px, 768px, 1024px+)
- Touch targets are minimum 44px on mobile
- No horizontal scrolling on any viewport

### Tasks

- [ ] T037 [US5] Run accessibility audit on all pages using axe DevTools or WAVE, document color contrast ratios, focus states, and semantic HTML usage
- [ ] T038 [US5] Fix any WCAG AA violations found in audit: add focus indicators, improve color contrast if needed, verify semantic HTML structure, test keyboard navigation

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)
**Recommended for initial launch**: Phase 1 + Phase 2 + User Story 1
- Delivers public landing page with Sign Up/Sign In CTAs
- Establishes design system foundation
- Enables user acquisition through landing page
- **Estimated**: 6-8 hours

### Phase 2 Scope (Marketing-Ready)
**Add after MVP**: All of Phase 3 (User Story 2)
- Polished task list UI improves authenticated experience
- Visual feedback on task state
- **Estimated**: +2-3 hours

### Phase 3 Scope (Production Quality)
**Add after Phase 2**: User Stories 3, 4, 5
- Complete form interaction polish
- Navigation clarity
- Full accessibility compliance
- **Estimated**: +6-9 hours

---

## Task Execution Order

### Sequential (must complete in order):
1. Phase 1 (T001-T007) - foundation setup
2. Phase 2 (T008-T015) - design system & routing

### Parallel Execution (after Phase 2):
- **Stream A**: T016-T023 (User Story 1: Landing Page) - independent
- **Stream B**: T024-T029 (User Story 2: Task List) - independent
- **Stream C**: T030-T034 (User Story 3: Forms) - independent
- **Stream D**: T035-T036 (User Story 4: Navigation) - can start after T024 begins
- **Stream E**: T037-T038 (User Story 5: Accessibility) - validation across all

### Parallel Example 1: After Phase 2 Complete
```
Team A (2 devs):  T016 → T017 → T018 → T019 → T020 (Landing page)
Team B (2 devs):  T024 → T025 → T026 → T027 → T028 (Task list)
Team C (1 dev):   T030 → T031 → T032 (Forms)
Team D (1 dev):   T035 → T036 (Navigation, can start after T025)
Team E (1 dev):   T037 → T038 (Accessibility validation)
```

### Sequential Backup (if limited resources):
T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010 → T011 → T012 → T013 → T014 → T015 → T016 → T017 → T018 → T019 → T020 → T021 → T022 → T023 → T024 → T025 → T026 → T027 → T028 → T029 → T030 → T031 → T032 → T033 → T034 → T035 → T036 → T037 → T038

---

## File Manifest

### New Files to Create
```
frontend/src/lib/styles/design-tokens.ts
frontend/src/components/common/Button.tsx
frontend/src/components/common/Card.tsx
frontend/src/components/common/LoadingSpinner.tsx
frontend/src/components/common/FormInput.tsx
frontend/src/components/common/ErrorDisplay.tsx
frontend/src/components/common/index.ts
frontend/src/components/landing/Hero.tsx
frontend/src/components/landing/Features.tsx
frontend/src/components/landing/ValueProp.tsx
frontend/src/components/landing/CTA.tsx
frontend/src/components/landing/Header.tsx
```

### Files to Enhance/Update
```
frontend/tailwind.config.ts
frontend/src/app/globals.css
frontend/src/middleware.ts
frontend/src/app/layout.tsx
frontend/src/app/page.tsx (new landing page route)
frontend/src/components/tasks/TaskList.tsx
frontend/src/components/tasks/TaskItem.tsx
frontend/src/components/tasks/EmptyState.tsx
frontend/src/components/tasks/TaskForm.tsx
frontend/src/components/auth/SignInForm.tsx
frontend/src/components/auth/SignUpForm.tsx
frontend/src/components/common/Navbar.tsx
frontend/src/app/(dashboard)/tasks/page.tsx
```

---

## Success Verification Checklist

### Phase 1 & 2 Verification (Foundation)
- [ ] Design tokens file compiles without errors
- [ ] Tailwind config includes all design colors
- [ ] globals.css applies Midnight Slate background
- [ ] Button, Card, LoadingSpinner components render correctly
- [ ] Middleware routes public/protected pages correctly
- [ ] Navbar renders in layout

### User Story 1 Verification (Landing Page)
- [ ] Landing page route `/` exists and renders
- [ ] Hero section displays headline/subheading above the fold
- [ ] Features section shows 3+ key benefits
- [ ] Sign Up/Sign In buttons in header and body
- [ ] Responsive layout on 320px, 768px, 1024px+ viewports
- [ ] Authenticated users redirect `/` → `/tasks`
- [ ] CTAs navigate to `/signup` and `/signin` correctly

### User Story 2 Verification (Task List)
- [ ] Task list uses Card layout with proper spacing
- [ ] Pending tasks display with Midnight Slate/Paper White
- [ ] Completed tasks have strikethrough + Momentum Lime
- [ ] Empty state displays with CTA
- [ ] Responsive layout on mobile/tablet/desktop
- [ ] Touch targets minimum 44px on mobile

### User Story 3 Verification (Forms)
- [ ] Form inputs have Focus Violet focus state
- [ ] Submit buttons show loading state
- [ ] Error messages display inline
- [ ] Success feedback shows before redirect
- [ ] Forms are responsive on all viewports

### User Story 4 Verification (Navigation)
- [ ] Navbar shows active page (Focus Violet highlight)
- [ ] User email displays in navbar
- [ ] Sign Out button exists and works
- [ ] Sign out redirects to `/` (landing page)

### User Story 5 Verification (Accessibility)
- [ ] WCAG AA audit passes (all pages)
- [ ] Color contrast meets 4.5:1 (text) and 3:1 (graphics)
- [ ] Keyboard navigation works on all pages
- [ ] Focus indicators visible on all interactive elements
- [ ] No horizontal scrolling on any viewport
- [ ] Responsive typography scales correctly

---

## Notes for Implementation Agents

1. **Design System First**: Complete Phase 1 & 2 before starting user stories. These establish foundation for all components.

2. **Use Design Tokens**: Reference `design-tokens.ts` constants (colors, spacing, typography) in all components for consistency.

3. **Tailwind CSS Utilities**: Leverage Tailwind utilities for spacing, flexbox, and responsive design. Minimize custom CSS.

4. **Accessibility Throughout**: Each task should include keyboard navigation and focus state testing. Don't leave accessibility for the end.

5. **Responsive First**: Design components with mobile (320px) as baseline, then enhance for larger viewports.

6. **Color Palette**: Strictly follow design-guide.md colors:
   - Midnight Slate (#323843): Backgrounds, structure
   - Focus Violet (#c68dff): Buttons, active states, focus indicators
   - Momentum Lime (#cbe857): Success states, completed tasks
   - Paper White (#f5f5f5): Text content, contrast

7. **Component Reuse**: Use Button, Card, FormInput, and ErrorDisplay components throughout. Don't duplicate styles.

8. **Testing**: Each task includes acceptance criteria. Test before moving to next task. Don't batch testing at the end.

9. **Git Commits**: Commit after each task or logical group (e.g., after T007, T015, T023, etc.) with clear message reflecting story goal.

10. **No Backend Changes**: This spec involves frontend-only changes. Do not modify backend APIs, auth logic, or database schema.

---

**Status**: ✅ Task breakdown complete. All 38 tasks organized, parallelizable, and ready for implementation agents.
**Next Step**: Agents can begin with Phase 1 (T001-T007) immediately.
