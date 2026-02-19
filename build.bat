@echo off
REM Build script for Render deployment (Windows)
REM This script builds the frontend and prepares the backend

echo Building frontend...
cd frontend
call npm install
call npm run build
cd ..

echo Installing Python dependencies...
pip install -r requirements.txt

echo Running database migrations...
alembic upgrade head

echo Build complete!
