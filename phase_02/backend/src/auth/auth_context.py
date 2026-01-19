"""Authenticated user context extracted from JWT"""
from pydantic import BaseModel
from typing import Optional, Dict, Any


class AuthenticatedUser(BaseModel):
    """
    Authenticated user context extracted from JWT claims

    Attributes:
        user_id: Unique user identifier from JWT "sub" or "user_id" claim
        email: User email if present in JWT claims
        claims: Full JWT payload for extensibility
    """
    user_id: str
    email: Optional[str] = None
    claims: Dict[str, Any] = {}

    @classmethod
    def from_jwt_claims(cls, claims: Dict[str, Any]) -> "AuthenticatedUser":
        """
        Create AuthenticatedUser from JWT claims

        Args:
            claims: JWT payload dictionary

        Returns:
            AuthenticatedUser instance

        Raises:
            ValueError: If user_id cannot be extracted
        """
        # Extract user ID from "sub" or "user_id" claim
        user_id = claims.get("sub") or claims.get("user_id")

        if not user_id:
            raise ValueError("JWT claims missing required 'sub' or 'user_id' field")

        # Extract optional email
        email = claims.get("email")

        return cls(
            user_id=str(user_id),
            email=email,
            claims=claims
        )
