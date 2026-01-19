/**
 * API Response Types
 * Shared types for all API responses
 */

export interface User {
  id: string
  email: string
  name?: string
  createdAt?: string
  updatedAt?: string
}

export interface Task {
  id: string
  userId: string
  title: string
  description?: string
  completed: boolean
  priority?: string  // "low", "medium", or "high"
  createdAt: string
  updatedAt: string
}

export interface AuthError {
  code: string
  message: string
  details?: Record<string, unknown>
}

export interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  error?: AuthError
}

export interface TaskListResponse {
  tasks: Task[]
  total: number
  page: number
  pageSize: number
}

export interface CreateTaskRequest {
  title: string
  description?: string
  priority?: string  // "low", "medium", or "high"
}

export interface UpdateTaskRequest {
  title?: string
  description?: string
  completed?: boolean
  priority?: string  // "low", "medium", or "high"
}

export interface SignUpRequest {
  email: string
  password: string
  name?: string
}

export interface SignInRequest {
  email: string
  password: string
}

export interface AuthResponse {
  user: User
  token: string
  expiresAt?: string
}
