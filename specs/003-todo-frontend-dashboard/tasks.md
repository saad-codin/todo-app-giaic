# Tasks: Todo App Frontend Dashboard

**Input**: Design documents from `/specs/003-todo-frontend-dashboard/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-client.md

**Tests**: Not explicitly requested in spec. Test tasks omitted per template guidelines.

**Organization**: Tasks grouped by user story (13 stories: 3 P1, 5 P2, 5 P3) for independent implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US13)
- Paths follow plan.md structure: `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Next.js 14 configuration

- [x] T001 Create Next.js 14 project with App Router in frontend/ using create-next-app
- [x] T002 Install dependencies: @tanstack/react-query, better-auth, date-fns, react-hook-form, zod, @hookform/resolvers
- [x] T003 [P] Configure Tailwind CSS with custom priority colors in frontend/tailwind.config.js
- [x] T004 [P] Create environment variables file frontend/.env.local with NEXT_PUBLIC_API_URL
- [x] T005 [P] Configure TypeScript with path aliases in frontend/tsconfig.json

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create TypeScript types for User, Task, Tag in frontend/src/types/task.ts
- [x] T007 [P] Create TypeScript types for API requests/responses in frontend/src/types/api.ts
- [x] T008 [P] Create Zod validation schemas in frontend/src/lib/utils/validation.ts
- [x] T009 Implement API client with fetchWithAuth wrapper in frontend/src/lib/api.ts
- [x] T010 [P] Configure Better Auth client in frontend/src/lib/auth.ts
- [x] T011 [P] Create date utility functions in frontend/src/lib/utils/date.ts
- [x] T012 Setup React Query provider in frontend/src/app/layout.tsx
- [x] T013 [P] Create shared Button component in frontend/src/components/ui/Button.tsx
- [x] T014 [P] Create shared Input component in frontend/src/components/ui/Input.tsx
- [x] T015 [P] Create shared Badge component in frontend/src/components/ui/Badge.tsx
- [x] T016 [P] Create shared Toast component in frontend/src/components/ui/Toast.tsx
- [x] T017 Configure global styles in frontend/src/styles/globals.css

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - User Authentication (Priority: P1) 🎯 MVP

**Goal**: Users can sign up, sign in, and sign out securely with JWT-based auth

**Independent Test**: Create account, sign in, view dashboard, sign out. Verify protected routes redirect.

### Implementation for User Story 1

- [x] T018 [US1] Create root layout with providers in frontend/src/app/layout.tsx
- [x] T019 [P] [US1] Create landing page with auth links in frontend/src/app/page.tsx
- [x] T020 [P] [US1] Create auth route group layout in frontend/src/app/(auth)/layout.tsx
- [x] T021 [P] [US1] Create SignUpForm component in frontend/src/components/auth/SignUpForm.tsx
- [x] T022 [P] [US1] Create SignInForm component in frontend/src/components/auth/SignInForm.tsx
- [x] T023 [US1] Create sign-up page in frontend/src/app/(auth)/signup/page.tsx
- [x] T024 [US1] Create sign-in page in frontend/src/app/(auth)/signin/page.tsx
- [x] T025 [US1] Create useAuth hook with sign-in/sign-up/sign-out mutations in frontend/src/lib/hooks/useAuth.ts
- [x] T026 [US1] Create auth middleware for protected routes in frontend/src/middleware.ts
- [x] T027 [US1] Handle auth errors with user-friendly messages in SignInForm and SignUpForm
- [x] T028 [US1] Implement session persistence check on app load in useAuth hook

**Checkpoint**: Users can authenticate and access protected dashboard

---

## Phase 4: User Story 2 - Task CRUD Operations (Priority: P1)

**Goal**: Authenticated users can create, view, update, and delete tasks

**Independent Test**: Create task via Quick Add, view in list, edit description, delete. Verify persistence.

### Implementation for User Story 2

