# Database Migration Guide

This guide explains how to work with database migrations in the RentRate project using Flask-Migrate (Alembic).

## Table of Contents

- [Overview](#overview)
- [Why Migrations?](#why-migrations)
- [Quick Start](#quick-start)
- [Common Tasks](#common-tasks)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

## Overview

RentRate uses **Flask-Migrate** (built on Alembic) for database schema management. This ensures that database schemas are:

- ✅ **Version controlled** alongside your code
- ✅ **Consistent** across all environments (local, Docker, production)
- ✅ **Reversible** - easy to rollback if needed
- ✅ **Documented** - every change has a migration file with description

## Why Migrations?

### Before (Manual Scripts) ❌

```python
# Manual script that could fail silently
cursor.execute("ALTER TABLE review ADD COLUMN user_id INTEGER")
# What if this column already exists?
# What if another developer ran a different script?
# How do we track what was applied where?
```

### After (Flask-Migrate) ✅

```bash
# Generate migration from model changes
flask db migrate -m "Add user_id to review"

# Review the generated migration
# Apply it safely
flask db upgrade

# Everyone gets the same schema!
```

## Quick Start

### For New Developers

When you clone the repository:

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Apply all migrations (creates database if needed)
export FLASK_APP=app.py
flask db upgrade

# Start the app
python app.py
```

Or simply use the clean start script:

```bash
./start_clean.sh  # Linux/Mac
start_clean.bat   # Windows
```

### For Docker Users

Migrations run automatically:

```bash
docker compose up --build
```

The `startup.sh` script automatically runs `flask db upgrade` before starting the Flask app.

## Common Tasks

### 1. Applying Migrations

Apply all pending migrations to bring your database up to date:

```bash
cd backend
export FLASK_APP=app.py
flask db upgrade
```

Or use the helper script:

```bash
./migrate.sh upgrade
```

### 2. Creating a New Migration

When you modify database models in `app.py`:

**Step 1: Update the Model**

```python
# In backend/app.py
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)
    # Add new field:
    neighborhood = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Step 2: Generate Migration**

```bash
export FLASK_APP=app.py
flask db migrate -m "Add neighborhood to Property model"
```

Or:

```bash
./migrate.sh migrate "Add neighborhood to Property model"
```

**Step 3: Review the Migration**

Check the generated file in `migrations/versions/`:

```python
def upgrade():
    op.add_column('property', sa.Column('neighborhood', sa.String(length=100), nullable=True))

def downgrade():
    op.drop_column('property', 'neighborhood')
```

**Step 4: Apply the Migration**

```bash
flask db upgrade
```

**Step 5: Commit the Migration**

```bash
git add migrations/versions/
git commit -m "Add neighborhood field to Property model"
git push
```

### 3. Checking Migration Status

See which migrations have been applied:

```bash
flask db current    # Show current revision
flask db history    # Show all migrations
```

### 4. Rolling Back a Migration

If you need to undo the last migration:

```bash
flask db downgrade
```

**⚠️ Warning:** Only do this in development. In production, create a new migration instead.

### 5. Viewing Migration History

```bash
flask db history
```

Output:
```
001_initial_schema (head)
└── <base>
```

## Best Practices

### DO ✅

1. **Always review generated migrations** before applying them
2. **Test migrations in development first** before production
3. **Write descriptive migration messages** 
   - Good: `"Add user_id foreign key to review with CASCADE delete"`
   - Bad: `"update db"`
4. **Keep migrations focused** - one logical change per migration
5. **Commit migration files** to version control
6. **Run migrations before deploying** new code
7. **Back up production data** before running migrations

### DON'T ❌

1. **Don't modify applied migrations** - create a new one instead
2. **Don't skip migrations** - apply them in order
3. **Don't delete migration files** from version control
4. **Don't run raw SQL** unless absolutely necessary
5. **Don't forget to test `downgrade()`** functions
6. **Don't commit migration files without reviewing** them

## Troubleshooting

### Issue: "Can't locate revision identified by 'xxxxx'"

**Cause:** Your database migration version doesn't match the migration files.

**Solution:**

1. Backup your data
2. Check current version: `flask db current`
3. If completely out of sync, reset:
   ```bash
   # Backup data first!
   rm backend/rentrate.db  # or drop PostgreSQL database
   flask db upgrade        # Apply all migrations fresh
   # Restore data if needed
   ```

### Issue: "Target database is not up to date"

**Cause:** You have pending migrations that haven't been applied.

**Solution:**

```bash
flask db upgrade
```

### Issue: Migration fails with data integrity error

**Cause:** The migration conflicts with existing data.

**Example:** Adding a NOT NULL column to a table with existing rows.

**Solution:** Modify the migration to handle existing data:

```python
def upgrade():
    # First add column as nullable
    op.add_column('property', sa.Column('neighborhood', sa.String(length=100), nullable=True))
    
    # Set default value for existing rows
    op.execute("UPDATE property SET neighborhood = 'Unknown' WHERE neighborhood IS NULL")
    
    # Then make it NOT NULL if needed
    # op.alter_column('property', 'neighborhood', nullable=False)

def downgrade():
    op.drop_column('property', 'neighborhood')
```

### Issue: "ImportError: cannot import name 'Migrate'"

**Cause:** Flask-Migrate is not installed.

**Solution:**

```bash
pip install Flask-Migrate
```

### Issue: Changes not detected by `flask db migrate`

**Cause:** Model changes might not be detectable by Alembic autogenerate.

**Solution:**

1. Ensure models are imported in `app.py`
2. For complex changes, write the migration manually
3. Check Alembic documentation for limitations of autogenerate

## Examples

### Example 1: Adding a New Column

**Model Change:**

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80))
    password_hash = db.Column(db.String(255), nullable=False)
    # NEW: Add phone number
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Generate and Apply:**

```bash
flask db migrate -m "Add phone number to User model"
flask db upgrade
```

### Example 2: Adding a Foreign Key

**Model Change:**

```python
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    review = db.relationship('Review', backref='comments')
    user = db.relationship('User', backref='comments')
```

**Generate and Apply:**

```bash
flask db migrate -m "Add Comment model with foreign keys"
flask db upgrade
```

### Example 3: Adding an Index

**Model Change:**

```python
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add index for faster queries
    __table_args__ = (
        db.Index('idx_property_rating', 'property_id', 'rating'),
    )
```

**Generate and Apply:**

```bash
flask db migrate -m "Add index on property_id and rating"
flask db upgrade
```

### Example 4: Renaming a Column

**This requires a custom migration:**

```bash
flask db revision -m "Rename reviewer_name to author_name"
```

**Edit the generated migration:**

```python
def upgrade():
    op.alter_column('review', 'reviewer_name', new_column_name='author_name')

def downgrade():
    op.alter_column('review', 'author_name', new_column_name='reviewer_name')
```

**Apply:**

```bash
flask db upgrade
```

## Migration Workflow for Teams

### When Starting Work

```bash
# Pull latest code
git pull

# Apply any new migrations
cd backend
flask db upgrade
```

### When Making Schema Changes

```bash
# 1. Update models in app.py
# 2. Generate migration
flask db migrate -m "Descriptive message"

# 3. Review the migration file
cat migrations/versions/[latest_file].py

# 4. Test the migration
flask db upgrade
# Test your application

# 5. Commit and push
git add migrations/versions/
git commit -m "Add migration: Descriptive message"
git push
```

### When Deploying

```bash
# In production:
git pull
cd backend
flask db upgrade
# Restart application
```

## Advanced Topics

### Custom Migrations

Sometimes you need to write custom migrations:

```bash
flask db revision -m "Custom data transformation"
```

Edit the file:

```python
def upgrade():
    # Custom SQL or Python code
    connection = op.get_bind()
    connection.execute("UPDATE review SET rating = 5 WHERE rating > 5")

def downgrade():
    pass  # Can't undo data changes
```

### Multiple Databases

If you have multiple databases, you can specify which one:

```python
# In app.py
migrate = Migrate(app, db, directory='migrations')
```

### Checking for Pending Migrations

```bash
# Returns non-zero exit code if migrations pending
flask db current
```

## Getting Help

- **Flask-Migrate Documentation**: https://flask-migrate.readthedocs.io/
- **Alembic Documentation**: https://alembic.sqlalchemy.org/
- **Project README**: [backend/README.md](backend/README.md)
- **Ask the team**: If you're unsure about a migration, ask for a review!

## Quick Reference

```bash
# Apply migrations
flask db upgrade

# Create new migration
flask db migrate -m "message"

# Show current version
flask db current

# Show history
flask db history

# Rollback one migration
flask db downgrade

# Help
flask db --help
```

---

Remember: Migrations are your database's source of truth. Treat them with care! 🚀
