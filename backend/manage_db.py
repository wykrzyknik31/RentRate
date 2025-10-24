#!/usr/bin/env python
"""
Database migration script for RentRate application.
This script provides a convenient interface for running database migrations
using Flask-Migrate/Alembic.

Usage:
    python manage_db.py init      # Initialize migrations (already done)
    python manage_db.py migrate   # Generate new migration from model changes
    python manage_db.py upgrade   # Apply pending migrations
    python manage_db.py downgrade # Revert last migration
    python manage_db.py current   # Show current migration
    python manage_db.py history   # Show migration history
"""

import os
import sys
from flask_migrate import init, migrate, upgrade, downgrade, current, history
from app import app, db

def run_command(command):
    """Run a Flask-Migrate command"""
    with app.app_context():
        if command == 'init':
            print("Initializing migrations...")
            init()
            print("Migrations initialized successfully!")
        elif command == 'migrate':
            message = input("Enter migration message (or press Enter for auto-generated): ").strip()
            print("Generating migration...")
            if message:
                migrate(message=message)
            else:
                migrate()
            print("Migration generated successfully!")
        elif command == 'upgrade':
            print("Applying migrations...")
            upgrade()
            print("Database upgraded successfully!")
        elif command == 'downgrade':
            print("Reverting last migration...")
            downgrade()
            print("Database downgraded successfully!")
        elif command == 'current':
            print("Current database revision:")
            current()
        elif command == 'history':
            print("Migration history:")
            history()
        else:
            print(f"Unknown command: {command}")
            print(__doc__)
            sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    try:
        run_command(command)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
