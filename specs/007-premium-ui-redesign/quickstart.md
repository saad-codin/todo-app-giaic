# Quickstart: Premium UI/UX Redesign

**Feature**: 007-premium-ui-redesign
**Branch**: `007-premium-ui-redesign`

---

## Prerequisites

- Node.js 18+
- Running backend at `http://localhost:8000` (or port-forwarded Kubernetes service)
- Git on branch `007-premium-ui-redesign`

---

## Step 1 — Install New Dependencies

```bash
cd frontend

# Install framer-motion, next-themes, lucide-react
npm install framer-motion next-themes lucide-react

# Initialize shadcn/ui (interactive prompts — choose defaults)
npx shadcn@latest init
# Select: Style = Default, Base color = Neutral, CSS variables = Yes

# Add shadcn/ui components used in the redesign
npx shadcn@latest add button card badge input dialog dropdown-menu sheet
npx shadcn@latest add separator scroll-area tooltip popover label textarea
```

---

## Step 2 — Verify Tailwind Dark Mode Config

After `shadcn init`, confirm `tailwind.config.js` has:
```js
darkMode: ["class"],
```
This is required for `next-themes` class-based dark mode to work.

---

## Step 3 — Run Development Server

```bash
cd frontend
npm run dev
```

App available at `http://localhost:3000`.

---

## Step 4 — Test Key Scenarios

### Landing Page
1. Open `http://localhost:3000` in incognito (unauthenticated)
2. Verify: hero section, feature highlights, CTA buttons visible
3. Verify: smooth scroll animations, fully responsive on mobile

### Authentication
1. Navigate to `http://localhost:3000/signin`
2. Verify: polished layout with branding, inline validation, smooth transition to dashboard

### Dashboard Sidebar
1. Sign in and open dashboard
2. Verify: left sidebar with Dashboard, AI Assistant, Calendar navigation
3. Resize to mobile (< 768px): sidebar hidden, hamburger visible → click opens overlay

### Dark Mode
1. Click theme toggle in sidebar footer
2. Verify: entire interface transitions smoothly to dark theme
3. Refresh page: dark mode is still active (persisted in localStorage)

### Task Animations
1. Create a task
2. Check the checkbox: completion animation plays
3. Hover over task card: subtle lift animation

### Notification Bell
1. Bell icon visible in header/sidebar
2. When a WebSocket reminder fires: badge increments, item appears in history
3. Click "Mark all read": badge clears

---

## Step 5 — Production Build Check

```bash
cd frontend
npm run build
```

**Expected**: zero TypeScript errors, zero ESLint errors. This satisfies SC-008.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `framer-motion` hydration error | Wrap animated components in `'use client'` and use `initial={false}` on `AnimatePresence` |
| Dark mode flash on load | Ensure `<html>` has `suppressHydrationWarning` (next-themes requires this) |
| shadcn components missing styles | Run `npx shadcn@latest add [component]` — components must be added individually |
| CSS variable conflicts | Check `globals.css` — shadcn init appends variables; ensure no duplicates with existing styles |
| `lucide-react` not found | Run `npm install lucide-react` in `frontend/` directory |
