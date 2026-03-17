# Research: Premium UI/UX Redesign

**Feature**: 007-premium-ui-redesign
**Date**: 2026-02-22
**Phase**: 0 — Research & Technology Decisions

---

## 1. shadcn/ui — Installation & Configuration

**Decision**: Use `shadcn@latest` CLI to initialize and selectively add components.

**Installation steps**:
```bash
cd frontend
npx shadcn@latest init
```
This CLI prompts for:
- Style: Default (uses CSS variables, not Tailwind HSL classes directly)
- Base color: Neutral (closest to sage green direction)
- CSS variables: Yes

Generates `components/ui/` with copied component source files (not node_modules — source owned by consumer), updates `tailwind.config.js` to add `content` paths and CSS variable color tokens, and writes `globals.css` CSS variables for both light and dark themes.

**Adding components individually**:
```bash
npx shadcn@latest add button card badge input dialog dropdown-menu sheet
npx shadcn@latest add separator scroll-area tooltip popover
```

**Key pattern**: shadcn/ui components are fully styled with Tailwind and CSS variable design tokens. They support dark mode natively via `dark:` variants when `darkMode: "class"` is set in Tailwind config.

**Conflict with existing**: Current `globals.css` uses minimal Tailwind directives. shadcn init merges CSS variable blocks — review and merge manually if needed.

**Rationale**: shadcn/ui gives polished, accessible components without a large bundle (tree-shaking works because components are source files). Directly spec-required.

---

## 2. framer-motion — Animation Library

**Decision**: Use `framer-motion` v11.x for all animations.

**Installation**:
```bash
npm install framer-motion
```

**Key patterns for Next.js 14 App Router**:
- All `motion.*` components must be in `'use client'` files — they use browser APIs
- `AnimatePresence` wraps conditional renders to enable exit animations
- `LayoutGroup` for shared layout transitions (e.g., active sidebar item pill)

**Core APIs used in this redesign**:
```typescript
import { motion, AnimatePresence } from 'framer-motion';

// Sidebar collapse
<motion.aside animate={{ width: isOpen ? 264 : 80 }} transition={{ duration: 0.25, ease: 'easeInOut' }} />

// Modal entrance
<motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} transition={{ duration: 0.2 }} />

// Task card hover
<motion.div whileHover={{ y: -2 }} transition={{ duration: 0.15 }} />

// Task completion
<motion.div animate={{ opacity: isCompleted ? 0.6 : 1 }} transition={{ duration: 0.3 }} />

// Staggered list
const container = { hidden: {}, show: { transition: { staggerChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0 } };
```

**SSR consideration**: framer-motion v11 supports SSR. Use `initial={false}` on `AnimatePresence` to suppress mount animations on server-rendered content.

**Reduced-motion**: Honor `prefers-reduced-motion` via `useReducedMotion()` hook — set `transition={{ duration: 0 }}` when true.

**Rationale**: spec-required. Framer-motion is the industry standard for React animations, with the best DX and performance.

---

## 3. next-themes — Dark Mode

**Decision**: Use `next-themes` with `class` strategy (Tailwind compatible).

**Installation**:
```bash
npm install next-themes
```

**Setup**:
1. Wrap app in `ThemeProvider` in `app/layout.tsx`:
```tsx
import { ThemeProvider } from 'next-themes';
<ThemeProvider attribute="class" defaultTheme="system" enableSystem>
  {children}
</ThemeProvider>
```

2. Tailwind config must have `darkMode: 'class'` (shadcn init sets this automatically).

3. Toggle button in sidebar/header:
```tsx
import { useTheme } from 'next-themes';
const { theme, setTheme } = useTheme();
<button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>Toggle</button>
```

**Persistence**: next-themes automatically persists preference to `localStorage` and applies it on page load with zero flash (uses `suppressHydrationWarning` on `<html>`).

**Default theme**: `defaultTheme="system"` → respects OS preference on first visit, as per spec assumption.

**Rationale**: next-themes is the standard solution for Next.js dark mode. Zero-flash, SSR-safe, and integrates perfectly with Tailwind's `darkMode: 'class'`.

---

## 4. lucide-react — Icons

**Decision**: Replace all inline SVG icons with `lucide-react` named components.

**Installation**: Already available as part of shadcn/ui ecosystem; install separately:
```bash
npm install lucide-react
```

