#!/bin/bash
# Startup script for RentRate backend
# This script runs database migrations before starting the Flask application

set -e  # Exit on error

echo "Starting RentRate backend..."

# Set Flask app for migration commands
export FLASK_APP=app.py

# Run database migrations using Flask-Migrate
echo "Running database migrations..."
flask db upgrade

# Check migration status
if [ $? -eq 0 ]; then
    echo "✓ Database migrations completed successfully"
else
    echo "Error: Database migrations failed!"
    exit 1
fi

# Start Flask application
echo "Starting Flask application..."
exec flask run --host=0.0.0.0 --port=5000
