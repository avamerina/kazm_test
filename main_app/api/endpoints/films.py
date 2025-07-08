from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
import logging

from main_app.core.dependencies import get_film_service
from main_app.core.services import FilmService
from main_app import schemas

logger = logging.getLogger('films_api')

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_films(
    sort: str = Query("-rating", description="Sort field with prefix - for descending"),
    page_size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    page_number: int = Query(1, ge=1, description="Page number"),
    genre: Optional[uuid.UUID] = Query(None, description="Filter by genre UUID"),
    film_service: FilmService = Depends(get_film_service),
    request: Request = None
):
    """
    Get list of films with optional filtering and sorting.
    """
    user = request.headers.get('X-User', 'anonymous') if request else 'anonymous'
    logger.info(f"User {user} requested films list: sort={sort}, page={page_number}, size={page_size}, genre={genre}")
    skip = (page_number - 1) * page_size
    
    films = await film_service.get_films(
        skip=skip,
        limit=page_size,
        sort_by=sort,
        genre_id=genre
    )
    
    return [
        {
            "uuid": str(film.id),
            "title": film.title,
            "imdb_rating": film.rating
        }
        for film in films
    ]

@router.get("/search/", response_model=List[dict])
async def search_films(
    query: str = Query(..., description="Search query"),
    page_number: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    film_service: FilmService = Depends(get_film_service)
):
    """
    Search films by title.
    """
    skip = (page_number - 1) * page_size
    
    films = await film_service.search_films(query=query, skip=skip, limit=page_size)
    
    return [
        {
            "uuid": str(film.id),
            "title": film.title,
            "imdb_rating": film.rating
        }
        for film in films
    ]


@router.get("/{film_id}/", response_model=dict)
async def get_film_detail(
    film_id: uuid.UUID, 
    film_service: FilmService = Depends(get_film_service),
    request: Request = None
):
    """
    Get detailed information about a specific film.
    """
    user = request.headers.get('X-User', 'anonymous') if request else 'anonymous'
    film_detail = await film_service.get_film_detail(film_id)
    if not film_detail:
        logger.warning(f"User {user} requested missing film: {film_id}")
        raise HTTPException(status_code=404, detail="Film not found")
    logger.info(f"User {user} viewed film detail: {film_id}")
    return film_detail

@router.post("/", response_model=schemas.FilmResponse)
async def create_film(
    film: schemas.FilmCreate, 
    film_service: FilmService = Depends(get_film_service),
    request: Request = None
):
    """
    Create a new film.
    """
    user = request.headers.get('X-User', 'anonymous') if request else 'anonymous'
    logger.info(f"User {user} creating film: {film}")
    return await film_service.create_film(film)

@router.put("/{film_id}/", response_model=schemas.FilmResponse)
async def update_film(
    film_id: uuid.UUID,
    film: schemas.FilmUpdate,
    film_service: FilmService = Depends(get_film_service),
    request: Request = None
):
    """
    Update film information.
    """
    user = request.headers.get('X-User', 'anonymous') if request else 'anonymous'
    db_film = await film_service.update_film(film_id, film)
    if not db_film:
        logger.warning(f"User {user} tried to update missing film: {film_id}")
        raise HTTPException(status_code=404, detail="Film not found")
    logger.info(f"User {user} updated film: {film_id}")
    return db_film

@router.delete("/{film_id}/")
async def delete_film(
    film_id: uuid.UUID, 
    film_service: FilmService = Depends(get_film_service),
    request: Request = None
):
    """
    Delete a film.
    """
    user = request.headers.get('X-User', 'anonymous') if request else 'anonymous'
    success = await film_service.delete(film_id)
    if not success:
        logger.warning(f"User {user} tried to delete missing film: {film_id}")
        raise HTTPException(status_code=404, detail="Film not found")
    logger.info(f"User {user} deleted film: {film_id}")
    return {"message": "Film deleted successfully"} 