from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
import logging

from main_app.core.repositories import FilmRepository, GenreRepository, PersonRepository
from main_app.core.services import FilmService, GenreService, PersonService, SearchService


class AsyncUnitOfWork:
    """Async Unit of Work implementation"""
    
    def __init__(self, session, search_service: Optional[SearchService] = None):
        self.session = session
        self.search_service = search_service
        self.logger = logging.getLogger(__name__)
        
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
            self.logger.error(f"Transaction rolled back due to exception: {exc_type.__name__}: {exc_val}")
        else:
            await self.commit()
            self.logger.info("Transaction committed successfully.")
    
    async def commit(self):
        await self.session.commit()
        self.logger.debug("Session commit executed.")
    
    async def rollback(self):
        await self.session.rollback()
        self.logger.debug("Session rollback executed.")


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
            except Exception as e:
                await uow.rollback()
                logging.getLogger(__name__).exception("Exception in UnitOfWorkProvider.get_uow: %s", e)
                raise
            else:
                await uow.commit()
                logging.getLogger(__name__).info("UnitOfWorkProvider: Transaction committed.")


# Factory function for creating Unit of Work
def create_uow_provider(session_factory, search_service: Optional[SearchService] = None) -> UnitOfWorkProvider:
    """Create a Unit of Work provider"""
    return UnitOfWorkProvider(session_factory, search_service) 