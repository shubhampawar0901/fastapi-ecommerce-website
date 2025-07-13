#!/bin/bash
# Production startup script for FastAPI E-commerce application

set -e

echo "Starting FastAPI E-commerce application..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations (if using Alembic)
# echo "Running database migrations..."
# alembic upgrade head

# Initialize sample data if needed
if [ "$INIT_SAMPLE_DATA" = "true" ]; then
    echo "Initializing sample data..."
    python init_data.py
fi

# Start the application
echo "Starting application on port ${PORT:-8000}..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WORKERS:-1}
