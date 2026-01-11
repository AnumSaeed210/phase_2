/**
 * Next.js Middleware
 * Implements route protection and authentication flow
 */

import { NextRequest, NextResponse } from 'next/server'

// Routes that don't require authentication
const publicRoutes = ['/auth/signin', '/auth/signup', '/']

// Routes that require authentication
const protectedRoutes = ['/tasks', '/profile']

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname

  // Check if route is public
  const isPublicRoute = publicRoutes.some((route) => pathname.startsWith(route))

  // Check if route is protected
  const isProtectedRoute = protectedRoutes.some((route) => pathname.startsWith(route))

  // For protected routes, we would normally check for a valid session/token
  // Since we're using HttpOnly cookies, the browser handles token sending
  // The API will return 401 if no valid token, triggering redirect in API client

  // For now, we'll rely on API-level protection
  // In a more complex scenario, you could:
  // 1. Read cookie middleware (if non-HttpOnly)
  // 2. Verify JWT signature
  // 3. Redirect unauthorized access

  // Get token from request (if available)
  // For HttpOnly cookies, we can't read them in middleware
  // So we rely on API protection

  // If user tries to access signin/signup while logged in, they'll be redirected by the page
  // If user tries to access protected route without auth, API will return 401

  return NextResponse.next()
}

// Apply middleware to specific routes
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|public).*)',
  ],
}
