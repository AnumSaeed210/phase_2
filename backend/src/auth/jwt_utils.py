"""JWT signature verification utilities"""
import os
import jwt
from typing import Optional, Dict, Any
from datetime import datetime


def get_jwt_secret() -> str:
    """
    Get JWT secret from environment variable

    Returns:
        JWT secret string

    Raises:
        ValueError: If BETTER_AUTH_SECRET is not configured or too short
    """
    secret = os.getenv("BETTER_AUTH_SECRET")

    if not secret:
        raise ValueError(
            "BETTER_AUTH_SECRET environment variable is not configured. "
            "This secret is required for JWT signature verification."
        )

    if len(secret) < 32:
        raise ValueError(
            f"BETTER_AUTH_SECRET must be at least 32 characters long. "
            f"Current length: {len(secret)} characters."
        )

    return secret


def verify_jwt_signature(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify JWT signature and extract claims

    Args:
        token: JWT token string (without "Bearer " prefix)

    Returns:
        Dict containing JWT claims if valid, None if invalid

    Security checks:
        - Verifies signature using BETTER_AUTH_SECRET
        - Checks expiration time (exp claim)
        - Validates token structure
    """
    try:
        secret = get_jwt_secret()

        # Decode and verify JWT signature
        # verify_exp=True ensures expiration is checked
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256", "HS512"],  # Support common HMAC algorithms
            options={
                "verify_signature": True,
                "verify_exp": True,
                "require": ["sub"]  # Require user ID in token
            }
        )

        return payload

    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Invalid signature, malformed token, or missing required claims
        return None
    except Exception:
        # Unexpected error (secret not configured, etc.)
        return None


def extract_user_id(claims: Dict[str, Any]) -> Optional[str]:
    """
    Extract user ID from JWT claims

    Args:
        claims: JWT payload dictionary

    Returns:
        User ID string if present, None otherwise

    Note:
        Checks both "sub" (standard JWT claim) and "user_id" (custom claim)
    """
    # Try standard "sub" claim first
    user_id = claims.get("sub")

    # Fallback to custom "user_id" claim
    if not user_id:
        user_id = claims.get("user_id")

    return user_id if user_id else None
