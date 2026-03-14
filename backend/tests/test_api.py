import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from backend.config import settings
from backend.database import init_db


@pytest_asyncio.fixture
async def client(tmp_path):
    """Create test client with isolated database."""
    test_db = str(tmp_path / "test.db")
    settings.database_path = test_db
    await init_db()

    # Import app after settings override to pick up test DB
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_list_projects_empty(client):
    resp = await client.get("/api/projects/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["projects"] == []
    assert data["count"] == 0


@pytest.mark.asyncio
async def test_get_project_not_found(client):
    resp = await client.get("/api/projects/999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_project_state_not_found(client):
    resp = await client.get("/api/projects/999/state")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_dashboard_empty(client):
    resp = await client.get("/api/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert data["projects"] == []
    assert data["count"] == 0


@pytest.mark.asyncio
async def test_register_project_invalid_path(client):
    resp = await client.post(
        "/api/projects/",
        json={"name": "test", "path": "/nonexistent/path"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_and_list_project(client, tmp_path):
    # Create a fake .paul directory
    paul_dir = tmp_path / "myproject" / ".paul"
    paul_dir.mkdir(parents=True)

    resp = await client.post(
        "/api/projects/",
        json={"name": "My Project", "path": str(tmp_path / "myproject")},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "My Project"
    assert "id" in data

    # List should now have 1 project
    resp = await client.get("/api/projects/")
    assert resp.status_code == 200
    assert resp.json()["count"] == 1


@pytest.mark.asyncio
async def test_delete_project(client, tmp_path):
    paul_dir = tmp_path / "delme" / ".paul"
    paul_dir.mkdir(parents=True)

    resp = await client.post(
        "/api/projects/",
        json={"name": "Delete Me", "path": str(tmp_path / "delme")},
    )
    project_id = resp.json()["id"]

    resp = await client.delete(f"/api/projects/{project_id}")
    assert resp.status_code == 204

    resp = await client.get(f"/api/projects/{project_id}")
    assert resp.status_code == 404
