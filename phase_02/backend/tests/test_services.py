"""Unit tests for TaskService business logic"""
import pytest
from datetime import datetime, timezone
from sqlmodel import Session

from src.models import Task, User
from src.services import TaskService


class TestTaskServiceCreateTask:
    """Tests for TaskService.create_task()"""

    def test_create_task_with_title_only(self, session: Session, test_user: User):
        """Test creating task with title only (description optional)"""
        service = TaskService(session)
        task = service.create_task(
            user_id=test_user.id,
            title="Buy groceries"
        )

        assert task.id is not None
        assert task.user_id == test_user.id
        assert task.title == "Buy groceries"
        assert task.description is None
        assert task.status == "incomplete"
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_create_task_with_title_and_description(self, session: Session, test_user: User):
        """Test creating task with title and description"""
        service = TaskService(session)
        task = service.create_task(
            user_id=test_user.id,
            title="Buy groceries",
            description="Milk, eggs, bread"
        )

        assert task.id is not None
        assert task.user_id == test_user.id
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"
        assert task.status == "incomplete"

    def test_create_task_persists_to_database(self, session: Session, test_user: User):
        """Test that created task is persisted to database"""
        service = TaskService(session)
        task = service.create_task(
            user_id=test_user.id,
            title="Test task"
        )

        # Retrieve task directly from database
        db_task = session.get(Task, task.id)
        assert db_task is not None
        assert db_task.id == task.id
        assert db_task.title == "Test task"


class TestTaskServiceGetTasksForUser:
    """Tests for TaskService.get_tasks_for_user()"""

    def test_get_tasks_empty_list(self, session: Session, test_user: User):
        """Test getting tasks when user has none"""
        service = TaskService(session)
        tasks = service.get_tasks_for_user(test_user.id)

        assert tasks == []

    def test_get_tasks_returns_user_tasks(self, session: Session, test_user: User):
        """Test getting tasks returns all user's tasks"""
        service = TaskService(session)

        # Create multiple tasks
        task1 = service.create_task(test_user.id, "Task 1")
        task2 = service.create_task(test_user.id, "Task 2")

        tasks = service.get_tasks_for_user(test_user.id)

        assert len(tasks) == 2
        assert any(t.id == task1.id for t in tasks)
        assert any(t.id == task2.id for t in tasks)

    def test_get_tasks_filters_by_user(self, session: Session, test_user: User, test_user_2: User):
        """Test that get_tasks_for_user filters by user_id"""
        service = TaskService(session)

        # Create tasks for user 1
        task1 = service.create_task(test_user.id, "User 1 Task")

        # Create tasks for user 2
        task2 = service.create_task(test_user_2.id, "User 2 Task")

        # Get tasks for user 1
        user1_tasks = service.get_tasks_for_user(test_user.id)
        assert len(user1_tasks) == 1
        assert user1_tasks[0].id == task1.id

        # Get tasks for user 2
        user2_tasks = service.get_tasks_for_user(test_user_2.id)
        assert len(user2_tasks) == 1
        assert user2_tasks[0].id == task2.id

    def test_get_tasks_with_status_filter(self, session: Session, test_user: User):
        """Test filtering tasks by status"""
        service = TaskService(session)

        # Create incomplete and complete tasks
        incomplete = service.create_task(test_user.id, "Incomplete")
        complete = service.mark_complete(incomplete.id, test_user.id)

        other_incomplete = service.create_task(test_user.id, "Another incomplete")

        # Filter by incomplete
        incomplete_tasks = service.get_tasks_for_user(test_user.id, status="incomplete")
        assert len(incomplete_tasks) == 1
        assert incomplete_tasks[0].id == other_incomplete.id

        # Filter by complete
        complete_tasks = service.get_tasks_for_user(test_user.id, status="complete")
        assert len(complete_tasks) == 1
        assert complete_tasks[0].id == complete.id


