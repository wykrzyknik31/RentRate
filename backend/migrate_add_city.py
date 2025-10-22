"""
Migration script to add city column to property table.
This script handles adding the city column for existing databases.

Run this script if you have an existing database without the city column:
    python backend/migrate_add_city.py
"""

import os
import sys
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

def migrate():
    """Add city column to property table if it doesn't exist"""
    database_uri = get_database_uri()
    print(f"Connecting to database: {database_uri.split('@')[-1] if '@' in database_uri else database_uri}")
    
    engine = create_engine(database_uri)
    
    # Check if property table exists
    inspector = inspect(engine)
    if 'property' not in inspector.get_table_names():
        print("Property table doesn't exist yet. No migration needed.")
        return
    
    # Check if city column exists
    columns = [col['name'] for col in inspector.get_columns('property')]
    
    if 'city' in columns:
        print("City column already exists in property table.")
        
        # Check if there are any properties without city
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM property WHERE city IS NULL"))
            null_count = result.scalar()
            
            if null_count > 0:
                print(f"Found {null_count} properties with NULL city values.")
                print("Updating properties with NULL city to 'Unknown'...")
                conn.execute(text("UPDATE property SET city = 'Unknown' WHERE city IS NULL"))
                conn.commit()
                print("Migration complete: Updated NULL city values to 'Unknown'")
            else:
                print("All properties have city values. No update needed.")
    else:
        print("City column doesn't exist. Adding it now...")
        
        # Get database type
        is_sqlite = 'sqlite' in database_uri
        is_postgres = 'postgresql' in database_uri
        
        with engine.connect() as conn:
            try:
                if is_sqlite:
                    # SQLite doesn't support adding NOT NULL columns with DEFAULT in one step
                    # First add the column as nullable with default
                    conn.execute(text("ALTER TABLE property ADD COLUMN city VARCHAR(100) DEFAULT 'Unknown'"))
                    conn.commit()
                    print("Added city column to property table (SQLite)")
                    
                    # Update NULL values to 'Unknown'
                    conn.execute(text("UPDATE property SET city = 'Unknown' WHERE city IS NULL"))
                    conn.commit()
                    print("Updated existing properties with default city value")
                    
                elif is_postgres:
                    # PostgreSQL can add NOT NULL column with DEFAULT
                    conn.execute(text("ALTER TABLE property ADD COLUMN city VARCHAR(100) DEFAULT 'Unknown' NOT NULL"))
                    conn.commit()
                    print("Added city column to property table (PostgreSQL)")
                else:
                    print(f"Unknown database type: {database_uri}")
                    return
                
                print("Migration complete!")
                
            except (OperationalError, ProgrammingError) as e:
                print(f"Error during migration: {e}")
                conn.rollback()
                raise

if __name__ == '__main__':
    try:
        migrate()
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)
