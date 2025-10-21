# Docker Setup Verification

This document describes the Docker setup for the RentRate project and how to verify it works.

## What Was Added

### 1. Backend Dockerfile (`/backend/Dockerfile`)
- Base image: `python:3.11-slim`
- Installs Flask dependencies from `requirements.txt`
- Installs `psycopg2-binary` for PostgreSQL support
- Installs `curl` for healthchecks
- Exposes port 5000
- Runs Flask with `flask run --host=0.0.0.0 --port=5000`
- Includes healthcheck endpoint at `/api/health`

### 2. Frontend Dockerfile (`/frontend/Dockerfile`)
- Base image: `node:18-alpine`
- Installs npm dependencies
- Exposes port 3000
- Runs Next.js dev server with `npm run dev`

### 3. Docker Compose (`/docker-compose.yml`)
Defines three services:

#### Database (db)
- Image: `postgres:15-alpine`
- Environment: POSTGRES_USER=rentrate, POSTGRES_PASSWORD=rentrate, POSTGRES_DB=rentrate
- Port: 5432
- Volume: `postgres_data` for data persistence
- Healthcheck: `pg_isready` command

#### Backend (backend)
- Builds from `./backend/Dockerfile`
- Connected to PostgreSQL via environment variables
- Port: 5000
- Depends on: db (with healthcheck)
- Volume mounted for hot-reload

#### Frontend (frontend)
- Builds from `./frontend/Dockerfile`
- Port: 3000
- Depends on: backend
- Volume mounted for hot-reload

### 4. Backend Database Configuration
Updated `backend/app.py` to support both PostgreSQL (Docker) and SQLite (local):
- If `DB_HOST` environment variable is set → uses PostgreSQL
- Otherwise → uses SQLite (for local development)

### 5. .dockerignore Files
Created for both backend and frontend to exclude:
- `node_modules/`, `.venv/`
- `__pycache__/`, `*.pyc`
- `.env` files
- Build artifacts
- IDE files

### 6. Makefile
Convenient commands:
- `make build` - Build images
- `make up` - Start services
- `make up-build` - Build and start
- `make down` - Stop services
- `make logs` - View logs
- `make clean` - Remove all containers and volumes
- And more...

### 7. Updated README.md
Added comprehensive Docker usage instructions including:
- Quick start guide
- Docker commands reference
- Architecture overview

## How to Test

### Prerequisites
- Docker Desktop or Docker Engine + Docker Compose installed

### Step 1: Build the Images
```bash
cd /path/to/RentRate
docker compose build
```

Expected output:
- Backend image builds successfully with Python dependencies
- Frontend image builds successfully with npm packages
- Both images tagged as `rentrate-backend` and `rentrate-frontend`

### Step 2: Start the Services
```bash
docker compose up
```

Or in detached mode:
```bash
docker compose up -d
```

Expected behavior:
1. PostgreSQL starts first and becomes healthy
2. Backend starts after DB is healthy
3. Frontend starts after backend is up

### Step 3: Verify Services

#### Check all containers are running:
```bash
docker compose ps
```

Expected output: All three services (db, backend, frontend) should be "Up"

#### Test Backend API:
```bash
curl http://localhost:5000/
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "ok",
  "message": "RentRate API is running",
  "version": "1.0.0",
  ...
}
```

#### Test Frontend:
Open browser to: http://localhost:3000

Expected: Next.js application loads successfully

#### Test Database Connection:
```bash
docker compose exec backend flask shell
```

Then in the Flask shell:
```python
from app import db
db.engine.execute('SELECT 1')
```

Expected: Connection successful

### Step 4: Test Data Persistence

1. Create some data via the API:
```bash
curl -X POST http://localhost:5000/api/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "address": "123 Test St",
    "property_type": "apartment",
    "rating": 5,
    "review_text": "Great place!"
  }'
```

2. Stop containers:
```bash
docker compose down
```

3. Start again:
```bash
docker compose up -d
```

4. Check data still exists:
```bash
curl http://localhost:5000/api/reviews
```

Expected: The review created in step 1 should still be there

### Step 5: Test Hot Reload

With containers running:

1. Edit a file (e.g., change a message in `backend/app.py`)
2. Save the file
3. Check the logs:
```bash
docker compose logs -f backend
```

Expected: Backend detects the change and reloads

### Troubleshooting

#### Issue: Backend can't connect to database
**Solution**: Check that DB_HOST environment variable is set correctly in docker-compose.yml

#### Issue: Port already in use
**Solution**: Stop any local services running on ports 3000, 5000, or 5432

#### Issue: Containers won't start
**Solution**: Check logs with `docker compose logs` or `docker compose logs <service-name>`

#### Issue: Build fails with SSL errors
**Solution**: The backend Dockerfile includes `--trusted-host` flags to handle SSL certificate issues

#### Issue: Frontend build is slow
**Solution**: This is normal. npm install can take several minutes on first build. Subsequent builds use cache and are faster.

### Clean Up

To stop and remove all containers:
```bash
docker compose down
```

To also remove volumes (deletes database data):
```bash
docker compose down -v
```

Or use the Makefile:
```bash
make clean
```

## Architecture Diagram

```
┌─────────────────┐
│   Frontend      │ :3000
│   (Next.js)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Backend       │ :5000
│   (Flask)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Database      │ :5432
│   (PostgreSQL)  │
└─────────────────┘
```

All services communicate through the `rentrate-network` Docker network.

## Success Criteria ✓

- [x] Backend Dockerfile created with Python 3.11-slim
- [x] Frontend Dockerfile created with Node 18-alpine
- [x] docker-compose.yml defines all three services
- [x] PostgreSQL configured with environment variables
- [x] All ports mapped correctly (3000, 5000, 5432)
- [x] Volume for PostgreSQL data persistence
- [x] Healthchecks for backend and database
- [x] .dockerignore files exclude unnecessary files
- [x] Makefile with convenience commands
- [x] README.md updated with Docker instructions
- [x] Backend supports both PostgreSQL (Docker) and SQLite (local)

## Notes

- The setup uses development mode with hot-reload enabled
- For production, consider:
  - Multi-stage builds for smaller images
  - Running Next.js in production mode
  - Using production WSGI server (e.g., gunicorn) for Flask
  - Securing environment variables
  - Using Docker secrets for sensitive data
  - Adding nginx as reverse proxy
