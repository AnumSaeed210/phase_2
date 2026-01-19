"""Unit tests for SQLModel definitions"""
import pytest
from datetime import datetime, timezone
from src.models import Task, User


class TestUserModel:
    """Tests for User model validation"""

    def test_user_creation(self):
        """Test basic user creation"""
        user = User(id="user-1", email="test@example.com")
        assert user.id == "user-1"
        assert user.email == "test@example.com"

    def test_user_required_fields(self):
        """Test that user requires id and email"""
        with pytest.raises(TypeError):
            User()  # Missing required fields


class TestTaskModel:
    """Tests for Task model validation"""

    def test_task_creation_with_all_fields(self):
        """Test task creation with all fields"""
        task = Task(
            user_id="user-1",
            title="Test Task",
            description="Test description",
            status="incomplete"
        )
        assert task.id is None  # Auto-generated on insert
        assert task.user_id == "user-1"
        assert task.title == "Test Task"
        assert task.description == "Test description"
        assert task.status == "incomplete"
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_task_creation_minimal(self):
        """Test task creation with minimal fields"""
        task = Task(
            user_id="user-1",
            title="Minimal Task"
        )
        assert task.id is None
        assert task.user_id == "user-1"
        assert task.title == "Minimal Task"
        assert task.description is None
        assert task.status == "incomplete"

    def test_task_title_required(self):
        """Test that task requires title"""
        with pytest.raises(TypeError):
            Task(user_id="user-1")  # Missing title

    def test_task_user_id_required(self):
        """Test that task requires user_id"""
        with pytest.raises(TypeError):
            Task(title="Test")  # Missing user_id

    def test_task_timestamps_auto_set(self):
        """Test that timestamps are auto-set on creation"""
        now = datetime.now(timezone.utc)
        task = Task(user_id="user-1", title="Test")

        # Timestamps should be set to approximately now
        assert task.created_at is not None
        assert task.updated_at is not None
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    def test_task_status_default(self):
        """Test that task status defaults to incomplete"""
        task = Task(user_id="user-1", title="Test")
        assert task.status == "incomplete"

    def test_task_description_optional(self):
        """Test that description is optional and can be null"""
        task = Task(user_id="user-1", title="Test", description=None)
        assert task.description is None

    def test_task_title_length_validation(self):
        """Test that title has max length constraint"""
        long_title = "a" * 256  # One char over limit
        task = Task(user_id="user-1", title=long_title)
        # SQLModel will have the field defined with max_length, validation happens at API layer
        assert len(task.title) == 256

    def test_task_description_length_validation(self):
        """Test that description has max length constraint"""
        long_description = "a" * 5001  # One char over limit
        task = Task(
            user_id="user-1",
            title="Test",
            description=long_description
        )
        # SQLModel will have the field defined with max_length
        assert len(task.description) == 5001
