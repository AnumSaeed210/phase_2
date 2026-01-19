"""Authentication API endpoints - signup, signin, signout"""
import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash
from pydantic import EmailStr

from src.database import get_session
from src.models import User
from src.schemas import (
    SignUpRequest,
    SignInRequest,
    AuthTokenResponse,
    SignOutResponse,
    UserResponse,
    ErrorResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Password hasher using Argon2
pwd_hasher = PasswordHasher()

# JWT token expiration: 7 days in seconds
TOKEN_EXPIRATION_SECONDS = 604800  # 7 days


def get_jwt_secret() -> str:
    """
    Get JWT secret from environment variable

    Returns:
        JWT secret string

    Raises:
        ValueError: If BETTER_AUTH_SECRET is not configured
    """
    secret = os.getenv("BETTER_AUTH_SECRET")

    if not secret:
        raise ValueError(
            "BETTER_AUTH_SECRET environment variable is not configured. "
            "This secret is required for JWT token generation."
        )

    if len(secret) < 32:
        raise ValueError(
            f"BETTER_AUTH_SECRET must be at least 32 characters long. "
            f"Current length: {len(secret)} characters."
        )

    return secret


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2

    Args:
        password: Plaintext password

    Returns:
        Argon2 hash of the password

    Security:
        - Uses Argon2 algorithm for strong, modern password hashing
        - Automatically handles salt generation
        - Supports passwords up to 4096 characters
    """
    return pwd_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against an Argon2 hash

    Args:
        plain_password: User-provided password
        hashed_password: Argon2 hash from database

    Returns:
        True if password matches hash, False otherwise
    """
    try:
        pwd_hasher.verify(hashed_password, plain_password)
        return True
    except (VerifyMismatchError, InvalidHash):
        return False


def create_jwt_token(user_id: str, email: str) -> tuple[str, int]:
    """
    Create a JWT token for authenticated user

    Args:
        user_id: User ID (from UUID)
        email: User email address

    Returns:
        Tuple of (token, expires_in_seconds)

    Token Claims:
        - sub: User ID (standard JWT claim for subject/user ID)
        - email: User email
        - iat: Issued at time (unix timestamp)
        - exp: Expiration time (unix timestamp, 7 days from now)

    Algorithm:
        - HS256 (HMAC with SHA-256)
        - Uses BETTER_AUTH_SECRET from environment
    """
    secret = get_jwt_secret()

    # Calculate expiration time (7 days from now)
    now = datetime.now(timezone.utc)
    expiration = now + timedelta(seconds=TOKEN_EXPIRATION_SECONDS)

    # Create JWT payload
    payload = {
        "sub": user_id,  # Standard JWT claim: subject (user ID)
        "email": email,
        "iat": int(now.timestamp()),  # Issued at
        "exp": int(expiration.timestamp()),  # Expiration
    }

    # Encode JWT token
    token = jwt.encode(
        payload,
        secret,
        algorithm="HS256",
    )

    return token, TOKEN_EXPIRATION_SECONDS


# ============================================================================
# Authentication Endpoints
# ============================================================================


@router.post(
    "/signup",
    status_code=201,
    response_model=AuthTokenResponse,
    responses={
        201: {"description": "User created successfully"},
        409: {"model": ErrorResponse, "description": "Email already exists"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
def signup(
    request: SignUpRequest,
    session: Session = Depends(get_session),
) -> AuthTokenResponse:
    """
    Create a new user account and return JWT token

    Request Body:
        - email: User email (must be unique)
        - password: Password (8-4096 characters)
        - name: Display name (1-255 characters)

    Response:
        - user: User object with id, email, name
        - token: JWT token for authentication
        - token_type: "Bearer"
        - expires_in: Token expiration in seconds (604800 = 7 days)

    Error Cases:
        - 409 Conflict: Email already exists
        - 422 Unprocessable Entity: Validation error
    """
    # Validate password length (Argon2 supports 8-4096 characters)
    # EmailStr validation is handled by Pydantic automatically
    if len(request.password) < 8 or len(request.password) > 4096:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "Validation Error",
                "message": "Password must be between 8 and 4096 characters",
            },
        )

    # Check if email already exists
    statement = select(User).where(User.email == request.email.lower())
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "Conflict",
                "message": "Email already registered",
            },
        )

    # Create new user
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=request.email.lower(),
        password_hash=hash_password(request.password),
        name=request.name,
    )

    # Save user to database
    session.add(user)
    session.commit()
    session.refresh(user)

    # Generate JWT token
    token, expires_in = create_jwt_token(user.id, user.email)

    return AuthTokenResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
        ),
        token=token,
        token_type="Bearer",
        expires_in=expires_in,
    )


@router.post(
    "/signin",
    status_code=200,
    response_model=AuthTokenResponse,
    responses={
        200: {"description": "Sign in successful"},
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
def signin(
    request: SignInRequest,
    session: Session = Depends(get_session),
) -> AuthTokenResponse:
    """
    Authenticate user and return JWT token

    Request Body:
        - email: User email
        - password: User password

    Response:
        - user: User object with id, email, name
        - token: JWT token for authentication
        - token_type: "Bearer"
        - expires_in: Token expiration in seconds (604800 = 7 days)

    Error Cases:
        - 401 Unauthorized: Invalid email or password
        - 422 Unprocessable Entity: Validation error
    """
    # Look up user by email (case-insensitive)
    statement = select(User).where(User.email == request.email.lower())
    user = session.exec(statement).first()

    # Check if user exists and password is correct
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Unauthorized",
                "message": "Invalid email or password",
            },
        )

    # Generate JWT token
    token, expires_in = create_jwt_token(user.id, user.email)

    return AuthTokenResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
        ),
        token=token,
        token_type="Bearer",
        expires_in=expires_in,
    )


@router.post(
    "/signout",
    status_code=200,
    response_model=SignOutResponse,
    responses={
        200: {"description": "Sign out successful"},
    },
)
def signout() -> SignOutResponse:
    """
    Sign out user (stateless, JWT is invalidated by frontend)

    This is a simple endpoint that returns success. Since JWT tokens are
    stateless and don't require server-side session management, signout
    is handled on the frontend by deleting the token.

    Response:
        - message: "Signed out successfully"
        - status: "success"
    """
    return SignOutResponse(
        message="Signed out successfully",
        status="success",
    )
