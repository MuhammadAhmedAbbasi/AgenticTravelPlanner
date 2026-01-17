"""Configuration settings for Travel Planner"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from .env file"""
    
    # API Keys
    google_places_key: str
    google_api_key: str
    tavily_api_key: str
    serpapi_key: str
    
    # Model Configuration
    flash_model: str = "gemini-2.5-flash"
    pro_model: str = "gemini-3-pro-preview"
    request_timeout: int = 120
    max_retries: int = 5
    temperature: float = 0.0
    
    # Database
    database_url: str = "sqlite:///travel_planner.db"
    
    # Cache
    cache_ttl_hours: int = 24
    enable_cache: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "src/logging/logs/travel_planner.log"
    
    # Proxy (Optional)
    http_proxy: Optional[str] = None
    https_proxy: Optional[str] = None
    
    # Application
    debug: bool = False
    environment: str = "production"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get cached settings instance"""
    if not hasattr(get_settings, "_instance"):
        get_settings._instance = Settings()
    return get_settings._instance


settings = get_settings()