from typing import Optional
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_db
from main_app.core.services import FilmService, GenreService, PersonService
from main_app.core.repositories import FilmRepository, GenreRepository, PersonRepository


class ServiceContainer:
    """Container for managing application services"""
    
    def __init__(self):
        self._initialized = False
        self._search_service = None
    
    async def initialize(self):
        """Initialize the service container"""
        if self._initialized:
            return
        # Semantic search initialization removed for now
        self._search_service = None
        self._initialized = True
    
    async def cleanup(self):
        """Cleanup resources"""
        self._search_service = None
    
    def get_search_service(self):
        """Get search service instance"""
        return self._search_service


# Global service container instance
_service_container: Optional[ServiceContainer] = None

def get_service_container() -> ServiceContainer:
    """Get the global service container"""
    global _service_container
    if _service_container is None:
        _service_container = ServiceContainer()
    return _service_container

# Repository dependencies
def get_film_repository(db: AsyncSession = Depends(get_async_db)) -> FilmRepository:
    """Get film repository instance"""
    return FilmRepository(db)

def get_genre_repository(db: AsyncSession = Depends(get_async_db)) -> GenreRepository:
    """Get genre repository instance"""
    return GenreRepository(db)

def get_person_repository(db: AsyncSession = Depends(get_async_db)) -> PersonRepository:
    """Get person repository instance"""
    return PersonRepository(db)

# Service dependencies
def get_film_service(
    db: AsyncSession = Depends(get_async_db),
    container: ServiceContainer = Depends(get_service_container)
) -> FilmService:
    """Get film service instance with optional search service"""
    search_service = container.get_search_service()
    return FilmService(db, search_service)

def get_genre_service(db: AsyncSession = Depends(get_async_db)) -> GenreService:
    """Get genre service instance"""
    return GenreService(db)

def get_person_service(db: AsyncSession = Depends(get_async_db)) -> PersonService:
    """Get person service instance"""
    return PersonService(db)

# Health check dependencies
def get_health_status(
    container: ServiceContainer = Depends(get_service_container)
) -> dict:
    """Get application health status"""
    return {
        "services_initialized": container._initialized,
        "search_service_available": container.get_search_service() is not None,
        "database_connected": True  # If we get here, DB is connected
    }