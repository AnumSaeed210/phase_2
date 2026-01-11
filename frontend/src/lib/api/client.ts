/**
 * Centralized API Client
 * Handles all HTTP requests with automatic JWT injection
 * Implements 401 error handling and consistent error serialization
 */

import { AuthError, ApiResponse } from './types'

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

interface FetchOptions extends RequestInit {
  skipAuth?: boolean
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = BASE_URL) {
    this.baseUrl = baseUrl
  }

  /**
   * Get JWT token from storage
   * Token is stored in HttpOnly cookie (set by backend via Set-Cookie)
   * For XHR requests, credentials: 'include' sends the cookie automatically
   */
  private async getAuthHeader(): Promise<string | null> {
    try {
      // Token is in HttpOnly cookie, no need to read it directly
      // The browser will send it automatically with credentials: 'include'
      return null
    } catch {
      return null
    }
  }

  /**
   * Handle API response
   * Parses JSON and handles error cases
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('content-type')
    let data: unknown

    if (contentType?.includes('application/json')) {
      data = await response.json()
    } else {
      data = await response.text()
    }

    // Handle 401 - Redirect to signin
    if (response.status === 401) {
      if (typeof window !== 'undefined') {
        window.location.href = '/auth/signin'
      }
      const error: AuthError = {
        code: 'UNAUTHORIZED',
        message: 'Session expired. Please sign in again.',
      }
      throw error
    }

    // Handle other error status codes
    if (!response.ok) {
      let error: AuthError
      if (typeof data === 'object' && data !== null && 'error' in data) {
        error = data.error as AuthError
      } else {
        error = {
          code: `HTTP_${response.status}`,
          message: typeof data === 'string' ? data : 'An error occurred',
        }
      }
      throw error
    }

    return data as T
  }

  /**
   * Make GET request
   */
  async get<T = unknown>(path: string, options?: FetchOptions): Promise<T> {
    const url = `${this.baseUrl}${path}`
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options?.headers,
    }

    const response = await fetch(url, {
      ...options,
      method: 'GET',
      headers,
      credentials: 'include', // Send HttpOnly cookies
    })

    return this.handleResponse<T>(response)
  }

  /**
   * Make POST request
   */
  async post<T = unknown>(
    path: string,
    body?: unknown,
    options?: FetchOptions
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options?.headers,
    }

    const response = await fetch(url, {
      ...options,
      method: 'POST',
      headers,
      body: body ? JSON.stringify(body) : undefined,
      credentials: 'include', // Send HttpOnly cookies
    })

    return this.handleResponse<T>(response)
  }

  /**
   * Make PUT request
   */
  async put<T = unknown>(
    path: string,
    body?: unknown,
    options?: FetchOptions
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options?.headers,
    }

    const response = await fetch(url, {
      ...options,
      method: 'PUT',
      headers,
      body: body ? JSON.stringify(body) : undefined,
      credentials: 'include', // Send HttpOnly cookies
    })

    return this.handleResponse<T>(response)
  }

  /**
   * Make PATCH request
   */
  async patch<T = unknown>(
    path: string,
    body?: unknown,
    options?: FetchOptions
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options?.headers,
    }

    const response = await fetch(url, {
      ...options,
      method: 'PATCH',
      headers,
      body: body ? JSON.stringify(body) : undefined,
      credentials: 'include', // Send HttpOnly cookies
    })

    return this.handleResponse<T>(response)
  }

  /**
   * Make DELETE request
   */
  async delete<T = unknown>(path: string, options?: FetchOptions): Promise<T> {
    const url = `${this.baseUrl}${path}`
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options?.headers,
    }

    const response = await fetch(url, {
      ...options,
      method: 'DELETE',
      headers,
      credentials: 'include', // Send HttpOnly cookies
    })

    return this.handleResponse<T>(response)
  }
}

// Export singleton instance
export const apiClient = new ApiClient()
