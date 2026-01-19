'use client'

/**
 * useTasks Hook
 * Custom hook for managing task operations
 */

import { useState, useCallback } from 'react'
import { Task, CreateTaskRequest, UpdateTaskRequest } from '@/lib/api/types'
import { apiClient } from '@/lib/api/client'


/**
 * Transform task from API (snake_case) to frontend (camelCase)
 * Ensures timestamps are properly parsed as UTC
 */
function transformTask(task: any): Task {
  // Ensure timestamps are in UTC by appending Z if missing
  const normalizeTimestamp = (timestamp: string | undefined): string => {
    if (!timestamp) return new Date().toISOString()
    const str = String(timestamp)
    // If it doesn't have timezone info, assume it's UTC
    if (!str.includes('Z') && !str.includes('+') && !str.includes('-00:00')) {
      return `${str}Z`
    }
    return str
  }

  return {
    id: String(task.id),
    userId: task.user_id,
    title: task.title,
    description: task.description,
    completed: task.status === 'complete',
    priority: task.priority,
    createdAt: normalizeTimestamp(task.created_at),
    updatedAt: normalizeTimestamp(task.updated_at),
  }
}

export interface UseTasksResult {
  tasks: Task[]
  isLoading: boolean
  error: string | null
  fetchTasks: (userId: string) => Promise<void>
  createTask: (userId: string, data: CreateTaskRequest) => Promise<Task>
  updateTask: (userId: string, taskId: string, data: UpdateTaskRequest) => Promise<Task>
  completeTask: (userId: string, taskId: string) => Promise<Task>
  incompleteTask: (userId: string, taskId: string) => Promise<Task>
  deleteTask: (userId: string, taskId: string) => Promise<void>
  clearError: () => void
}

export function useTasks(): UseTasksResult {
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const fetchTasks = useCallback(async (userId: string) => {
    setIsLoading(true)
    setError(null)

    try {
      const taskData = await apiClient.get<any[]>(`/api/${userId}/tasks`)
      setTasks(taskData.map(transformTask))
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch tasks'
      setError(message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const createTask = useCallback(
    async (userId: string, data: CreateTaskRequest): Promise<Task> => {
      setIsLoading(true)
      setError(null)

      try {
        const newTaskData = await apiClient.post<any>(`/api/${userId}/tasks`, data)
        const newTask = transformTask(newTaskData)

        // Optimistic update
        setTasks((prev) => [...prev, newTask])

        return newTask
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to create task'
        setError(message)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  const updateTask = useCallback(
    async (userId: string, taskId: string, data: UpdateTaskRequest): Promise<Task> => {
      setIsLoading(true)
      setError(null)

      try {
        const updatedTaskData = await apiClient.put<any>(
          `/api/${userId}/tasks/${taskId}`,
          data
        )
        const updatedTask = transformTask(updatedTaskData)

        // Optimistic update
        setTasks((prev) =>
          prev.map((task) => (task.id === taskId ? updatedTask : task))
        )

        return updatedTask
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to update task'
        setError(message)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  const completeTask = useCallback(
    async (userId: string, taskId: string): Promise<Task> => {
      setIsLoading(true)
      setError(null)

      try {
        const updatedTaskData = await apiClient.patch<any>(
          `/api/${userId}/tasks/${taskId}/status`,
          { status: 'complete' }
        )
        const updatedTask = transformTask(updatedTaskData)

        // Optimistic update
        setTasks((prev) =>
          prev.map((task) => (task.id === taskId ? updatedTask : task))
        )

        return updatedTask
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to complete task'
        setError(message)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  const incompleteTask = useCallback(
    async (userId: string, taskId: string): Promise<Task> => {
      setIsLoading(true)
      setError(null)

      try {
        const updatedTaskData = await apiClient.patch<any>(
          `/api/${userId}/tasks/${taskId}/status`,
          { status: 'incomplete' }
        )
        const updatedTask = transformTask(updatedTaskData)

        // Optimistic update
        setTasks((prev) =>
          prev.map((task) => (task.id === taskId ? updatedTask : task))
        )

        return updatedTask
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to mark task incomplete'
        setError(message)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  const deleteTask = useCallback(
    async (userId: string, taskId: string): Promise<void> => {
      setIsLoading(true)
      setError(null)

      try {
        await apiClient.delete(`/api/${userId}/tasks/${taskId}`)

        // Optimistic update
        setTasks((prev) => prev.filter((task) => task.id !== taskId))
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to delete task'
        setError(message)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  return {
    tasks,
    isLoading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    completeTask,
    incompleteTask,
    deleteTask,
    clearError,
  }
}
