/**
 * JWT Token Storage
 * Handles JWT token retrieval (stored in HttpOnly cookies)
 *
 * NOTE: JWT tokens are stored in HttpOnly cookies by the backend via Set-Cookie header.
 * This approach prevents XSS attacks as JavaScript cannot access HttpOnly cookies.
 * The browser automatically sends the cookie with credentials: 'include' in fetch requests.
 */

/**
 * Get JWT token from HttpOnly cookie
 *
 * NOTE: This function cannot directly read HttpOnly cookies due to browser security.
 * Instead, the token is automatically sent by the browser when:
 * - Making fetch requests with credentials: 'include'
 * - The backend sends Set-Cookie header with HttpOnly flag
 *
 * This function exists for reference and to show the pattern.
 * In practice, token management is handled by the browser and backend.
 */
export function getJWTToken(): string | null {
  // HttpOnly cookies cannot be read by JavaScript
  // The browser automatically includes them in fetch requests
  // with credentials: 'include'

  // For debugging or verification purposes only:
  // Check if we're in a browser environment
  if (typeof window === 'undefined') {
    return null
  }

  // Token is automatically sent by browser in fetch requests
  // No explicit retrieval needed
  return null
}

/**
 * Check if JWT token exists in cookie
 * Used to determine if user is authenticated
 */
export function hasJWTToken(): boolean {
  // Token existence check is implicit:
  // If the user is authenticated, their browser has the token cookie
  // Subsequent fetch requests will include it automatically

  if (typeof window === 'undefined') {
    return false
  }

  // A better approach: Check if API requests are successful
  // Or maintain auth state in React Context
  return false
}

/**
 * Clear JWT token (sign out)
 * The server will clear the HttpOnly cookie on sign-out request
 */
export function clearJWTToken(): void {
  // Token is cleared server-side via Set-Cookie with empty value
  // and Max-Age=0 or expires in past

  // No client-side action needed for HttpOnly cookies
  // Just ensure the logout endpoint is called
}

/**
 * Decode JWT token to extract claims
 * NOTE: This is for verification only - never use decoded token for authorization
 * Always validate tokens server-side
 */
export function decodeJWT(token: string): Record<string, unknown> | null {
  try {
    // JWT format: header.payload.signature
    const parts = token.split('.')
    if (parts.length !== 3) return null

    // Decode payload (second part)
    const payload = parts[1]
    const decoded = JSON.parse(atob(payload))
    return decoded
  } catch {
    return null
  }
}

/**
 * Extract user ID from JWT token
 * Used in API calls to identify the user
 */
export function extractUserIdFromToken(token: string): string | null {
  const decoded = decodeJWT(token)
  if (!decoded || !decoded.sub) return null
  return decoded.sub as string
}
