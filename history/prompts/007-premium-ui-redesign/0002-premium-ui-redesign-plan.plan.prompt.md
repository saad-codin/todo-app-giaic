---
id: "0002"
title: premium-ui-redesign-plan
stage: plan
date: 2026-02-22
surface: claude-code
model: claude-sonnet-4-6
feature: 007-premium-ui-redesign
branch: 007-premium-ui-redesign
user: galaxy
command: /sp.plan
labels: [ui-redesign, shadcn-ui, framer-motion, next-themes, dark-mode, sidebar, animations]
links:
  spec: specs/007-premium-ui-redesign/spec.md
  ticket: ""
  adr: ""
  pr: ""
files:
  - specs/007-premium-ui-redesign/plan.md
  - specs/007-premium-ui-redesign/research.md
  - specs/007-premium-ui-redesign/data-model.md
  - specs/007-premium-ui-redesign/quickstart.md
  - specs/007-premium-ui-redesign/contracts/api-contracts.md
tests:
  - "npm run build passes with zero TypeScript/ESLint errors"
---

## Prompt

/sp.plan

Execute the implementation planning workflow for feature 007-premium-ui-redesign. Read the spec at specs/007-premium-ui-redesign/spec.md, research required technologies (shadcn/ui, framer-motion, next-themes, lucide-react), explore the existing frontend codebase, and produce: research.md, data-model.md, contracts/, quickstart.md, and a complete plan.md with 8 implementation phases.

## Response snapshot

Completed the full sp.plan workflow:

1. **Research**: Documented shadcn/ui CLI setup, framer-motion v11 patterns for Next.js 14 App Router, next-themes dark mode configuration, lucide-react icon migration, and sage green color palette decisions.

2. **Data model**: Identified that this is a frontend-only redesign — zero backend schema changes. Documented client-side entities: Theme (next-themes localStorage), AppNotification (existing from 006), SidebarState (local React state).

3. **Contracts**: Confirmed no new API endpoints. Documented all 11 consumed existing endpoints for reference.

4. **Quickstart**: Step-by-step installation guide (npm install, shadcn init, shadcn add components, dev server, key test scenarios, build check).

5. **Plan**: 8 implementation phases:
   - Phase A: Foundation (deps, Tailwind dark mode, shadcn CSS vars, ThemeProvider)
   - Phase B: Sidebar & Layout Shell (new nav structure, Sheet mobile overlay)
   - Phase C: Landing Page (hero, features grid, scroll animations)
   - Phase D: Auth Pages (polished card layout)
   - Phase E: Dashboard + Task Components (TaskCard animations, Dialog modal, staggered list)
   - Phase F: AI Assistant Chat (bubble UI, typing indicator, auto-scroll)
   - Phase G: Dark Mode Polish (all dark: variants, WCAG AA check)
   - Phase H: Real-Time & Notification Integration (bell styling, WS status dot)

All 7 constitution gates pass. SC-001 through SC-008 mapped to concrete implementation steps.

## Outcome

- ✅ Impact: Complete implementation plan for full premium frontend redesign — 8 phases, zero backend changes, zero regressions
- 🧪 Tests: SC-008 — `npm run build` must pass with zero errors after each phase
- 📁 Files: specs/007-premium-ui-redesign/plan.md, research.md, data-model.md, quickstart.md, contracts/api-contracts.md
- 🔁 Next prompts: /sp.tasks, /sp.implement
- 🧠 Reflection: Frontend-only redesign makes constitution gates straightforward — preserving all hook/API logic means correctness is guaranteed structurally. Key insight: shadcn/ui components are source-owned (not node_modules), so they can be customized freely without version conflicts.

## Evaluation notes (flywheel)

- Failure modes observed: Background research agent was blocked (WebSearch/WebFetch/mcp__context7 denied) — fell back to built-in knowledge for library documentation, which was sufficient for well-established libraries like shadcn/ui and framer-motion
- Graders run and results (PASS/FAIL): Constitution check PASS (all 7 gates)
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): n/a
