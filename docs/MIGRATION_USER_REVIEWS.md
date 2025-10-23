# Database Migration for User Review Ownership

## Overview
This migration adds proper foreign key constraints and indexing to link reviews to users in the RentRate application.

## Changes Made

### 1. Database Schema Updates

#### Review Table
- **Foreign Key Constraint**: Added `ON DELETE CASCADE` to the `user_id` foreign key
  - When a user is deleted, all their reviews are automatically deleted
  - Prevents orphaned reviews in the database

- **Index**: Created `idx_review_user_id` on the `user_id` column
  - Improves query performance when filtering reviews by user
  - Essential for the "My Reviews" feature

### 2. Backend Changes (`backend/app.py`)

#### Review Model
```python
class Review(db.Model):
    # ... other columns ...
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True)
    
    # Create index for faster filtering by user_id
    __table_args__ = (
        db.Index('idx_review_user_id', 'user_id'),
    )
```

#### SQLite Foreign Key Support
- Added event listener to enable foreign key constraints for SQLite connections
- This ensures ON DELETE CASCADE works correctly in SQLite

### 3. Migration Script (`backend/migrate_add_user_id.py`)

For existing databases, run the migration script:

```bash
python backend/migrate_add_user_id.py
```

The migration script:
- Detects database type (SQLite or PostgreSQL)
- Adds the `idx_review_user_id` index if not present
- Updates the foreign key constraint to include ON DELETE CASCADE
- For SQLite: Recreates the table with proper constraints (SQLite limitation)
- For PostgreSQL: Drops and recreates the foreign key constraint

## Running the Migration

### For Local Development (SQLite)

```bash
cd backend
python migrate_add_user_id.py
```

### For Docker/Production (PostgreSQL)

The migration script automatically detects PostgreSQL and handles it appropriately:

```bash
# The migration will be run automatically on container startup
# Or run manually:
docker exec -it rentrate-backend python migrate_add_user_id.py
```

## Testing

Run the tests to verify the migration:

```bash
# Test the schema changes
pytest tests/test_cascade_delete.py -v

# Test the My Reviews functionality
pytest tests/test_my_reviews.py -v

# Run all tests
pytest tests/ --ignore=tests/test_auth.py -v
```

## Features Enabled

With these changes, the following features are now fully functional:

1. **My Reviews Page** (`/my-reviews`)
   - Users can view all their submitted reviews
   - Reviews are sorted by most recent first

2. **Edit Reviews**
   - Users can edit their own reviews
   - PUT `/api/reviews/<id>` endpoint enforces ownership

3. **Delete Reviews**
   - Users can delete their own reviews
   - DELETE `/api/reviews/<id>` endpoint enforces ownership
   - Reviews are automatically deleted when a user account is deleted

4. **Performance**
   - Faster queries when filtering reviews by user
   - Index on `user_id` improves "My Reviews" page load time

## Important Notes

### Anonymous Reviews
- Reviews created without authentication have `user_id = NULL`
- These reviews cannot be edited or deleted through the API
- This is by design to maintain data integrity

### SQLite Specifics
- SQLite requires `PRAGMA foreign_keys=ON` for each connection
- This is automatically handled by the event listener in `app.py`
- Foreign key constraints must be set when the table is created (hence the table recreation in migration)

### PostgreSQL Specifics
- PostgreSQL fully supports ALTER TABLE for foreign key constraints
- Migration is simpler and faster than SQLite

## Rollback

If you need to rollback the migration:

### SQLite
Restore from a backup of your `rentrate.db` file

### PostgreSQL
```sql
-- Drop the index
DROP INDEX idx_review_user_id;

-- Drop and recreate the foreign key without CASCADE
ALTER TABLE review DROP CONSTRAINT review_user_id_fkey;
ALTER TABLE review ADD CONSTRAINT review_user_id_fkey 
    FOREIGN KEY(user_id) REFERENCES "user"(id);
```

## Verification

After running the migration, verify:

1. **Index exists**:
   ```sql
   -- SQLite
   .indexes review
   
   -- PostgreSQL
   SELECT indexname FROM pg_indexes WHERE tablename = 'review';
   ```

2. **Foreign key constraint**:
   ```sql
   -- SQLite
   .schema review
   
   -- PostgreSQL
   SELECT * FROM information_schema.table_constraints 
   WHERE table_name = 'review';
   ```

3. **Cascade delete works**:
   - Create a test user and review
   - Delete the user
   - Verify the review is also deleted
