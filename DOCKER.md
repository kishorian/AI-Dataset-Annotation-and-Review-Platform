# Docker Deployment Guide

## Overview

This project includes a production-ready multi-stage Dockerfile that:
- Builds the React frontend
- Sets up the FastAPI backend
- Combines both in a single optimized image
- Uses security best practices (non-root user)
- Includes health checks
- Optimized for production deployment

## Dockerfile Structure

The Dockerfile uses a multi-stage build process:

1. **frontend-builder**: Builds React app using Node.js
2. **python-base**: Base Python image with system dependencies
3. **python-deps**: Installs Python dependencies
4. **production**: Final image combining everything

## Building the Image

### Basic Build

```bash
docker build -t ai-dataset-annotation-platform .
```

### Build with Cache

```bash
docker build --cache-from ai-dataset-annotation-platform:latest -t ai-dataset-annotation-platform .
```

### Build Arguments (if needed)

The Dockerfile doesn't currently use build arguments, but you can add them if needed:

```dockerfile
ARG NODE_VERSION=18
ARG PYTHON_VERSION=3.11
```

## Running the Container

### Basic Run

```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/dbname \
  -e SECRET_KEY=your-secret-key \
  ai-dataset-annotation-platform
```

### With Environment File

```bash
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  ai-dataset-annotation-platform
```

### With Volume Mounts (for development)

```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/app:/app/app \
  -e DATABASE_URL=postgresql://user:pass@host:5432/dbname \
  -e SECRET_KEY=your-secret-key \
  ai-dataset-annotation-platform
```

## Docker Compose

The included `docker-compose.yml` provides a complete development environment:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Docker Compose Services

- **web**: FastAPI + React application
- **db**: PostgreSQL database

## Environment Variables

Required environment variables:

```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=your-secret-key-here
```

Optional environment variables:

```bash
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_NAME=AI Dataset Annotation Platform
APP_VERSION=1.0.0
DEBUG=False
LOG_LEVEL=INFO
CORS_ORIGINS=
```

## Database Migrations

### Run Migrations in Container

```bash
# One-time migration
docker run --rm \
  -e DATABASE_URL=postgresql://user:pass@host:5432/dbname \
  ai-dataset-annotation-platform \
  alembic upgrade head

# With docker-compose
docker-compose exec web alembic upgrade head
```

### Create New Migration

```bash
docker-compose exec web alembic revision --autogenerate -m "description"
```

## Health Checks

The Dockerfile includes a health check that monitors the `/health` endpoint:

```bash
# Check container health
docker ps

# Inspect health status
docker inspect --format='{{.State.Health.Status}}' <container-id>
```

## Production Deployment

### Render

1. **Create Web Service** in Render
2. **Set Dockerfile Path**: `Dockerfile`
3. **Set Docker Context**: `.` (root)
4. **Configure environment variables**
5. **Deploy**

Render will automatically:
- Build the Docker image
- Run the container
- Handle health checks

### Other Platforms

The Dockerfile is compatible with:
- **AWS ECS/Fargate**
- **Google Cloud Run**
- **Azure Container Instances**
- **DigitalOcean App Platform**
- **Heroku** (with container registry)

## Image Optimization

The Dockerfile is optimized for:
- **Small image size**: Multi-stage builds, alpine base images
- **Fast builds**: Layer caching, minimal dependencies
- **Security**: Non-root user, minimal attack surface
- **Performance**: Production Python, optimized Node.js build

### Image Size

Expected final image size: ~500-700MB

To reduce size further:
- Use `python:3.11-alpine` (may need additional dependencies)
- Remove build tools in final stage
- Use distroless images (advanced)

## Troubleshooting

### Container Won't Start

1. **Check logs**:
   ```bash
   docker logs <container-id>
   ```

2. **Check environment variables**:
   ```bash
   docker inspect <container-id> | grep -A 20 Env
   ```

3. **Test database connection**:
   ```bash
   docker-compose exec web python -c "from app.database import check_db_connection; print(check_db_connection())"
   ```

### Frontend Not Loading

1. **Verify build exists**:
   ```bash
   docker exec <container-id> ls -la /app/frontend/dist
   ```

2. **Check static file serving**:
   ```bash
   docker logs <container-id> | grep "Serving static files"
   ```

### Database Connection Issues

1. **Verify DATABASE_URL format**:
   ```
   postgresql://user:password@host:5432/dbname
   ```

2. **Test connection**:
   ```bash
   docker-compose exec web psql $DATABASE_URL -c "SELECT 1;"
   ```

### Performance Issues

1. **Check worker count**:
   - Default: 4 workers
   - Adjust in Dockerfile CMD: `--workers N`

2. **Monitor resources**:
   ```bash
   docker stats <container-id>
   ```

## Development vs Production

### Development

- Use `docker-compose.yml` for local development
- Mount source code as volumes
- Enable hot reload (if configured)

### Production

- Use built Docker image
- Set `DEBUG=False`
- Use production database
- Enable logging
- Configure proper CORS

## Security Considerations

1. **Non-root user**: Container runs as `appuser`
2. **Minimal dependencies**: Only production packages
3. **No secrets in image**: Use environment variables
4. **Health checks**: Monitor application status
5. **Regular updates**: Keep base images updated

## Best Practices

1. **Use specific tags**: `python:3.11-slim` not `python:latest`
2. **Layer caching**: Order Dockerfile commands by change frequency
3. **Multi-stage builds**: Keep final image small
4. **Health checks**: Enable monitoring
5. **Environment variables**: Never hardcode secrets
6. **Logging**: Configure proper log levels
7. **Resource limits**: Set memory/CPU limits in production

## Advanced Configuration

### Custom Uvicorn Settings

Modify the CMD in Dockerfile:

```dockerfile
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--log-level", "info", \
     "--access-log"]
```

### Custom Health Check

Modify HEALTHCHECK in Dockerfile:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s \
    CMD curl -f http://localhost:8000/health || exit 1
```

### Build with Different Node/Python Versions

```bash
docker build \
  --build-arg NODE_VERSION=20 \
  --build-arg PYTHON_VERSION=3.12 \
  -t ai-dataset-annotation-platform .
```
