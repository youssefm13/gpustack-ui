"""
Environment configuration and settings management for GPUStack UI backend.
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables from .env files
# Load .env first (template), then .env.local (local overrides)
load_dotenv(".env")
load_dotenv(".env.local", override=True)


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Environment
    env: str = Field(default="development", env="ENV")
    
    # GPUStack API Configuration
    gpustack_api_base: str = Field(default="http://localhost:80", env="GPUSTACK_API_BASE")
    gpustack_api_token: Optional[str] = Field(default=None, env="GPUSTACK_API_TOKEN")
    
    # Tavily Search API
    tavily_api_key: Optional[str] = Field(default=None, env="TAVILY_API_KEY")
    
    # JWT Authentication
    jwt_secret_key: str = Field(
        default="your-super-secret-jwt-key-change-in-production",
        env="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Backend Configuration
    backend_host: str = Field(default="0.0.0.0", env="BACKEND_HOST")
    backend_port: int = Field(default=8001, env="BACKEND_PORT")
    workers: int = Field(default=3, env="WORKERS")
    log_level: str = Field(default="info", env="LOG_LEVEL")
    
    # Database (Optional - for future use)
    database_url: str = Field(default="sqlite:///./gpustack_ui.db", env="DATABASE_URL")
    
    # Redis Configuration (Optional)
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # File Upload
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    
    # Logging
    log_dir: str = Field(default="./logs", env="LOG_DIR")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # Security
    cors_origins: List[str] = Field(
        default=["http://localhost:8001"],
        env="CORS_ORIGINS"
    )
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        env="ALLOWED_HOSTS"
    )
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.env.lower() in ["development", "dev"]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.env.lower() in ["production", "prod"]
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.env.lower() in ["testing", "test"] or os.getenv("TESTING") == "1"
    
    def get_production_overrides(self) -> dict:
        """Get production-specific configuration overrides."""
        if not self.is_production:
            return {}
        
        overrides = {}
        
        # Use production-specific JWT secret if provided
        prod_jwt_secret = os.getenv("PROD_JWT_SECRET_KEY")
        if prod_jwt_secret:
            overrides["jwt_secret_key"] = prod_jwt_secret
        
        # Use production database URL if provided
        prod_db_url = os.getenv("PROD_DATABASE_URL")
        if prod_db_url:
            overrides["database_url"] = prod_db_url
        
        # Use production Redis URL if provided
        prod_redis_url = os.getenv("PROD_REDIS_URL")
        if prod_redis_url:
            overrides["redis_url"] = prod_redis_url
        
        return overrides
    
    class Config:
        """Pydantic configuration."""
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


class DevelopmentSettings(Settings):
    """Development-specific settings."""
    log_level: str = "debug"
    workers: int = 1


class ProductionSettings(Settings):
    """Production-specific settings."""
    log_level: str = "warning"
    workers: int = 4


class TestingSettings(Settings):
    """Testing-specific settings."""
    env: str = "testing"
    database_url: str = "sqlite:///./test_gpustack_ui.db"
    jwt_secret_key: str = "test-secret-key"
    tavily_api_key: str = "test-key"


def get_settings() -> Settings:
    """Get settings based on environment."""
    env = os.getenv("ENV", "development").lower()
    
    if env in ["testing", "test"] or os.getenv("TESTING") == "1":
        return TestingSettings()
    elif env in ["production", "prod"]:
        return ProductionSettings()
    else:
        return DevelopmentSettings()


# Global settings instance
settings = get_settings()
