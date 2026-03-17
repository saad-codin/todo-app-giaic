# Tasks: Premium UI/UX Redesign

**Input**: Design documents from `/specs/007-premium-ui-redesign/`
**Branch**: `007-premium-ui-redesign`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Total tasks**: 32
**Tests**: Build verification via `npm run build` (SC-008) — no additional test files needed for a visual redesign

**Organization**: Grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with siblings (different files, no intra-phase dependency)
- **[Story]**: Which user story this task serves (US1–US8)
- All paths are relative to repository root

---

## Phase 1: Setup (Dependencies Installation)

**Purpose**: Install all new libraries and generate shadcn/ui component source files.

**⚠️ NOTE**: shadcn init is interactive. Run the commands exactly as shown. All subsequent phases depend on this phase completing.

- [ ] T001 Install framer-motion, next-themes, lucide-react in `frontend/` — run `npm install framer-motion next-themes lucide-react` from `frontend/`
- [ ] T002 Initialize shadcn/ui in `frontend/` — run `npx shadcn@latest init` and select: Style=Default, Base color=Neutral, CSS variables=Yes; this updates `frontend/tailwind.config.js` and `frontend/src/app/globals.css`
- [ ] T003 Add shadcn/ui component source files to `frontend/src/components/ui/` — run `npx shadcn@latest add button card badge input dialog dropdown-menu sheet separator scroll-area tooltip label textarea`

---

## Phase 2: Foundation (Blocking Prerequisites)

