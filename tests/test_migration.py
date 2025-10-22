"""Unit tests for database migration script"""
import pytest
import sys
import os
import tempfile
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text, inspect
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import migrate_add_city


@pytest.fixture
def test_db():
    """Create a temporary test database"""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


class TestMigrationScript:
    """Test suite for migration script"""
    
    def test_migration_adds_city_column_to_existing_table(self, test_db):
        """Test that migration adds city column to property table without it"""
        # Create old schema (without city column)
        Base = declarative_base()
        
        class Property(Base):
            __tablename__ = 'property'
            id = Column(Integer, primary_key=True)
            address = Column(String(200), nullable=False)
            property_type = Column(String(50), nullable=False)
            created_at = Column(DateTime, default=datetime.utcnow)
        
        engine = create_engine(f'sqlite:///{test_db}')
        Base.metadata.create_all(engine)
        
        # Add test data
        Session = sessionmaker(bind=engine)
        session = Session()
        prop = Property(address='123 Test St', property_type='apartment')
        session.add(prop)
        session.commit()
        session.close()
        
        # Verify city column doesn't exist
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('property')]
        assert 'city' not in columns, "City column should not exist before migration"
        
        # Override get_database_uri to use test database
        original_get_uri = migrate_add_city.get_database_uri
        migrate_add_city.get_database_uri = lambda: f'sqlite:///{test_db}'
        
        try:
            # Run migration
            migrate_add_city.migrate()
            
            # Verify city column was added
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('property')]
            assert 'city' in columns, "City column should exist after migration"
            
            # Verify data was preserved and city was set to default
            with engine.connect() as conn:
                result = conn.execute(text("SELECT id, address, city, property_type FROM property"))
                row = result.fetchone()
                assert row is not None
                assert row[1] == '123 Test St'  # address
                assert row[2] == 'Unknown'  # city (default value)
                assert row[3] == 'apartment'  # property_type
        finally:
            # Restore original function
            migrate_add_city.get_database_uri = original_get_uri
    
    def test_migration_is_idempotent(self, test_db):
        """Test that running migration twice doesn't cause errors"""
        # Create old schema
        Base = declarative_base()
        
        class Property(Base):
            __tablename__ = 'property'
            id = Column(Integer, primary_key=True)
            address = Column(String(200), nullable=False)
            property_type = Column(String(50), nullable=False)
            created_at = Column(DateTime, default=datetime.utcnow)
        
        engine = create_engine(f'sqlite:///{test_db}')
        Base.metadata.create_all(engine)
        
        # Override get_database_uri
        original_get_uri = migrate_add_city.get_database_uri
        migrate_add_city.get_database_uri = lambda: f'sqlite:///{test_db}'
        
        try:
            # Run migration first time
            migrate_add_city.migrate()
            
            # Verify city column exists
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('property')]
            assert 'city' in columns
            
            # Run migration second time (should not raise error)
            migrate_add_city.migrate()
            
            # Verify city column still exists
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('property')]
            assert 'city' in columns
        finally:
            migrate_add_city.get_database_uri = original_get_uri
    
    def test_migration_skips_when_no_property_table(self, test_db):
        """Test that migration skips gracefully when property table doesn't exist"""
        # Create empty database
        engine = create_engine(f'sqlite:///{test_db}')
        
        # Override get_database_uri
        original_get_uri = migrate_add_city.get_database_uri
        migrate_add_city.get_database_uri = lambda: f'sqlite:///{test_db}'
        
        try:
            # Run migration (should not raise error)
            migrate_add_city.migrate()
            
            # Verify no tables were created
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            assert len(tables) == 0
        finally:
            migrate_add_city.get_database_uri = original_get_uri
    
    def test_migration_updates_null_city_values(self, test_db):
        """Test that migration updates NULL city values to 'Unknown'"""
        # Create schema with city column but allow NULLs
        engine = create_engine(f'sqlite:///{test_db}')
        
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE property (
                    id INTEGER PRIMARY KEY,
                    address VARCHAR(200) NOT NULL,
                    city VARCHAR(100),
                    property_type VARCHAR(50) NOT NULL,
                    created_at DATETIME
                )
            """))
            conn.execute(text("""
                INSERT INTO property (address, city, property_type)
                VALUES ('123 Test St', NULL, 'apartment')
            """))
            conn.execute(text("""
                INSERT INTO property (address, city, property_type)
                VALUES ('456 Main Ave', 'TestCity', 'house')
            """))
            conn.commit()
        
        # Override get_database_uri
        original_get_uri = migrate_add_city.get_database_uri
        migrate_add_city.get_database_uri = lambda: f'sqlite:///{test_db}'
        
        try:
            # Run migration
            migrate_add_city.migrate()
            
            # Verify NULL city was updated
            with engine.connect() as conn:
                result = conn.execute(text("SELECT address, city FROM property ORDER BY id"))
                rows = result.fetchall()
                assert len(rows) == 2
                assert rows[0][0] == '123 Test St'
                assert rows[0][1] == 'Unknown'  # NULL updated to 'Unknown'
                assert rows[1][0] == '456 Main Ave'
                assert rows[1][1] == 'TestCity'  # Existing value preserved
        finally:
            migrate_add_city.get_database_uri = original_get_uri


class TestDatabaseRetryLogic:
    """Test suite for database connection retry logic"""
    
    def test_wait_for_db_succeeds_on_first_attempt(self, test_db):
        """Test that wait_for_db succeeds when database is immediately available"""
        database_uri = f'sqlite:///{test_db}'
        
        # Create database
        engine = create_engine(database_uri)
        with engine.connect() as conn:
            conn.execute(text("CREATE TABLE test (id INTEGER)"))
            conn.commit()
        
        # Test wait_for_db
        result_engine = migrate_add_city.wait_for_db(database_uri)
        assert result_engine is not None
        
        # Verify it can execute queries
        with result_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
    
    def test_wait_for_db_raises_after_max_retries(self):
        """Test that wait_for_db raises error after max retries"""
        # Use invalid database URI
        database_uri = 'postgresql://invalid:invalid@nonexistent:5432/invalid'
        
        with pytest.raises(Exception):
            migrate_add_city.wait_for_db(database_uri, max_retries=2, retry_delay=0.1)
