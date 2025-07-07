from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid

from main_app.core.dependencies import get_person_service
from main_app.core.services import PersonService
from main_app import schemas

router = APIRouter()

@router.get("/search/", response_model=List[dict])
async def search_persons(
    query: str = Query(..., description="Search query"),
    page_number: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    person_service: PersonService = Depends(get_person_service)
):
    """
    Search persons by name.
    """
    skip = (page_number - 1) * page_size
    
    persons = await person_service.search_persons(query=query, skip=skip, limit=page_size)
    
    return [
        {
            "uuid": str(person.id),
            "full_name": person.full_name
        }
        for person in persons
    ]

@router.get("/{person_id}/", response_model=dict)
async def get_person_detail(
    person_id: uuid.UUID, 
    person_service: PersonService = Depends(get_person_service)
):
    """
    Get detailed information about a specific person.
    """
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    return {
        "uuid": str(person.id),
        "full_name": person.full_name,
        "films": [
            {
                "uuid": str(film.id),
                "title": film.title,
                "imdb_rating": film.rating
            }
            for film in person.films
        ]
    }

@router.get("/{person_id}/film/", response_model=List[dict])
async def get_person_films(
    person_id: uuid.UUID,
    page_number: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    person_service: PersonService = Depends(get_person_service)
):
    """
    Get films by person.
    """
    skip = (page_number - 1) * page_size
    
    films = await person_service.get_person_films(person_id, skip=skip, limit=page_size)
    
    return [
        {
            "uuid": str(film.id),
            "title": film.title,
            "imdb_rating": film.rating
        }
        for film in films
    ]

@router.post("/", response_model=schemas.PersonResponse)
async def create_person(
    person: schemas.PersonCreate, 
    person_service: PersonService = Depends(get_person_service)
):
    """
    Create a new person.
    """
    return await person_service.create_person(person)

@router.put("/{person_id}/", response_model=schemas.PersonResponse)
async def update_person(
    person_id: uuid.UUID,
    person: schemas.PersonUpdate,
    person_service: PersonService = Depends(get_person_service)
):
    """
    Update person information.
    """
    db_person = await person_service.update_person(person_id, person)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    return db_person

@router.delete("/{person_id}/")
async def delete_person(
    person_id: uuid.UUID, 
    person_service: PersonService = Depends(get_person_service)
):
    """
    Delete a person.
    """
    success = await person_service.delete_person(person_id)
    if not success:
        raise HTTPException(status_code=404, detail="Person not found")
    return {"message": "Person deleted successfully"} 