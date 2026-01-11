/**
 * Better Auth Configuration
 * Initialize Better Auth with JWT configuration
 */

// This file will be used to configure Better Auth
// For now, we'll export a placeholder for the client configuration

export const betterAuthConfig = {
  apiUrl: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:3000',
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  // JWT configuration will be handled by Better Auth server
  // Client signs in via /api/auth/signin -> Better Auth issues JWT -> stored in HttpOnly cookie
}

/**
 * Better Auth client initialization
 * This would typically call better-auth's client setup
 * For now, we reference it for API calls
 */
export function initBetterAuth() {
  // Initialize Better Auth client
  // The actual implementation depends on better-auth version
  // Typically: createBetterAuthClient({ baseURL: betterAuthConfig.baseURL })
}
