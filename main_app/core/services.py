from abc import ABC
from typing import List, Optional, Tuple, Protocol, Dict, Any, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import logging

from .repositories import BaseRepository, FilmRepository, GenreRepository, PersonRepository
from .. import models, schemas

T = TypeVar('T', bound=models.Base)
CreateSchema = TypeVar('CreateSchema')
UpdateSchema = TypeVar('UpdateSchema')


class SearchService(Protocol):
    """Protocol for search service dependency injection"""

    async def search_by_description(
            self,
            user_description: str,
            db: AsyncSession,
            limit: int = 10
    ) -> List[Tuple[models.FilmWork, float]]:
        """Search films by semantic similarity"""
        ...


class BaseService(ABC, Generic[T]):
    """Abstract base service for business logic"""

    def __init__(self, session: AsyncSession, repository: BaseRepository[T]):
        self.session = session
        self.repository = repository
        self.logger = logging.getLogger('films_api')

    async def get_all(self, skip: int = 0, limit: int = 50, **filters) -> List[T]:
        """Get all entities with pagination and filtering"""
        return await self.repository.get_all(skip=skip, limit=limit, **filters)

    async def get_by_id(self, entity_id: uuid.UUID, load_relationships: bool = False) -> Optional[T]:
        """Get entity by ID"""
        return await self.repository.get_by_id(entity_id, load_relationships=load_relationships)

    async def create(self, entity_data: Dict[str, Any], user: str = 'anonymous') -> T:
        """Create new entity"""
        entity = await self.repository.create(entity_data)
        self.logger.info(f"User {user} created {self.repository.model.__name__}: {entity}")
        return entity

    async def update(self, entity_id: uuid.UUID, entity_data: Dict[str, Any], user: str = 'anonymous') -> Optional[T]:
        """Update entity"""
        entity = await self.repository.update(entity_id, entity_data)
        if entity:
            self.logger.info(f"User {user} updated {self.repository.model.__name__} {entity_id}")
        else:
            self.logger.warning(f"User {user} tried to update missing {self.repository.model.__name__} {entity_id}")
        return entity

    async def delete(self, entity_id: uuid.UUID, user: str = 'anonymous') -> bool:
        """Delete entity"""
        result = await self.repository.delete(entity_id)
        if result:
            self.logger.info(f"User {user} deleted {self.repository.model.__name__} {entity_id}")
        else:
            self.logger.warning(f"User {user} tried to delete missing {self.repository.model.__name__} {entity_id}")
        return result

    async def bulk_delete(self, entity_ids: List[uuid.UUID]) -> int:
        """Delete multiple entities"""
        return await self.repository.bulk_delete(entity_ids)

    async def count(self, **filters) -> int:
        """Count entities with optional filtering"""
        return await self.repository.count(**filters)

    def _convert_schema_to_dict(self, schema_obj) -> Dict[str, Any]:
        """Convert Pydantic schema to dict, handling exclude_unset"""
        if hasattr(schema_obj, 'dict'):
            return schema_obj.dict(exclude_unset=True)
        return schema_obj if isinstance(schema_obj, dict) else {}


