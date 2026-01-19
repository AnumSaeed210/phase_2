"""Integration tests for protected endpoints with JWT authentication"""
import os
import pytest
import jwt
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from src.database import get_session
from src.models import Task
from sqlmodel import Session, select


def create_test_jwt(user_id: str, email: str = "test@example.com", exp_minutes: int = 60) -> str:
    """Helper to create valid test JWT tokens"""
    secret = os.getenv("BETTER_AUTH_SECRET")
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=exp_minutes),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, secret, algorithm="HS256")


@pytest.fixture
def client():
    """Create test client"""
    from main import app
    return TestClient(app)


@pytest.fixture
def auth_headers_user1():
    """Create auth headers for user1"""
    token = create_test_jwt("user1", "user1@example.com")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_user2():
    """Create auth headers for user2"""
    token = create_test_jwt("user2", "user2@example.com")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_task_user1(client, auth_headers_user1):
    """Create a sample task for user1"""
    response = client.post(
        "/api/user1/tasks",
        json={"title": "User1 Task", "description": "Task owned by user1"},
        headers=auth_headers_user1
    )
    return response.json()


class TestAuthenticationRequired:
    """Test that all endpoints require authentication"""

    def test_create_task_without_auth(self, client):
        """Test POST /api/{user_id}/tasks requires authentication"""
        response = client.post(
            "/api/user1/tasks",
            json={"title": "Test Task"}
        )
        assert response.status_code == 401
        data = response.json()
        # FastAPI returns 401 errors with "detail" key
        assert "detail" in data

    def test_list_tasks_without_auth(self, client):
        """Test GET /api/{user_id}/tasks requires authentication"""
        response = client.get("/api/user1/tasks")
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_get_task_without_auth(self, client):
        """Test GET /api/{user_id}/tasks/{id} requires authentication"""
        response = client.get("/api/user1/tasks/1")
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_update_task_without_auth(self, client):
        """Test PUT /api/{user_id}/tasks/{id} requires authentication"""
        response = client.put(
            "/api/user1/tasks/1",
            json={"title": "Updated"}
        )
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_delete_task_without_auth(self, client):
        """Test DELETE /api/{user_id}/tasks/{id} requires authentication"""
        response = client.delete("/api/user1/tasks/1")
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_mark_complete_without_auth(self, client):
        """Test PATCH /api/{user_id}/tasks/{id}/complete requires authentication"""
        response = client.patch("/api/user1/tasks/1/complete")
        assert response.status_code == 401
        assert "detail" in response.json()


class TestInvalidTokens:
    """Test handling of invalid JWT tokens"""

    def test_malformed_token(self, client):
        """Test request with malformed JWT token"""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/api/user1/tasks", headers=headers)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_expired_token(self, client):
        """Test request with expired JWT token"""
        expired_token = create_test_jwt("user1", exp_minutes=-5)
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/user1/tasks", headers=headers)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_missing_bearer_prefix(self, client):
        """Test request without Bearer prefix"""
        token = create_test_jwt("user1")
        headers = {"Authorization": token}  # Missing "Bearer " prefix
        response = client.get("/api/user1/tasks", headers=headers)

        assert response.status_code == 401
        assert "detail" in response.json()

    def test_token_without_user_id(self, client):
        """Test token without required user_id claim"""
        secret = os.getenv("BETTER_AUTH_SECRET")
        payload = {
            "email": "test@example.com",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, secret, algorithm="HS256")
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/user1/tasks", headers=headers)
        assert response.status_code == 401


