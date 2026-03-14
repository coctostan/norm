import os
import tempfile

import aiosqlite
import pytest

from backend.config import settings
from backend.database import init_db
from backend.main import app
from backend.models import create_project, upsert_project_state
from backend.parser_models import (
    ParsedProject,
    ParsedRoadmap,
    ParsedState,
    ProjectFullState,
)
from backend.websocket import ConnectionManager


@pytest.fixture(autouse=True)
async def setup_test_db(tmp_path):
    """Use a temporary database for each test."""
    db_path = tmp_path / "test.db"
    original = settings.database_path
    settings.database_path = db_path
    await init_db()
    yield
    settings.database_path = original


# --- ConnectionManager unit tests ---


def test_connection_manager_init():
    cm = ConnectionManager()
    assert cm.active_connections == []


def test_disconnect_removes_connection():
    cm = ConnectionManager()
    # Simulate adding a mock connection
    mock_ws = object()
    cm.active_connections.append(mock_ws)
    assert len(cm.active_connections) == 1
    cm.disconnect(mock_ws)
    assert len(cm.active_connections) == 0


def test_disconnect_nonexistent_is_noop():
    cm = ConnectionManager()
    mock_ws = object()
    cm.disconnect(mock_ws)  # Should not raise
    assert len(cm.active_connections) == 0


async def test_broadcast_empty_connections():
    cm = ConnectionManager()
    # Should not raise with no connections
    await cm.broadcast({"type": "test"})


# --- WebSocket integration tests via Starlette TestClient ---


async def test_websocket_connect_and_initial_state():
    """Test WebSocket connection sends initial_state message."""
    from starlette.testclient import TestClient

    with TestClient(app) as tc:
            with tc.websocket_connect("/ws") as ws:
                data = ws.receive_json()
                assert data["type"] == "initial_state"
                assert "projects" in data
                assert isinstance(data["projects"], list)


async def test_websocket_connect_with_project():
    """Test WebSocket initial state includes registered projects."""
    with tempfile.TemporaryDirectory() as tmpdir:
        paul_dir = os.path.join(tmpdir, ".paul")
        os.makedirs(paul_dir)

        # Register a project and sync state
        async with aiosqlite.connect(settings.database_path) as db:
            db.row_factory = aiosqlite.Row
            result = await create_project(db, "WSTest", tmpdir)
            project_id = result["id"]
            parsed = ProjectFullState(
                state=ParsedState(
                    milestone="v0.1",
                    phase_number=1,
                    phase_total=3,
                    phase_name="Core",
                ),
                roadmap=ParsedRoadmap(),
                project=ParsedProject(name="WSTest"),
                synced_at="2026-03-13T12:00:00",
            )
            await upsert_project_state(db, project_id, parsed)

        from starlette.testclient import TestClient

        with TestClient(app) as tc:
            with tc.websocket_connect("/ws") as ws:
                data = ws.receive_json()
                assert data["type"] == "initial_state"
                assert len(data["projects"]) == 1
                assert data["projects"][0]["name"] == "WSTest"
                assert data["projects"][0]["milestone"] == "v0.1"


async def test_broadcast_sends_to_mock_connections():
    """Test that broadcast sends JSON to all connections and removes failed ones."""
    from unittest.mock import AsyncMock

    cm = ConnectionManager()

    ws1 = AsyncMock()
    ws2 = AsyncMock()
    ws_bad = AsyncMock()
    ws_bad.send_json.side_effect = RuntimeError("disconnected")

    cm.active_connections = [ws1, ws2, ws_bad]

    await cm.broadcast({"type": "project_updated", "projects": []})

    ws1.send_json.assert_called_once_with({"type": "project_updated", "projects": []})
    ws2.send_json.assert_called_once_with({"type": "project_updated", "projects": []})
    ws_bad.send_json.assert_called_once()
    # Failed connection should be removed
    assert ws_bad not in cm.active_connections
    assert len(cm.active_connections) == 2
