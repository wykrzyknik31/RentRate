#!/bin/bash
# Startup script for RentRate backend
# This script runs database migrations before starting the Flask application

set -e  # Exit on error

echo "Starting RentRate backend..."

# Run database migration to add city column if needed
echo "Running city migration..."
python migrate_add_city.py

# Check migration status
if [ $? -eq 0 ]; then
    echo "City migration completed successfully"
else
    echo "Warning: City migration encountered issues, but continuing..."
fi

# Run database migration to add user_id column with proper constraints if needed
echo "Running user_id migration..."
python migrate_add_user_id.py

# Check migration status
if [ $? -eq 0 ]; then
    echo "User_id migration completed successfully"
else
    echo "Warning: User_id migration encountered issues, but continuing..."
fi

# Start Flask application
echo "Starting Flask application..."
exec flask run --host=0.0.0.0 --port=5000