**Purpose**: Configure the design system, dark mode infrastructure, and root layout provider. All user story phases depend on this.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T004 [P] Customize `frontend/tailwind.config.js` — ensure `darkMode: ["class"]`, add sage green color tokens under `theme.extend.colors.sage` with shades 50–900 (#f2f7f4 through #142e24), verify shadcn `content` paths are present
- [ ] T005 [P] Update `frontend/src/app/globals.css` — customize the `--primary` CSS variable in the `:root` block to sage green `152 40% 40%` and in `.dark` block to `152 40% 55%`; keep all other shadcn-generated variables intact
- [ ] T006 [P] Update `frontend/src/app/layout.tsx` — import `ThemeProvider` from `next-themes`, add `suppressHydrationWarning` to `<html>`, wrap `<Providers>` with `<ThemeProvider attribute="class" defaultTheme="system" enableSystem>`
- [ ] T007 [P] Create `frontend/src/components/ui/ThemeToggle.tsx` — client component using `useTheme()` from next-themes; renders Sun icon (light mode) / Moon icon (dark mode) from lucide-react; framer-motion `AnimatePresence` for smooth icon swap; button with `rounded-full p-2 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors`

**Checkpoint**: Design system configured — user story work can now begin

---

## Phase 3: User Story 3 — Premium Dashboard with Sidebar Navigation (Priority: P1)

**Goal**: Replace the plain sidebar with a premium navigation shell that defines the entire app's layout paradigm.

**Independent Test**: Log in → sidebar visible with Dashboard/AI Assistant/Calendar/Sticky Wall nav items → active route highlighted → resize to < 768px → sidebar hidden, hamburger visible → click hamburger → sidebar slides in as overlay

- [ ] T008 [US3] Redesign `frontend/src/components/dashboard/Sidebar.tsx` — replace existing implementation with: (1) top logo section with app name, (2) Navigation section with LayoutDashboard/Bot/Calendar/StickyNote lucide icons for Dashboard/AI Assistant/Calendar/Sticky Wall routes, (3) My Lists section with Personal and Work items, (4) Tags section showing user tag pills (map from useTasks data passed as prop or use `usePathname`), (5) footer with ThemeToggle + connection dot + user avatar + sign-out; active item: `bg-sage-100 text-sage-700 border-l-2 border-sage-500`; hover: `hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors duration-150`; framer-motion `whileHover={{ x: 2 }}` on nav links; full dark: variants
- [ ] T009 [US3] Update `frontend/src/app/dashboard/layout.tsx` — keep auth guard (`useAuthContext` + redirect to `/signin`) and loading spinner; replace static sidebar render with new `<Sidebar />` component; add `useState` for `mobileOpen`; render `<Sheet>` from shadcn wrapping `<Sidebar />` for mobile overlay (trigger: `onOpenChange={setMobileOpen}`); pass `mobileOpen` and `setMobileOpen` as props to `<Header />`; desktop: `<aside className="hidden lg:flex ..."><Sidebar /></aside>`
- [ ] T010 [US3] Redesign `frontend/src/components/dashboard/Header.tsx` — mobile-only (`lg:hidden`); Menu icon from lucide-react for hamburger; app title centered; matches design tokens `bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800`; accepts `onMenuClick: () => void` prop; height `h-16`

---

## Phase 4: User Story 1 — First Impression on Landing Page (Priority: P1)

**Goal**: Marketing-grade public homepage that converts visitors to sign-ups.

**Independent Test**: Open `http://localhost:3000` while logged out → hero section with headline and CTAs → scroll → feature cards animate in → CTA banner → footer → fully responsive at 320px

- [ ] T011 [P] [US1] Redesign `frontend/src/app/page.tsx` — replace existing implementation with four sections: (1) **Hero**: `min-h-screen` gradient `from-sage-50 to-white dark:from-gray-900 dark:to-gray-800`, headline "Organize your work, amplify your focus", subheadline, two shadcn Buttons (Get Started → /signup, Sign In → /signin), framer-motion `initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}`; (2) **Features Grid**: 6 cards (Task Management, AI Assistant, Calendar View, Dark Mode, Real-time Sync, Recurring Tasks) with lucide icons, `whileInView={{ opacity: 1, y: 0 }} initial={{ opacity: 0, y: 20 }} viewport={{ once: true }}` with staggered delay; (3) **CTA Banner**: sage-500 background, "Start for free today" text, Button `whileHover={{ scale: 1.03 }}`; (4) **Footer**: brand name, copyright; preserve existing redirect logic for authenticated users

---

## Phase 5: User Story 2 — Beautiful Authentication Experience (Priority: P1)

**Goal**: Premium sign-in and sign-up screens with polished card layout and smooth animations.

**Independent Test**: Navigate to `/signin` → polished card on gradient background → submit invalid credentials → inline error appears with animation → navigate to `/signup` → same premium look → complete sign-up → redirect to dashboard

- [ ] T012 [P] [US2] Redesign sign-in page — update `frontend/src/app/(auth)/signin/page.tsx` and its `SignInForm` component (located at `frontend/src/components/auth/SignInForm.tsx` or inline): gradient background `bg-gradient-to-br from-sage-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 min-h-screen flex items-center justify-center`; centered card `bg-white dark:bg-gray-900 shadow-xl rounded-2xl p-8 w-full max-w-md`; app logo/name above form; shadcn `Input`, `Label`, `Button` for form fields; inline error messages with `text-red-500 text-sm` and `motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}`; card entrance `initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}`; "Don't have an account? Sign up" link; preserve all existing form logic (`react-hook-form`, `zod`, existing auth calls)
- [ ] T013 [P] [US2] Redesign sign-up page — update `frontend/src/app/(auth)/signup/page.tsx` and its `SignUpForm` component: same card/gradient layout as T012; same shadcn form components; same entrance animation; "Already have an account? Sign in" link; preserve all existing form fields and validation logic

---

## Phase 6: User Story 4 — Polished Task List and Task Cards (Priority: P2)

**Goal**: The most-used surface redesigned with elegant cards, animations, and a polished filter bar.

**Independent Test**: Create tasks with all 4 priority levels → cards show correct color badges → mark a task complete → completion animation plays → filter by priority → smooth transition → overdue task shows red date → recurring task shows recurrence icon

- [ ] T014 [US4] Redesign `frontend/src/components/tasks/TaskCard.tsx` — wrap root in `motion.div whileHover={{ y: -1, boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }} transition={{ duration: 0.15 }}`; card base: `bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm p-4 group`; checkbox: animate between Circle and CheckCircle2 lucide icons using `motion.div animate={{ scale: completed ? [1, 1.2, 1] : 1 }}`; description: `line-through text-gray-400` when complete, `motion.div animate={{ opacity: completed ? 0.5 : 1 }}`; priority badge: shadcn `Badge` with variant classes `urgent=bg-purple-100 text-purple-700`, `high=bg-red-100 text-red-700`, `medium=bg-amber-100 text-amber-700`, `low=bg-green-100 text-green-700`; due date: red text when overdue (`text-red-500`), blue when today (`text-blue-500`); recurrence: `RepeatIcon` from lucide-react; tags: clickable badges; edit/delete buttons: `opacity-0 group-hover:opacity-100 transition-opacity duration-150`; preserve all existing props and callback logic
- [ ] T015 [P] [US4] Redesign `frontend/src/components/tasks/TaskFilters.tsx` — replace existing implementation with horizontal tab row: All / Urgent / High / Medium / Low / Overdue; active tab: `bg-sage-100 text-sage-700 rounded-full px-3 py-1`; framer-motion `layoutId="activeTab"` pill for smooth indicator slide; search input on the right with Search lucide icon; dark: variants `dark:text-gray-300 dark:hover:bg-gray-800`; preserve all existing filter state props and callbacks
- [ ] T016 [US4] Update dashboard page header in `frontend/src/app/dashboard/page.tsx` — replace existing header section with: greeting `"Good morning, {user.name}"` (or "Good evening" based on hour), current date in human-readable format, shadcn search `Input` with Search icon, shadcn `Button` "+ New Task" that opens TaskForm; preserve all existing `useTasks`, `useWebSocket`, `useState` wiring
- [ ] T017 [P] [US4] Add today's progress bar to `frontend/src/app/dashboard/page.tsx` — compute `todayCompleted` and `todayTotal` from task list (filter tasks with `due_date === today`); render `div` with `bg-sage-500 h-2 rounded-full` animated width via `motion.div animate={{ width: '${pct}%' }} transition={{ duration: 0.5, ease: 'easeOut' }}`; show "X of Y tasks completed today" label; dark: variants
- [ ] T018 [P] [US4] Add staggered list animation to task list in `frontend/src/app/dashboard/page.tsx` — wrap task list in `motion.ul` with `variants={{ show: { transition: { staggerChildren: 0.05 } } }}`; wrap each `TaskCard` in `motion.li` with `variants={{ hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0 } }}`; use `AnimatePresence` for add/remove transitions
- [ ] T019 [P] [US4] Add empty state to `frontend/src/app/dashboard/page.tsx` — shown when `filteredTasks.length === 0`; centered layout with SVG checkmark/clipboard illustration (inline SVG ~60px), heading "No tasks yet", subtext "Create your first task to get started", shadcn `Button` that triggers new task modal; motion.div entrance animation; dark: variants

---

## Phase 7: User Story 5 — Task Creation and Editing Modal (Priority: P2)

**Goal**: Premium modal with smooth animations, keyboard accessibility, and all existing fields.

**Independent Test**: Click "+ New Task" → Dialog animates open → focus lands on description field → fill all fields → save → task appears in list → edit existing task → all fields pre-populated → Escape closes dialog with exit animation

- [ ] T020 [US5] Update `frontend/src/components/tasks/TaskForm.tsx` — replace any custom modal wrapper with shadcn `Dialog` / `DialogContent` / `DialogHeader` / `DialogTitle` / `DialogFooter`; add framer-motion to `DialogContent` via `asChild` + `motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }} transition={{ duration: 0.2 }}`; replace any plain `<input>` with shadcn `Input`; replace `<textarea>` with shadcn `Textarea`; replace `<select>` with shadcn `DropdownMenu` or native `<select>` styled; replace `<label>` with shadcn `Label`; replace submit button with shadcn `Button`; wrap in `AnimatePresence` in parent; preserve 100% of existing form state, validation (react-hook-form + zod), and submission logic; `autoFocus` on description field; dark: variants on all form elements

---

## Phase 8: User Story 6 — AI Assistant Chat Interface (Priority: P2)

**Goal**: Premium chat UI with message bubbles, typing indicator, and auto-scroll.

**Independent Test**: Navigate to `/chat` via sidebar → clean chat interface visible → send message → typing indicator appears → AI response renders with animation → view auto-scrolls → long AI responses scroll correctly

- [ ] T021 [US6] Redesign `frontend/src/app/chat/page.tsx` — full-height flex column layout `flex flex-col h-full`; scrollable message history `flex-1 overflow-y-auto px-4 py-6 space-y-4`; message bubbles: user messages `ml-auto bg-sage-500 text-white rounded-2xl rounded-tr-sm max-w-[75%] px-4 py-2`, AI messages `mr-auto bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-2xl rounded-tl-sm max-w-[75%] px-4 py-2`; each message wrapped in `motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }}`; input area fixed at bottom `border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-4 py-3 flex gap-2`; shadcn `Input` + `Button` (send); preserve all existing chat API calls and message state; `useEffect` to `scrollIntoView({ behavior: 'smooth' })` on new message using a `bottomRef`
- [ ] T022 [P] [US6] Add typing indicator to `frontend/src/app/chat/page.tsx` — shown when `isLoading` is true; three dot component: `div` with three `motion.div` children each with `animate={{ y: [0, -4, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0 | 0.1 | 0.2 }}`; styled same as AI message bubble `bg-gray-100 dark:bg-gray-800 rounded-2xl rounded-tl-sm px-4 py-3 w-16`; wrapped in `AnimatePresence` for smooth appear/disappear

---

## Phase 9: User Story 7 — Dark Mode Polish (Priority: P3)

**Goal**: Audit every component for complete dark: variant coverage and WCAG AA contrast.

**Independent Test**: Toggle dark mode via ThemeToggle → entire interface switches instantly → refresh page → dark mode persists → check each page (landing, sign-in, sign-up, dashboard, chat) → no broken elements, no illegible text

- [ ] T023 [US7] Verify dark: variants completeness in `frontend/src/components/dashboard/Sidebar.tsx` — ensure all background, border, text, and hover states have corresponding `dark:` classes; sidebar bg: `dark:bg-gray-900`; borders: `dark:border-gray-800`; nav text: `dark:text-gray-300`; user section: `dark:bg-gray-900`; active item: `dark:bg-sage-900/30 dark:text-sage-400`
- [ ] T024 [P] [US7] Verify dark: variants completeness in `frontend/src/app/page.tsx` — hero gradient: `dark:from-gray-900 dark:to-gray-800`; feature cards: `dark:bg-gray-800 dark:border-gray-700`; all headings: `dark:text-white`; body text: `dark:text-gray-300`; CTA banner: `dark:bg-sage-700`; footer: `dark:bg-gray-900 dark:text-gray-400`
- [ ] T025 [P] [US7] Verify dark: variants completeness in auth pages `frontend/src/app/(auth)/signin/page.tsx` and `frontend/src/app/(auth)/signup/page.tsx` — background gradient: `dark:from-gray-900 dark:to-gray-800`; card: `dark:bg-gray-900`; inputs: `dark:bg-gray-800 dark:border-gray-700 dark:text-white dark:placeholder-gray-500`; labels: `dark:text-gray-300`; link text: `dark:text-sage-400`
- [ ] T026 [P] [US7] Verify dark: variants completeness in `frontend/src/components/tasks/TaskCard.tsx` — card: `dark:bg-gray-800 dark:border-gray-700`; description: `dark:text-gray-100`; secondary text: `dark:text-gray-400`; all priority badge dark variants — `dark:bg-purple-900/30 dark:text-purple-400`, `dark:bg-red-900/30 dark:text-red-400`, `dark:bg-amber-900/30 dark:text-amber-400`, `dark:bg-green-900/30 dark:text-green-400`
- [ ] T027 [P] [US7] Verify dark: variants completeness in `frontend/src/components/tasks/TaskForm.tsx` (Dialog modal) — DialogContent: `dark:bg-gray-900`; form inputs: `dark:bg-gray-800 dark:border-gray-700 dark:text-white`; labels: `dark:text-gray-300`; dialog overlay: `dark:bg-black/70`
- [ ] T028 Run `npm run build` from `frontend/` — fix all TypeScript type errors and ESLint warnings reported; build must exit with code 0

---

## Phase 10: User Story 8 — Real-Time Sync Indicator and Notification Bell (Priority: P3)

**Goal**: Notification bell and WebSocket status integrated into new layout with design system tokens.

**Independent Test**: On dashboard → notification bell icon visible in sidebar → WebSocket status dot visible → trigger a reminder (or simulate via console) → bell badge increments → dropdown shows notification history → click "Mark all read" → badge clears

- [ ] T029 [US8] Restyle `frontend/src/components/ui/NotificationBell.tsx` with new design tokens — update panel: `bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl shadow-xl`; unread badge: `bg-sage-500` (replace red if desired, or keep red for urgency); unread row: `bg-sage-50 dark:bg-sage-900/20`; read row: `bg-white dark:bg-gray-900`; ensure z-50 works within the new sidebar layout (may need `z-[100]`); verify dropdown positioning is correct when mounted inside sidebar footer
- [ ] T030 [US8] Add WebSocket connection status dot to `frontend/src/components/dashboard/Sidebar.tsx` sidebar footer — import `isConnected` state from parent (or via prop from dashboard layout); green dot `bg-green-400 w-2 h-2 rounded-full` when connected; gray dot `bg-gray-400 w-2 h-2 rounded-full` when disconnected; framer-motion `animate={{ scale: [1, 1.3, 1] }} transition={{ repeat: Infinity, duration: 2 }}` on green dot only; label "Live" / "Offline" in `text-xs text-gray-500`

---

## Final Phase: Production Verification

**Purpose**: Final build check and smoke test to confirm SC-001 (zero regressions) and SC-008 (zero build errors).

- [ ] T031 Run `npm run build` from `frontend/` for final production build verification — must exit with code 0, zero TypeScript errors, zero ESLint errors (satisfies SC-008)
- [ ] T032 Manual smoke test against all 8 acceptance scenarios — verify: (1) landing page hero + scroll animations, (2) sign-in/sign-up polished layout + error animation, (3) sidebar nav + mobile overlay, (4) task cards with priority badges + completion animation, (5) task creation modal animations, (6) AI chat bubbles + typing indicator, (7) dark mode toggle + persistence, (8) notification bell + WS status dot

---

## Dependency Graph

```
Phase 1 (T001→T003)
    ↓
Phase 2 (T004→T007) — Foundation [can all run in parallel]
    ↓
Phase 3 (T008→T010) — US3 [must complete before US4, US5, US8 since they depend on dashboard layout]
    ↓ (in parallel)
Phase 4 (T011)   — US1 [independent; only needs Foundation]
Phase 5 (T012-T013) — US2 [independent; only needs Foundation]
Phase 6 (T014→T019) — US4 [needs US3 for dashboard shell]
    ↓
Phase 7 (T020)   — US5 [needs US4 dashboard page with task list wired]
Phase 8 (T021-T022) — US6 [needs US3 for sidebar nav link to /chat]
    ↓ (after all components built)
Phase 9 (T023→T028) — US7 [dark mode audit; all components must exist first]
Phase 10 (T029-T030) — US8 [notification bell; dashboard layout from US3 required]
    ↓
Final (T031-T032) — Verification
```

---

## Parallel Execution Opportunities

### After Phase 2 completes, these can run in parallel:
- US3 (T008-T010): Sidebar + Layout → most time-intensive, start first
- US1 (T011): Landing page → fully independent, different files
- US2 (T012-T013): Auth pages → fully independent, different files

### Within Phase 6 (US4), these can run in parallel:
- T014: TaskCard.tsx redesign
- T015: TaskFilters.tsx redesign
- T017: Progress bar (dashboard/page.tsx section)
- T018: Staggered animation (dashboard/page.tsx section)
- T019: Empty state (dashboard/page.tsx section)
> Note: T016 must be done before T017/T018/T019 since all modify dashboard/page.tsx — coordinate carefully or treat T016 as the base edit and T017-T019 as additive patches

### Within Phase 9 (US7 audit), all parallel:
- T023: Sidebar dark mode
- T024: Landing page dark mode
- T025: Auth pages dark mode
- T026: TaskCard dark mode
- T027: Modal dark mode

---

## Implementation Strategy

### MVP (P1 stories — shippable first increment):
Complete Phases 1–5 in order:
1. Phase 1 + 2: Foundation (T001–T007)
2. Phase 3: US3 Sidebar (T008–T010)
3. Phases 4+5 in parallel: US1 Landing (T011) + US2 Auth (T012–T013)

After MVP: App has premium landing page, polished auth, and new sidebar navigation. All P1 acceptance scenarios pass.

### Increment 2 (P2 stories):
4. Phase 6: US4 Task Cards (T014–T019)
5. Phase 7: US5 Task Modal (T020)
6. Phase 8: US6 AI Chat (T021–T022)

### Increment 3 (P3 stories + polish):
7. Phase 9: US7 Dark Mode Audit (T023–T028)
8. Phase 10: US8 Notifications (T029–T030)
9. Final: Verification (T031–T032)

---

## Success Criteria Coverage

| SC | Tasks That Satisfy It |
|----|----------------------|
| SC-001: Zero regressions | T009 (preserve auth guard), T014 (preserve TaskCard callbacks), T020 (preserve TaskForm logic), T031 (build check) |
| SC-002: TTI < 3s | T004 (Tailwind purge), T001–T003 (framer-motion lazy) |
| SC-003: 320px mobile | T009 (Sheet overlay), T014 (card truncation), T011 (responsive hero) |
| SC-004: Sidebar animation < 300ms | T009 (Sheet default 250ms) |
| SC-005: All animations < 300ms | T014, T020, T021, T022 (all transitions capped at 0.2–0.3s) |
| SC-006: Dark mode < 100ms | T006 (CSS class swap via ThemeProvider) |
| SC-007: WCAG AA contrast | T023–T027 (dark mode audit per component) |
| SC-008: Zero build errors | T028 (intermediate), T031 (final) |
