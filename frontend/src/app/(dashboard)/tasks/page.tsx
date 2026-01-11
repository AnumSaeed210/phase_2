'use client'

/**
 * Task List Page
 * Main dashboard showing user's tasks
 */

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/src/lib/auth/useAuth'
import { useTasks } from '@/src/lib/hooks/useTasks'
import { Button } from '@/src/components/common/Button'
import { TaskList } from '@/src/components/tasks/TaskList'
import { EmptyState } from '@/src/components/tasks/EmptyState'
import { ErrorAlert } from '@/src/components/common/ErrorAlert'
import { LoadingSpinner } from '@/src/components/common/LoadingSpinner'

export default function TasksPage() {
  const router = useRouter()
  const { user, isAuthenticated } = useAuth()
  const { tasks, isLoading, error, fetchTasks, deleteTask, completeTask, clearError } =
    useTasks()
  const [isInitialized, setIsInitialized] = useState(false)

  // Fetch tasks on component mount
  useEffect(() => {
    if (!isAuthenticated || !user?.id) {
      return
    }

    const loadTasks = async () => {
      try {
        await fetchTasks(user.id)
      } catch {
        // Error is handled by the hook
      } finally {
        setIsInitialized(true)
      }
    }

    loadTasks()
  }, [isAuthenticated, user?.id, fetchTasks])

  // Show loading state while initializing
  if (!isInitialized && isLoading) {
    return <LoadingSpinner message="Loading your tasks..." />
  }

  // Handle unauthenticated access
  if (!isAuthenticated || !user?.id) {
    return null // Middleware should redirect to signin
  }

  const handleEdit = (taskId: string) => {
    router.push(`/tasks/${taskId}`)
  }

  const handleDelete = async (taskId: string) => {
    try {
      await deleteTask(user.id, taskId)
    } catch {
      // Error is handled by the hook
    }
  }

  const handleComplete = async (taskId: string) => {
    try {
      await completeTask(user.id, taskId)
    } catch {
      // Error is handled by the hook
    }
  }

  const handleCreateClick = () => {
    router.push('/tasks/new')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
          <p className="mt-2 text-gray-600">
            {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'}
          </p>
        </div>
        <Button onClick={handleCreateClick} disabled={isLoading}>
          + Create Task
        </Button>
      </div>

      {/* Error Alert */}
      {error && (
        <ErrorAlert
          message={error}
          title="Failed to load tasks"
          onDismiss={clearError}
        />
      )}

      {/* Task List */}
      {tasks.length > 0 ? (
        <TaskList
          tasks={tasks}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onComplete={handleComplete}
          isLoading={isLoading}
        />
      ) : (
        <EmptyState onCreateClick={handleCreateClick} />
      )}
    </div>
  )
}
