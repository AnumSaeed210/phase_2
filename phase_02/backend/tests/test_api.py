"""Integration tests for Task API endpoints"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.models import Task, User


class TestCreateTask:
    """Tests for POST /api/{user_id}/tasks endpoint (User Story 1)"""

    def test_create_task_with_title_only(self, client: TestClient, test_user: User):
        """Test creating task with title only"""
        response = client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": "Buy groceries"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Buy groceries"
        assert data["description"] is None
        assert data["status"] == "incomplete"
        assert data["user_id"] == test_user.id
        assert data["id"] is not None
        assert data["created_at"] is not None
        assert data["updated_at"] is not None

    def test_create_task_with_description(self, client: TestClient, test_user: User):
        """Test creating task with title and description"""
        response = client.post(
            f"/api/{test_user.id}/tasks",
            json={
                "title": "Buy groceries",
                "description": "Milk, eggs, bread"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Buy groceries"
        assert data["description"] == "Milk, eggs, bread"

    def test_create_task_missing_title(self, client: TestClient, test_user: User):
        """Test creating task without title returns 400"""
        response = client.post(
            f"/api/{test_user.id}/tasks",
            json={"description": "Some description"}
        )

        assert response.status_code == 422  # Pydantic validation error

    def test_create_task_empty_title(self, client: TestClient, test_user: User):
        """Test creating task with empty title returns 400"""
        response = client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": ""}
        )

        # Empty string should fail validation
        assert response.status_code == 400
        assert "Title is required" in response.json()["detail"]["error"]

    def test_create_task_title_too_long(self, client: TestClient, test_user: User):
        """Test creating task with title over 255 chars returns 400"""
        long_title = "a" * 256
        response = client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": long_title}
        )

        assert response.status_code == 400
        assert "255 characters" in response.json()["detail"]["error"]

    def test_create_task_description_too_long(self, client: TestClient, test_user: User):
        """Test creating task with description over 5000 chars returns 400"""
        long_desc = "a" * 5001
        response = client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": "Task", "description": long_desc}
        )

        assert response.status_code == 400
        assert "5000 characters" in response.json()["detail"]["error"]

    def test_create_task_returned_as_response(self, client: TestClient, test_user: User, session: Session):
        """Test that created task matches database"""
        response = client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": "Test"}
        )

        assert response.status_code == 201
        task_id = response.json()["id"]

        # Verify in database
        db_task = session.get(Task, task_id)
        assert db_task is not None
        assert db_task.title == "Test"


class TestListTasks:
    """Tests for GET /api/{user_id}/tasks endpoint (User Story 2)"""

    def test_list_tasks_empty(self, client: TestClient, test_user: User):
        """Test listing tasks when user has none"""
        response = client.get(f"/api/{test_user.id}/tasks")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_tasks_returns_user_tasks(self, client: TestClient, test_user: User):
        """Test listing returns all user's tasks"""
        # Create two tasks
        client.post(f"/api/{test_user.id}/tasks", json={"title": "Task 1"})
        client.post(f"/api/{test_user.id}/tasks", json={"title": "Task 2"})

        response = client.get(f"/api/{test_user.id}/tasks")

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 2
        assert tasks[0]["title"] in ["Task 1", "Task 2"]
        assert tasks[1]["title"] in ["Task 1", "Task 2"]

    def test_list_tasks_multi_user_isolation(self, client: TestClient, test_user: User, test_user_2: User, session: Session):
        """Test that users only see their own tasks"""
        # Create task for user 1
        client.post(f"/api/{test_user.id}/tasks", json={"title": "User 1 task"})

        # Create task for user 2
        client.post(f"/api/{test_user_2.id}/tasks", json={"title": "User 2 task"})

        # User 1 lists tasks
        response1 = client.get(f"/api/{test_user.id}/tasks")
        assert response1.status_code == 200
        tasks1 = response1.json()
        assert len(tasks1) == 1
        assert tasks1[0]["title"] == "User 1 task"

        # User 2 lists tasks
        response2 = client.get(f"/api/{test_user_2.id}/tasks")
        assert response2.status_code == 200
        tasks2 = response2.json()
        assert len(tasks2) == 1
        assert tasks2[0]["title"] == "User 2 task"

    def test_list_tasks_with_status_filter_incomplete(self, client: TestClient, test_user: User):
        """Test filtering tasks by incomplete status"""
        # Create incomplete and complete tasks
        client.post(f"/api/{test_user.id}/tasks", json={"title": "Incomplete"})
        complete_response = client.post(f"/api/{test_user.id}/tasks", json={"title": "To complete"})
        task_id = complete_response.json()["id"]

        # Mark one complete
        client.patch(f"/api/{test_user.id}/tasks/{task_id}/complete")

        # Filter by incomplete
        response = client.get(f"/api/{test_user.id}/tasks?status=incomplete")

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Incomplete"

    def test_list_tasks_with_status_filter_complete(self, client: TestClient, test_user: User):
        """Test filtering tasks by complete status"""
        # Create complete task
        complete_response = client.post(f"/api/{test_user.id}/tasks", json={"title": "Complete me"})
        task_id = complete_response.json()["id"]
        client.patch(f"/api/{test_user.id}/tasks/{task_id}/complete")

        # Create incomplete task
        client.post(f"/api/{test_user.id}/tasks", json={"title": "Incomplete"})

        # Filter by complete
        response = client.get(f"/api/{test_user.id}/tasks?status=complete")

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Complete me"

    def test_list_tasks_invalid_status_filter(self, client: TestClient, test_user: User):
        """Test invalid status filter returns 400"""
        response = client.get(f"/api/{test_user.id}/tasks?status=invalid")

        assert response.status_code == 400
        assert "Invalid status value" in response.json()["detail"]["error"]


