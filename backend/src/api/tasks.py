"""Task API endpoints - CRUD operations for todo tasks"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from src.database import get_session
from src.models import Task
from src.schemas import TaskCreate, TaskUpdate, TaskResponse, ErrorResponse
from src.services import TaskService
from src.auth.jwt_deps import verify_path_user_id
from src.auth.auth_context import AuthenticatedUser

router = APIRouter(prefix="/api", tags=["Tasks"])


def get_task_service(session: Session = Depends(get_session)) -> TaskService:
    """Dependency to get TaskService instance"""
    return TaskService(session)


# ============================================================================
# User Story 1: Create a Task (POST)
# ============================================================================

@router.post(
    "/{user_id}/tasks",
    status_code=201,
    response_model=TaskResponse,
    responses={
        201: {"description": "Task created successfully"},
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"}
    }
)
def create_task(
    user_id: str,
    task_create: TaskCreate,
    service: TaskService = Depends(get_task_service),
    current_user: AuthenticatedUser = Depends(verify_path_user_id)
) -> TaskResponse:
    """
    Create a new task for authenticated user

    - **user_id**: Authenticated user ID from JWT context
    - **title**: Task title (required, 1-255 characters)
    - **description**: Task description (optional, max 5000 characters)
    - **priority**: Task priority (optional, defaults to "medium"; low|medium|high)

    Returns 201 Created with complete task metadata including auto-generated ID and timestamps.
    """
    # Validate title
    if not task_create.title or not task_create.title.strip():
        raise HTTPException(
            status_code=400,
            detail={"error": "Title is required"}
        )

    if len(task_create.title) > 255:
        raise HTTPException(
            status_code=400,
            detail={"error": "Title must be 255 characters or less"}
        )

    # Validate description
    if task_create.description and len(task_create.description) > 5000:
        raise HTTPException(
            status_code=400,
            detail={"error": "Description must be 5000 characters or less"}
        )

    # Create task (priority validation already done by schema)
    task = service.create_task(
        user_id=user_id,
        title=task_create.title,
        description=task_create.description,
        priority=task_create.priority
    )

    return TaskResponse.model_validate(task)


# ============================================================================
# User Story 2: List All Tasks (GET)
# ============================================================================

@router.get(
    "/{user_id}/tasks",
    status_code=200,
    response_model=List[TaskResponse],
    responses={
        200: {"description": "Array of tasks (may be empty)"},
        400: {"model": ErrorResponse, "description": "Invalid status parameter"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"}
    }
)
def list_tasks(
    user_id: str,
    status: Optional[str] = Query(None, description="Filter by status (incomplete|complete)"),
    sort: Optional[str] = Query(None, description="Sort option (priority for priority sorting)"),
    service: TaskService = Depends(get_task_service),
    current_user: AuthenticatedUser = Depends(verify_path_user_id)
) -> List[TaskResponse]:
    """
    List all tasks for authenticated user

    - **user_id**: Authenticated user ID from JWT context
    - **status**: Optional filter (incomplete or complete)
    - **sort**: Optional sort parameter (priority for High→Medium→Low ordering)

    Returns array of tasks owned by the user, filtered by optional status parameter.
    Returns empty array [] if user has no tasks.
    """
    # Validate status parameter
    if status and status not in ["incomplete", "complete"]:
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid status value. Must be 'incomplete' or 'complete'"}
        )

    # Validate sort parameter
    if sort and sort not in ["priority"]:
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid sort value. Must be 'priority' or omitted"}
        )

    tasks = service.get_tasks_for_user(user_id, status, sort)
    return [TaskResponse.model_validate(task) for task in tasks]


# ============================================================================
# User Story 3: Get Single Task (GET)
# ============================================================================

@router.get(
    "/{user_id}/tasks/{id}",
    status_code=200,
    response_model=TaskResponse,
    responses={
        200: {"description": "Task retrieved successfully"},
        400: {"model": ErrorResponse, "description": "Invalid task ID"},
        404: {"model": ErrorResponse, "description": "Task not found or not owned"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"}
    }
)
def get_task(
    user_id: str,
    id: int,
    service: TaskService = Depends(get_task_service),
    current_user: AuthenticatedUser = Depends(verify_path_user_id)
) -> TaskResponse:
    """
    Retrieve a single task by ID

    - **user_id**: Authenticated user ID from JWT context
    - **id**: Task ID (numeric)

    Returns task details if task exists and is owned by authenticated user.
    Returns 404 if task doesn't exist or belongs to different user (same error message for security).
    """
    # Validate task ID is numeric (already done by FastAPI path parameter type)
    try:
        task_id = int(id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid task ID"}
        )

    task = service.get_task_by_id(task_id, user_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail={"error": "Task not found"}
        )

    return TaskResponse.model_validate(task)


# ============================================================================
# User Story 4: Update Task (PUT)
# ============================================================================

@router.put(
    "/{user_id}/tasks/{id}",
    status_code=200,
    response_model=TaskResponse,
    responses={
        200: {"description": "Task updated successfully"},
        400: {"model": ErrorResponse, "description": "Validation error"},
        404: {"model": ErrorResponse, "description": "Task not found or not owned"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"}
    }
)
def update_task(
    user_id: str,
    id: int,
    task_update: TaskUpdate,
    service: TaskService = Depends(get_task_service),
    current_user: AuthenticatedUser = Depends(verify_path_user_id)
) -> TaskResponse:
    """
    Update a task's title, description, and/or priority

    - **user_id**: Authenticated user ID from JWT context
    - **id**: Task ID (numeric)
    - **title**: New title (optional, 1-255 characters)
    - **description**: New description (optional, max 5000 characters)
    - **priority**: New priority (optional; low|medium|high)

    At least one field must be provided.
    Returns updated task with new updated_at timestamp.
    Returns 404 if task doesn't exist or belongs to different user.
    """
    # Validate task ID
    try:
        task_id = int(id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid task ID"}
        )

    # Validate at least one field provided
    if task_update.title is None and task_update.description is None and task_update.priority is None:
        raise HTTPException(
            status_code=400,
            detail={"error": "At least one field (title, description, or priority) must be provided"}
        )

    # Validate title if provided
    if task_update.title is not None:
        if not task_update.title or not task_update.title.strip():
            raise HTTPException(
                status_code=400,
                detail={"error": "Title cannot be empty"}
            )
        if len(task_update.title) > 255:
            raise HTTPException(
                status_code=400,
                detail={"error": "Title must be 255 characters or less"}
            )

    # Validate description if provided
    if task_update.description and len(task_update.description) > 5000:
        raise HTTPException(
            status_code=400,
            detail={"error": "Description must be 5000 characters or less"}
        )

    # Update task (priority validation already done by schema)
    task = service.update_task(
        task_id=task_id,
        user_id=user_id,
        title=task_update.title,
        description=task_update.description,
        priority=task_update.priority
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail={"error": "Task not found"}
        )

    return TaskResponse.model_validate(task)


# ============================================================================
# User Story 5: Delete Task (DELETE)
# ============================================================================

@router.delete(
    "/{user_id}/tasks/{id}",
    status_code=204,
    responses={
        204: {"description": "Task deleted successfully"},
        400: {"model": ErrorResponse, "description": "Invalid task ID"},
        404: {"model": ErrorResponse, "description": "Task not found or not owned"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"}
    }
)
def delete_task(
    user_id: str,
    id: int,
    service: TaskService = Depends(get_task_service),
    current_user: AuthenticatedUser = Depends(verify_path_user_id)
) -> None:
    """
    Delete a task

    - **user_id**: Authenticated user ID from JWT context
    - **id**: Task ID (numeric)

    Permanently removes task from database.
    Returns 204 No Content on success (empty response body).
    Returns 404 if task doesn't exist or belongs to different user.
    """
    # Validate task ID
    try:
        task_id = int(id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid task ID"}
        )

    # Delete task
    deleted = service.delete_task(task_id, user_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail={"error": "Task not found"}
        )

    # Return 204 No Content (implicit via status_code)


# ============================================================================
# User Story 6: Mark Task Complete (PATCH)
# ============================================================================

@router.patch(
    "/{user_id}/tasks/{id}/complete",
    status_code=200,
    response_model=TaskResponse,
    responses={
        200: {"description": "Task marked as complete"},
        400: {"model": ErrorResponse, "description": "Invalid task ID"},
        404: {"model": ErrorResponse, "description": "Task not found or not owned"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"}
    }
)
def mark_complete(
    user_id: str,
    id: int,
    service: TaskService = Depends(get_task_service),
    current_user: AuthenticatedUser = Depends(verify_path_user_id)
) -> TaskResponse:
    """
    Mark a task as complete

    - **user_id**: Authenticated user ID from JWT context
    - **id**: Task ID (numeric)

    Changes task status to "complete" and updates the updated_at timestamp.
    Operation is idempotent - safe to call multiple times on same task.
    Returns updated task with status = "complete".
    Returns 404 if task doesn't exist or belongs to different user.
    """
    # Validate task ID
    try:
        task_id = int(id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid task ID"}
        )

    # Mark task complete
    task = service.mark_complete(task_id, user_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail={"error": "Task not found"}
        )

    return TaskResponse.model_validate(task)
