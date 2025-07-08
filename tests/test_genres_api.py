import pytest
from httpx import AsyncClient
from main import app
from unittest.mock import AsyncMock

VALID_UUID = "550e8400-e29b-41d4-a716-446655440000"

class MockGenreService:
    async def get_genres(self, *args, **kwargs):
        return [type("Genre", (), {"id": VALID_UUID, "name": "Test Genre", "description": "Desc"})()]
    async def create_genre(self, genre):
        return {"uuid": VALID_UUID, "name": genre.name, "description": genre.description}
    async def update_genre(self, genre_id, genre):
        if str(genre_id) == VALID_UUID:
            return {"uuid": VALID_UUID, "name": genre.name, "description": genre.description}
        return None
    async def delete_genre(self, genre_id):
        return str(genre_id) == VALID_UUID

@pytest.fixture(autouse=True)
def override_genres_dependency():
    from main_app.core.dependencies import get_genre_service
    app.dependency_overrides[get_genre_service] = lambda: MockGenreService()
    yield
    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_genres_list():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/genres/")
    assert response.status_code == 200
    assert response.json()[0]["name"] == "Test Genre"

@pytest.mark.asyncio
async def test_genres_create():
    payload = {"name": "New Genre", "description": "desc"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/genres/", json=payload)
    assert response.status_code == 200
    assert response.json()["name"] == "New Genre"

@pytest.mark.asyncio
async def test_genres_update():
    payload = {"name": "Updated Genre", "description": "desc"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(f"/api/v1/genres/{VALID_UUID}/", json=payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Genre"

@pytest.mark.asyncio
async def test_genres_delete():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(f"/api/v1/genres/{VALID_UUID}/")
    assert response.status_code == 200
    assert response.json()["message"] == "Genre deleted successfully" 