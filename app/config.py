from pydantic_settings import BaseSettings
from typing import Optional
import json


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "FastAPI Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str
    
    # Database Connection Pool Settings
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600  # Recycle connections after 1 hour
    DB_POOL_PRE_PING: bool = True  # Verify connections before using
    DB_ECHO: bool = False  # Log SQL queries (set to True for debugging)
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS - can be comma-separated string or JSON array
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "*"
    CORS_ALLOW_HEADERS: str = "*"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS into a list."""
        if not self.CORS_ORIGINS:
            return []
        # Try JSON first, then fall back to comma-separated
        try:
            return json.loads(self.CORS_ORIGINS)
        except (json.JSONDecodeError, TypeError):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    @property
    def cors_methods_list(self) -> list[str]:
        """Parse CORS_ALLOW_METHODS into a list."""
        if self.CORS_ALLOW_METHODS == "*":
            return ["*"]
        try:
            return json.loads(self.CORS_ALLOW_METHODS)
        except (json.JSONDecodeError, TypeError):
            return [method.strip() for method in self.CORS_ALLOW_METHODS.split(",") if method.strip()]
    
    @property
    def cors_headers_list(self) -> list[str]:
        """Parse CORS_ALLOW_HEADERS into a list."""
        if self.CORS_ALLOW_HEADERS == "*":
            return ["*"]
        try:
            return json.loads(self.CORS_ALLOW_HEADERS)
        except (json.JSONDecodeError, TypeError):
            return [header.strip() for header in self.CORS_ALLOW_HEADERS.split(",") if header.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
