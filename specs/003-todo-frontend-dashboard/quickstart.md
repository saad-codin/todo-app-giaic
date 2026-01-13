# Quickstart Guide: Todo App Frontend Dashboard

**Feature**: 003-todo-frontend-dashboard
**Date**: 2026-01-10
**Purpose**: Get the frontend development environment running quickly

## Prerequisites

- Node.js 18+ (LTS recommended)
- npm 9+ or pnpm 8+
- Backend API running on `http://localhost:8000` (see backend feature)
- Git

## Quick Setup

### 1. Create Next.js Project

```bash
# From repository root
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
cd frontend
```

### 2. Install Dependencies

```bash
npm install @tanstack/react-query better-auth date-fns react-hook-form zod @hookform/resolvers
npm install -D @types/node @testing-library/react @testing-library/jest-dom playwright
```

### 3. Environment Setup

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
BETTER_AUTH_URL=http://localhost:3000
```

### 4. Start Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## Project Structure Quick Reference

```text
frontend/src/
├── app/                    # Pages (App Router)
│   ├── (auth)/             # Auth routes (public)
│   │   ├── signin/page.tsx
│   │   └── signup/page.tsx
│   ├── (dashboard)/        # Dashboard (protected)
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── calendar/page.tsx
│   └── layout.tsx          # Root layout
├── components/             # React components
│   ├── auth/
│   ├── dashboard/
│   ├── tasks/
│   ├── calendar/
│   └── ui/
├── lib/                    # Utilities
│   ├── api.ts              # API client
│   ├── auth.ts             # Better Auth config
│   └── hooks/              # Custom hooks
└── types/                  # TypeScript types
```

---

## Key Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server (port 3000) |
| `npm run build` | Production build |
| `npm run lint` | Run ESLint |
| `npm run test` | Run component tests |
| `npx playwright test` | Run E2E tests |

---

## Backend API Requirement

This frontend requires the FastAPI backend running. Ensure:

1. Backend is running on `http://localhost:8000`
2. CORS is configured to allow `http://localhost:3000`
3. Auth endpoints are available at `/api/auth/*`
4. Task endpoints are available at `/api/tasks/*`

See `specs/003-todo-frontend-dashboard/contracts/api-client.md` for full API contract.

---

## Development Workflow

1. **Start backend** (in separate terminal):
   ```bash
   cd backend && uvicorn main:app --reload
   ```

2. **Start frontend**:
   ```bash
   cd frontend && npm run dev
   ```

3. **Open browser**: http://localhost:3000

4. **Hot reload**: Changes auto-refresh in browser

---

## Tailwind Configuration

The project uses custom colors for priority indicators. Add to `tailwind.config.js`:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        priority: {
          high: '#ef4444',    // red-500
          medium: '#f59e0b',  // amber-500
          low: '#22c55e',     // green-500
        }
      }
    }
  }
}
```

---

## Testing Setup

### Component Tests (Jest + RTL)

```bash
npm run test
```

### E2E Tests (Playwright)

```bash
# Install browsers first
npx playwright install

# Run tests
npx playwright test

# Run with UI
npx playwright test --ui
```

---

## Troubleshooting

### CORS Errors
- Ensure backend has CORS middleware allowing `http://localhost:3000`
- Check `credentials: 'include'` in fetch calls

### Auth Not Working
- Verify `BETTER_AUTH_SECRET` is set and matches backend
- Check cookies are being set (DevTools > Application > Cookies)

### API Connection Failed
- Confirm backend is running on correct port
- Check `NEXT_PUBLIC_API_URL` in `.env.local`

---

## Next Steps

After setup, implement features in this order:

1. Auth components (SignIn, SignUp forms)
2. Dashboard layout with Sidebar
3. Task CRUD components
4. Calendar grid view
5. Filtering and search
6. Notifications

See `specs/003-todo-frontend-dashboard/tasks.md` for detailed implementation tasks.
