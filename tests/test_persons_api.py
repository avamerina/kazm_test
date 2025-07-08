import pytest
from httpx import AsyncClient
from main import app
from unittest.mock import AsyncMock

VALID_UUID = "550e8400-e29b-41d4-a716-446655440000"

class MockPersonService:
    async def search_persons(self, *args, **kwargs):
        return [type("Person", (), {"id": VALID_UUID, "full_name": "Test Person"})()]
    async def create_person(self, person):
        return {"uuid": VALID_UUID, "full_name": person.full_name}
    async def update_person(self, person_id, person):
        if str(person_id) == VALID_UUID:
            return {"uuid": VALID_UUID, "full_name": person.full_name}
        return None
    async def delete_person(self, person_id):
        return str(person_id) == VALID_UUID

@pytest.fixture(autouse=True)
def override_persons_dependency():
    from main_app.core.dependencies import get_person_service
    app.dependency_overrides[get_person_service] = lambda: MockPersonService()
    yield
    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_persons_search():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/persons/search/?query=test")
    assert response.status_code == 200
    assert response.json()[0]["full_name"] == "Test Person"

@pytest.mark.asyncio
async def test_persons_create():
    payload = {"full_name": "New Person"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/persons/", json=payload)
    assert response.status_code == 200
    assert response.json()["full_name"] == "New Person"

@pytest.mark.asyncio
async def test_persons_update():
    payload = {"full_name": "Updated Person"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(f"/api/v1/persons/{VALID_UUID}/", json=payload)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Person"

@pytest.mark.asyncio
async def test_persons_delete():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(f"/api/v1/persons/{VALID_UUID}/")
    assert response.status_code == 200
    assert response.json()["message"] == "Person deleted successfully" 