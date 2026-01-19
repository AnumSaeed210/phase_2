"""Tests for JWT validation utilities"""
import os
import pytest
import jwt
from datetime import datetime, timedelta
from src.auth.jwt_utils import verify_jwt_signature, extract_user_id, get_jwt_secret
from src.auth.auth_context import AuthenticatedUser


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


class TestJWTUtils:
    """Test JWT utility functions"""

    def test_get_jwt_secret_success(self):
        """Test successful retrieval of JWT secret"""
        secret = get_jwt_secret()
        assert secret is not None
        assert len(secret) >= 32

    def test_verify_valid_jwt(self):
        """Test verification of valid JWT token"""
        token = create_test_jwt("user123")
        claims = verify_jwt_signature(token)

        assert claims is not None
        assert claims["sub"] == "user123"
        assert claims["email"] == "test@example.com"

    def test_verify_expired_jwt(self):
        """Test verification rejects expired JWT"""
        token = create_test_jwt("user123", exp_minutes=-5)  # Expired 5 minutes ago
        claims = verify_jwt_signature(token)

        assert claims is None

    def test_verify_invalid_signature(self):
        """Test verification rejects JWT with invalid signature"""
        # Create token with wrong secret
        wrong_secret = "wrong-secret-key-at-least-32-chars-long"
        payload = {
            "sub": "user123",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, wrong_secret, algorithm="HS256")

        claims = verify_jwt_signature(token)
        assert claims is None

    def test_verify_malformed_jwt(self):
        """Test verification rejects malformed JWT"""
        claims = verify_jwt_signature("not.a.valid.jwt.token")
        assert claims is None

    def test_extract_user_id_from_sub(self):
        """Test user ID extraction from 'sub' claim"""
        claims = {"sub": "user123", "email": "test@example.com"}
        user_id = extract_user_id(claims)
        assert user_id == "user123"

    def test_extract_user_id_from_user_id_claim(self):
        """Test user ID extraction from 'user_id' claim"""
        claims = {"user_id": "user456", "email": "test@example.com"}
        user_id = extract_user_id(claims)
        assert user_id == "user456"

    def test_extract_user_id_missing(self):
        """Test user ID extraction returns None when missing"""
        claims = {"email": "test@example.com"}
        user_id = extract_user_id(claims)
        assert user_id is None


class TestAuthenticatedUser:
    """Test AuthenticatedUser model"""

    def test_from_jwt_claims_with_sub(self):
        """Test creating AuthenticatedUser from claims with 'sub'"""
        claims = {
            "sub": "user123",
            "email": "test@example.com",
            "exp": 1234567890
        }
        user = AuthenticatedUser.from_jwt_claims(claims)

        assert user.user_id == "user123"
        assert user.email == "test@example.com"
        assert user.claims == claims

    def test_from_jwt_claims_with_user_id(self):
        """Test creating AuthenticatedUser from claims with 'user_id'"""
        claims = {
            "user_id": "user456",
            "email": "user456@example.com"
        }
        user = AuthenticatedUser.from_jwt_claims(claims)

        assert user.user_id == "user456"
        assert user.email == "user456@example.com"

    def test_from_jwt_claims_missing_user_id(self):
        """Test creating AuthenticatedUser fails without user ID"""
        claims = {"email": "test@example.com"}

        with pytest.raises(ValueError, match="missing required 'sub' or 'user_id'"):
            AuthenticatedUser.from_jwt_claims(claims)

    def test_from_jwt_claims_without_email(self):
        """Test creating AuthenticatedUser without email"""
        claims = {"sub": "user789"}
        user = AuthenticatedUser.from_jwt_claims(claims)

        assert user.user_id == "user789"
        assert user.email is None
