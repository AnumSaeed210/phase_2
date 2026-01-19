"""Custom error handlers for authentication errors"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException


async def unauthorized_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Custom handler for 401 Unauthorized errors

    Returns consistent error response format:
    {
        "error": "Unauthorized",
        "message": "Detailed error message"
    }
    """
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": "Unauthorized",
            "message": exc.detail.get("message", "Authentication required") if isinstance(exc.detail, dict) else str(exc.detail)
        }
    )


async def forbidden_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Custom handler for 403 Forbidden errors

    Returns consistent error response format:
    {
        "error": "Forbidden",
        "message": "Detailed error message"
    }
    """
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error": "Forbidden",
            "message": exc.detail.get("message", "Access denied") if isinstance(exc.detail, dict) else str(exc.detail)
        }
    )
