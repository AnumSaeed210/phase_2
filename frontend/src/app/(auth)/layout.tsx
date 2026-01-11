/**
 * Auth Layout
 * Layout for authentication pages (signup, signin)
 * No navbar - centered form layout
 */

import { ReactNode } from 'react'

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12">
      <div className="w-full max-w-md space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">Taskie</h1>
          <p className="mt-2 text-gray-600">Manage your tasks with ease</p>
        </div>

        {/* Form Container */}
        <div className="rounded-lg bg-white p-8 shadow-md">{children}</div>
      </div>
    </div>
  )
}
