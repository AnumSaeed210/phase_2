"""FastAPI application entry point"""
import os
import sys
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables BEFORE importing src modules
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from datetime import datetime

from src.database import create_db_and_tables, engine
# Import actual models, not SQLModel
from src.models import User, Task

print("[MAIN] Importing tasks router...")
from src.api.tasks import router as tasks_router
print(f"[MAIN] Tasks router imported. Routes: {[r.path for r in tasks_router.routes]}")

print("[MAIN] Importing auth router...")
from src.api.auth import router as auth_router
print(f"[MAIN] Auth router imported. Routes: {[r.path for r in auth_router.routes]}")


def validate_environment():
    """Validate required environment variables on startup"""
    try:
        # Validate DATABASE_URL
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not configured")
        print("[OK] DATABASE_URL configured")

        # Validate BETTER_AUTH_SECRET (T039-T040)
        auth_secret = os.getenv("BETTER_AUTH_SECRET")
        if not auth_secret:
            raise ValueError(
                "BETTER_AUTH_SECRET environment variable is not configured. "
                "This secret is required for JWT signature verification."
            )
        if len(auth_secret) < 32:
            raise ValueError(
                f"BETTER_AUTH_SECRET must be at least 32 characters long for security. "
                f"Current length: {len(auth_secret)} characters."
            )
        print(f"[OK] BETTER_AUTH_SECRET configured ({len(auth_secret)} characters)")

    except ValueError as e:
        print(f"\n[ERROR] STARTUP VALIDATION FAILED: {str(e)}\n")
        print("Required environment variables:")
        print("  - DATABASE_URL (PostgreSQL connection string)")
        print("  - BETTER_AUTH_SECRET (JWT signing secret, minimum 32 characters)")
        sys.exit(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Startup: Validate environment
    validate_environment()

    # Startup: Create database tables
    create_db_and_tables()
    print("Database tables created successfully")

    yield
    # Shutdown: Close database connections
    # SQLModel/SQLAlchemy handles this automatically


# Create FastAPI application
print("[MAIN] Creating FastAPI app...")
app = FastAPI(
    title="Todo Backend API",
    description="Backend API for multi-user todo task management",
    version="1.0.0",
    lifespan=lifespan
)
print("[MAIN] FastAPI app created")

# Configure CORS
# SECURITY: Restrict to specific origins instead of wildcard
# In production, set to actual frontend domain(s)
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003,http://localhost:3004,http://localhost:3005,http://localhost:3006,http://localhost:3007,http://localhost:3008,http://localhost:3009,http://localhost:3010").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # Restrict to specific origins
    allow_credentials=True,  # Required for HttpOnly cookie transmission
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],  # Explicit methods
    allow_headers=["Content-Type", "Authorization"],  # Explicit headers
)


# Include routers
print(f"[MAIN] Including auth_router with {len(auth_router.routes)} routes...")
app.include_router(auth_router)

print(f"[MAIN] Including tasks_router with {len(tasks_router.routes)} routes...")
app.include_router(tasks_router)

print(f"[MAIN] All app routes: {sorted([r.path for r in app.routes if hasattr(r, 'path')])}")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Todo Backend API",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )



# """FastAPI application entry point"""
# import os
# import sys
# from contextlib import asynccontextmanager
# from dotenv import load_dotenv

# # Load environment variables BEFORE importing src modules
# load_dotenv()

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from sqlmodel import SQLModel
# from src.database import create_db_and_tables, engine
# from src.models import User, Task  # <-- import your actual models, not SQLModel

# print("[MAIN] Importing tasks router...")
# from src.api.tasks import router as tasks_router
# print(f"[MAIN] Tasks router imported. Routes: {[r.path for r in tasks_router.routes]}")

# print("[MAIN] Importing auth router...")
# from src.api.auth import router as auth_router
# print(f"[MAIN] Auth router imported. Routes: {[r.path for r in auth_router.routes]}")


# def validate_environment():
#     """Validate required environment variables on startup"""
#     try:
#         # Validate DATABASE_URL
#         database_url = os.getenv("DATABASE_URL")
#         if not database_url:
#             raise ValueError("DATABASE_URL environment variable is not configured")
#         print("[OK] DATABASE_URL configured")

#         # Validate BETTER_AUTH_SECRET (T039-T040)
#         auth_secret = os.getenv("BETTER_AUTH_SECRET")
#         if not auth_secret:
#             raise ValueError(
#                 "BETTER_AUTH_SECRET environment variable is not configured. "
#                 "This secret is required for JWT signature verification."
#             )
#         if len(auth_secret) < 32:
#             raise ValueError(
#                 f"BETTER_AUTH_SECRET must be at least 32 characters long for security. "
#                 f"Current length: {len(auth_secret)} characters."
#             )
#         print(f"[OK] BETTER_AUTH_SECRET configured ({len(auth_secret)} characters)")

#     except ValueError as e:
#         print(f"\n[ERROR] STARTUP VALIDATION FAILED: {str(e)}\n")
#         sys.exit(1)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Application lifecycle management"""
#     # Startup: Validate environment
#     validate_environment()

#     # Startup: Create database tables
#     SQLModel.metadata.create_all(engine)
#     print("[MAIN] Database tables created successfully")

#     yield
#     # Shutdown: SQLModel/SQLAlchemy handles connections automatically


# # Create FastAPI application
# print("[MAIN] Creating FastAPI app...")
# app = FastAPI(
#     title="Todo Backend API",
#     description="Backend API for multi-user todo task management",
#     version="1.0.0",
#     lifespan=lifespan
# )
# print("[MAIN] FastAPI app created")

# # Configure CORS
# cors_origins = os.getenv(
#     "CORS_ORIGINS",
#     "http://localhost:3000"
# ).split(",")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=cors_origins,
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
#     allow_headers=["Content-Type", "Authorization"],
# )

# # Include routers
# app.include_router(auth_router)
# app.include_router(tasks_router)

# print(f"[MAIN] All app routes: {sorted([r.path for r in app.routes if hasattr(r, 'path')])}")


# @app.get("/health")
# def health_check():
#     """Health check endpoint"""
#     return {"status": "healthy"}


# @app.get("/")
# def root():
#     """Root endpoint"""
#     return {
#         "message": "Todo Backend API",
#         "docs": "/docs",
#         "openapi": "/openapi.json"
#     }


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True
#     )
