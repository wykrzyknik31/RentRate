# Database Migration Guide: Adding City Field to Property Table

## Overview

This guide explains how to migrate existing RentRate databases to include the mandatory `city` field in the `property` table.

## What Changed

- The `city` field in the `property` table is now **mandatory** (NOT NULL)
- All new properties must include a city when created
- The frontend form now requires users to enter a city
- Existing properties without a city will be updated to have "Unknown" as default

## Why This Change

The city field was previously optional, which caused issues when fetching reviews:
- Error: `sqlalchemy.exc.ProgrammingError: column property.city does not exist`
- Reviews would fail to load if properties didn't have city information
- The city field is essential for organizing and filtering properties

## Migration for Existing Databases

### Option 1: Using the Migration Script (Recommended)

Run the migration script to automatically add the city column and update existing data:

```bash
# For local development (SQLite)
python backend/migrate_add_city.py

# For Docker (PostgreSQL)
docker compose exec backend python migrate_add_city.py
```

The script will:
1. Check if the `property` table exists
2. Check if the `city` column already exists
3. Add the column if missing (with default value "Unknown")
4. Update any existing properties with NULL city to "Unknown"

### Option 2: Manual Migration

#### For SQLite (Local Development)

```sql
-- Add city column with default value
ALTER TABLE property ADD COLUMN city VARCHAR(100) DEFAULT 'Unknown';

-- Update existing properties
UPDATE property SET city = 'Unknown' WHERE city IS NULL;
```

#### For PostgreSQL (Docker)

```sql
-- Add city column with default value and NOT NULL constraint
ALTER TABLE property ADD COLUMN city VARCHAR(100) DEFAULT 'Unknown' NOT NULL;
```

### Option 3: Fresh Start

If you don't have important data, you can simply delete the existing database:

```bash
# For local development
rm backend/rentrate.db

# For Docker
docker compose down -v
docker compose up -d
```

The database will be recreated automatically with the new schema.

## Verifying the Migration

After running the migration, verify it worked:

```bash
# Run tests to ensure everything works
python -m pytest tests/test_api.py -v

# Check the database schema (SQLite)
sqlite3 backend/rentrate.db ".schema property"

# Check the database schema (PostgreSQL)
docker compose exec db psql -U rentrate -d rentrate -c "\d property"
```

## Impact on API

### Before Migration
```json
{
  "address": "123 Main St",
  "city": null,
  "property_type": "apartment"
}
```

### After Migration
```json
{
  "address": "123 Main St",
  "city": "Unknown",  // or actual city name
  "property_type": "apartment"
}
```

### API Changes

**POST /api/reviews** now requires the `city` field:

```json
{
  "address": "123 Main St",
  "city": "New York",         // ← Now required!
  "property_type": "apartment",
  "rating": 5,
  "review_text": "Great place!"
}
```

Missing the city field will return:
```json
{
  "error": "Missing required field: city"
}
```

## Frontend Changes

The "Add Review" form now requires users to enter a city:
- The city field has a red asterisk (*) indicating it's required
- Form validation prevents submission without a city
- The field is marked as `required` in HTML

## Troubleshooting

### Error: "column property.city does not exist"

This means your database hasn't been migrated yet. Run the migration script:
```bash
python backend/migrate_add_city.py
```

### Error: "NOT NULL constraint failed: property.city"

This means you're trying to create a property without a city. Ensure all API calls include the city field.

### Migration Script Fails

If the migration script fails:
1. Check database connectivity
2. Ensure you have write permissions
3. Backup your database before trying manual migration
4. Check the error message for specific issues

## Rollback (Not Recommended)

If you need to rollback this change:

⚠️ **Warning**: Rolling back will break the API as the code expects the city field.

```sql
-- SQLite: Cannot drop columns in SQLite
-- You would need to recreate the table without city

-- PostgreSQL:
ALTER TABLE property DROP COLUMN city;
```

After rollback, you'll also need to revert the code changes.

## Best Practices

1. **Always backup your database** before running migrations
2. **Test migrations** on a development database first
3. **Update existing data** properly - use meaningful default values
4. **Coordinate with frontend** to ensure forms collect required data
5. **Document breaking changes** for API consumers

## Need Help?

If you encounter issues with the migration:
1. Check the error message carefully
2. Ensure you're using the correct database connection
3. Verify database permissions
4. Review the migration script logs
5. Open an issue on GitHub with details about your setup