class TestTaskServiceGetTaskById:
    """Tests for TaskService.get_task_by_id()"""

    def test_get_task_by_id_success(self, session: Session, test_user: User):
        """Test retrieving task by ID when owned by user"""
        service = TaskService(session)
        created = service.create_task(test_user.id, "Test task")

        retrieved = service.get_task_by_id(created.id, test_user.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.title == "Test task"

    def test_get_task_by_id_not_found(self, session: Session, test_user: User):
        """Test retrieving non-existent task returns None"""
        service = TaskService(session)

        task = service.get_task_by_id(9999, test_user.id)

        assert task is None

    def test_get_task_by_id_ownership_check(self, session: Session, test_user: User, test_user_2: User):
        """Test that get_task_by_id enforces ownership"""
        service = TaskService(session)

        # Create task for user 1
        task = service.create_task(test_user.id, "User 1 task")

        # Try to get task as user 2 (should fail)
        retrieved = service.get_task_by_id(task.id, test_user_2.id)

        assert retrieved is None


class TestTaskServiceUpdateTask:
    """Tests for TaskService.update_task()"""

    def test_update_task_title(self, session: Session, test_user: User):
        """Test updating task title"""
        service = TaskService(session)
        task = service.create_task(test_user.id, "Old title")
        original_updated_at = task.updated_at

        updated = service.update_task(
            task.id,
            test_user.id,
            title="New title"
        )

        assert updated is not None
        assert updated.title == "New title"
        assert updated.updated_at > original_updated_at

    def test_update_task_description(self, session: Session, test_user: User):
        """Test updating task description"""
        service = TaskService(session)
        task = service.create_task(test_user.id, "Task")

        updated = service.update_task(
            task.id,
            test_user.id,
            description="New description"
        )

        assert updated is not None
        assert updated.description == "New description"

    def test_update_task_both_fields(self, session: Session, test_user: User):
        """Test updating both title and description"""
        service = TaskService(session)
        task = service.create_task(test_user.id, "Old", "Old desc")

        updated = service.update_task(
            task.id,
            test_user.id,
            title="New",
            description="New desc"
        )

        assert updated.title == "New"
        assert updated.description == "New desc"

    def test_update_task_not_found(self, session: Session, test_user: User):
        """Test updating non-existent task returns None"""
        service = TaskService(session)

        result = service.update_task(9999, test_user.id, title="New")

        assert result is None

    def test_update_task_ownership_check(self, session: Session, test_user: User, test_user_2: User):
        """Test that update_task enforces ownership"""
        service = TaskService(session)
        task = service.create_task(test_user.id, "Task")

        # Try to update as user 2
        result = service.update_task(task.id, test_user_2.id, title="Hacked")

        assert result is None

    def test_update_preserves_created_at(self, session: Session, test_user: User):
        """Test that update preserves created_at timestamp"""
        service = TaskService(session)
        task = service.create_task(test_user.id, "Task")
        original_created_at = task.created_at

        updated = service.update_task(task.id, test_user.id, title="Updated")

        assert updated.created_at == original_created_at


class TestTaskServiceDeleteTask:
    """Tests for TaskService.delete_task()"""

    def test_delete_task_success(self, session: Session, test_user: User):
        """Test successful task deletion"""
        service = TaskService(session)
        task = service.create_task(test_user.id, "Task to delete")

        result = service.delete_task(task.id, test_user.id)

        assert result is True

        # Verify task is gone
        retrieved = service.get_task_by_id(task.id, test_user.id)
        assert retrieved is None

    def test_delete_task_not_found(self, session: Session, test_user: User):
        """Test deleting non-existent task returns False"""
        service = TaskService(session)

        result = service.delete_task(9999, test_user.id)

        assert result is False

    def test_delete_task_ownership_check(self, session: Session, test_user: User, test_user_2: User):
        """Test that delete_task enforces ownership"""
        service = TaskService(session)
        task = service.create_task(test_user.id, "Task")

        # Try to delete as user 2
        result = service.delete_task(task.id, test_user_2.id)

        assert result is False

        # Task should still exist
        retrieved = service.get_task_by_id(task.id, test_user.id)
        assert retrieved is not None


class TestTaskServiceMarkComplete:
    """Tests for TaskService.mark_complete()"""

    def test_mark_complete_success(self, session: Session, test_user: User):
        """Test marking task as complete"""
        service = TaskService(session)
        task = service.create_task(test_user.id, "Task")

        completed = service.mark_complete(task.id, test_user.id)

        assert completed is not None
        assert completed.status == "complete"

    def test_mark_complete_idempotent(self, session: Session, test_user: User):
        """Test that marking complete twice is idempotent"""
        service = TaskService(session)
        task = service.create_task(test_user.id, "Task")

        first = service.mark_complete(task.id, test_user.id)
        second = service.mark_complete(task.id, test_user.id)

        assert first.id == second.id
        assert first.status == "complete"
        assert second.status == "complete"

    def test_mark_complete_updates_timestamp(self, session: Session, test_user: User):
        """Test that marking complete updates updated_at"""
        service = TaskService(session)
        task = service.create_task(test_user.id, "Task")
        original_updated_at = task.updated_at

        completed = service.mark_complete(task.id, test_user.id)

        assert completed.updated_at > original_updated_at

    def test_mark_complete_not_found(self, session: Session, test_user: User):
        """Test marking non-existent task returns None"""
        service = TaskService(session)

        result = service.mark_complete(9999, test_user.id)

        assert result is None

    def test_mark_complete_ownership_check(self, session: Session, test_user: User, test_user_2: User):
        """Test that mark_complete enforces ownership"""
        service = TaskService(session)
        task = service.create_task(test_user.id, "Task")

        # Try to mark complete as user 2
        result = service.mark_complete(task.id, test_user_2.id)

        assert result is None

        # Task should still be incomplete
        retrieved = service.get_task_by_id(task.id, test_user.id)
        assert retrieved.status == "incomplete"