- [x] T029 [P] [US2] Create dashboard route group layout with Sidebar in frontend/src/app/(dashboard)/layout.tsx
- [x] T030 [P] [US2] Create main dashboard page shell in frontend/src/app/(dashboard)/page.tsx
- [x] T031 [US2] Create useTasks hook with CRUD operations in frontend/src/lib/hooks/useTasks.ts
- [x] T032 [P] [US2] Create TaskCard component in frontend/src/components/tasks/TaskCard.tsx
- [x] T033 [P] [US2] Create TaskList component in frontend/src/components/tasks/TaskList.tsx
- [x] T034 [US2] Create TaskForm component for create/edit in frontend/src/components/tasks/TaskForm.tsx
- [x] T035 [US2] Create QuickAdd component for rapid task creation in frontend/src/components/tasks/QuickAdd.tsx
- [x] T036 [US2] Implement optimistic updates for task mutations in useTasks hook
- [x] T037 [US2] Add delete confirmation dialog to TaskCard component
- [x] T038 [US2] Integrate QuickAdd and TaskList into dashboard page

**Checkpoint**: Full task CRUD working with API synchronization

---

## Phase 5: User Story 3 - Task Completion Toggle (Priority: P1)

**Goal**: Users can mark tasks complete/incomplete with visual feedback

**Independent Test**: Toggle task completion, verify visual change and progress update.

### Implementation for User Story 3

- [x] T039 [US3] Add completion checkbox to TaskCard component in frontend/src/components/tasks/TaskCard.tsx
- [x] T040 [US3] Implement completeTask and incompleteTask API calls in useTasks hook
- [x] T041 [US3] Add strikethrough and visual styling for completed tasks in TaskCard
- [x] T042 [US3] Handle recurring task completion (show next occurrence if returned) in TaskCard

**Checkpoint**: Task completion with visual feedback working

---

## Phase 6: User Story 4 - Calendar-Based Task View (Priority: P2)

**Goal**: Tasks displayed in monthly/weekly calendar grid with day indicators

**Independent Test**: Create tasks with due dates, view on calendar grid, click date to see tasks.

### Implementation for User Story 4

- [x] T043 [P] [US4] Create CalendarGrid component in frontend/src/components/calendar/CalendarGrid.tsx
- [x] T044 [P] [US4] Create CalendarDay component in frontend/src/components/calendar/CalendarDay.tsx
- [x] T045 [P] [US4] Create CalendarNav component (month/week toggle, Today button) in frontend/src/components/calendar/CalendarNav.tsx
- [x] T046 [US4] Create useCalendar hook for date navigation state in frontend/src/lib/hooks/useCalendar.ts
- [x] T047 [US4] Create calendar page in frontend/src/app/(dashboard)/calendar/page.tsx
- [x] T048 [US4] Implement monthly grid layout using CSS Grid in CalendarGrid
- [x] T049 [US4] Implement weekly view toggle in CalendarGrid
- [x] T050 [US4] Add task count indicators to CalendarDay component
- [x] T051 [US4] Implement date click to show task details for that day
- [x] T052 [US4] Add "Today" button navigation in CalendarNav

**Checkpoint**: Calendar view with task indicators working

---

## Phase 7: User Story 5 - Task Priority and Tags (Priority: P2)

**Goal**: Tasks have priority levels and tags with visual indicators

**Independent Test**: Create task with high priority and tags, verify color indicators and badges.

### Implementation for User Story 5

- [x] T053 [US5] Add priority selector to TaskForm component
- [x] T054 [US5] Add priority color indicator to TaskCard component (red/amber/green per priority)
- [x] T055 [US5] Add tag input field to TaskForm component with multi-select
- [x] T056 [US5] Display tags as Badge components on TaskCard
- [x] T057 [US5] Add tag click handler to trigger filter (integration with US7)

**Checkpoint**: Priority and tags with visual styling working

---

