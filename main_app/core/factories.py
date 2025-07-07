from typing import Optional

from main_app.core.services import FilmService, GenreService, PersonService, SearchService
from main_app.core.repositories import FilmRepository, GenreRepository, PersonRepository


class ServiceFactory:
    """Factory for creating services with dependency injection"""
    
    def __init__(self, search_service: Optional[SearchService] = None):
        self.search_service = search_service
    
    def create_film_service(self, session) -> FilmService:
        """Create a FilmService instance"""
        return FilmService(session, self.search_service)
    
    def create_genre_service(self, session) -> GenreService:
        """Create a GenreService instance"""
        return GenreService(session)
    
    def create_person_service(self, session) -> PersonService:
        """Create a PersonService instance"""
        return PersonService(session)
    
    def set_search_service(self, search_service: Optional[SearchService]):
        """Set the search service for dependency injection"""
        self.search_service = search_service



class RepositoryFactory:
    """Factory for creating repositories"""
    
    @staticmethod
    def create_film_repository(session) -> FilmRepository:
        """Create a FilmRepository instance"""
        return FilmRepository(session)
    
    @staticmethod
    def create_genre_repository(session) -> GenreRepository:
        """Create a GenreRepository instance"""
        return GenreRepository(session)
    
    @staticmethod
    def create_person_repository(session) -> PersonRepository:
        """Create a PersonRepository instance"""
        return PersonRepository(session)


# Global factory instances
service_factory = ServiceFactory()
repository_factory = RepositoryFactory()


def configure_service_factory(search_service: Optional[SearchService]):
    """Configure the global service factory with dependencies"""
    service_factory.set_search_service(search_service) 