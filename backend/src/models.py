"""SQLModel definitions for Task and User entities"""
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """User model - represents a user"""
    __tablename__ = "users"

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str = Field(max_length=255)
    name: Optional[str] = Field(default=None, max_length=255)


class Task(SQLModel, table=True):
    """Task model - represents a single to-do item owned by a user"""
    __tablename__ = "tasks"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign Key
    user_id: str = Field(foreign_key="users.id", index=True)

    # Content
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=5000)

    # State
    status: str = Field(default="incomplete")  # Enum: incomplete | complete
    priority: str = Field(default="medium")  # Enum: low | medium | high

    # Timestamps (UTC)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