## Phase 8: User Story 6 - Due Dates and Times (Priority: P2)

**Goal**: Tasks can have due dates and times with deadline indicators

**Independent Test**: Create task with due date, see on calendar, verify "today" and "overdue" indicators.

### Implementation for User Story 6

- [x] T058 [US6] Add date picker to TaskForm component
- [x] T059 [US6] Add optional time picker to TaskForm component
- [x] T060 [US6] Display due date/time on TaskCard component
- [x] T061 [US6] Add "due today" visual indicator to TaskCard
- [x] T062 [US6] Add "overdue" warning indicator to TaskCard for past due dates
- [x] T063 [US6] Integrate due date tasks with CalendarDay display

**Checkpoint**: Due dates with visual indicators working

---

## Phase 9: User Story 7 - Search and Filter Tasks (Priority: P2)

**Goal**: Real-time search and filter by status, priority, tag

**Independent Test**: Create multiple tasks, search by keyword, filter by status/priority, clear filters.

### Implementation for User Story 7

- [x] T064 [P] [US7] Create TaskFilters component in frontend/src/components/tasks/TaskFilters.tsx
- [x] T065 [US7] Add search input with debounced onChange in TaskFilters
- [x] T066 [US7] Add status filter dropdown (all/complete/incomplete) in TaskFilters
- [x] T067 [US7] Add priority filter dropdown in TaskFilters
- [x] T068 [US7] Add tag filter dropdown in TaskFilters
- [x] T069 [US7] Implement filter state management in useTasks hook
- [x] T070 [US7] Add "Clear Filters" button to TaskFilters
- [x] T071 [US7] Integrate TaskFilters into dashboard page above TaskList

**Checkpoint**: Search and filter with real-time updates working

---

## Phase 10: User Story 8 - Sort Tasks (Priority: P3)

**Goal**: Sort tasks by due date, priority, or alphabetically

**Independent Test**: Create tasks with different dates/priorities, toggle sort options, verify order.

### Implementation for User Story 8

- [x] T072 [US8] Add sort dropdown to TaskFilters component
- [x] T073 [US8] Implement sortBy and sortOrder state in useTasks hook
- [x] T074 [US8] Apply sort to task list query parameters in API call

**Checkpoint**: Task sorting working

---

## Phase 11: User Story 9 - Progress Indicators (Priority: P3)

**Goal**: Visual progress bars showing completion percentage

**Independent Test**: Complete tasks and watch progress bar update in real-time.

### Implementation for User Story 9

- [x] T075 [P] [US9] Create ProgressBar component in frontend/src/components/dashboard/ProgressBar.tsx
- [x] T076 [US9] Calculate completion percentage from task list data
- [x] T077 [US9] Add ProgressBar to dashboard header showing overall progress
- [x] T078 [US9] Add mini progress indicator to CalendarDay component for daily progress

**Checkpoint**: Progress indicators updating in real-time

---

## Phase 12: User Story 10 - Recurring Tasks (Priority: P3)

**Goal**: Tasks can recur daily, weekly, or monthly

**Independent Test**: Create daily recurring task, mark complete, verify next occurrence created.

### Implementation for User Story 10

- [x] T079 [US10] Add recurrence selector to TaskForm component
- [x] T080 [US10] Display recurrence indicator on TaskCard
- [x] T081 [US10] Handle nextOccurrence response when completing recurring task in useTasks
- [x] T082 [US10] Add new occurrence to task list optimistically after completion

**Checkpoint**: Recurring tasks auto-creating next occurrences

---

## Phase 13: User Story 11 - Browser Notifications (Priority: P3)

**Goal**: Browser notifications for task reminders

**Independent Test**: Set reminder on task, receive browser notification at specified time.

### Implementation for User Story 11

