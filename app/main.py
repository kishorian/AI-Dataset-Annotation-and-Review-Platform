from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import os
from app.config import settings
from app.database import check_db_connection
from app.routers import auth, users, projects, data_samples, annotations, reviews, analytics
from app.core.logging import logger
from app.core.exceptions import AppException, handle_app_exception

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/api/docs" if not settings.DEBUG else "/docs",  # Move docs to /api/docs in production
    redoc_url="/api/redoc" if not settings.DEBUG else "/redoc",
)

# CORS middleware - only needed if frontend is on different origin
# In production with static files served from same origin, CORS may not be needed
# But keeping it for flexibility
if settings.cors_origins_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.cors_methods_list,
        allow_headers=settings.cors_headers_list,
    )


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """
    Handle application-specific exceptions.
    """
    logger.error(f"Application exception: {exc}", exc_info=True)
    http_exc = handle_app_exception(exc)
    return JSONResponse(
        status_code=http_exc.status_code,
        content={"detail": http_exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle general exceptions.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    db_status = check_db_connection()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "version": settings.APP_VERSION,
        "database": "connected" if db_status else "disconnected"
    }


# Include API routers (must be before static files)
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(data_samples.router, prefix="/api")
app.include_router(annotations.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")

# Serve static files from React build
# Path to React build directory (relative to project root)
static_dir = Path(__file__).parent.parent / "frontend" / "dist"

if static_dir.exists() and (static_dir / "index.html").exists():
    # Mount static assets directory (JS, CSS, images, etc.)
    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
    
    # Serve other static files from dist root (favicon, robots.txt, etc.)
    # This must come before the catch-all route
    @app.get("/favicon.ico")
    async def favicon():
        favicon_path = static_dir / "favicon.ico"
        if favicon_path.exists():
            return FileResponse(str(favicon_path))
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    
    @app.get("/robots.txt")
    async def robots():
        robots_path = static_dir / "robots.txt"
        if robots_path.exists():
            return FileResponse(str(robots_path))
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    
    # Serve index.html for all non-API routes (SPA routing)
    # This catch-all must be last to not interfere with API routes
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str, request: Request):
        """
        Serve React app for all non-API routes.
        This enables client-side routing for the SPA.
        """
        # Don't serve index.html for API routes, health check, or docs
        if (
            full_path.startswith("api/") or 
            full_path == "api" or
            full_path.startswith("docs") or 
            full_path.startswith("redoc") or
            full_path == "health"
        ):
            return JSONResponse(
                status_code=404,
                content={"detail": "Not found"}
            )
        
        # Check if it's a static file request (has extension)
        static_file = static_dir / full_path
        if static_file.exists() and static_file.is_file():
            return FileResponse(str(static_file))
        
        # Serve index.html for all other routes (SPA routing)
        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        else:
            logger.warning(f"React build not found at {index_path}")
            return JSONResponse(
                status_code=404,
                content={"detail": "Frontend build not found. Please build the React app."}
            )
    
    logger.info(f"Serving static files from {static_dir}")
else:
    logger.warning(
        f"React build directory not found at {static_dir}. "
        "Static file serving disabled. Build the frontend with 'npm run build' in the frontend directory."
    )


@app.on_event("startup")
async def startup_event():
    """
    Startup event handler.
    """
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Check database connection on startup
    if check_db_connection():
        logger.info("Database connection established successfully")
    else:
        logger.warning("Database connection check failed - application may not function correctly")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler.
    """
    logger.info(f"Shutting down {settings.APP_NAME}")
