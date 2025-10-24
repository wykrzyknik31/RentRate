#!/bin/bash
# Clean start script for RentRate backend
# This script clears Python cache, runs migrations, and starts the server fresh

echo "🧹 Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null

echo "✨ Cache cleared!"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Set Flask app for migration commands
export FLASK_APP=app.py

echo "🔄 Running database migrations..."
flask db upgrade

if [ $? -eq 0 ]; then
    echo "✓ Database migrations completed successfully"
else
    echo "⚠️  Warning: Database migrations encountered issues, continuing anyway..."
fi

echo ""
echo "🚀 Starting Flask server..."
echo ""

# Start the server
python app.py
