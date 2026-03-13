import os
import tempfile

import aiosqlite
import pytest
from httpx import ASGITransport, AsyncClient

from backend.config import settings
from backend.database import init_db
from backend.main import app
from backend.models import create_project, upsert_project_state
from backend.parser_models import (
    LoopPosition,
    ParsedProject,
    ParsedRoadmap,
    ParsedState,
    ProjectFullState,
)


@pytest.fixture(autouse=True)
async def setup_test_db(tmp_path):
    """Use a temporary database for each test."""
    db_path = tmp_path / "test.db"
    original = settings.database_path
    settings.database_path = db_path
    await init_db()
    yield
    settings.database_path = original


@pytest.fixture
def transport():
    return ASGITransport(app=app, raise_app_exceptions=False)


@pytest.fixture
async def client(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def _register_project(db: aiosqlite.Connection, name: str, path: str) -> dict:
    return await create_project(db, name, path)


async def _sync_project(db: aiosqlite.Connection, project_id: int) -> None:
    parsed = ProjectFullState(
        state=ParsedState(
            milestone="v0.1 Foundation (v0.1.0)",
            phase_number=2,
            phase_total=4,
            phase_name="API & WebSocket",
            plan="02-01",
            status="APPLY in progress",
            loop=LoopPosition(plan=True, apply=False, unify=False, description="Executing"),
            progress_milestone=25.0,
            progress_phase=0.0,
            last_activity="2026-03-13",
            blockers=["Waiting on API design"],
        ),
        roadmap=ParsedRoadmap(
            milestone_name="v0.1 Foundation",
            milestone_version="v0.1.0",
            milestone_status="In Progress",
        ),
        project=ParsedProject(
            name="NORM",
            description="Real-time PALS monitoring",
            version="0.1.0",
            status="In Progress",
        ),
        synced_at="2026-03-13T12:00:00",
    )
    await upsert_project_state(db, project_id, parsed)


# --- Dashboard endpoint tests ---


async def test_dashboard_empty(client):
    resp = await client.get("/api/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 0
    assert data["projects"] == []


async def test_dashboard_with_project_no_state(client):
    # Create a project with a real .paul/ dir
    with tempfile.TemporaryDirectory() as tmpdir:
        paul_dir = os.path.join(tmpdir, ".paul")
        os.makedirs(paul_dir)

        # Register via API
        resp = await client.post("/api/projects/", json={"name": "TestProj", "path": tmpdir})
        assert resp.status_code == 201

        resp = await client.get("/api/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        proj = data["projects"][0]
        assert proj["name"] == "TestProj"
        # No state synced yet — state fields should be null
        assert proj["milestone"] is None
        assert proj["phase_number"] is None
        assert proj["blocker_count"] == 0


async def test_dashboard_with_project_and_state(client):
    with tempfile.TemporaryDirectory() as tmpdir:
        paul_dir = os.path.join(tmpdir, ".paul")
        os.makedirs(paul_dir)

        # Register via API
        resp = await client.post("/api/projects/", json={"name": "TestProj", "path": tmpdir})
        assert resp.status_code == 201
        project_id = resp.json()["id"]

        # Sync state directly via model
        async with aiosqlite.connect(settings.database_path) as db:
            db.row_factory = aiosqlite.Row
            await _sync_project(db, project_id)

        resp = await client.get("/api/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        proj = data["projects"][0]
        assert proj["milestone"] == "v0.1 Foundation (v0.1.0)"
        assert proj["phase_number"] == 2
        assert proj["phase_total"] == 4
        assert proj["phase_name"] == "API & WebSocket"
        assert proj["loop_plan"] is True
        assert proj["loop_apply"] is False
        assert proj["progress_milestone"] == 25.0
        assert proj["blocker_count"] == 1
        assert proj["last_activity"] == "2026-03-13"


async def test_dashboard_response_shape(client):
    """Verify all expected fields are present in response."""
    resp = await client.get("/api/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert "projects" in data
    assert "count" in data
