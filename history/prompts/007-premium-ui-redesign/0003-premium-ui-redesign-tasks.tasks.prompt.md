---
id: "0003"
title: premium-ui-redesign-tasks
stage: tasks
date: 2026-02-22
surface: claude-code
model: claude-sonnet-4-6
feature: 007-premium-ui-redesign
branch: 007-premium-ui-redesign
user: galaxy
command: /sp.tasks
labels: [ui-redesign, shadcn-ui, framer-motion, next-themes, dark-mode, sidebar, tasks]
links:
  spec: specs/007-premium-ui-redesign/spec.md
  ticket: ""
  adr: ""
  pr: ""
files:
  - specs/007-premium-ui-redesign/tasks.md
tests:
  - "npm run build passes with zero TypeScript/ESLint errors (T028, T031)"
---

## Prompt

/sp.tasks

Generate an actionable, dependency-ordered tasks.md for feature 007-premium-ui-redesign based on plan.md (8 implementation phases A–H), spec.md (8 user stories P1–P3), data-model.md (client-side entities only), and contracts/ (no new endpoints).

## Response snapshot

Generated `specs/007-premium-ui-redesign/tasks.md` with 32 tasks across 11 phases:

- **Phase 1** (Setup, T001–T003): Install framer-motion, next-themes, lucide-react; shadcn init; add shadcn components
- **Phase 2** (Foundation, T004–T007): tailwind.config.js dark mode + sage tokens, globals.css CSS vars, layout.tsx ThemeProvider, ThemeToggle component
- **Phase 3** (US3 P1, T008–T010): Sidebar.tsx redesign, dashboard/layout.tsx Sheet mobile overlay, Header.tsx redesign
- **Phase 4** (US1 P1, T011): Landing page redesign with framer-motion scroll animations [parallel with Phase 3]
- **Phase 5** (US2 P1, T012–T013): Sign-in and sign-up polished card layouts [parallel with Phase 3]
- **Phase 6** (US4 P2, T014–T019): TaskCard animations + badges, TaskFilters tabs, dashboard header, progress bar, staggered list, empty state
- **Phase 7** (US5 P2, T020): TaskForm wrapped in shadcn Dialog with AnimatePresence
- **Phase 8** (US6 P2, T021–T022): AI chat bubbles + typing indicator
- **Phase 9** (US7 P3, T023–T028): Dark mode audit across all components + intermediate build check
- **Phase 10** (US8 P3, T029–T030): NotificationBell restyle + WS status dot in sidebar
- **Final** (T031–T032): Production build + manual smoke test

**Parallelism**: Phases 3+4+5 can all run in parallel after Foundation. Within Phase 6, T014/T015/T017/T018/T019 can run in parallel. Within Phase 9, T023–T027 all run in parallel.

**MVP scope**: Phases 1–5 (T001–T013) deliver all P1 acceptance scenarios.

## Outcome

- ✅ Impact: 32 executable tasks covering all 8 user stories, with concrete file paths and implementation details
- 🧪 Tests: T028 (intermediate build check) and T031 (final production build = SC-008)
- 📁 Files: specs/007-premium-ui-redesign/tasks.md
- 🔁 Next prompts: /sp.implement
- 🧠 Reflection: Frontend-only redesign allows many parallel tracks. Organizing US3 (sidebar) as a dependency for US4+ is correct since dashboard pages require the layout shell. US1 and US2 are fully independent and can be implemented simultaneously with US3.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): format validation — all 32 tasks have checkbox + ID + story label (where required) + file path
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): n/a
