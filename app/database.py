from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from app.config import settings
from app.core.logging import logger


def prepare_database_url(url: str) -> str:
    """
    Prepare database URL for production deployment (e.g., Render).
    Adds SSL parameters if not present and URL uses postgresql:// scheme.
    """
    parsed = urlparse(url)
    
    # Convert postgresql:// to postgresql+psycopg2:// if needed
    if parsed.scheme == "postgresql":
        # Replace scheme to explicitly use psycopg2
        parsed = parsed._replace(scheme="postgresql+psycopg2")
    elif parsed.scheme == "postgres":
        parsed = parsed._replace(scheme="postgresql+psycopg2")
    
    # Parse query parameters
    query_params = parse_qs(parsed.query)
    
    # Add SSL mode for production (Render requires SSL)
    # Check if we're in production (not localhost)
    is_production = "localhost" not in parsed.hostname.lower() if parsed.hostname else False
    
    if is_production and "sslmode" not in query_params:
        query_params["sslmode"] = ["require"]
        logger.info("Added SSL mode to database URL for production")
    
    # Reconstruct query string
    new_query = urlencode(query_params, doseq=True)
    parsed = parsed._replace(query=new_query)
    
    return urlunparse(parsed)


# Prepare database URL with SSL configuration
database_url = prepare_database_url(settings.DATABASE_URL)

# Create engine with production-ready settings
engine = create_engine(
    database_url,
    # Connection Pool Settings
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    # Connection Settings
    connect_args={
        "connect_timeout": 10,
        "options": "-c statement_timeout=30000",  # 30 second statement timeout
    },
    # Logging
    echo=settings.DB_ECHO,
    # Performance
    future=True,  # Use SQLAlchemy 2.0 style
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,  # Prevent lazy loading issues
)

# Base class for declarative models
Base = declarative_base()


# Event listeners for connection pool monitoring
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Set connection-level settings when a connection is created.
    """
    # For PostgreSQL, we can set session-level settings here if needed
    pass


@event.listens_for(Engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """
    Log when a connection is checked out from the pool.
    """
    if settings.DEBUG:
        logger.debug("Database connection checked out from pool")


@event.listens_for(Engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """
    Log when a connection is returned to the pool.
    """
    if settings.DEBUG:
        logger.debug("Database connection returned to pool")


def get_db():
    """
    Dependency function to get database session.
    Yields a database session and ensures it's closed after use.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    Should be called after Alembic migrations in production.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise


def check_db_connection() -> bool:
    """
    Check if database connection is working.
    Returns True if connection is successful, False otherwise.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection check successful")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}", exc_info=True)
        return False
