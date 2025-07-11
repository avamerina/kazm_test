from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
import logging

from main_app.core.dependencies import get_genre_service
from main_app.core.services import GenreService
from main_app import schemas

logger = logging.getLogger('films_api')

router = APIRouter()

@router.get("/", response_model=List[schemas.GenreResponse])
async def get_genres(
    page_size: int = Query(100, ge=1, le=200, description="Number of items per page"),
    page_number: int = Query(1, ge=1, description="Page number"),
    genre_service: GenreService = Depends(get_genre_service)
):
    """
    Get list of all genres.
    """
    logger.info(f"Requested genres list: page={page_number}, size={page_size}")
    skip = (page_number - 1) * page_size
    
    genres = await genre_service.get_genres(skip=skip, limit=page_size)
    
    return [
        {
            "uuid": str(genre.id),
            "name": genre.name,
            "description": genre.description
        }
        for genre in genres
    ]

@router.get("/{genre_id}/", response_model=schemas.GenreResponse)
async def get_genre_detail(
    genre_id: uuid.UUID, 
    genre_service: GenreService = Depends(get_genre_service)
):
    """
    Get detailed information about a specific genre.
    """
    genre = await genre_service.get_genre(genre_id)
    if not genre:
        logger.warning(f"Requested missing genre: {genre_id}")
        raise HTTPException(status_code=404, detail="Genre not found")
    logger.info(f"Viewed genre detail: {genre_id}")
    
    return {
        "uuid": str(genre.id),
        "name": genre.name,
        "description": genre.description
    }

@router.post("/", response_model=schemas.GenreResponse)
async def create_genre(
    genre: schemas.GenreCreate, 
    genre_service: GenreService = Depends(get_genre_service)
):
    """
    Create a new genre.
    """
    logger.info(f"Creating genre: {genre}")
    return await genre_service.create_genre(genre)

@router.put("/{genre_id}/", response_model=schemas.GenreResponse)
async def update_genre(
    genre_id: uuid.UUID,
    genre: schemas.GenreUpdate,
    genre_service: GenreService = Depends(get_genre_service)
):
    """
    Update genre information.
    """
    db_genre = await genre_service.update_genre(genre_id, genre)
    if not db_genre:
        logger.warning(f"Tried to update missing genre: {genre_id}")
        raise HTTPException(status_code=404, detail="Genre not found")
    logger.info(f"Updated genre: {genre_id}")
    return db_genre

@router.delete("/{genre_id}/")
async def delete_genre(
    genre_id: uuid.UUID, 
    genre_service: GenreService = Depends(get_genre_service)
):
    """
    Delete a genre.
    """
    success = await genre_service.delete_genre(genre_id)
    if not success:
        logger.warning(f"Tried to delete missing genre: {genre_id}")
        raise HTTPException(status_code=404, detail="Genre not found")
    logger.info(f"Deleted genre: {genre_id}")
    return {"message": "Genre deleted successfully"} 