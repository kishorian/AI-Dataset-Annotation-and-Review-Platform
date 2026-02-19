#!/bin/bash
# Build script for Render deployment
# This script builds the frontend and prepares the backend

set -e

echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Running database migrations..."
alembic upgrade head

echo "Build complete!"
