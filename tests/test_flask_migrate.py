"""
Test Flask-Migrate integration and migration structure
"""

import os
import sys
import pytest

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)


def test_migrations_directory_exists():
    """Test that migrations directory exists"""
    migrations_dir = os.path.join(backend_path, 'migrations')
    assert os.path.exists(migrations_dir), "Migrations directory should exist"


def test_migrations_has_versions():
    """Test that migrations/versions directory exists"""
    versions_dir = os.path.join(backend_path, 'migrations', 'versions')
    assert os.path.exists(versions_dir), "Migrations versions directory should exist"


def test_baseline_migration_exists():
    """Test that baseline migration exists"""
    baseline_migration = os.path.join(
        backend_path, 'migrations', 'versions', '001_initial_schema.py'
    )
    assert os.path.exists(baseline_migration), "Baseline migration should exist"


def test_alembic_ini_exists():
    """Test that alembic.ini exists"""
    alembic_ini = os.path.join(backend_path, 'migrations', 'alembic.ini')
    assert os.path.exists(alembic_ini), "alembic.ini should exist"


def test_env_py_exists():
    """Test that env.py exists"""
    env_py = os.path.join(backend_path, 'migrations', 'env.py')
    assert os.path.exists(env_py), "env.py should exist"


def test_script_mako_exists():
    """Test that script.py.mako exists"""
    script_mako = os.path.join(backend_path, 'migrations', 'script.py.mako')
    assert os.path.exists(script_mako), "script.py.mako should exist"


def test_flask_migrate_imported():
    """Test that Flask-Migrate is properly imported in app.py"""
    app_py = os.path.join(backend_path, 'app.py')
    with open(app_py, 'r') as f:
        content = f.read()
        assert 'from flask_migrate import Migrate' in content, \
            "Flask-Migrate should be imported in app.py"
        assert 'migrate = Migrate(app, db)' in content, \
            "Migrate should be initialized in app.py"


def test_requirements_has_flask_migrate():
    """Test that Flask-Migrate is in requirements.txt"""
    requirements = os.path.join(backend_path, 'requirements.txt')
    with open(requirements, 'r') as f:
        content = f.read()
        assert 'Flask-Migrate' in content, \
            "Flask-Migrate should be in requirements.txt"


def test_baseline_migration_structure():
    """Test that baseline migration has correct structure"""
    baseline_migration = os.path.join(
        backend_path, 'migrations', 'versions', '001_initial_schema.py'
    )
    
    with open(baseline_migration, 'r') as f:
        content = f.read()
        
        # Check for required migration attributes
        assert "revision = '001_initial_schema'" in content, \
            "Migration should have revision identifier"
        assert "down_revision = None" in content, \
            "Baseline migration should have down_revision = None"
        
        # Check for upgrade function
        assert "def upgrade():" in content, \
            "Migration should have upgrade function"
        
        # Check for downgrade function
        assert "def downgrade():" in content, \
            "Migration should have downgrade function"
        
        # Check that all tables are created
        assert "op.create_table('user'" in content, \
            "Migration should create user table"
        assert "op.create_table('property'" in content, \
            "Migration should create property table"
        assert "op.create_table('review'" in content, \
            "Migration should create review table"
        assert "op.create_table('photo'" in content, \
            "Migration should create photo table"
        assert "op.create_table('translation'" in content, \
            "Migration should create translation table"


def test_helper_scripts_exist():
    """Test that helper scripts exist"""
    migrate_sh = os.path.join(backend_path, 'migrate.sh')
    manage_db_py = os.path.join(backend_path, 'manage_db.py')
    
    assert os.path.exists(migrate_sh), "migrate.sh should exist"
    assert os.path.exists(manage_db_py), "manage_db.py should exist"
    
    # Check that migrate.sh is executable
    assert os.access(migrate_sh, os.X_OK), "migrate.sh should be executable"
    assert os.access(manage_db_py, os.X_OK), "manage_db.py should be executable"


def test_startup_script_uses_migrations():
    """Test that startup.sh uses flask db upgrade"""
    startup_sh = os.path.join(backend_path, 'startup.sh')
    
    with open(startup_sh, 'r') as f:
        content = f.read()
        assert 'flask db upgrade' in content, \
            "startup.sh should run flask db upgrade"
        assert 'export FLASK_APP=app.py' in content, \
            "startup.sh should set FLASK_APP"


def test_old_migrations_deprecated():
    """Test that old migration scripts are marked as deprecated"""
    old_migrations = [
        os.path.join(backend_path, 'migrate_add_city.py'),
        os.path.join(backend_path, 'migrate_add_user_id.py')
    ]
    
    for migration in old_migrations:
        with open(migration, 'r') as f:
            content = f.read()
            assert 'DEPRECATED' in content, \
                f"{os.path.basename(migration)} should be marked as deprecated"
            assert 'Flask-Migrate' in content, \
                f"{os.path.basename(migration)} should reference Flask-Migrate"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
