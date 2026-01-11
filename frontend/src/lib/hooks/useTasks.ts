'use client'

/**
 * useTasks Hook
 * Custom hook for managing task operations
 */

import { useState, useCallback } from 'react'
import { Task, CreateTaskRequest, UpdateTaskRequest } from '@/src/lib/api/types'
import { apiClient } from '@/src/lib/api/client'

export interface UseTasksResult {
  tasks: Task[]
  isLoading: boolean
  error: string | null
  fetchTasks: (userId: string) => Promise<void>
  createTask: (userId: string, data: CreateTaskRequest) => Promise<Task>
  updateTask: (userId: string, taskId: string, data: UpdateTaskRequest) => Promise<Task>
  completeTask: (userId: string, taskId: string) => Promise<Task>
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
      const data = await apiClient.get<{ tasks: Task[] }>(`/api/${userId}/tasks`)
      setTasks(data.tasks)
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
        const newTask = await apiClient.post<Task>(`/api/${userId}/tasks`, data)

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
        const updatedTask = await apiClient.put<Task>(
          `/api/${userId}/tasks/${taskId}`,
          data
        )

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
        const updatedTask = await apiClient.patch<Task>(
          `/api/${userId}/tasks/${taskId}/complete`,
          {}
        )

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
    deleteTask,
    clearError,
  }
}
