/**
 * Task Form Validation
 * Title and description validation rules
 */

export interface ValidationError {
  field: string
  message: string
}

/**
 * Validate task title
 */
export function validateTaskTitle(title: string): ValidationError | null {
  if (!title || !title.trim()) {
    return { field: 'title', message: 'Task title is required' }
  }

  if (title.trim().length < 3) {
    return {
      field: 'title',
      message: 'Task title must be at least 3 characters long',
    }
  }

  if (title.length > 200) {
    return {
      field: 'title',
      message: 'Task title must not exceed 200 characters',
    }
  }

  return null
}

/**
 * Validate task description (optional)
 */
export function validateTaskDescription(
  description: string | undefined
): ValidationError | null {
  if (!description) return null

  if (description.length > 1000) {
    return {
      field: 'description',
      message: 'Task description must not exceed 1000 characters',
    }
  }

  return null
}

/**
 * Validate task creation form
 */
export function validateTaskForm(
  title: string,
  description?: string
): ValidationError | null {
  // Check title
  let error = validateTaskTitle(title)
  if (error) return error

  // Check description if provided
  if (description) {
    error = validateTaskDescription(description)
    if (error) return error
  }

  return null
}
