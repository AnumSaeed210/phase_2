# Taskie Backend - Quick Start Guide

## 5-Minute Setup

### Step 1: Get Neon Database (2 minutes)

1. Go to [neon.tech](https://neon.tech) and sign up (free tier available)
2. Create a new project named "taskie"
3. Copy your connection string from the dashboard

**Connection string format:**
```
postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### Step 2: Configure Environment (30 seconds)

Create a `.env` file in `backend/` directory:

```bash
DATABASE_URL=<your-neon-connection-string>
BETTER_AUTH_SECRET=my-secret-key-123
```

### Step 3: Install Dependencies (1 minute)

```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Run Migrations (30 seconds)

```bash
alembic upgrade head
```

This creates the `tasks` table with optimized indexes.

### Step 5: Start Backend (10 seconds)

```bash
uvicorn main:app --reload
```

**Backend is now running at:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

---

## Test Your Setup

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response: `{"status": "healthy"}`

### Create a Task

```bash
curl -X POST http://localhost:8000/api/user-123/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "This is a test"}'
```

Expected response:
```json
{
  "id": 1,
  "user_id": "user-123",
  "title": "Test task",
  "description": "This is a test",
  "status": "incomplete",
  "created_at": "2025-01-09T12:34:56Z",
  "updated_at": "2025-01-09T12:34:56Z"
}
```

### List Tasks

```bash
curl http://localhost:8000/api/user-123/tasks
```

Expected response: Array of tasks

---

## What's Configured?

### Database Optimizations

- ✅ **Connection pooling** optimized for Neon (10 connections, 5 overflow)
- ✅ **SSL enforced** for secure connections
- ✅ **Connection recycling** after 1 hour (prevents stale connections)
- ✅ **Pre-ping enabled** to handle serverless compute scaling

### Database Schema

- ✅ **Tasks table** with SERIAL primary key
- ✅ **Composite index** (user_id, created_at DESC) for fast listing
- ✅ **Status index** (user_id, status) for filtering
- ✅ **Automatic timestamps** via PostgreSQL trigger
- ✅ **Foreign key** to users table (CASCADE delete)

### Performance Targets

| Operation | Expected Time |
|-----------|---------------|
| Create task | <100ms |
| Get task by ID | <50ms |
| List user tasks | <200ms |
| Update task | <150ms |
| Delete task | <100ms |

---

## Next Steps

### Development

1. **Read the API documentation** at http://localhost:8000/docs
2. **Test all endpoints** using Swagger UI
3. **Monitor connection pool** at http://localhost:8000/health/pool

### Deployment

1. **Set environment variables** on your hosting platform
2. **Run migrations** in production: `alembic upgrade head`
3. **Use Gunicorn** for production server:
   ```bash
   gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
   ```

### Monitoring

1. **Neon Dashboard** - Monitor compute units and active connections
2. **Connection pool status** - `GET /health/pool`
3. **Query logging** - Set `DEBUG=true` (development only)

---

## Troubleshooting

### Error: `DATABASE_URL environment variable is not set`

**Solution:** Create `.env` file with DATABASE_URL (see Step 2)

### Error: `connection timeout`

**Solution:** Verify connection string includes `sslmode=require`

### Error: `alembic: command not found`

**Solution:** Ensure you installed dependencies: `pip install -r requirements.txt`

---

## Additional Resources

- **README.md** - Complete setup and usage guide
- **NEON_CONFIGURATION.md** - Detailed Neon optimization guide
- **DATABASE_IMPLEMENTATION_SUMMARY.md** - Technical implementation details
- **Neon Documentation** - https://neon.tech/docs
- **FastAPI Documentation** - https://fastapi.tiangolo.com

---

## Support

For issues or questions:
1. Check **NEON_CONFIGURATION.md** troubleshooting section
2. Review **README.md** for detailed documentation
3. Consult **Neon Dashboard** for database metrics
