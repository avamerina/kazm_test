from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from main_app.api import api
from main_app.core.config import config_provider
from main_app.core.dependencies import get_service_container

# Get configuration
config = config_provider.settings

app = FastAPI(
    title=config.project_name,
    description="""
    REST API for managing films, persons, and genres.

    ## Features

    * **Films**: Get popular films, search films, get film details, CRUD operations
    * **Persons**: Search persons, get person details, get films by person, CRUD operations
    * **Genres**: Get all genres, get genre details, CRUD operations

    ## Architecture

    This API uses:
    * **Dependency Injection**: Clean separation of concerns with service layer
    * **Repository Pattern**: Abstract data access layer
    * **Service Layer**: Business logic encapsulation
    * **Async/Await**: Full asynchronous support for better performance

    ## API Endpoints

    ### Films
    * `GET /api/v1/films/` - Get list of films with filtering and sorting
    * `GET /api/v1/films/search/` - Search films by title
    * `GET /api/v1/films/{film_id}/` - Get detailed film information
    * `POST /api/v1/films/` - Create a new film
    * `PUT /api/v1/films/{film_id}/` - Update film information
    * `DELETE /api/v1/films/{film_id}/` - Delete a film

    ### Persons
    * `GET /api/v1/persons/search/` - Search persons by name
    * `GET /api/v1/persons/{person_id}/` - Get detailed person information
    * `GET /api/v1/persons/{person_id}/film/` - Get films by person
    * `POST /api/v1/persons/` - Create a new person
    * `PUT /api/v1/persons/{person_id}/` - Update person information
    * `DELETE /api/v1/persons/{person_id}/` - Delete a person

    ### Genres
    * `GET /api/v1/genres/` - Get list of all genres
    * `GET /api/v1/genres/{genre_id}/` - Get detailed genre information
    * `POST /api/v1/genres/` - Create a new genre
    * `PUT /api/v1/genres/{genre_id}/` - Update genre information
    * `DELETE /api/v1/genres/{genre_id}/` - Delete a genre
    """,
    version=config.version
)

# Add CORS middleware with config
cors_config = config_provider.get_cors_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config["allow_origins"],
    allow_credentials=cors_config["allow_credentials"],
    allow_methods=cors_config["allow_methods"],
    allow_headers=cors_config["allow_headers"],
)

# Include API router with config prefix
app.include_router(api.api_router, prefix=config_provider.get_api_prefix())


@app.on_event("startup")
async def startup_event():
    # Initialize the service container (async)
    container = get_service_container()
    await container.initialize()
    print("Service container initialized.")


@app.on_event("shutdown")
async def shutdown_event():
    # Cleanup the service container (async)
    container = get_service_container()
    await container.cleanup()
    print("Service container cleaned up.")


@app.get("/")
def read_root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Welcome to Films API",
        "version": config.version,
        "architecture": "Dependency Injection + Repository Pattern + Service Layer",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)