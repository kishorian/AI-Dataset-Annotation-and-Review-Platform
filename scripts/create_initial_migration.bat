@echo off
REM Script to create initial database migration for Windows

echo Creating initial Alembic migration...
alembic revision --autogenerate -m "Initial migration"

echo Migration created! Review the migration file in alembic/versions/
echo Then run: alembic upgrade head
