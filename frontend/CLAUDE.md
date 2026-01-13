# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS

## Commands

```bash
# Development server
npm run dev

# Production build
npm run build

# Lint code
npm run lint
```

## Patterns

- Use server components by default
- Client components only when needed (interactivity)
- API calls go through `/lib/api.ts`

## Component Structure

- `/components` - Reusable UI components
- `/app` - Pages and layouts

## API Client

All backend calls should use the api client:

```typescript
import { api } from '@/lib/api'
const tasks = await api.getTasks()
```

## Styling

- Use Tailwind CSS classes
- No inline styles
- Follow existing component patterns