class FilmService(BaseService[models.FilmWork]):
    """Service for Film business logic"""

    def __init__(self, session: AsyncSession, search_service: Optional[SearchService] = None):
        repository = FilmRepository(session)
        super().__init__(session, repository)
        self.search_service = search_service

    async def get_films(
            self,
            skip: int = 0,
            limit: int = 50,
            sort_by: str = "-rating",
            genre_id: Optional[uuid.UUID] = None
    ) -> List[models.FilmWork]:
        """Get films with filtering and sorting"""
        return await self.repository.get_all(skip=skip, limit=limit, sort_by=sort_by, genre_id=genre_id)

    async def get_film(self, film_id: uuid.UUID) -> Optional[models.FilmWork]:
        """Get film by ID with related data"""
        return await self.repository.get_by_id(film_id, load_relationships=True)

    async def create_film(self, film_data: schemas.FilmCreate) -> models.FilmWork:
        """Create new film"""
        data_dict = self._convert_schema_to_dict(film_data)
        return await self.create(data_dict)

    async def update_film(self, film_id: uuid.UUID, film_data: schemas.FilmUpdate) -> Optional[models.FilmWork]:
        """Update film"""
        data_dict = self._convert_schema_to_dict(film_data)
        return await self.update(film_id, data_dict)

    async def search_films(self, query: str, skip: int = 0, limit: int = 50) -> List[models.FilmWork]:
        """Search films by title"""
        return await self.repository.search_by_title(query, skip, limit)

    async def get_film_detail(self, film_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Get detailed film information with related data"""
        film = await self.get_film(film_id)
        if not film:
            return None

        # Get persons by role
        actors = await self.repository.get_persons_by_role(film_id, "actor")
        writers = await self.repository.get_persons_by_role(film_id, "writer")
        directors = await self.repository.get_persons_by_role(film_id, "director")

        return {
            "uuid": str(film.id),
            "title": film.title,
            "imdb_rating": film.rating,
            "description": film.description,
            "genre": [
                {"uuid": str(genre.id), "name": genre.name}
                for genre in film.genres
            ],
            "actors": [
                {"uuid": str(actor.id), "full_name": actor.full_name}
                for actor in actors
            ],
            "writers": [
                {"uuid": str(writer.id), "full_name": writer.full_name}
                for writer in writers
            ],
            "directors": [
                {"uuid": str(director.id), "full_name": director.full_name}
                for director in directors
            ]
        }

    async def get_films_by_genre(self, genre_id: uuid.UUID, skip: int = 0, limit: int = 50) -> List[models.FilmWork]:
        """Get films filtered by genre"""
        return await self.get_films(skip=skip, limit=limit, genre_id=genre_id)


class GenreService(BaseService[models.Genre]):
    """Service for Genre business logic"""

    def __init__(self, session: AsyncSession):
        repository = GenreRepository(session)
        super().__init__(session, repository)

    async def get_genres(self, skip: int = 0, limit: int = 100) -> List[models.Genre]:
        """Get all genres"""
        return await self.get_all(skip=skip, limit=limit)

    async def get_genre(self, genre_id: uuid.UUID) -> Optional[models.Genre]:
        """Get genre by ID"""
        return await self.get_by_id(genre_id)

    async def create_genre(self, genre_data: schemas.GenreCreate) -> models.Genre:
        """Create new genre"""
        data_dict = self._convert_schema_to_dict(genre_data)
        return await self.create(data_dict)

    async def update_genre(self, genre_id: uuid.UUID, genre_data: schemas.GenreUpdate) -> Optional[models.Genre]:
        """Update genre"""
        data_dict = self._convert_schema_to_dict(genre_data)
        return await self.update(genre_id, data_dict)

    async def delete_genre(self, genre_id: uuid.UUID) -> bool:
        """Delete genre"""
        return await self.delete(genre_id)


class PersonService(BaseService[models.Person]):
    """Service for Person business logic"""

    def __init__(self, session: AsyncSession):
        repository = PersonRepository(session)
        super().__init__(session, repository)

    async def get_persons(self, skip: int = 0, limit: int = 50) -> List[models.Person]:
        """Get all persons"""
        return await self.get_all(skip=skip, limit=limit)

    async def get_person(self, person_id: uuid.UUID) -> Optional[models.Person]:
        """Get person by ID with related films"""
        return await self.get_by_id(person_id, load_relationships=True)

    async def create_person(self, person_data: schemas.PersonCreate) -> models.Person:
        """Create new person"""
        data_dict = self._convert_schema_to_dict(person_data)
        return await self.create(data_dict)

    async def update_person(self, person_id: uuid.UUID, person_data: schemas.PersonUpdate) -> Optional[models.Person]:
        """Update person"""
        data_dict = self._convert_schema_to_dict(person_data)
        return await self.update(person_id, data_dict)

    async def delete_person(self, person_id: uuid.UUID) -> bool:
        """Delete person"""
        return await self.delete(person_id)

    async def search_persons(self, query: str, skip: int = 0, limit: int = 50) -> List[models.Person]:
        """Search persons by name"""
        return await self.repository.search_by_name(query, skip, limit)

    async def get_person_films(self, person_id: uuid.UUID, skip: int = 0, limit: int = 50) -> List[models.FilmWork]:
        """Get films by person"""
        return await self.repository.get_films_by_person(person_id, skip, limit)


# Utility service for common operations
class CRUDService(BaseService[T]):
    """Generic CRUD service for simple entities"""

    def __init__(self, session: AsyncSession, repository: BaseRepository[T]):
        super().__init__(session, repository)

    async def create_from_schema(self, schema_obj) -> T:
        """Create entity from Pydantic schema"""
        data_dict = self._convert_schema_to_dict(schema_obj)
        return await self.create(data_dict)

    async def update_from_schema(self, entity_id: uuid.UUID, schema_obj) -> Optional[T]:
        """Update entity from Pydantic schema"""
        data_dict = self._convert_schema_to_dict(schema_obj)
        return await self.update(entity_id, data_dict)

    async def get_paginated(self, page: int, page_size: int, **filters) -> Dict[str, Any]:
        """Get paginated results with metadata"""
        skip = (page - 1) * page_size
        entities = await self.get_all(skip=skip, limit=page_size, **filters)
        total = await self.count(**filters)

        return {
            "items": entities,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }