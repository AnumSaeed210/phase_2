# Neon Serverless PostgreSQL Configuration Guide

## Overview

This document provides Neon-specific configuration, optimization strategies, and operational guidance for the Taskie backend.

## Connection Configuration

### Connection String Format

Neon connection strings follow this format:

```
postgresql://user:password@ep-project-id-region.neon.tech/database?sslmode=require
```

**Example:**
```
postgresql://user123:pass456@ep-taskie-123-us-east-2.aws.neon.tech/neondb?sslmode=require
```

### Required Environment Variables

```bash
# Neon PostgreSQL connection (REQUIRED)
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require

# Better Auth secret for JWT validation (REQUIRED)
BETTER_AUTH_SECRET=your-secret-key-here

# Optional: Enable SQL query logging (DEBUG only)
DEBUG=false
```

### Connection String Best Practices

1. **Always use `sslmode=require`** - Neon requires SSL for security
2. **Normalize prefix** - Backend automatically converts `postgres://` to `postgresql://`
3. **Store in environment variables** - Never hardcode connection strings
4. **Use connection pooling** - Backend uses optimized pool settings (see below)

---

## Connection Pooling Strategy

### Neon Architecture

Neon uses **PgBouncer** for connection pooling at the infrastructure level. Your application should:

- Use a **moderate connection pool size** (5-10 connections recommended)
- Enable **connection recycling** to prevent stale connections
- Use **pre-ping** to verify connections before use

### Backend Pool Configuration

The backend uses the following pool settings (configured in `src/database.py`):

```python
NEON_POOL_CONFIG = {
    "pool_size": 10,           # Maximum connections in pool
    "max_overflow": 5,         # Additional connections for burst traffic
    "pool_timeout": 30,        # Wait time for connection acquisition (seconds)
    "pool_recycle": 3600,      # Recycle connections after 1 hour
    "pool_pre_ping": True,     # Test connections before using
}
```

### Why These Settings?

| Setting | Value | Rationale |
|---------|-------|-----------|
| **pool_size** | 10 | Neon's PgBouncer multiplexes connections; 10 is sufficient for most workloads |
| **max_overflow** | 5 | Handles burst traffic without exhausting compute units |
| **pool_timeout** | 30s | Reasonable wait time for serverless workloads |
| **pool_recycle** | 3600s | Prevents stale connections in serverless environment |
| **pool_pre_ping** | True | Handles Neon's compute scaling gracefully |

### Tuning for Your Workload

**Low-traffic applications (< 100 req/min):**
```python
pool_size = 5
max_overflow = 3
```

**Medium-traffic applications (100-1000 req/min):**
```python
pool_size = 10
max_overflow = 5
```

**High-traffic applications (> 1000 req/min):**
```python
pool_size = 15
max_overflow = 10
```

**IMPORTANT:** Monitor Neon compute unit consumption. Higher pool sizes consume more compute units even when idle.

---

## Query Optimization for Neon

### Indexed Queries (Fast)

**Task retrieval by ID:**
```sql
SELECT * FROM tasks WHERE id = 1;
-- Uses primary key index
-- Performance: <50ms
```

**User task listing:**
```sql
SELECT * FROM tasks WHERE user_id = 'user-123' ORDER BY created_at DESC;
-- Uses composite index (user_id, created_at DESC)
-- Performance: <200ms for 100+ tasks
```

**Status filtering:**
```sql
SELECT * FROM tasks WHERE user_id = 'user-123' AND status = 'complete';
-- Uses composite index (user_id, status)
-- Performance: <200ms
```

### Query Anti-Patterns (Slow)

**Avoid:**
```sql
-- No WHERE clause (scans entire table)
SELECT * FROM tasks;

-- LIKE with leading wildcard (cannot use index)
SELECT * FROM tasks WHERE title LIKE '%groceries%';

-- Complex OR conditions (may skip indexes)
SELECT * FROM tasks WHERE user_id = 'user-1' OR user_id = 'user-2';
```

**Instead, use:**
```sql
-- Always filter by user_id
SELECT * FROM tasks WHERE user_id = 'user-123';

-- Exact match or prefix LIKE
SELECT * FROM tasks WHERE title = 'Buy groceries';
SELECT * FROM tasks WHERE title LIKE 'Buy%';

-- Use IN for multiple values
SELECT * FROM tasks WHERE user_id IN ('user-1', 'user-2');
```

---

## Performance Benchmarks

### Expected Response Times (Neon)

