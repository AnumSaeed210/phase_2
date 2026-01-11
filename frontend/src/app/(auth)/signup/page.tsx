'use client'

/**
 * Sign Up Page
 * User registration page
 */

import { useState } from 'react'
import { SignUpForm } from '@/src/components/auth/SignUpForm'
import { useAuth } from '@/src/lib/auth/useAuth'
import { LoadingSpinner } from '@/src/components/common/LoadingSpinner'

export default function SignUpPage() {
  const { signUp, isLoading, error, clearError } = useAuth()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (
    email: string,
    password: string,
    name?: string
  ) => {
    setIsSubmitting(true)
    try {
      await signUp(email, password, name)
      // Redirect is handled by auth context
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return <LoadingSpinner message="Creating your account..." fullscreen />
  }

  return (
    <div>
      <SignUpForm
        onSubmit={handleSubmit}
        isLoading={isSubmitting}
        error={error?.message || null}
        onErrorDismiss={clearError}
      />
    </div>
  )
}
