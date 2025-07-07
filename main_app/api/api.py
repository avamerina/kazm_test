from fastapi import APIRouter
from main_app.api.endpoints import films, persons, genres

api_router = APIRouter()

api_router.include_router(films.router, prefix="/films", tags=["films"])
api_router.include_router(persons.router, prefix="/persons", tags=["persons"])
api_router.include_router(genres.router, prefix="/genres", tags=["genres"])