| Operation | Query Type | Expected Time | Index Used |
|-----------|-----------|---------------|-----------|
| **Create task** | INSERT | <100ms | Primary key |
| **Get task by ID** | SELECT (pk) | <50ms | Primary key |
| **List user tasks** | SELECT (user + sort) | <200ms | Composite (user_id, created_at DESC) |
| **Update task** | UPDATE (pk) | <150ms | Primary key |
| **Delete task** | DELETE (pk) | <100ms | Primary key |
| **Mark complete** | UPDATE (pk) | <150ms | Primary key |
| **Filter by status** | SELECT (user + status) | <200ms | Composite (user_id, status) |

### Compute Unit Consumption

**Typical usage:**
- Idle connection pool (10 connections): ~0.1 CU/hour
- Single query execution: ~0.001 CU
- 1000 requests/hour: ~1-2 CU/hour (depends on query complexity)

**Optimization tips:**
- Reduce pool_size if idle compute unit usage is high
- Use connection recycling to close unused connections
- Monitor Neon dashboard for compute unit spikes

---

## Database Migrations with Alembic

### Initial Setup

1. **Set DATABASE_URL environment variable:**
```bash
export DATABASE_URL="postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require"
```

2. **Run initial migration:**
```bash
cd backend
alembic upgrade head
```

This creates:
- `tasks` table with schema defined in `alembic/versions/001_initial_schema.py`
- Composite indexes for efficient querying
- Foreign key constraint to `users` table
- Timestamp trigger for `updated_at` auto-update

### Migration Workflow

**Create new migration:**
```bash
alembic revision --autogenerate -m "Add new column to tasks"
```

**Apply migration:**
```bash
alembic upgrade head
```

**Rollback migration:**
```bash
alembic downgrade -1
```

**Check current version:**
```bash
alembic current
```

### Migration Best Practices

1. **Always test migrations on staging first** - Use Neon branches for safe testing
2. **Use transactional DDL** - Most PostgreSQL DDL is transactional (auto-rollback on error)
3. **Avoid breaking changes** - Use backward-compatible migrations (add columns, not remove)
4. **Keep migrations idempotent** - Safe to run multiple times
5. **Backup before production migrations** - Neon provides point-in-time recovery

---

## Monitoring and Observability

### Connection Pool Health

Monitor pool status via FastAPI endpoint:

```python
from src.database import get_pool_status

@app.get("/health/pool")
def pool_health():
    return get_pool_status()
```

**Example response:**
```json
{
  "size": 10,
  "checked_in": 8,
  "checked_out": 2,
  "overflow": 0,
  "total": 10
}
```

**Interpretation:**
- `checked_in`: Available connections in pool
- `checked_out`: Connections currently in use
- `overflow`: Connections beyond pool_size (should be 0 most of the time)
- `total`: Total active connections

**Warning signs:**
- `overflow > 0` consistently: Increase pool_size
- `checked_out == pool_size + max_overflow`: Connection pool exhausted (increase limits or investigate connection leaks)
- `checked_in == 0`: All connections in use (may need scaling)

### Query Performance Monitoring

**Enable query logging (development only):**
```bash
export DEBUG=true
```

This logs all SQL queries to console. **Disable in production** for performance.

**Neon Dashboard Metrics:**
- Go to Neon Console → Project → Monitoring
- Monitor:
  - **Compute units consumed** (should be <5 CU/hour for low-traffic apps)
  - **Active connections** (should be ≤ pool_size + max_overflow)
  - **Query duration** (avg should be <200ms)
  - **Database size** (monitor growth over time)

### Alert Thresholds

Set up alerts for:
- **Compute units > 10 CU/hour** (investigate inefficient queries)
- **Active connections > pool_size + max_overflow** (connection leak or traffic spike)
- **Query duration > 1 second** (slow queries, needs optimization)
- **Database size > 1 GB** (consider archiving old tasks)

---

## Backup and Disaster Recovery

### Neon Backup Strategy

**Automatic backups:**
- Neon provides **point-in-time recovery (PITR)** for up to 7 days (Free tier) or 30 days (Pro tier)
- No manual backup configuration needed
- Recovery granularity: 1 second

**Manual backups (pg_dump):**
```bash
pg_dump $DATABASE_URL > backup.sql
```

**Restore from backup:**
```bash
psql $DATABASE_URL < backup.sql
```

### Disaster Recovery Plan

**Scenario 1: Accidental data deletion**
1. Use Neon PITR to restore to before deletion
2. Neon Console → Project → Branches → Restore from history
3. Select timestamp before deletion
4. Verify data integrity

**Scenario 2: Schema migration failure**
1. Alembic migrations are transactional (auto-rollback on error)
2. If manual intervention needed: `alembic downgrade -1`
3. Fix migration script and re-run

