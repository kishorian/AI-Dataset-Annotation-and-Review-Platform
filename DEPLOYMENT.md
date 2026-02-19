# Deployment Guide

## Deployment Options

This application can be deployed in two ways:
1. **Docker Deployment** (Recommended for production)
2. **Native Render Deployment** (Using build scripts)

## Docker Deployment

### Building the Docker Image

```bash
docker build -t ai-dataset-annotation-platform .
```

### Running Locally with Docker Compose

```bash
docker-compose up -d
```

This will start:
- FastAPI backend + React frontend on `http://localhost:8000`
- PostgreSQL database on `localhost:5432`

### Running the Docker Container

```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/dbname \
  -e SECRET_KEY=your-secret-key \
  ai-dataset-annotation-platform
```

### Docker on Render

1. **Create a new Web Service** in Render
2. **Connect your repository**
3. **Set the following**:
   - **Dockerfile Path**: `Dockerfile`
   - **Docker Context**: `.` (root directory)
4. **Set environment variables** (same as native deployment)
5. **Deploy**

Render will automatically:
- Build the Docker image
- Run database migrations (if configured)
- Start the container with Uvicorn

### Docker Image Features

- **Multi-stage build** for optimized image size
- **Non-root user** for security
- **Health checks** for monitoring
- **Layer caching** for faster builds
- **Production-optimized** Python and Node.js

### Running Migrations in Docker

If you need to run migrations manually:

```bash
docker run --rm \
  -e DATABASE_URL=postgresql://user:pass@host:5432/dbname \
  ai-dataset-annotation-platform \
  alembic upgrade head
```

## Single Service Deployment (Render - Native)

This application is configured for single-service deployment where both the React frontend and FastAPI backend are served from the same service.

## Architecture

```
Render Web Service
├── FastAPI Backend
│   ├── API Routes (/api/*)
│   └── Static Files (React build)
└── React Frontend
    └── Served from / (all non-API routes)
```

## Render Setup

### 1. Create New Web Service

1. Go to Render dashboard
2. Click "New +" → "Web Service"
3. Connect your repository

### 2. Configure Build Settings

**Build Command**:
```bash
cd frontend && npm install && npm run build && cd .. && pip install -r requirements.txt
```

**Start Command**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 3. Environment Variables

Set the following environment variables in Render:

**Required**:
- `DATABASE_URL` - PostgreSQL connection string (from Render PostgreSQL service)
- `SECRET_KEY` - Strong random string for JWT (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)

**Optional** (with defaults):
- `ALGORITHM=HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES=30`
- `APP_NAME=AI Dataset Annotation Platform`
- `APP_VERSION=1.0.0`
- `DEBUG=False`
- `LOG_LEVEL=INFO`
- `CORS_ORIGINS` - Leave empty for same-origin (not needed when serving static files)

### 4. Database Setup

1. Create a PostgreSQL database in Render
2. Copy the Internal Database URL
3. Set as `DATABASE_URL` environment variable
4. Run migrations (can be done in post-deploy script or manually)

**Post-Deploy Script** (optional):
```bash
alembic upgrade head
```

## File Structure for Deployment

```
project-root/
├── app/                    # FastAPI application
├── frontend/
│   ├── dist/              # React build output (created during build)
│   └── src/                # React source
├── alembic/                # Database migrations
├── requirements.txt        # Python dependencies
├── render.yaml             # Render configuration (optional)
└── README.md
```

## Build Process

1. **Frontend Build**: React app is built to `frontend/dist/`
2. **Static Mounting**: FastAPI serves files from `frontend/dist/`
3. **SPA Routing**: All non-API routes return `index.html`

## Route Handling

- `/api/*` → FastAPI API routes
- `/health` → Health check endpoint
- `/api/docs` → API documentation (production)
- `/*` → React app (index.html)

## Troubleshooting

### Frontend Not Loading

1. **Check build output**: Ensure `frontend/dist/` exists after build
2. **Check logs**: Look for "React build directory not found" warnings
3. **Verify paths**: Ensure static directory path is correct

### API Routes Not Working

1. **Check prefix**: All API routes should be under `/api/`
2. **Check CORS**: If accessing from different origin, configure CORS
3. **Check authentication**: Verify token is being sent

### Database Connection Issues

1. **Verify DATABASE_URL**: Check it's set correctly
2. **Check SSL**: Render PostgreSQL requires SSL
3. **Run migrations**: Ensure `alembic upgrade head` has been run

## Development vs Production

### Development
- Frontend runs on `localhost:3000` (Vite dev server)
- Backend runs on `localhost:8000`
- CORS enabled for cross-origin requests
- API docs at `/docs`

### Production
- Single service on Render
- Frontend served as static files
- Backend serves both API and frontend
- API docs at `/api/docs`
- CORS may not be needed (same origin)

## Manual Deployment Steps

1. **Build frontend**:
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

4. **Start server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

## Environment-Specific Configuration

### Development (.env)
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
SECRET_KEY=dev-secret-key
DEBUG=True
CORS_ORIGINS=http://localhost:3000
```

### Production (Render Environment Variables)
```env
DATABASE_URL=<render-postgres-internal-url>
SECRET_KEY=<strong-random-key>
DEBUG=False
CORS_ORIGINS=  # Empty or your domain
```

## Health Check

The application provides a health check endpoint:

```
GET /health
```

Returns:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected"
}
```

Use this for Render health checks or monitoring.