class TestUserIsolation:
    """Test that users can only access their own resources"""

    def test_user_cannot_create_task_for_other_user(self, client, auth_headers_user1):
        """Test user1 cannot create task for user2"""
        response = client.post(
            "/api/user2/tasks",  # Trying to access user2's endpoint
            json={"title": "Malicious Task"},
            headers=auth_headers_user1  # Using user1's token
        )

        assert response.status_code == 403
        assert "detail" in response.json()

    def test_user_cannot_list_other_user_tasks(self, client, auth_headers_user1):
        """Test user1 cannot list user2's tasks"""
        response = client.get(
            "/api/user2/tasks",
            headers=auth_headers_user1
        )

        assert response.status_code == 403
        assert "detail" in response.json()

    def test_user_cannot_view_other_user_task(self, client, auth_headers_user1, auth_headers_user2):
        """Test user1 cannot view user2's task"""
        # Create task as user2
        create_response = client.post(
            "/api/user2/tasks",
            json={"title": "User2 Task"},
            headers=auth_headers_user2
        )
        task_id = create_response.json()["id"]

        # Try to access as user1
        response = client.get(
            f"/api/user2/tasks/{task_id}",
            headers=auth_headers_user1
        )

        assert response.status_code == 403

    def test_user_cannot_update_other_user_task(self, client, auth_headers_user1, auth_headers_user2):
        """Test user1 cannot update user2's task"""
        # Create task as user2
        create_response = client.post(
            "/api/user2/tasks",
            json={"title": "User2 Task"},
            headers=auth_headers_user2
        )
        task_id = create_response.json()["id"]

        # Try to update as user1
        response = client.put(
            f"/api/user2/tasks/{task_id}",
            json={"title": "Hacked"},
            headers=auth_headers_user1
        )

        assert response.status_code == 403

    def test_user_cannot_delete_other_user_task(self, client, auth_headers_user1, auth_headers_user2):
        """Test user1 cannot delete user2's task"""
        # Create task as user2
        create_response = client.post(
            "/api/user2/tasks",
            json={"title": "User2 Task"},
            headers=auth_headers_user2
        )
        task_id = create_response.json()["id"]

        # Try to delete as user1
        response = client.delete(
            f"/api/user2/tasks/{task_id}",
            headers=auth_headers_user1
        )

        assert response.status_code == 403


class TestValidAuthentication:
    """Test successful authentication flows"""

    def test_create_task_with_valid_token(self, client, auth_headers_user1):
        """Test creating task with valid JWT token"""
        response = client.post(
            "/api/user1/tasks",
            json={"title": "Authenticated Task", "description": "Created with valid JWT"},
            headers=auth_headers_user1
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Authenticated Task"
        assert data["user_id"] == "user1"

    def test_list_own_tasks_with_valid_token(self, client, auth_headers_user1, sample_task_user1):
        """Test listing own tasks with valid JWT token"""
        response = client.get(
            "/api/user1/tasks",
            headers=auth_headers_user1
        )

        assert response.status_code == 200
        tasks = response.json()
        assert isinstance(tasks, list)
        assert len(tasks) > 0
        assert all(task["user_id"] == "user1" for task in tasks)

    def test_multiple_users_isolated_data(self, client, auth_headers_user1, auth_headers_user2):
        """Test that two users see only their own tasks"""
        # Create tasks for user1
        client.post(
            "/api/user1/tasks",
            json={"title": "User1 Task 1"},
            headers=auth_headers_user1
        )
        client.post(
            "/api/user1/tasks",
            json={"title": "User1 Task 2"},
            headers=auth_headers_user1
        )

        # Create tasks for user2
        client.post(
            "/api/user2/tasks",
            json={"title": "User2 Task 1"},
            headers=auth_headers_user2
        )

        # Verify user1 sees only their tasks
        response1 = client.get("/api/user1/tasks", headers=auth_headers_user1)
        user1_tasks = response1.json()
        assert all(task["user_id"] == "user1" for task in user1_tasks)
        assert any("User1 Task" in task["title"] for task in user1_tasks)
        assert not any("User2 Task" in task["title"] for task in user1_tasks)

        # Verify user2 sees only their tasks
        response2 = client.get("/api/user2/tasks", headers=auth_headers_user2)
        user2_tasks = response2.json()
        assert all(task["user_id"] == "user2" for task in user2_tasks)
        assert any("User2 Task" in task["title"] for task in user2_tasks)
        assert not any("User1 Task" in task["title"] for task in user2_tasks)
