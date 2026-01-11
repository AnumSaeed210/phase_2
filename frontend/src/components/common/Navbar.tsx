'use client'

/**
 * Navbar Component
 * Navigation bar with user info and sign-out button
 */

import { useState } from 'react'
import Link from 'next/link'
import { useAuth } from '@/src/lib/auth/useAuth'
import { Button } from './Button'

export function Navbar() {
  const { user, signOut, isLoading } = useAuth()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const handleSignOut = async () => {
    try {
      await signOut()
    } catch {
      // Error is handled by auth context
    }
  }

  return (
    <nav className="border-b border-gray-200 bg-white shadow-sm">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 justify-between items-center">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Link href="/tasks" className="text-2xl font-bold text-blue-600">
              Taskie
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex md:items-center md:gap-6">
            {user && (
              <>
                <div className="flex flex-col gap-0.5">
                  <p className="text-sm font-medium text-gray-900">{user.name || user.email}</p>
                  <p className="text-xs text-gray-500">{user.email}</p>
                </div>

                <div className="h-8 w-px bg-gray-200"></div>

                <Link href="/profile" className="text-sm text-gray-600 hover:text-gray-900">
                  Profile
                </Link>

                <Button
                  variant="secondary"
                  size="sm"
                  onClick={handleSignOut}
                  disabled={isLoading}
                  isLoading={isLoading}
                >
                  Sign Out
                </Button>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="inline-flex items-center justify-center rounded-md p-2 text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              aria-expanded="false"
            >
              <span className="sr-only">Open main menu</span>
              <svg
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth="1.5"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200 py-4 space-y-3">
            {user && (
              <>
                <div className="px-2">
                  <p className="text-sm font-medium text-gray-900">{user.name || user.email}</p>
                  <p className="text-xs text-gray-500">{user.email}</p>
                </div>

                <Link
                  href="/profile"
                  className="block px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 rounded-md"
                >
                  Profile
                </Link>

                <Button
                  variant="danger"
                  size="sm"
                  fullWidth
                  onClick={handleSignOut}
                  disabled={isLoading}
                  isLoading={isLoading}
                >
                  Sign Out
                </Button>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  )
}