class TestGetTask:
    """Tests for GET /api/{user_id}/tasks/{id} endpoint (User Story 3)"""

    def test_get_task_success(self, client: TestClient, test_user: User):
        """Test retrieving existing task"""
        create_response = client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": "Test task", "description": "Description"}
        )
        task_id = create_response.json()["id"]

        response = client.get(f"/api/{test_user.id}/tasks/{task_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test task"
        assert data["description"] == "Description"

    def test_get_task_not_found(self, client: TestClient, test_user: User):
        """Test getting non-existent task returns 404"""
        response = client.get(f"/api/{test_user.id}/tasks/9999")

        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]["error"]

    def test_get_task_invalid_id_format(self, client: TestClient, test_user: User):
        """Test getting task with invalid ID format returns 400"""
        response = client.get(f"/api/{test_user.id}/tasks/invalid")

        assert response.status_code == 400
        assert "Invalid task ID" in response.json()["detail"]["error"]

    def test_get_task_ownership_check(self, client: TestClient, test_user: User, test_user_2: User):
        """Test that user cannot get another user's task"""
        # Create task for user 1
        response = client.post(f"/api/{test_user.id}/tasks", json={"title": "User 1 task"})
        task_id = response.json()["id"]

        # User 2 tries to get user 1's task
        response = client.get(f"/api/{test_user_2.id}/tasks/{task_id}")

        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]["error"]


