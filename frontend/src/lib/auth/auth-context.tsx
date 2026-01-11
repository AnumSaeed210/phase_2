'use client'

/**
 * Auth Context and Provider
 * Manages global authentication state
 * Provides sign-up, sign-in, sign-out functions
 */

import React, { createContext, useState, useCallback, ReactNode } from 'react'
import { User, AuthError } from '@/src/lib/api/types'

export interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: AuthError | null
  signUp: (email: string, password: string, name?: string) => Promise<void>
  signIn: (email: string, password: string) => Promise<void>
  signOut: () => Promise<void>
  clearError: () => void
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

export interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<AuthError | null>(null)

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const signUp = useCallback(
    async (email: string, password: string, name?: string) => {
      setIsLoading(true)
      setError(null)

      try {
        // Call Better Auth sign-up endpoint
        const response = await fetch('/api/auth/signup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ email, password, name }),
        })

        if (!response.ok) {
          const error = await response.json()
          throw error.error || { code: 'SIGNUP_FAILED', message: 'Sign-up failed' }
        }

        const data = await response.json()
        setUser(data.user)

        // Redirect to tasks page on successful signup
        if (typeof window !== 'undefined') {
          window.location.href = '/tasks'
        }
      } catch (err) {
        const authError = err as AuthError
        setError(authError)
        throw authError
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  const signIn = useCallback(
    async (email: string, password: string) => {
      setIsLoading(true)
      setError(null)

      try {
        // Call Better Auth sign-in endpoint
        const response = await fetch('/api/auth/signin', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ email, password }),
        })

        if (!response.ok) {
          const error = await response.json()
          throw error.error || { code: 'SIGNIN_FAILED', message: 'Sign-in failed' }
        }

        const data = await response.json()
        setUser(data.user)

        // Redirect to tasks page on successful signin
        if (typeof window !== 'undefined') {
          window.location.href = '/tasks'
        }
      } catch (err) {
        const authError = err as AuthError
        setError(authError)
        throw authError
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  const signOut = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      // Call Better Auth sign-out endpoint
      const response = await fetch('/api/auth/signout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      })

      if (!response.ok) {
        const error = await response.json()
        throw error.error || { code: 'SIGNOUT_FAILED', message: 'Sign-out failed' }
      }

      setUser(null)

      // Redirect to signin page on successful signout
      if (typeof window !== 'undefined') {
        window.location.href = '/auth/signin'
      }
    } catch (err) {
      const authError = err as AuthError
      setError(authError)
      throw authError
    } finally {
      setIsLoading(false)
    }
  }, [])

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
    signUp,
    signIn,
    signOut,
    clearError,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
