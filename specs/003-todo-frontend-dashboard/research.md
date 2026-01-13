# Phase 0 Research: Todo App Frontend Dashboard

**Feature**: 003-todo-frontend-dashboard
**Date**: 2026-01-10
**Purpose**: Resolve technical decisions before implementation

## Research Topics

### 1. Authentication Strategy (Better Auth)

**Decision**: Use Better Auth with JWT tokens stored in httpOnly cookies

**Rationale**:
- Better Auth provides built-in Next.js integration with App Router support
- JWT in httpOnly cookies prevents XSS attacks (tokens not accessible via JavaScript)
- Automatic token refresh handling
- Built-in session management

**Alternatives Considered**:
- NextAuth.js: More mature but heavier, Better Auth is simpler for this use case
- Custom JWT implementation: More work, less secure without expertise
- Session-based auth: Requires server-side state, not ideal for stateless API

**Implementation Notes**:
- Configure Better Auth client in `/lib/auth.ts`
- Use middleware for route protection
- Store user context in React Context or Zustand

---

### 2. State Management Approach

**Decision**: React Query (TanStack Query) for server state, React Context for UI state

**Rationale**:
- React Query handles caching, refetching, and optimistic updates automatically
- Reduces boilerplate compared to Redux
- Built-in loading/error states
- Perfect for "backend as source of truth" pattern

**Alternatives Considered**:
- Redux Toolkit + RTK Query: More powerful but overkill for this scope
- Zustand: Good for client state but doesn't handle server state as well
- SWR: Similar to React Query but fewer features for mutations

**Implementation Notes**:
- QueryClient provider at app root
- Custom hooks (`useTasks`, `useAuth`) wrap React Query
- Optimistic updates for better UX on task operations

---

### 3. Calendar Component Strategy

**Decision**: Build custom calendar grid with Tailwind CSS

**Rationale**:
- Reference UI (Notion-style) requires specific layout not easily achieved with libraries
- Custom implementation gives full control over styling and behavior
- date-fns for date calculations (tree-shakeable, lightweight)

**Alternatives Considered**:
- react-big-calendar: Feature-rich but hard to customize to match reference
- FullCalendar: Heavy, overkill for simple grid display
- @fullcalendar/react: Good but brings significant bundle size

**Implementation Notes**:
- Use CSS Grid for calendar layout
- date-fns for date arithmetic (`startOfMonth`, `endOfMonth`, `eachDayOfInterval`)
- Virtualization not needed for month view (max 42 cells)

---

### 4. Notification Implementation

**Decision**: Browser Notification API with permission request flow

**Rationale**:
- Native browser support, no external dependencies
- Works across all target browsers
- Simple API for basic notifications

**Alternatives Considered**:
- Push notifications via service worker: More complex, requires backend push service
- Third-party services (OneSignal, Pusher): Overkill for browser-only notifications
- In-app notifications only: User requested browser notifications specifically

**Implementation Notes**:
- Request permission on first reminder setup
- Store permission status in localStorage
- Fallback gracefully if denied
- Use `useNotifications` hook for abstraction

---

### 5. Form Handling and Validation

**Decision**: React Hook Form with Zod schemas

**Rationale**:
- React Hook Form is performant (minimal re-renders)
- Zod provides TypeScript-first validation
- Schema can be shared with API types
- Excellent error handling UX

**Alternatives Considered**:
- Formik: More verbose, more re-renders
- Native form handling: Too much boilerplate
- Yup: Less TypeScript-friendly than Zod

**Implementation Notes**:
- Define Zod schemas in `/types/`
- Use `zodResolver` with React Hook Form
- Display validation errors inline

---

### 6. Styling Approach

**Decision**: Tailwind CSS with custom design tokens

**Rationale**:
- Fast development with utility classes
- Easy to match reference UI design
- Built-in responsive utilities
- Small production bundle (purges unused classes)

**Alternatives Considered**:
- CSS Modules: More boilerplate, slower development
- Styled Components: Runtime overhead, bundle size
- Chakra UI: Good but enforces its design system

**Implementation Notes**:
- Extend Tailwind config with custom colors for priority indicators
- Use Tailwind's `@apply` sparingly in globals.css
- Mobile-first responsive design

---

### 7. API Client Pattern

**Decision**: Centralized fetch wrapper with automatic JWT injection

**Rationale**:
- Single point for auth header injection
- Consistent error handling
- Easy to mock for testing
- TypeScript generics for type safety

**Alternatives Considered**:
- Axios: Larger bundle, fetch is sufficient
- Generated client from OpenAPI: Good but adds build step complexity
- Direct fetch calls: Duplicated logic across components

**Implementation Notes**:
```typescript
// lib/api.ts pattern
const api = {
  get: <T>(url: string) => fetchWithAuth<T>(url, { method: 'GET' }),
  post: <T>(url: string, data: unknown) => fetchWithAuth<T>(url, { method: 'POST', body: JSON.stringify(data) }),
  // ...
}
```

---

### 8. Testing Strategy

**Decision**: Component tests with React Testing Library, E2E with Playwright

**Rationale**:
- RTL encourages testing behavior, not implementation
- Playwright for cross-browser E2E testing
- Matches Phase II testing standards

**Alternatives Considered**:
- Cypress: Good but slower, single browser focus
- Vitest: Fast but less ecosystem support
- Jest alone: Missing E2E coverage

**Implementation Notes**:
- Unit test utility functions
- Component tests for interactive components
- E2E tests for critical user flows (auth, task CRUD)
- Mock API responses in component tests

---

## Dependency Summary

| Package | Version | Purpose |
|---------|---------|---------|
| next | 14.x | Framework |
| better-auth | latest | Authentication |
| @tanstack/react-query | 5.x | Server state management |
| react-hook-form | 7.x | Form handling |
| zod | 3.x | Validation |
| date-fns | 3.x | Date utilities |
| tailwindcss | 3.x | Styling |
| @testing-library/react | 14.x | Component testing |
| playwright | 1.x | E2E testing |

## Resolved Clarifications

All technical decisions resolved. No NEEDS CLARIFICATION markers remain.