class TestUpdateTask:
    """Tests for PUT /api/{user_id}/tasks/{id} endpoint (User Story 4)"""

    def test_update_task_title(self, client: TestClient, test_user: User):
        """Test updating task title"""
        create_response = client.post(f"/api/{test_user.id}/tasks", json={"title": "Old"})
        task_id = create_response.json()["id"]
        original_updated_at = create_response.json()["updated_at"]

        response = client.put(
            f"/api/{test_user.id}/tasks/{task_id}",
            json={"title": "New"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New"
        assert data["updated_at"] > original_updated_at

    def test_update_task_description(self, client: TestClient, test_user: User):
        """Test updating task description"""
        create_response = client.post(f"/api/{test_user.id}/tasks", json={"title": "Task"})
        task_id = create_response.json()["id"]

        response = client.put(
            f"/api/{test_user.id}/tasks/{task_id}",
            json={"description": "New description"}
        )

        assert response.status_code == 200
        assert response.json()["description"] == "New description"

    def test_update_task_both_fields(self, client: TestClient, test_user: User):
        """Test updating both title and description"""
        create_response = client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": "Old", "description": "Old desc"}
        )
        task_id = create_response.json()["id"]

        response = client.put(
            f"/api/{test_user.id}/tasks/{task_id}",
            json={"title": "New", "description": "New desc"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New"
        assert data["description"] == "New desc"

    def test_update_task_no_fields(self, client: TestClient, test_user: User):
        """Test updating with no fields returns 400"""
        create_response = client.post(f"/api/{test_user.id}/tasks", json={"title": "Task"})
        task_id = create_response.json()["id"]

        response = client.put(
            f"/api/{test_user.id}/tasks/{task_id}",
            json={}
        )

        assert response.status_code == 400
        assert "At least one field" in response.json()["detail"]["error"]

    def test_update_task_empty_title(self, client: TestClient, test_user: User):
        """Test updating title to empty returns 400"""
        create_response = client.post(f"/api/{test_user.id}/tasks", json={"title": "Task"})
        task_id = create_response.json()["id"]

        response = client.put(
            f"/api/{test_user.id}/tasks/{task_id}",
            json={"title": ""}
        )

        assert response.status_code == 400
        assert "cannot be empty" in response.json()["detail"]["error"]

    def test_update_task_title_too_long(self, client: TestClient, test_user: User):
        """Test updating title over 255 chars returns 400"""
        create_response = client.post(f"/api/{test_user.id}/tasks", json={"title": "Task"})
        task_id = create_response.json()["id"]

        response = client.put(
            f"/api/{test_user.id}/tasks/{task_id}",
            json={"title": "a" * 256}
        )

        assert response.status_code == 400
        assert "255 characters" in response.json()["detail"]["error"]

    def test_update_task_not_found(self, client: TestClient, test_user: User):
        """Test updating non-existent task returns 404"""
        response = client.put(
            f"/api/{test_user.id}/tasks/9999",
            json={"title": "New"}
        )

        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]["error"]

    def test_update_task_ownership_check(self, client: TestClient, test_user: User, test_user_2: User):
        """Test that user cannot update another user's task"""
        # Create task for user 1
        response = client.post(f"/api/{test_user.id}/tasks", json={"title": "User 1 task"})
        task_id = response.json()["id"]

        # User 2 tries to update user 1's task
        response = client.put(
            f"/api/{test_user_2.id}/tasks/{task_id}",
            json={"title": "Hacked"}
        )

        assert response.status_code == 404

    def test_update_preserves_created_at(self, client: TestClient, test_user: User):
        """Test that update preserves created_at timestamp"""
        create_response = client.post(f"/api/{test_user.id}/tasks", json={"title": "Task"})
        task_id = create_response.json()["id"]
        original_created_at = create_response.json()["created_at"]

        response = client.put(
            f"/api/{test_user.id}/tasks/{task_id}",
            json={"title": "Updated"}
        )

        assert response.json()["created_at"] == original_created_at


class TestDeleteTask:
    """Tests for DELETE /api/{user_id}/tasks/{id} endpoint (User Story 5)"""

    def test_delete_task_success(self, client: TestClient, test_user: User):
        """Test deleting task returns 204"""
        create_response = client.post(f"/api/{test_user.id}/tasks", json={"title": "Delete me"})
        task_id = create_response.json()["id"]

        response = client.delete(f"/api/{test_user.id}/tasks/{task_id}")

        assert response.status_code == 204
        assert response.content == b""

    def test_delete_task_actually_deleted(self, client: TestClient, test_user: User):
        """Test that deleted task cannot be retrieved"""
        create_response = client.post(f"/api/{test_user.id}/tasks", json={"title": "Delete me"})
        task_id = create_response.json()["id"]

        client.delete(f"/api/{test_user.id}/tasks/{task_id}")

        # Try to get deleted task
        response = client.get(f"/api/{test_user.id}/tasks/{task_id}")
        assert response.status_code == 404

    def test_delete_task_not_found(self, client: TestClient, test_user: User):
        """Test deleting non-existent task returns 404"""
        response = client.delete(f"/api/{test_user.id}/tasks/9999")

        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]["error"]

    def test_delete_task_invalid_id_format(self, client: TestClient, test_user: User):
        """Test deleting with invalid ID format returns 400"""
        response = client.delete(f"/api/{test_user.id}/tasks/invalid")

        assert response.status_code == 400
        assert "Invalid task ID" in response.json()["detail"]["error"]

    def test_delete_task_ownership_check(self, client: TestClient, test_user: User, test_user_2: User):
        """Test that user cannot delete another user's task"""
        # Create task for user 1
        response = client.post(f"/api/{test_user.id}/tasks", json={"title": "User 1 task"})
        task_id = response.json()["id"]

        # User 2 tries to delete user 1's task
        response = client.delete(f"/api/{test_user_2.id}/tasks/{task_id}")

        assert response.status_code == 404

        # Task should still exist for user 1
        response = client.get(f"/api/{test_user.id}/tasks/{task_id}")
        assert response.status_code == 200


class TestCompleteTask:
    """Tests for PATCH /api/{user_id}/tasks/{id}/complete endpoint (User Story 6)"""

    def test_mark_complete_success(self, client: TestClient, test_user: User):
        """Test marking task complete changes status"""
        create_response = client.post(f"/api/{test_user.id}/tasks", json={"title": "Task"})
        task_id = create_response.json()["id"]

        response = client.patch(f"/api/{test_user.id}/tasks/{task_id}/complete")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "complete"

    def test_mark_complete_idempotent(self, client: TestClient, test_user: User):
        """Test marking complete twice returns 200 both times"""
        create_response = client.post(f"/api/{test_user.id}/tasks", json={"title": "Task"})
        task_id = create_response.json()["id"]

        # First completion
        response1 = client.patch(f"/api/{test_user.id}/tasks/{task_id}/complete")
        assert response1.status_code == 200
        first_data = response1.json()

        # Second completion (should be idempotent)
        response2 = client.patch(f"/api/{test_user.id}/tasks/{task_id}/complete")
        assert response2.status_code == 200
        second_data = response2.json()

        assert first_data["status"] == "complete"
        assert second_data["status"] == "complete"

    def test_mark_complete_updates_timestamp(self, client: TestClient, test_user: User):
        """Test that marking complete updates updated_at"""
        create_response = client.post(f"/api/{test_user.id}/tasks", json={"title": "Task"})
        task_id = create_response.json()["id"]
        original_updated_at = create_response.json()["updated_at"]

        response = client.patch(f"/api/{test_user.id}/tasks/{task_id}/complete")

        assert response.json()["updated_at"] > original_updated_at

    def test_mark_complete_not_found(self, client: TestClient, test_user: User):
        """Test marking non-existent task complete returns 404"""
        response = client.patch(f"/api/{test_user.id}/tasks/9999/complete")

        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]["error"]

    def test_mark_complete_invalid_id_format(self, client: TestClient, test_user: User):
        """Test marking complete with invalid ID format returns 400"""
        response = client.patch(f"/api/{test_user.id}/tasks/invalid/complete")

        assert response.status_code == 400
        assert "Invalid task ID" in response.json()["detail"]["error"]

    def test_mark_complete_ownership_check(self, client: TestClient, test_user: User, test_user_2: User):
        """Test that user cannot mark another user's task complete"""
        # Create task for user 1
        response = client.post(f"/api/{test_user.id}/tasks", json={"title": "User 1 task"})
        task_id = response.json()["id"]

        # User 2 tries to mark user 1's task complete
        response = client.patch(f"/api/{test_user_2.id}/tasks/{task_id}/complete")

        assert response.status_code == 404

        # Task should still be incomplete for user 1
        response = client.get(f"/api/{test_user.id}/tasks/{task_id}")
        assert response.json()["status"] == "incomplete"


class TestErrorHandling:
    """Tests for error responses and status codes"""

    def test_error_response_format(self, client: TestClient, test_user: User):
        """Test that errors have consistent format"""
        response = client.get(f"/api/{test_user.id}/tasks/invalid")

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"]
        assert isinstance(data["detail"]["error"], str)

    def test_validation_error_status_code(self, client: TestClient, test_user: User):
        """Test that validation errors return 400"""
        response = client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": "a" * 256}
        )

        assert response.status_code == 400

    def test_not_found_status_code(self, client: TestClient, test_user: User):
        """Test that not found errors return 404"""
        response = client.get(f"/api/{test_user.id}/tasks/9999")

        assert response.status_code == 404
