from abc import ABC
from typing import List, Optional, TypeVar, Generic, Dict, Any, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc, delete as sql_delete
from sqlalchemy.orm import selectinload
import uuid
import logging

from .. import models, schemas

T = TypeVar('T', bound=models.Base)


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository for all entities"""

    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model
        self.logger = logging.getLogger(__name__)

    async def get_by_id(self, entity_id: uuid.UUID, load_relationships: bool = False) -> Optional[T]:
        """Get entity by ID with optional relationship loading"""
        query = select(self.model).where(self.model.id == entity_id)

        if load_relationships:
            query = self._add_relationship_loading(query)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 50, **filters) -> List[T]:
        """Get all entities with pagination and optional filtering"""
        query = select(self.model)

        # Apply filters
        for field, value in filters.items():
            if hasattr(self.model, field) and value is not None:
                query = query.where(getattr(self.model, field) == value)

        # Apply sorting if model has default sort field
        if hasattr(self, '_default_sort_field'):
            sort_field = getattr(self.model, self._default_sort_field)
            query = query.order_by(desc(sort_field))

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, entity_data: Dict[str, Any]) -> T:
        """Create new entity"""
        # Filter out None values and invalid fields
        cleaned_data = self._clean_entity_data(entity_data)

        db_entity = self.model(**cleaned_data)
        self.session.add(db_entity)
        await self.session.commit()
        await self.session.refresh(db_entity)
        return db_entity

    async def update(self, entity_id: uuid.UUID, entity_data: Dict[str, Any]) -> Optional[T]:
        """Update entity"""
        db_entity = await self.get_by_id(entity_id)
        if not db_entity:
            self.logger.warning(f"Update failed: {self.model.__name__} with id {entity_id} not found.")
            return None

        cleaned_data = self._clean_entity_data(entity_data)

        for field, value in cleaned_data.items():
            if hasattr(db_entity, field):
                setattr(db_entity, field, value)

        await self.session.commit()
        await self.session.refresh(db_entity)
        return db_entity

    async def delete(self, entity_id: uuid.UUID) -> bool:
        """Delete entity"""
        db_entity = await self.get_by_id(entity_id)
        if not db_entity:
            self.logger.warning(f"Delete failed: {self.model.__name__} with id {entity_id} not found.")
            return False

        await self.session.delete(db_entity)
        await self.session.commit()
        return True

    async def bulk_delete(self, entity_ids: List[uuid.UUID]) -> int:
        """Delete multiple entities by IDs"""
        query = sql_delete(self.model).where(self.model.id.in_(entity_ids))
        result = await self.session.execute(query)
        await self.session.commit()
        self.logger.info(f"Bulk delete: {result.rowcount} {self.model.__name__} entities deleted.")
        return result.rowcount

    async def count(self, **filters) -> int:
        """Count entities with optional filtering"""
        from sqlalchemy import func

        query = select(func.count(self.model.id))

        for field, value in filters.items():
            if hasattr(self.model, field) and value is not None:
                query = query.where(getattr(self.model, field) == value)

        result = await self.session.execute(query)
        return result.scalar()

    def _clean_entity_data(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean entity data by removing None values and invalid fields"""
        if not entity_data:
            return {}

        # Get valid model fields
        valid_fields = {col.name for col in self.model.__table__.columns}

        return {
            field: value
            for field, value in entity_data.items()
            if field in valid_fields and value is not None
        }

    def _add_relationship_loading(self, query):
        """Override in subclasses to add specific relationship loading"""
        return query

    async def search_by_field(self, field_name: str, search_term: str,
                              skip: int = 0, limit: int = 50) -> List[T]:
        """Generic search by field using ILIKE"""
        if not hasattr(self.model, field_name):
            return []

        field = getattr(self.model, field_name)
        query = select(self.model).where(
            field.ilike(f"%{search_term}%")
        ).offset(skip).limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()


class FilmRepository(BaseRepository[models.FilmWork]):
    """Repository for Film operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, models.FilmWork)
        self._default_sort_field = 'rating'

    def _add_relationship_loading(self, query):
        """Add film-specific relationship loading"""
        return query.options(
            selectinload(models.FilmWork.genres),
            selectinload(models.FilmWork.persons)
        )

    async def get_all(self, skip: int = 0, limit: int = 50,
                      sort_by: str = "-rating", genre_id: Optional[uuid.UUID] = None) -> List[models.FilmWork]:
        """Get all films with advanced sorting and filtering"""
        query = select(self.model)

        # Genre filtering
        if genre_id:
            query = query.join(models.genre_film_work).where(
                models.genre_film_work.c.genre_id == genre_id
            )

        # Dynamic sorting
        query = self._apply_sorting(query, sort_by)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    def _apply_sorting(self, query, sort_by: str):
        """Apply dynamic sorting to query"""
        sort_mapping = {
            'rating': models.FilmWork.rating,
            'creation_date': models.FilmWork.creation_date,
            'title': models.FilmWork.title
        }

        if sort_by.startswith("-"):
            field_name = sort_by[1:]
            if field_name in sort_mapping:
                query = query.order_by(desc(sort_mapping[field_name]))
        else:
            if sort_by in sort_mapping:
                query = query.order_by(asc(sort_mapping[sort_by]))

        return query

    async def search_by_title(self, query: str, skip: int = 0, limit: int = 50) -> List[models.FilmWork]:
        """Search films by title"""
        return await self.search_by_field('title', query, skip, limit)

    async def get_persons_by_role(self, film_id: uuid.UUID, role: str) -> List[models.Person]:
        """Get persons associated with film by role"""
        query = select(models.Person).join(models.person_film_work).where(
            models.person_film_work.c.film_work_id == film_id,
            models.person_film_work.c.role == role
        )
        result = await self.session.execute(query)
        return result.scalars().all()


class GenreRepository(BaseRepository[models.Genre]):
    """Repository for Genre operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, models.Genre)


class PersonRepository(BaseRepository[models.Person]):
    """Repository for Person operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(session, models.Person)

    def _add_relationship_loading(self, query):
        """Add person-specific relationship loading"""
        return query.options(selectinload(models.Person.films))

    async def search_by_name(self, query: str, skip: int = 0, limit: int = 50) -> List[models.Person]:
        """Search persons by name"""
        return await self.search_by_field('full_name', query, skip, limit)

    async def get_films_by_person(self, person_id: uuid.UUID, skip: int = 0, limit: int = 50) -> List[models.FilmWork]:
        """Get films associated with person"""
        query = select(models.FilmWork).join(models.person_film_work).where(
            models.person_film_work.c.person_id == person_id
        ).order_by(desc(models.FilmWork.rating)).offset(skip).limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()