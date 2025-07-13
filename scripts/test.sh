#!/bin/bash
# Test script for FastAPI E-commerce application

set -e

echo "Running tests for FastAPI E-commerce application..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install test dependencies
echo "Installing test dependencies..."
pip install pytest pytest-asyncio pytest-cov

# Set testing environment
export ENVIRONMENT=testing

# Run tests with coverage
echo "Running unit tests..."
pytest tests/unit/ -v --cov=app --cov-report=html --cov-report=term

echo "Running integration tests..."
pytest tests/integration/ -v

echo "Tests completed successfully!"
