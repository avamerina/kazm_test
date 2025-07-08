import pytest
from httpx import AsyncClient
from main import app
from unittest.mock import AsyncMock

VALID_UUID = "550e8400-e29b-41d4-a716-446655440000"  # valid v4 UUID

class MockFilmService:
    async def get_films(self, *args, **kwargs):
        return [type("Film", (), {"id": VALID_UUID, "title": "Test Film", "rating": 8.5, "type": "movie", "description": "desc", "creation_date": "2023-01-01"})()]
    async def search_films(self, *args, **kwargs):
        return [type("Film", (), {"id": VALID_UUID, "title": "Test Film", "rating": 8.5, "type": "movie", "description": "desc", "creation_date": "2023-01-01"})()]
    async def create_film(self, film):
        return {"uuid": VALID_UUID, "title": film.title, "imdb_rating": film.rating if hasattr(film, 'rating') else 7.0, "type": film.type, "description": getattr(film, 'description', 'desc'), "creation_date": getattr(film, 'creation_date', '2023-01-01')}
    async def update_film(self, film_id, film):
        if str(film_id) == VALID_UUID:
            return {"uuid": VALID_UUID, "title": film.title, "imdb_rating": film.rating if hasattr(film, 'rating') else 7.0, "type": film.type, "description": getattr(film, 'description', 'desc'), "creation_date": getattr(film, 'creation_date', '2023-01-01')}
        return None
    async def delete_film(self, film_id):
        return str(film_id) == VALID_UUID
    async def delete(self, film_id):
        return await self.delete_film(film_id)

@pytest.fixture(autouse=True)
def override_films_dependency():
    from main_app.core.dependencies import get_film_service
    app.dependency_overrides[get_film_service] = lambda: MockFilmService()
    yield
    app.dependency_overrides = {}

@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.unit
async def test_films_list():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/films/")
    assert response.status_code == 200
    assert response.json()[0]["title"] == "Test Film"

@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.unit
async def test_films_search():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/films/search/?query=test")
    assert response.status_code == 200
    assert response.json()[0]["title"] == "Test Film"

@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.unit
async def test_films_create():
    payload = {"title": "New Film", "description": "desc", "creation_date": "2023-01-01", "rating": 7.0, "type": "movie"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/films/", json=payload)
    assert response.status_code == 200
    assert response.json()["title"] == "New Film"
    assert response.json()["type"] == "movie"

@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.unit
async def test_films_update():
    payload = {"title": "Updated Film", "description": "desc", "creation_date": "2023-01-01", "rating": 7.0, "type": "movie"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(f"/api/v1/films/{VALID_UUID}/", json=payload)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Film"
    assert response.json()["type"] == "movie"

@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.unit
async def test_films_delete():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(f"/api/v1/films/{VALID_UUID}/")
    assert response.status_code == 200
    assert response.json()["message"] == "Film deleted successfully" 