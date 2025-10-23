"""Test the database schema for user_id foreign key and index"""
import pytest
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app, db


def test_index_exists_on_user_id():
    """Test that the idx_review_user_id index exists"""
    from sqlalchemy import inspect
    
    with app.app_context():
        db.create_all()  # Ensure tables are created
        inspector = inspect(db.engine)
        indexes = inspector.get_indexes('review')
        
        # Check if idx_review_user_id exists
        index_names = [idx['name'] for idx in indexes]
        assert 'idx_review_user_id' in index_names, f"Index not found. Available indexes: {index_names}"
        
        # Verify the index is on user_id column
        for idx in indexes:
            if idx['name'] == 'idx_review_user_id':
                assert 'user_id' in idx['column_names'], "Index should be on user_id column"


def test_foreign_key_constraint_exists():
    """Test that the user_id foreign key constraint exists"""
    from sqlalchemy import inspect
    
    with app.app_context():
        db.create_all()  # Ensure tables are created
        inspector = inspect(db.engine)
        foreign_keys = inspector.get_foreign_keys('review')
        
        # Find the user_id foreign key
        user_fk = None
        for fk in foreign_keys:
            if 'user_id' in fk['constrained_columns']:
                user_fk = fk
                break
        
        assert user_fk is not None, "user_id foreign key constraint not found"
        assert user_fk['referred_table'] == 'user', "Foreign key should reference user table"
        assert user_fk['referred_columns'] == ['id'], "Foreign key should reference id column"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