- [x] T083 [P] [US11] Create useNotifications hook in frontend/src/lib/hooks/useNotifications.ts
- [x] T084 [US11] Implement notification permission request flow in useNotifications
- [x] T085 [US11] Add reminder time picker to TaskForm component
- [x] T086 [US11] Implement reminder scheduling with setTimeout in useNotifications
- [x] T087 [US11] Send browser notification using Notification API at reminder time
- [x] T088 [US11] Handle notification click to focus app and show task
- [x] T089 [US11] Gracefully handle notification permission denial with user message

**Checkpoint**: Browser notifications working for task reminders

---

## Phase 14: User Story 12 - Sidebar Navigation (Priority: P2)

**Goal**: Collapsible sidebar with shortcuts and navigation

**Independent Test**: View sidebar on desktop, click shortcuts, collapse on mobile.

### Implementation for User Story 12

- [x] T090 [P] [US12] Create Sidebar component in frontend/src/components/dashboard/Sidebar.tsx
- [x] T091 [US12] Add navigation links (Dashboard, Calendar) to Sidebar
- [x] T092 [US12] Add "Today's Tasks" shortcut that filters to today's due date
- [x] T093 [US12] Add Quick Add shortcut in Sidebar
- [x] T094 [US12] Implement sidebar collapse toggle for desktop
- [x] T095 [US12] Create SidebarState context for collapse state persistence

**Checkpoint**: Sidebar with navigation and shortcuts working

---

## Phase 15: User Story 13 - Responsive Design (Priority: P2)

**Goal**: App works on mobile, tablet, and desktop

**Independent Test**: View app at 320px, 768px, 1920px widths and verify layout adapts.

### Implementation for User Story 13

- [x] T096 [US13] Add responsive breakpoints to Tailwind config for mobile/tablet/desktop
- [x] T097 [US13] Implement mobile hamburger menu that shows/hides Sidebar
- [x] T098 [US13] Create Header component with mobile menu toggle in frontend/src/components/dashboard/Header.tsx
- [x] T099 [US13] Apply responsive grid layout to dashboard page (stacked on mobile)
- [x] T100 [US13] Apply responsive layout to calendar view (simplified on mobile)
- [x] T101 [US13] Ensure touch targets are minimum 44px on mobile
- [x] T102 [US13] Test and adjust TaskCard for mobile readability

**Checkpoint**: Responsive layout working across all breakpoints

---

## Phase 16: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, performance, and final improvements

- [x] T103 [P] Add loading states to all async operations (skeleton loaders)
- [x] T104 [P] Add error toasts for failed API operations using Toast component
- [x] T105 Implement retry option on API errors
- [x] T106 Add virtual scrolling for 100+ tasks (or pagination)
- [x] T107 [P] Add session expiry handling with re-auth prompt
- [x] T108 [P] Add form validation error display for all forms
- [x] T109 Run Lighthouse performance audit and address issues
- [x] T110 Final responsive testing across devices
- [x] T111 Run quickstart.md validation to ensure setup works

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-15)**: All depend on Foundational phase completion
  - P1 Stories (US1-US3): Should complete first as they are core functionality
  - P2 Stories (US4-US7, US12-US13): Can proceed after P1 or in parallel with capacity
  - P3 Stories (US8-US11): Lower priority, complete after P2
- **Polish (Phase 16)**: Depends on all desired user stories being complete

### User Story Dependencies

| Story | Depends On | Notes |
|-------|------------|-------|
| US1 (Auth) | Foundational | Gateway to all functionality |
| US2 (CRUD) | US1 | Requires authenticated user |
| US3 (Completion) | US2 | Requires task to exist |
| US4 (Calendar) | US2, US6 | Requires tasks with due dates |
| US5 (Priority/Tags) | US2 | Requires task to exist |
| US6 (Due Dates) | US2 | Requires task to exist |
| US7 (Search/Filter) | US2 | Requires tasks to filter |
| US8 (Sort) | US7 | Extends filter functionality |
| US9 (Progress) | US3 | Requires completion state |
| US10 (Recurring) | US3 | Requires completion flow |
| US11 (Notifications) | US6 | Requires reminder time |
| US12 (Sidebar) | US1 | Part of dashboard layout |
| US13 (Responsive) | US12 | Affects sidebar behavior |

