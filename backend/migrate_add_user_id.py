"""
Migration script to add ON DELETE CASCADE to user_id foreign key and add index.
This script handles updating the review table for existing databases.

Run this script if you have an existing database without the proper foreign key constraint:
    python backend/migrate_add_user_id.py
"""

import os
import sys
import time
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError, ProgrammingError

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

def get_database_uri():
    """Get database URI from environment or use default SQLite"""
    db_host = os.environ.get('DB_HOST')
    if db_host:
        # PostgreSQL configuration for Docker
        postgres_user = os.environ.get('POSTGRES_USER', 'rentrate')
        postgres_password = os.environ.get('POSTGRES_PASSWORD', 'rentrate')
        postgres_db = os.environ.get('POSTGRES_DB', 'rentrate')
        return f'postgresql://{postgres_user}:{postgres_password}@{db_host}:5432/{postgres_db}'
    else:
        # SQLite configuration for local development
        basedir = os.path.abspath(os.path.dirname(__file__))
        return 'sqlite:///' + os.path.join(basedir, 'rentrate.db')

def wait_for_db(database_uri, max_retries=5, retry_delay=2):
    """Wait for database to be ready with retry logic"""
    for attempt in range(max_retries):
        try:
            engine = create_engine(database_uri)
            # Try to connect
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database connection successful")
            return engine
        except OperationalError as e:
            if attempt < max_retries - 1:
                print(f"Database not ready (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"Failed to connect to database after {max_retries} attempts")
                raise

def migrate():
    """Add ON DELETE CASCADE to user_id foreign key and create index"""
    database_uri = get_database_uri()
    
    # Redact credentials from URI for secure logging
    if '@' in database_uri:
        # Extract only the host/database part after the @ symbol (excludes username:password)
        db_location = database_uri.split('@')[-1]
    else:
        # For SQLite, just show the database filename
        db_location = database_uri.replace('sqlite:///', '')
    
    print(f"Connecting to database: {db_location}")
    
    # Wait for database to be ready with retry logic
    engine = wait_for_db(database_uri)
    
    # Check if review table exists
    inspector = inspect(engine)
    if 'review' not in inspector.get_table_names():
        print("Review table doesn't exist yet. No migration needed.")
        return
    
    # Get database type
    is_sqlite = 'sqlite' in database_uri
    is_postgres = 'postgresql' in database_uri
    
    if is_sqlite:
        print("SQLite database detected.")
        print("Note: SQLite requires recreating the table to modify foreign key constraints.")
        print("This migration will:")
        print("  1. Create a new review table with proper constraints")
        print("  2. Copy all data from the old table")
        print("  3. Drop the old table and rename the new one")
        
        with engine.connect() as conn:
            try:
                # Start transaction
                trans = conn.begin()
                
                # Check if the index already exists
                existing_indexes = inspector.get_indexes('review')
                index_exists = any(idx['name'] == 'idx_review_user_id' for idx in existing_indexes)
                
                if index_exists:
                    print("Index idx_review_user_id already exists.")
                else:
                    # For SQLite, we need to recreate the table to add ON DELETE CASCADE
                    # First, create the new table with proper constraints
                    print("Creating new review table with ON DELETE CASCADE constraint...")
                    
                    conn.execute(text("""
                        CREATE TABLE review_new (
                            id INTEGER NOT NULL, 
                            property_id INTEGER NOT NULL, 
                            user_id INTEGER, 
                            reviewer_name VARCHAR(100) NOT NULL, 
                            rating INTEGER NOT NULL, 
                            review_text TEXT, 
                            landlord_name VARCHAR(100), 
                            landlord_rating INTEGER, 
                            created_at DATETIME, 
                            PRIMARY KEY (id), 
                            FOREIGN KEY(property_id) REFERENCES property (id), 
                            FOREIGN KEY(user_id) REFERENCES user (id) ON DELETE CASCADE
                        )
                    """))
                    
                    # Create the index
                    print("Creating index idx_review_user_id...")
                    conn.execute(text("CREATE INDEX idx_review_user_id ON review_new(user_id)"))
                    
                    # Copy all data from old table to new table
                    print("Copying data from old table to new table...")
                    conn.execute(text("""
                        INSERT INTO review_new 
                        SELECT id, property_id, user_id, reviewer_name, rating, 
                               review_text, landlord_name, landlord_rating, created_at
                        FROM review
                    """))
                    
                    # Drop the old table
                    print("Dropping old review table...")
                    conn.execute(text("DROP TABLE review"))
                    
                    # Rename the new table to review
                    print("Renaming new table to review...")
                    conn.execute(text("ALTER TABLE review_new RENAME TO review"))
                    
                    print("Migration complete!")
                
                trans.commit()
                
            except (OperationalError, ProgrammingError) as e:
                print(f"Error during migration: {str(e)}")
                trans.rollback()
                raise
    
    elif is_postgres:
        print("PostgreSQL database detected.")
        
        with engine.connect() as conn:
            try:
                trans = conn.begin()
                
                # Check if the index already exists
                existing_indexes = inspector.get_indexes('review')
                index_exists = any(idx['name'] == 'idx_review_user_id' for idx in existing_indexes)
                
                if not index_exists:
                    print("Creating index idx_review_user_id...")
                    conn.execute(text("CREATE INDEX idx_review_user_id ON review(user_id)"))
                    print("Index created successfully.")
                else:
                    print("Index idx_review_user_id already exists.")
                
                # For PostgreSQL, we need to drop and recreate the foreign key with CASCADE
                # First, get the constraint name
                foreign_keys = inspector.get_foreign_keys('review')
                user_fk_name = None
                
                for fk in foreign_keys:
                    if fk['constrained_columns'] == ['user_id']:
                        user_fk_name = fk.get('name')
                        break
                
                if user_fk_name:
                    print(f"Dropping existing foreign key constraint: {user_fk_name}")
                    conn.execute(text(f"ALTER TABLE review DROP CONSTRAINT {user_fk_name}"))
                    
                    print("Adding new foreign key constraint with ON DELETE CASCADE...")
                    conn.execute(text(
                        "ALTER TABLE review ADD CONSTRAINT review_user_id_fkey "
                        "FOREIGN KEY(user_id) REFERENCES \"user\"(id) ON DELETE CASCADE"
                    ))
                    print("Foreign key constraint updated successfully.")
                else:
                    print("Warning: Could not find existing user_id foreign key constraint.")
                    print("Adding new foreign key constraint with ON DELETE CASCADE...")
                    conn.execute(text(
                        "ALTER TABLE review ADD CONSTRAINT review_user_id_fkey "
                        "FOREIGN KEY(user_id) REFERENCES \"user\"(id) ON DELETE CASCADE"
                    ))
                
                trans.commit()
                print("Migration complete!")
                
            except (OperationalError, ProgrammingError) as e:
                print(f"Error during migration: {str(e)}")
                trans.rollback()
                raise
    else:
        db_type = 'unknown'
        if 'postgresql' in database_uri:
            db_type = 'postgresql'
        elif 'mysql' in database_uri:
            db_type = 'mysql'
        elif 'sqlite' in database_uri:
            db_type = 'sqlite'
        print(f"Unsupported database type: {db_type}")
        return

if __name__ == '__main__':
    try:
        migrate()
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)
