"""Pydantic request and response models"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel
from pydantic import Field, EmailStr, field_validator


class TaskCreate(SQLModel):
    """Request model for POST /api/{user_id}/tasks"""
    title: str = Field(
        min_length=1,
        max_length=255,
        description="Task title (required)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Extended task description (optional)"
    )
    priority: Optional[str] = Field(
        default="medium",
        description="Task priority level: low, medium, or high (optional, defaults to medium)"
    )

    @field_validator('priority', mode='before')
    @classmethod
    def normalize_priority(cls, v):
        if v is None:
            return "medium"
        if isinstance(v, str):
            normalized = v.lower().strip()
            if normalized not in ["low", "medium", "high"]:
                raise ValueError("Priority must be 'low', 'medium', or 'high'")
            return normalized
        raise ValueError("Priority must be a string")


class TaskUpdate(SQLModel):
    """Request model for PUT /api/{user_id}/tasks/{id}"""
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Task title (optional)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Extended task description (optional)"
    )
    priority: Optional[str] = Field(
        default=None,
        description="Task priority level: low, medium, or high (optional)"
    )

    @field_validator('priority', mode='before')
    @classmethod
    def normalize_priority(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            normalized = v.lower().strip()
            if normalized not in ["low", "medium", "high"]:
                raise ValueError("Priority must be 'low', 'medium', or 'high'")
            return normalized
        raise ValueError("Priority must be a string")


class TaskResponse(SQLModel):
    """Response model for all GET/POST/PUT/PATCH endpoints"""
    id: int
    user_id: str
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime


class ErrorResponse(SQLModel):
    """Standard error response for all error cases"""
    error: str


class SignUpRequest(SQLModel):
    """Request model for POST /auth/signup"""
    email: EmailStr = Field(description="User email address (must be unique)")
    password: str = Field(
        min_length=8,
        max_length=72,
        description="Password (8-72 characters for bcrypt compatibility)"
    )
    name: str = Field(
        min_length=1,
        max_length=255,
        description="User display name"
    )


class SignInRequest(SQLModel):
    """Request model for POST /auth/signin"""
    email: EmailStr = Field(description="User email address")
    password: str = Field(description="User password")


class UserResponse(SQLModel):
    """Response model for user data"""
    id: str
    email: str
    name: Optional[str] = None


class AuthTokenResponse(SQLModel):
    """Response model for authentication endpoints"""
    user: UserResponse
    token: str
    token_type: str = "Bearer"
    expires_in: int  # Seconds until token expiration


class SignOutResponse(SQLModel):
    """Response model for POST /auth/signout"""
    message: str
    status: str


class TaskStatusUpdate(SQLModel):
    """Request model for PATCH /api/{user_id}/tasks/{id}/status"""
    status: str = Field(
        description="Task status: 'complete' or 'incomplete'"
    )

    @property
    def is_complete(self) -> bool:
        """Check if status is complete"""
        return self.status.lower() == "complete"
