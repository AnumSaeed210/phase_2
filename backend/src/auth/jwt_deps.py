"""FastAPI dependency injection for JWT authentication"""
from typing import Optional
from fastapi import Header, HTTPException, Depends
from src.auth.jwt_utils import verify_jwt_signature
from src.auth.auth_context import AuthenticatedUser


def get_current_user(authorization: Optional[str] = Header(None)) -> AuthenticatedUser:
    """
    FastAPI dependency to extract and validate JWT from Authorization header

    Args:
        authorization: Authorization header value (automatically injected by FastAPI)

    Returns:
        AuthenticatedUser instance with user context

    Raises:
        HTTPException 401: If JWT is missing, invalid, or expired

    Usage in route:
        @router.get("/endpoint")
        def protected_endpoint(current_user: AuthenticatedUser = Depends(get_current_user)):
            # Access current_user.user_id
            pass
    """
    # Check if Authorization header present
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Unauthorized",
                "message": "Authorization header is required"
            }
        )

    # Extract Bearer token
    parts = authorization.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Unauthorized",
                "message": "Authorization header must be in format: Bearer <token>"
            }
        )

    token = parts[1]

    # Verify JWT signature and extract claims
    claims = verify_jwt_signature(token)

    if not claims:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Unauthorized",
                "message": "Invalid or expired JWT token"
            }
        )

    # Create authenticated user context
    try:
        user = AuthenticatedUser.from_jwt_claims(claims)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Unauthorized",
                "message": f"Invalid JWT claims: {str(e)}"
            }
        )


def verify_path_user_id(
    user_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> AuthenticatedUser:
    """
    FastAPI dependency to verify JWT user_id matches route {user_id} parameter

    Args:
        user_id: User ID from route path parameter
        current_user: Authenticated user from JWT (injected)

    Returns:
        AuthenticatedUser instance if user_id matches

    Raises:
        HTTPException 403: If JWT user_id doesn't match route user_id

    Security:
        Prevents users from accessing other users' resources by manipulating URL

    Usage in route:
        @router.get("/{user_id}/tasks")
        def list_tasks(
            user_id: str,
            current_user: AuthenticatedUser = Depends(verify_path_user_id)
        ):
            # user_id is guaranteed to match JWT user_id
            pass
    """
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Forbidden",
                "message": "You are not authorized to access this user's resources"
            }
        )

    return current_user
