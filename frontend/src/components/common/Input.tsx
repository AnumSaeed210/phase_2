/**
 * Input Component
 * Reusable form input with validation feedback
 */

import React, { InputHTMLAttributes } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helpText?: string
}

export function Input({
  label,
  error,
  helpText,
  id,
  className = '',
  ...props
}: InputProps) {
  const inputId = id || props.name || 'input'

  return (
    <div className="space-y-1">
      {label && (
        <label htmlFor={inputId} className="block text-sm font-medium text-gray-700">
          {label}
          {props.required && <span className="text-red-600"> *</span>}
        </label>
      )}

      <input
        id={inputId}
        className={`
          w-full px-4 py-2 border rounded-lg
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
          transition-colors
          ${error ? 'border-red-300 bg-red-50' : 'border-gray-300'}
          ${className}
        `}
        {...props}
      />

      {error && <p className="text-sm text-red-600">{error}</p>}
      {helpText && !error && <p className="text-sm text-gray-500">{helpText}</p>}
    </div>
  )
}
