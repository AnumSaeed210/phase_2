"""Pytest configuration and fixtures for testing"""
import os
from typing import Generator
from unittest.mock import patch
from datetime import datetime, timedelta

import pytest
import jwt
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool

# Load environment variables first
load_dotenv()

from src.database import get_session
from src.models import Task, User


# Create test database URL (SQLite in-memory for speed)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(name="engine")
def engine_fixture():
    """Create test database engine with in-memory SQLite"""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    """Create test database session"""
    with Session(engine) as session:
        yield session


def create_test_jwt_token(user_id: str, email: str = "test@example.com", exp_minutes: int = 60) -> str:
    """Helper to create valid test JWT tokens"""
    secret = os.getenv("BETTER_AUTH_SECRET")
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=exp_minutes),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, secret, algorithm="HS256")


@pytest.fixture(name="test_secret")
def test_secret_fixture():
    """Provide test JWT secret for token generation"""
    # Use environment secret or fixed test secret
    return os.getenv("BETTER_AUTH_SECRET", "test_secret_minimum_32_characters_longggg")


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session) -> User:
    """Create a test user in database"""
    user = User(
        id="test-user-123",
        email="testuser@example.com",
        password_hash="hashed_password_here",
        name="Test User"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="test_token")
def test_token_fixture() -> str:
    """Create a valid test JWT token for test_user"""
    return create_test_jwt_token(user_id="test-user-123", email="testuser@example.com")


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """Create test client with dependency override"""
    from main import app

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