**Scenario 3: Complete database corruption**
1. Create new Neon project
2. Restore from latest pg_dump backup
3. Run migrations: `alembic upgrade head`
4. Update DATABASE_URL in application
5. Restart backend

---

## Scaling Strategies

### Vertical Scaling (Compute Units)

**Neon scales compute automatically** based on workload. No manual configuration needed.

**To optimize compute usage:**
- Reduce connection pool size (lower idle consumption)
- Optimize queries (reduce query duration)
- Use indexes for all user-scoped queries
- Enable connection recycling (close stale connections)

### Horizontal Scaling (Read Replicas)

**Neon supports read replicas** for read-heavy workloads.

**Setup:**
1. Neon Console → Project → Read Replicas → Create
2. Get read replica connection string
3. Update backend to route read queries to replica

**Example:**
```python
# Write queries (master)
engine_write = create_engine(os.getenv("DATABASE_URL"))

# Read queries (replica)
engine_read = create_engine(os.getenv("DATABASE_READ_URL"))
```

**When to use read replicas:**
- Read:write ratio > 10:1
- Task listing queries causing compute unit spikes
- Need to separate analytics queries from transactional workload

### Connection Pooling at Scale

**For > 1000 req/min:**
- Increase pool_size to 15-20
- Monitor Neon active connections (should not exceed Neon limits)
- Consider external connection pooler (PgBouncer) if needed

**For > 10,000 req/min:**
- Use external connection pooler (PgBouncer)
- Route read queries to read replicas
- Consider database sharding by user_id (advanced)

---

## Security Best Practices

### Connection Security

1. **Always use SSL** (`sslmode=require` in connection string)
2. **Rotate credentials regularly** (Neon Console → Project → Settings → Reset Password)
3. **Use environment variables** (never commit DATABASE_URL to Git)
4. **Restrict database access** (Neon Console → Project → Settings → IP Allowlist)

### Application-Level Security

1. **Enforce user ownership** (all queries filtered by user_id)
2. **Use parameterized queries** (SQLModel/SQLAlchemy prevents SQL injection)
3. **Validate all input** (Pydantic request models)
4. **Return 404 for unauthorized access** (don't leak information via 403)

### Database User Permissions

**Production database user should have:**
- `SELECT`, `INSERT`, `UPDATE`, `DELETE` on `tasks` table
- `SELECT` on `users` table (read-only for task ownership checks)
- **NO** `DROP`, `CREATE`, `ALTER` permissions (migrations run with admin user)

---

## Troubleshooting

### Issue: Connection timeout

**Symptom:** `psycopg2.OperationalError: connection timeout`

**Causes:**
- Neon compute scaled to zero (cold start delay)
- Network issues
- Incorrect connection string

**Solutions:**
1. Enable pre-ping: `pool_pre_ping=True` (already enabled)
2. Increase connect_timeout: `connect_args={"connect_timeout": 30}`
3. Verify connection string format (must include `sslmode=require`)

### Issue: Connection pool exhausted

**Symptom:** `TimeoutError: QueuePool limit exceeded`

**Causes:**
- Traffic spike exceeds pool capacity
- Connection leak (sessions not closed)
- pool_size too low

**Solutions:**
1. Increase pool_size and max_overflow (monitor compute units)
2. Check for connection leaks: `get_pool_status()` should show `checked_in > 0`
3. Use FastAPI dependency injection (`Depends(get_session)`) to auto-close sessions

### Issue: Slow queries

**Symptom:** Queries taking >1 second

**Causes:**
- Missing indexes
- Full table scans
- Inefficient queries

**Solutions:**
1. Check query plan: `EXPLAIN ANALYZE <query>`
2. Verify indexes exist: `\d tasks` in psql
3. Ensure queries filter by user_id (uses composite index)
4. Avoid LIKE with leading wildcard (`LIKE '%term%'`)

### Issue: High compute unit consumption

**Symptom:** Neon dashboard shows >10 CU/hour

**Causes:**
- Connection pool too large
- Inefficient queries
- Too many connections idle

**Solutions:**
1. Reduce pool_size (e.g., 10 → 5)
2. Enable connection recycling (pool_recycle=3600)
3. Monitor query duration (optimize slow queries)
4. Use read replicas for read-heavy workloads

---

## Additional Resources

- [Neon Documentation](https://neon.tech/docs)
- [PostgreSQL Performance Tuning](https://www.postgresql.org/docs/current/performance-tips.html)
- [SQLAlchemy Connection Pooling](https://docs.sqlalchemy.org/en/20/core/pooling.html)
- [Alembic Migrations](https://alembic.sqlalchemy.org/en/latest/)
