import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Middleware is disabled for now - auth is handled client-side
// The backend sets httpOnly cookies on a different port (8000)
// which can't be read by Next.js middleware on port 3000
export function middleware(request: NextRequest) {
  return NextResponse.next();
}

export const config = {
  matcher: [],
};
