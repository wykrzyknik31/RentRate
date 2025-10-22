# Automatic Database Migration on Startup

## Overview

The RentRate backend now automatically runs database migrations when the Docker container starts. This ensures that existing databases are updated with the latest schema changes without manual intervention.

## How It Works

When you start the RentRate backend (either via Docker or manually), the following process occurs:

1. **Startup Script Executes** (`backend/startup.sh`)
   - Runs before the Flask application starts
   - Executes database migration scripts
   - Validates migration success

2. **Migration Script Runs** (`backend/migrate_add_city.py`)
   - Checks if the property table exists
   - Checks if the city column exists
   - Adds the city column if missing
   - Updates existing properties with default value "Unknown"

3. **Flask Application Starts**
   - Only after successful migration
   - Ready to handle API requests with correct schema

## What Gets Migrated

### City Column Addition

The migration ensures the `property` table has a mandatory `city` column:

**Before Migration:**
```sql
CREATE TABLE property (
    id INTEGER PRIMARY KEY,
    address VARCHAR(200) NOT NULL,
    property_type VARCHAR(50) NOT NULL,
    created_at DATETIME
);
```

**After Migration:**
```sql
CREATE TABLE property (
    id INTEGER PRIMARY KEY,
    address VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,  -- ← New column
    property_type VARCHAR(50) NOT NULL,
    created_at DATETIME
);
```

### Data Preservation

Existing properties without a city value are automatically updated:
- Default value: `"Unknown"`
- No data loss
- All existing reviews remain intact

## Using with Docker

### First-Time Setup

```bash
# Clone the repository
git clone https://github.com/wykrzyknik31/RentRate.git
cd RentRate

# Start with Docker Compose
docker compose up -d
```

The migration runs automatically when the backend container starts.

### Upgrading from Previous Version

If you're upgrading from an older version without the city column:

```bash
# Pull latest changes
git pull

# Rebuild and restart containers
docker compose down
docker compose build
docker compose up -d
```

The migration will automatically detect the missing city column and add it during startup.

### Checking Migration Status

View the backend logs to verify migration success:

```bash
docker compose logs backend | grep -A 5 "migration"
```

Expected output:
```
Starting RentRate backend...
Running database migration...
Connecting to database: db:5432/rentrate
Migration completed successfully
Starting Flask application...
```

## Using Without Docker (Local Development)

### Manual Migration

If running locally without Docker:

```bash
# Navigate to backend directory
cd backend

# Run migration manually
python migrate_add_city.py

# Start the application
python app.py
```

### Automatic Migration

The startup script also works for local development:

```bash
cd backend
./startup.sh
```

## Troubleshooting

### Migration Fails to Run

**Symptom:** Backend starts but city column is missing

**Solution:**
```bash
# Check backend logs
docker compose logs backend

# If needed, run migration manually
docker compose exec backend python migrate_add_city.py
```

### Database Connection Issues

**Symptom:** "Could not connect to database" error

**Solution:**
1. Ensure PostgreSQL container is running:
   ```bash
   docker compose ps
   ```

2. Check database health:
   ```bash
   docker compose exec db pg_isready -U rentrate
   ```

3. Restart containers if needed:
   ```bash
   docker compose restart
   ```

### Permission Errors

**Symptom:** "Permission denied" when running startup.sh

**Solution:**
```bash
# Make script executable
chmod +x backend/startup.sh

# Rebuild Docker image
docker compose build backend
```

## Migration Script Details

### What It Does

The `migrate_add_city.py` script:
- ✅ Detects database type (SQLite or PostgreSQL)
- ✅ Checks if property table exists
- ✅ Checks if city column exists
- ✅ Adds column with appropriate SQL for each database type
- ✅ Updates NULL values to "Unknown"
- ✅ Logs all operations without exposing credentials
- ✅ Handles errors gracefully

### Database Support

- **PostgreSQL** (Docker/Production): Adds column with `NOT NULL` constraint
- **SQLite** (Local Development): Adds column, then updates NULL values

### Safety Features

- **Idempotent**: Can be run multiple times safely
- **Non-destructive**: Never deletes or modifies existing data
- **Logged**: All operations are logged for audit
- **Secure**: Database credentials are redacted from logs

## Testing the Migration

### Verify City Column Exists

**PostgreSQL (Docker):**
```bash
docker compose exec db psql -U rentrate -d rentrate -c "\d property"
```

**SQLite (Local):**
```bash
sqlite3 backend/rentrate.db ".schema property"
```

### Verify API Works

Test the /api/reviews endpoint:

```bash
# Create a review with city
curl -X POST http://localhost:5000/api/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "address": "123 Test St",
    "city": "New York",
    "property_type": "apartment",
    "rating": 5
  }'

# Should return 201 Created with property including city
```

```bash
# Try without city (should fail)
curl -X POST http://localhost:5000/api/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "address": "456 No City St",
    "property_type": "house",
    "rating": 4
  }'

# Should return 400 Bad Request: "Missing required field: city"
```

```bash
# Get all reviews
curl http://localhost:5000/api/reviews

# Should return 200 OK with reviews including city in property object
```

## Rollback (Emergency Only)

⚠️ **Warning**: Rolling back is not recommended as it will break the API.

If absolutely necessary:

```bash
# Stop containers
docker compose down

# Remove volumes (⚠️ DELETES ALL DATA)
docker compose down -v

# Check out previous version
git checkout <previous-commit>

# Rebuild
docker compose build
docker compose up -d
```

## Best Practices

1. **Always backup before upgrading**
   ```bash
   docker compose exec db pg_dump -U rentrate rentrate > backup.sql
   ```

2. **Test in development first**
   - Never upgrade production directly
   - Test migration in staging environment
   - Verify all endpoints work correctly

3. **Monitor logs during deployment**
   ```bash
   docker compose logs -f backend
   ```

4. **Keep migration scripts**
   - Don't delete old migration files
   - They may be needed for troubleshooting

## Additional Resources

- [City Field Migration Guide](./CITY_FIELD_MIGRATION.md) - Detailed migration information
- [City Field Implementation Summary](./CITY_FIELD_IMPLEMENTATION_SUMMARY.md) - Complete implementation details
- [API Documentation](../README.md) - Full API reference

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review backend logs: `docker compose logs backend`
3. Check database connectivity: `docker compose exec db pg_isready`
4. Open a GitHub issue with:
   - Error messages from logs
   - Your setup (Docker/local, PostgreSQL/SQLite)
   - Steps to reproduce the issue
