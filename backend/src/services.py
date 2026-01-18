"""Business logic layer - TaskService for CRUD operations"""
from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import Session, select
from src.models import Task


class TaskService:
    """Service class for task-related business logic with ownership validation"""

    def __init__(self, session: Session):
        """Initialize service with database session"""
        self.session = session

    def get_tasks_for_user(
        self,
        user_id: str,
        status: Optional[str] = None,
        sort: Optional[str] = None
    ) -> List[Task]:
        """
        Retrieve all tasks for a user, optionally filtered by status and sorted

        Args:
            user_id: Authenticated user ID
            status: Optional status filter ("incomplete" or "complete")
            sort: Optional sort parameter ("priority" for priority sorting)

        Returns:
            List of Task objects owned by the user, sorted as requested
        """
        query = select(Task).where(Task.user_id == user_id)

        if status:
            query = query.where(Task.status == status)

        results = self.session.exec(query).all()

        # Apply sorting in Python to handle priority ordering
        if sort == "priority":
            # Priority order: high (3) > medium (2) > low (1)
            priority_order = {"high": 3, "medium": 2, "low": 1}
            results = sorted(
                results,
                key=lambda t: (-priority_order.get(t.priority, 2), -t.created_at.timestamp())
            )
        else:
            # Default sort: newest first
            results = sorted(results, key=lambda t: -t.created_at.timestamp())

        return results

    def get_task_by_id(self, task_id: int, user_id: str) -> Optional[Task]:
        """
        Retrieve a single task by ID with ownership verification

        Args:
            task_id: Task ID to retrieve
            user_id: Authenticated user ID for ownership check

        Returns:
            Task object if found and owned by user, None otherwise
        """
        task = self.session.exec(
            select(Task).where(
                (Task.id == task_id) & (Task.user_id == user_id)
            )
        ).first()
        return task

    def create_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        priority: Optional[str] = None
    ) -> Task:
        """
        Create a new task for a user

        Args:
            user_id: Authenticated user ID (task owner)
            title: Task title (required)
            description: Task description (optional)
            priority: Task priority level (optional, defaults to "medium")

        Returns:
            Created Task object with auto-generated ID and timestamps
        """
        now = datetime.now(timezone.utc)
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            status="incomplete",
            priority=priority or "medium",
            created_at=now,
            updated_at=now
        )
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def update_task(
        self,
        task_id: int,
        user_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None
    ) -> Optional[Task]:
        """
        Update a task's title, description, and/or priority with ownership verification

        Args:
            task_id: Task ID to update
            user_id: Authenticated user ID for ownership check
            title: New title (optional)
            description: New description (optional)
            priority: New priority level (optional)

        Returns:
            Updated Task object if found and owned by user, None otherwise
        """
        task = self.get_task_by_id(task_id, user_id)
        if not task:
            return None

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if priority is not None:
            task.priority = priority

        task.updated_at = datetime.now(timezone.utc)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def delete_task(self, task_id: int, user_id: str) -> bool:
        """
        Delete a task with ownership verification

        Args:
            task_id: Task ID to delete
            user_id: Authenticated user ID for ownership check

        Returns:
            True if task was deleted, False if not found or not owned
        """
        task = self.get_task_by_id(task_id, user_id)
        if not task:
            return False

        self.session.delete(task)
        self.session.commit()
        return True

    def mark_complete(self, task_id: int, user_id: str) -> Optional[Task]:
        """
        Mark a task as complete with ownership verification

        Args:
            task_id: Task ID to mark complete
            user_id: Authenticated user ID for ownership check

        Returns:
            Updated Task object if found and owned by user, None otherwise
        """
        task = self.get_task_by_id(task_id, user_id)
        if not task:
            return None

        task.status = "complete"
        task.updated_at = datetime.now(timezone.utc)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task