### Parallel Opportunities

**Within Setup**: T003, T004, T005 can run in parallel
**Within Foundational**: T007, T008, T010, T011, T013-T016 can run in parallel
**Across Stories** (after foundation):
- US1 and US12 can start together (both foundational UI)
- US5, US6 can run in parallel (both task attributes)
- US9, US10, US11 can run in parallel (all P3, minimal overlap)

---

## Parallel Example: Foundational Phase

```bash
# Launch all parallelizable foundational tasks together:
Task: "Create TypeScript types for API in frontend/src/types/api.ts"
Task: "Create Zod validation schemas in frontend/src/lib/utils/validation.ts"
Task: "Configure Better Auth client in frontend/src/lib/auth.ts"
Task: "Create date utility functions in frontend/src/lib/utils/date.ts"
Task: "Create shared Button component in frontend/src/components/ui/Button.tsx"
Task: "Create shared Input component in frontend/src/components/ui/Input.tsx"
Task: "Create shared Badge component in frontend/src/components/ui/Badge.tsx"
Task: "Create shared Toast component in frontend/src/components/ui/Toast.tsx"
```

---

## Implementation Strategy

### MVP First (P1 Stories Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: US1 (Authentication)
4. Complete Phase 4: US2 (Task CRUD)
5. Complete Phase 5: US3 (Completion Toggle)
6. **STOP and VALIDATE**: Test P1 stories independently
7. Deploy/demo if ready - **This is MVP!**

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Auth) → Test → Users can sign in
3. Add US2 (CRUD) + US3 (Completion) → Test → Basic task management works
4. Add US4 (Calendar) + US6 (Due Dates) → Test → Calendar view works
5. Add US5 (Priority/Tags) + US7 (Search/Filter) → Test → Organization works
6. Add US12 (Sidebar) + US13 (Responsive) → Test → Full layout works
7. Add P3 stories as capacity allows

### Suggested Implementation Order

| Order | Phase | Story | Reason |
|-------|-------|-------|--------|
| 1 | 1-2 | Setup + Foundation | Required infrastructure |
| 2 | 3 | US1 Auth | Gateway to all features |
| 3 | 4-5 | US2-US3 CRUD + Completion | Core value proposition |
| 4 | 14 | US12 Sidebar | Layout structure |
| 5 | 6, 8 | US4 Calendar + US6 Due Dates | Key differentiator |
| 6 | 7, 9 | US5 Priority/Tags + US7 Filter | Task organization |
| 7 | 15 | US13 Responsive | Mobile support |
| 8 | 10-13 | US8-US11 (P3 stories) | Enhancement features |
| 9 | 16 | Polish | Final quality |

---

## Summary

| Metric | Count |
|--------|-------|
| Total Tasks | 111 |
| Setup Tasks | 5 |
| Foundational Tasks | 12 |
| US1 (Auth) Tasks | 11 |
| US2 (CRUD) Tasks | 10 |
| US3 (Completion) Tasks | 4 |
| US4 (Calendar) Tasks | 10 |
| US5 (Priority/Tags) Tasks | 5 |
| US6 (Due Dates) Tasks | 6 |
| US7 (Search/Filter) Tasks | 8 |
| US8 (Sort) Tasks | 3 |
| US9 (Progress) Tasks | 4 |
| US10 (Recurring) Tasks | 4 |
| US11 (Notifications) Tasks | 7 |
| US12 (Sidebar) Tasks | 6 |
| US13 (Responsive) Tasks | 7 |
| Polish Tasks | 9 |
| Parallelizable Tasks | 35 |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story designed to be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All paths relative to `frontend/` directory per plan.md structure
