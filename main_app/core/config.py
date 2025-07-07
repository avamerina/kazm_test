from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with dependency injection support"""

    sync_database_url: str = os.environ.get("SYNC_DATABASE_URL")
    async_database_url: str = os.environ.get("ASYNC_DATABASE_URL")

    # API settings
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Films API"
    version: str = "1.0.0"

    # CORS settings
    cors_origins: list[str] = ["*"]
    cors_credentials: bool = True
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]

    # Pagination defaults
    default_page_size: int = 50
    max_page_size: int = 100

    class Config:
        env_file = ".env"
        extra = "ignore"

# Global settings instance
settings = Settings()


class ConfigProvider:
    """Dependency injection provider for configuration"""
    
    def __init__(self, settings: Optional[Settings] = None):
        self._settings = settings or Settings()
    
    @property
    def settings(self) -> Settings:
        return self._settings
    
    def get_async_database_url(self) -> str:
        return self._settings.async_database_url

    def get_sync_database_url(self) -> str:
        return self._settings.sync_database_url
    
    def get_api_prefix(self) -> str:
        return self._settings.api_v1_prefix
    
    def get_cors_config(self) -> dict:
        return {
            "allow_origins": self._settings.cors_origins,
            "allow_credentials": self._settings.cors_credentials,
            "allow_methods": self._settings.cors_methods,
            "allow_headers": self._settings.cors_headers,
        }


# Global config provider instance
config_provider = ConfigProvider(settings) 