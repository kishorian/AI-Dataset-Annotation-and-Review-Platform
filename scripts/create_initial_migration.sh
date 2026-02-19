#!/bin/bash
# Script to create initial database migration

echo "Creating initial Alembic migration..."
alembic revision --autogenerate -m "Initial migration"

echo "Migration created! Review the migration file in alembic/versions/"
echo "Then run: alembic upgrade head"
