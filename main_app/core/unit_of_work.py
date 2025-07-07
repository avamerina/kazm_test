from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from main_app.core.repositories import FilmRepository, GenreRepository, PersonRepository
from main_app.core.services import FilmService, GenreService, PersonService, SearchService


class AsyncUnitOfWork:
    """Async Unit of Work implementation"""
    
    def __init__(self, session, search_service: Optional[SearchService] = None):
        self.session = session
        self.search_service = search_service
        
        # Initialize repositories
        self.films = FilmRepository(session)
        self.genres = GenreRepository(session)
        self.persons = PersonRepository(session)
        
        # Initialize services
        self.film_service = FilmService(session, search_service)
        self.genre_service = GenreService(session)
        self.person_service = PersonService(session)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
    
    async def commit(self):
        await self.session.commit()
    
    async def rollback(self):
        await self.session.rollback()


class UnitOfWorkProvider:
    """Provider for Unit of Work with dependency injection"""
    
    def __init__(self, session_factory, search_service: Optional[SearchService] = None):
        self.session_factory = session_factory
        self.search_service = search_service
    
    @asynccontextmanager
    async def get_uow(self) -> AsyncGenerator[AsyncUnitOfWork, None]:
        """Get a Unit of Work instance"""
        async with self.session_factory() as session:
            uow = AsyncUnitOfWork(session, self.search_service)
            try:
                yield uow
            except Exception:
                await uow.rollback()
                raise
            else:
                await uow.commit()


# Factory function for creating Unit of Work
def create_uow_provider(session_factory, search_service: Optional[SearchService] = None) -> UnitOfWorkProvider:
    """Create a Unit of Work provider"""
    return UnitOfWorkProvider(session_factory, search_service) 