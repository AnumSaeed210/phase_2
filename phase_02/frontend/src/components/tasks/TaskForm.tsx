'use client'

/**
 * TaskForm Component
 * Form for creating and editing tasks
 */

import React, { useState, useEffect } from 'react'
import { Task, CreateTaskRequest } from '@/lib/api/types'
import { Input } from '@/components/common/Input'
import { Button } from '@/components/common/Button'
import { ErrorAlert } from '@/components/common/ErrorAlert'
import { PrioritySelector } from '@/components/common/PrioritySelector'
import { validateTaskForm } from '@/lib/validation/tasks'

interface TaskFormProps {
  initialTask?: Task
  onSubmit: (data: CreateTaskRequest) => Promise<void>
  onCancel?: () => void
  isLoading?: boolean
  error?: string | null
  onErrorDismiss?: () => void
}

export function TaskForm({
  initialTask,
  onSubmit,
  onCancel,
  isLoading = false,
  error,
  onErrorDismiss,
}: TaskFormProps) {
  const [formData, setFormData] = useState({
    title: initialTask?.title || '',
    description: initialTask?.description || '',
    priority: initialTask?.priority || 'medium',
  })

  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})

  const isEditing = !!initialTask

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    // Clear field error when user starts typing
    if (fieldErrors[name]) {
      setFieldErrors((prev) => ({ ...prev, [name]: '' }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validate form
    const validationError = validateTaskForm(formData.title, formData.description)

    if (validationError) {
      setFieldErrors({ [validationError.field]: validationError.message })
      return
    }

    try {
      await onSubmit({
        title: formData.title,
        description: formData.description || undefined,
        priority: formData.priority || 'medium',
      })
    } catch {
      // Error is handled by parent
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <ErrorAlert
          message={error}
          title={isEditing ? 'Update Failed' : 'Creation Failed'}
          onDismiss={onErrorDismiss}
        />
      )}

      <Input
        label="Task Title"
        type="text"
        name="title"
        id="title"
        required
        value={formData.title}
        onChange={handleChange}
        placeholder="Enter task title"
        error={fieldErrors.title}
        disabled={isLoading}
        helpText="3-200 characters"
      />

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
          Description (Optional)
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Enter task description"
          disabled={isLoading}
          rows={4}
          className={`
            mt-1 w-full px-4 py-2 border rounded-lg
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
            transition-colors
            ${fieldErrors.description ? 'border-red-300 bg-red-50' : 'border-gray-300'}
          `}
        />
        {fieldErrors.description && (
          <p className="text-sm text-red-600 mt-1">{fieldErrors.description}</p>
        )}
        <p className="text-xs text-gray-500 mt-1">Maximum 1000 characters</p>
      </div>

      <PrioritySelector
        value={formData.priority}
        onChange={(value) => setFormData((prev) => ({ ...prev, priority: value }))}
        label="Priority"
      />

      <div className="flex gap-3">
        <Button
          type="submit"
          isLoading={isLoading}
          disabled={isLoading}
          className="flex-1"
        >
          {isEditing ? 'Update Task' : 'Create Task'}
        </Button>

        {onCancel && (
          <Button
            type="button"
            variant="secondary"
            onClick={onCancel}
            disabled={isLoading}
            className="flex-1"
          >
            Cancel
          </Button>
        )}
      </div>
    </form>
  )
}
