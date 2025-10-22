#!/bin/bash
# Startup script for RentRate backend
# This script runs database migrations before starting the Flask application

set -e  # Exit on error

echo "Starting RentRate backend..."

# Run database migration to add city column if needed
echo "Running database migration..."
python migrate_add_city.py

# Check migration status
if [ $? -eq 0 ]; then
    echo "Migration completed successfully"
else
    echo "Warning: Migration encountered issues, but continuing..."
fi

# Start Flask application
echo "Starting Flask application..."
exec flask run --host=0.0.0.0 --port=5000
