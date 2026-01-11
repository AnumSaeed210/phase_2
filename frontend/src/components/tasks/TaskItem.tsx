'use client'

/**
 * TaskItem Component
 * Single task display with actions
 */

import React, { useState } from 'react'
import { Task } from '@/src/lib/api/types'
import { formatRelativeTime } from '@/src/utils/formatting'
import { Button } from '@/src/components/common/Button'

interface TaskItemProps {
  task: Task
  onEdit?: (taskId: string) => void
  onDelete?: (taskId: string) => Promise<void>
  onComplete?: (taskId: string) => Promise<void>
  isLoading?: boolean
}

export function TaskItem({
  task,
  onEdit,
  onDelete,
  onComplete,
  isLoading = false,
}: TaskItemProps) {
  const [isDeleting, setIsDeleting] = useState(false)
  const [isCompleting, setIsCompleting] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  const handleDelete = async () => {
    if (!onDelete) return

    setIsDeleting(true)
    try {
      await onDelete(task.id)
      setShowDeleteConfirm(false)
    } catch {
      // Error is handled by parent
    } finally {
      setIsDeleting(false)
    }
  }

  const handleComplete = async () => {
    if (!onComplete) return

    setIsCompleting(true)
    try {
      await onComplete(task.id)
    } catch {
      // Error is handled by parent
    } finally {
      setIsCompleting(false)
    }
  }

  return (
    <div className="flex items-start gap-3 rounded-lg border border-gray-200 bg-white p-4 hover:shadow-sm transition-shadow">
      {/* Completion Checkbox */}
      <div className="flex-shrink-0 pt-1">
        <input
          type="checkbox"
          checked={task.completed}
          onChange={handleComplete}
          disabled={isCompleting || isLoading}
          className="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer disabled:opacity-50"
          aria-label="Mark task complete"
        />
      </div>

      {/* Task Content */}
      <div className="flex-1 min-w-0">
        <h3
          className={`text-base font-medium ${
            task.completed
              ? 'text-gray-400 line-through'
              : 'text-gray-900'
          }`}
        >
          {task.title}
        </h3>
        {task.description && (
          <p
            className={`mt-1 text-sm ${
              task.completed ? 'text-gray-400' : 'text-gray-600'
            }`}
          >
            {task.description}
          </p>
        )}
        <p className="mt-2 text-xs text-gray-500">
          Created {formatRelativeTime(task.createdAt)}
        </p>
      </div>

      {/* Actions */}
      <div className="flex-shrink-0 flex gap-2">
        {onEdit && (
          <Button
            variant="secondary"
            size="sm"
            onClick={() => onEdit(task.id)}
            disabled={isLoading || isDeleting}
          >
            Edit
          </Button>
        )}

        {onDelete && (
          <>
            {showDeleteConfirm ? (
              <Button
                variant="danger"
                size="sm"
                onClick={handleDelete}
                isLoading={isDeleting}
                disabled={isDeleting}
              >
                Confirm
              </Button>
            ) : (
              <Button
                variant="danger"
                size="sm"
                onClick={() => setShowDeleteConfirm(true)}
                disabled={isLoading || isDeleting}
              >
                Delete
              </Button>
            )}
          </>
        )}
      </div>

      {/* Delete Confirmation */}
      {showDeleteConfirm && !isDeleting && (
        <div className="absolute right-0 top-12 z-10 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          <p>Are you sure?</p>
          <div className="mt-2 flex gap-2">
            <button
              onClick={handleDelete}
              className="text-red-600 hover:text-red-700 font-medium"
              disabled={isDeleting}
            >
              Delete
            </button>
            <button
              onClick={() => setShowDeleteConfirm(false)}
              className="text-gray-600 hover:text-gray-700"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
