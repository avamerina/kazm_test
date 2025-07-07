from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from main_app.core.dependencies import get_film_service
from main_app.core.services import FilmService
from main_app import schemas

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_films(
    sort: str = Query("-rating", description="Sort field with prefix - for descending"),
    page_size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    page_number: int = Query(1, ge=1, description="Page number"),
    genre: Optional[uuid.UUID] = Query(None, description="Filter by genre UUID"),
    film_service: FilmService = Depends(get_film_service)
):
    """
    Get list of films with optional filtering and sorting.
    """
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
    film_service: FilmService = Depends(get_film_service)
):
    """
    Get detailed information about a specific film.
    """
    film_detail = await film_service.get_film_detail(film_id)
    if not film_detail:
        raise HTTPException(status_code=404, detail="Film not found")
    
    return film_detail

@router.post("/", response_model=schemas.FilmResponse)
async def create_film(
    film: schemas.FilmCreate, 
    film_service: FilmService = Depends(get_film_service)
):
    """
    Create a new film.
    """
    return await film_service.create_film(film)

@router.put("/{film_id}/", response_model=schemas.FilmResponse)
async def update_film(
    film_id: uuid.UUID,
    film: schemas.FilmUpdate,
    film_service: FilmService = Depends(get_film_service)
):
    """
    Update film information.
    """
    db_film = await film_service.update_film(film_id, film)
    if not db_film:
        raise HTTPException(status_code=404, detail="Film not found")
    return db_film

@router.delete("/{film_id}/")
async def delete_film(
    film_id: uuid.UUID, 
    film_service: FilmService = Depends(get_film_service)
):
    """
    Delete a film.
    """
    success = await film_service.delete_film(film_id)
    if not success:
        raise HTTPException(status_code=404, detail="Film not found")
    return {"message": "Film deleted successfully"} 