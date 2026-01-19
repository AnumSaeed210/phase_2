"""Manual test script for JWT authentication system"""
import os
import jwt
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Configuration
BASE_URL = "http://localhost:8000"
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")


def create_jwt_token(user_id: str, email: str = "test@example.com") -> str:
    """Create a test JWT token"""
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, BETTER_AUTH_SECRET, algorithm="HS256")


def test_auth_system():
    """Test the authentication system"""

    print("=" * 60)
    print("JWT Authentication System Tests")
    print("=" * 60)

    # Test 1: Health check (no auth required)
    print("\n[TEST 1] Health check (no auth)...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✓ PASSED")

    # Test 2: List tasks without auth (should fail)
    print("\n[TEST 2] List tasks without authentication...")
    response = requests.get(f"{BASE_URL}/api/user1/tasks")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 401
    print("✓ PASSED - Correctly rejected")

    # Test 3: Create valid JWT token for user1
    print("\n[TEST 3] Create valid JWT token for user1...")
    token_user1 = create_jwt_token("user1", "user1@example.com")
    print(f"Token: {token_user1[:50]}...")
    print("✓ Token created")

    # Test 4: List tasks with valid token
    print("\n[TEST 4] List tasks with valid token...")
    headers = {"Authorization": f"Bearer {token_user1}"}
    response = requests.get(f"{BASE_URL}/api/user1/tasks", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✓ PASSED")

    # Test 5: Create task with valid token
    print("\n[TEST 5] Create task with valid token...")
    response = requests.post(
        f"{BASE_URL}/api/user1/tasks",
        headers=headers,
        json={"title": "Test Task from Manual Test", "description": "Testing JWT auth"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 201
    task_id = response.json()["id"]
    print(f"✓ PASSED - Task created with ID: {task_id}")

    # Test 6: User isolation - user1 tries to access user2's endpoint
    print("\n[TEST 6] User isolation - user1 tries to access user2's tasks...")
    response = requests.get(f"{BASE_URL}/api/user2/tasks", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 403
    print("✓ PASSED - Correctly rejected with 403 Forbidden")

    # Test 7: Create user2 token and verify isolation
    print("\n[TEST 7] Create user2 token and verify data isolation...")
    token_user2 = create_jwt_token("user2", "user2@example.com")
    headers_user2 = {"Authorization": f"Bearer {token_user2}"}

    # Create task as user2
    response = requests.post(
        f"{BASE_URL}/api/user2/tasks",
        headers=headers_user2,
        json={"title": "User2 Task", "description": "Only visible to user2"}
    )
    print(f"Create task as user2 - Status: {response.status_code}")
    assert response.status_code == 201

    # List user1 tasks - should NOT see user2's task
    response = requests.get(f"{BASE_URL}/api/user1/tasks", headers=headers)
    user1_tasks = response.json()
    print(f"User1 tasks count: {len(user1_tasks)}")
    assert not any(task["title"] == "User2 Task" for task in user1_tasks)

    # List user2 tasks - should see only user2's task
    response = requests.get(f"{BASE_URL}/api/user2/tasks", headers=headers_user2)
    user2_tasks = response.json()
    print(f"User2 tasks count: {len(user2_tasks)}")
    assert any(task["title"] == "User2 Task" for task in user2_tasks)
    print("✓ PASSED - Data isolation verified")

    # Test 8: Invalid token
    print("\n[TEST 8] Invalid token...")
    headers_invalid = {"Authorization": "Bearer invalid.token.here"}
    response = requests.get(f"{BASE_URL}/api/user1/tasks", headers=headers_invalid)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 401
    print("✓ PASSED - Invalid token rejected")

    # Test 9: Expired token
    print("\n[TEST 9] Expired token...")
    expired_payload = {
        "sub": "user1",
        "email": "user1@example.com",
        "exp": datetime.utcnow() - timedelta(hours=1),  # Expired
        "iat": datetime.utcnow() - timedelta(hours=2)
    }
    expired_token = jwt.encode(expired_payload, BETTER_AUTH_SECRET, algorithm="HS256")
    headers_expired = {"Authorization": f"Bearer {expired_token}"}
    response = requests.get(f"{BASE_URL}/api/user1/tasks", headers=headers_expired)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 401
    print("✓ PASSED - Expired token rejected")

    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_auth_system()
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to backend. Is it running on port 8000?")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
