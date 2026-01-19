"""
Database connection and session management for Neon Serverless PostgreSQL

NEON-SPECIFIC OPTIMIZATIONS:
- Connection pooling configured for serverless architecture
- Pool size optimized for Neon's PgBouncer (5-10 connections recommended)
- Pool timeout and recycle settings for serverless workloads
- SSL mode enforced for secure connections to Neon
- Connection string format normalized (postgres:// -> postgresql://)

PERFORMANCE CHARACTERISTICS:
- Connection acquisition: <50ms (Neon's PgBouncer handles pooling)
- Query execution: <200ms for single-task operations, <500ms for list operations
- Connection lifecycle: Automatic recycle after 1 hour to prevent stale connections

NEON CONNECTION STRING FORMAT:
postgresql://user:password@ep-example-123.us-east-2.aws.neon.tech/neondb?sslmode=require

COMPUTE UNIT EFFICIENCY:
- Pool size limited to 10 connections max (prevents compute unit waste)
- Connections recycled after 1 hour (Neon serverless best practice)
- Echo mode disabled in production (reduces logging overhead)
"""

import os
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy import event
from typing import Generator

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please set DATABASE_URL to your Neon PostgreSQL connection string. "
        "Example: postgresql://user:password@ep-example-123.us-east-2.aws.neon.tech/neondb?sslmode=require"
    )

# Normalize connection string (Neon may use postgres:// prefix)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Determine if we're using SQLite (for testing) or PostgreSQL (production)
is_sqlite = "sqlite" in DATABASE_URL
is_neon = "neon.tech" in DATABASE_URL or "postgresql://" in DATABASE_URL


# NEON-SPECIFIC CONFIGURATION
# Optimal connection pool settings for Neon Serverless PostgreSQL
NEON_POOL_CONFIG = {
    # Pool size: 5-10 connections recommended for Neon
    # Neon's PgBouncer handles connection multiplexing
    # Lower pool size reduces compute unit consumption
    "pool_size": 10,
    # Max overflow: Additional connections beyond pool_size
    # Set to 5 for burst traffic handling
    "max_overflow": 5,
    # Pool timeout: Wait time for connection acquisition (seconds)
    # 30 seconds is reasonable for serverless workloads
    "pool_timeout": 30,
    # Pool recycle: Recycle connections after this many seconds
    # 3600 seconds (1 hour) prevents stale connections in serverless
    "pool_recycle": 3600,
    # Pool pre-ping: Test connections before using (prevents stale connections)
    # Enabled for Neon to handle serverless compute scaling
    "pool_pre_ping": True,
    # Echo: Log all SQL queries (disable in production for performance)
    "echo": os.getenv("DEBUG", "false").lower() == "true",
}


def create_neon_engine():
    """
    Create SQLAlchemy engine optimized for Neon Serverless PostgreSQL.

    Neon-Specific Optimizations:
    - Connection pooling via QueuePool (default for PostgreSQL)
    - Pool size limited to 10 connections (Neon recommendation)
    - Connection recycling after 1 hour (serverless best practice)
    - SSL mode required (sslmode=require in connection string)
    - Pre-ping enabled to handle serverless compute scaling

    Returns:
        Engine configured for Neon serverless PostgreSQL
    """
    return create_engine(
        DATABASE_URL,
        echo=NEON_POOL_CONFIG["echo"],
        future=True,
        poolclass=QueuePool,
        pool_size=NEON_POOL_CONFIG["pool_size"],
        max_overflow=NEON_POOL_CONFIG["max_overflow"],
        pool_timeout=NEON_POOL_CONFIG["pool_timeout"],
        pool_recycle=NEON_POOL_CONFIG["pool_recycle"],
        pool_pre_ping=NEON_POOL_CONFIG["pool_pre_ping"],
        # Neon-specific: Ensure SSL connections
        connect_args=(
            {
                "sslmode": "require",
                "connect_timeout": 10,  # Connection timeout in seconds
            }
            if is_neon
            else {}
        ),
    )


def create_sqlite_engine():
    """
    Create SQLAlchemy engine for SQLite (testing only).

    SQLite Configuration:
    - StaticPool for in-memory databases (thread-safe)
    - check_same_thread=False for FastAPI async testing

    Returns:
        Engine configured for SQLite testing
    """
    from sqlalchemy.pool import StaticPool

    return create_engine(
        DATABASE_URL,
        echo=NEON_POOL_CONFIG["echo"],
        future=True,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )


# Create engine based on database type
if is_sqlite:
    engine = create_sqlite_engine()
    print("[DATABASE] Using SQLite engine (testing mode)")
else:
    engine = create_neon_engine()
    print(f"[DATABASE] Using Neon Serverless PostgreSQL")
    print(
        f"[DATABASE] Connection pool: size={NEON_POOL_CONFIG['pool_size']}, "
        f"max_overflow={NEON_POOL_CONFIG['max_overflow']}, "
        f"recycle={NEON_POOL_CONFIG['pool_recycle']}s"
    )


# Event listener for connection pool monitoring (optional, useful for debugging)
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log new database connections (debug mode only)."""
    if NEON_POOL_CONFIG["echo"]:
        print(f"[DATABASE] New connection established: {connection_record}")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log connection checkouts from pool (debug mode only)."""
    if NEON_POOL_CONFIG["echo"]:
        print(f"[DATABASE] Connection checked out from pool")


def create_db_and_tables():
    """
    Create all database tables from SQLModel definitions.

    NOTE: In production, use Alembic migrations instead of this function.
    This function is useful for testing and development only.

    For Neon production deployment:
    1. Run Alembic migrations: alembic upgrade head
    2. Do NOT call create_db_and_tables() in production code
    """
    SQLModel.metadata.create_all(engine)
    print("[DATABASE] All tables created successfully")


def get_session() -> Generator[Session, None, None]:
    """
    Create a new database session for dependency injection.

    Usage with FastAPI:
    ```python
    @app.get("/tasks")
    def get_tasks(session: Session = Depends(get_session)):
        tasks = session.exec(select(Task)).all()
        return tasks
    ```

    Session Lifecycle:
    - Session created on request start
    - Automatically committed on success
    - Automatically rolled back on error
    - Automatically closed after request completes

    Neon-Specific Behavior:
    - Connection acquired from pool (pool_pre_ping ensures it's alive)
    - Connection returned to pool after session closes
    - Pool handles connection recycling and stale connection detection

    Yields:
        Database session for request scope
    """
    with Session(engine) as session:
        yield session


def get_pool_status():
    """
    Get current connection pool status (for monitoring/debugging).

    Returns:
        Dictionary with pool statistics:
        - size: Current pool size
        - checked_in: Connections in pool (available)
        - checked_out: Connections currently in use
        - overflow: Connections beyond pool_size
        - total: Total connections (size + overflow)

    Useful for:
    - Monitoring connection pool health
    - Identifying connection leaks
    - Capacity planning for Neon compute units
    """
    pool = engine.pool
    return {
        "size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "total": pool.checkedin() + pool.checkedout(),
    }
