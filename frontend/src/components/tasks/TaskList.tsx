/**
 * TaskList Component
 * Displays array of tasks
 */

import React from 'react'
import { Task } from '@/src/lib/api/types'
import { TaskItem } from './TaskItem'

interface TaskListProps {
  tasks: Task[]
  onEdit?: (taskId: string) => void
  onDelete?: (taskId: string) => Promise<void>
  onComplete?: (taskId: string) => Promise<void>
  isLoading?: boolean
}

export function TaskList({
  tasks,
  onEdit,
  onDelete,
  onComplete,
  isLoading = false,
}: TaskListProps) {
  if (tasks.length === 0) {
    return null
  }

  return (
    <div className="space-y-2">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onEdit={onEdit}
          onDelete={onDelete}
          onComplete={onComplete}
          isLoading={isLoading}
        />
      ))}
    </div>
  )
}