**Usage pattern**:
```tsx
import { LayoutDashboard, Bot, Calendar, Bell, Sun, Moon, Plus, Search, CheckCircle2, Circle, Tag, RepeatIcon, Clock } from 'lucide-react';
<LayoutDashboard className="w-5 h-5" />
```

**Rationale**: spec-required. lucide-react provides consistent, well-maintained icons with proper tree-shaking.

---

## 5. Color Palette Decision

**Decision**: Sage green accent palette with clean neutrals.

**Light theme tokens** (CSS variables set in globals.css via shadcn init):
```css
--background: 0 0% 100%;        /* white */
--foreground: 240 10% 3.9%;     /* near-black */
--primary: 152 40% 45%;         /* sage green */
--primary-foreground: 0 0% 100%;
--secondary: 152 20% 95%;       /* light sage tint */
--muted: 240 4.8% 95.9%;
--accent: 152 20% 92%;
--border: 240 5.9% 90%;
--sidebar-bg: 0 0% 99%;         /* near-white */
```

**Dark theme tokens**:
```css
--background: 240 10% 7%;       /* very dark */
--foreground: 0 0% 95%;
--primary: 152 40% 55%;         /* slightly lighter sage */
--secondary: 152 15% 15%;
--muted: 240 3.7% 15.9%;
--accent: 152 15% 18%;
--border: 240 3.7% 20%;
--sidebar-bg: 240 10% 9%;
```

**Priority badge colors** (FR-005 spec):
- Urgent: purple (`bg-purple-100 text-purple-700`)
- High: red (`bg-red-100 text-red-700`)
- Medium: amber (`bg-amber-100 text-amber-700`)
- Low: green (`bg-green-100 text-green-700`)

---

## 6. Existing Code Inventory (from exploration)

**What exists and is KEPT**:
- `app/layout.tsx` — root layout with `<Providers>` wrapper
- `app/providers.tsx` — QueryClient, ToastProvider, AuthProvider
- `lib/hooks/useTasks.ts` — full task CRUD with React Query
- `lib/hooks/useWebSocket.ts` — WebSocket real-time sync
- `lib/hooks/useAuth.ts` — authentication context
- `lib/api.ts` — all API calls
- `types/task.ts` — Task TypeScript types
- `components/tasks/TaskFilters.tsx` — filter state logic
- `components/tasks/TaskForm.tsx` — form logic
- `app/dashboard/page.tsx` — main dashboard with all wiring

**What is REDESIGNED** (visual layer only, logic preserved):
- `components/dashboard/Sidebar.tsx` — new design, same routes
- `components/dashboard/Header.tsx` — new design, same purpose
- `app/dashboard/layout.tsx` — add ThemeProvider, keep auth guard
- `app/page.tsx` — marketing landing page redesign
- `app/(auth)/signin/page.tsx` + components
- `app/(auth)/signup/page.tsx` + components
- `components/tasks/TaskCard.tsx` — add animations, same data
- `components/ui/NotificationBell.tsx` — already added, may restyle

**New files needed**:
- `components/ui/ThemeToggle.tsx` — dark/light mode button
- Possible: `components/landing/` — hero, features, footer sections

---

## 7. Dependency Conflict Check

Current `package.json` analysis:
- Next.js 14.2.35 + React 18.3.1 ✅ (fully compatible with framer-motion v11, next-themes, shadcn)
- Tailwind CSS ^3.4.17 ✅ (shadcn/ui requires Tailwind 3.x)
- No conflicting animation libraries
- No existing icon library (all SVGs inline → migrating to lucide-react)

**No breaking changes anticipated** to existing runtime behavior.

---

## Decisions Summary

| Topic | Decision | Rationale |
|-------|----------|-----------|
| UI Components | shadcn/ui (CLI init) | Spec-required; polished, accessible, source-owned |
| Animations | framer-motion v11 | Spec-required; industry standard |
| Dark mode | next-themes + Tailwind class | Spec-required; zero-flash, localStorage persistent |
| Icons | lucide-react | Spec-required; replaces inline SVGs |
| Color palette | Sage green (#3d8b6e area) + neutrals | Spec assumption from inspiration image |
| Component strategy | Redesign visual layer, preserve all logic hooks | SC-001: zero regressions |
| SSR | framer-motion with `initial={false}` on AnimatePresence | Suppress mount animations server-side |
