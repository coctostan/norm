from unittest.mock import AsyncMock, patch

import aiosqlite
import pytest

from backend.config import settings
from backend.database import init_db
from backend.models import create_project
from backend.watcher import (
    MONITORED_FILES,
    FileWatcher,
    _is_monitored,
    _path_to_project_path,
    sync_project_by_path,
)

# --- Unit tests for filter helpers ---


def test_is_monitored_state_md():
    assert _is_monitored("/some/project/.paul/STATE.md") is True


def test_is_monitored_roadmap_md():
    assert _is_monitored("/some/project/.paul/ROADMAP.md") is True


def test_is_monitored_project_md():
    assert _is_monitored("/some/project/.paul/PROJECT.md") is True


def test_is_monitored_ignores_handoff():
    assert _is_monitored("/some/project/.paul/HANDOFF-2026-03-13.md") is False


def test_is_monitored_ignores_summary():
    assert _is_monitored("/some/project/.paul/phases/01/01-01-SUMMARY.md") is False


def test_is_monitored_ignores_plan():
    assert _is_monitored("/some/project/.paul/phases/01/01-01-PLAN.md") is False


def test_path_to_project_path():
    result = _path_to_project_path("/home/user/myproject/.paul/STATE.md")
    assert result == "/home/user/myproject"


def test_path_to_project_path_none_for_non_paul():
    result = _path_to_project_path("/home/user/myproject/src/main.py")
    assert result is None


def test_monitored_files_set():
    assert MONITORED_FILES == {"STATE.md", "ROADMAP.md", "PROJECT.md"}


# --- Integration tests for sync_project_by_path ---


@pytest.fixture
async def test_db(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "test.db"
    original = settings.database_path
    settings.database_path = db_path
    await init_db()
    db = await aiosqlite.connect(db_path)
    db.row_factory = aiosqlite.Row
    yield db
    await db.close()
    settings.database_path = original


@pytest.fixture
def paul_project(tmp_path):
    """Create a temporary .paul/ directory with valid state files."""
    project_dir = tmp_path / "test-project"
    paul_dir = project_dir / ".paul"
    paul_dir.mkdir(parents=True)

    (paul_dir / "STATE.md").write_text(
        """# Project State

## Current Position

Milestone: v0.1 Test (v0.1.0)
Phase: 1 of 2 (Test Phase)
Plan: 01-01 complete
Status: Ready for next PLAN
Last activity: 2026-03-13 — Test

Progress:
- v0.1 Test: [█████░░░░░] 50%
- Phase 1: [██████████] 100%

## Loop Position

Current loop state:
```
PLAN ──▶ APPLY ──▶ UNIFY
  ✓        ✓        ✓     [Loop complete]
```
"""
    )

    (paul_dir / "ROADMAP.md").write_text(
        """# Roadmap: Test

## Current Milestone

**v0.1 Test** (v0.1.0)
Status: 🚧 In Progress
Phases: 0 of 2 complete

## Phases

| Phase | Name | Plans | Status | Completed |
|-------|------|-------|--------|-----------|
| 1 | Test Phase | 1 | Complete | 2026-03-13 |
| 2 | Next Phase | TBD | Not started | - |
"""
    )

    (paul_dir / "PROJECT.md").write_text(
        """# TestProject — A test project

## Current State

| Attribute | Value |
|-----------|-------|
| Version | 0.1.0 |
| Status | Active |
| Last Updated | 2026-03-13 |
"""
    )

    return project_dir


async def test_sync_project_by_path_success(test_db, paul_project):
    """Test syncing a registered project by its filesystem path."""
    project_path = str(paul_project)
    await create_project(test_db, "test-project", project_path)

    result = await sync_project_by_path(test_db, project_path)
    assert result is True

    # Verify state was cached
    rows = await test_db.execute_fetchall("SELECT * FROM project_state WHERE project_id = 1")
    assert len(rows) == 1
    state = dict(rows[0])
    assert state["milestone"] == "v0.1 Test (v0.1.0)"
    assert state["phase_number"] == 1


async def test_sync_project_by_path_unknown_path(test_db):
    """Test syncing with an unregistered path returns False."""
    result = await sync_project_by_path(test_db, "/nonexistent/path")
    assert result is False


async def test_sync_project_by_path_missing_paul_dir(test_db, tmp_path):
    """Test syncing a project with no .paul/ directory handles gracefully."""
    project_dir = tmp_path / "empty-project"
    project_dir.mkdir()
    await create_project(test_db, "empty", str(project_dir))

    # Should succeed but with None state (graceful degradation from parser)
    result = await sync_project_by_path(test_db, str(project_dir))
    assert result is True


# --- FileWatcher lifecycle tests ---


async def test_watcher_start_stop():
    """Test that watcher can start and stop without errors."""
    watcher = FileWatcher()
    with patch.object(watcher, "_watch_loop", new_callable=AsyncMock):
        await watcher.start()
        assert watcher._task is not None
        await watcher.stop()
        assert watcher._task.done()


async def test_watcher_stop_when_not_started():
    """Test that stopping a never-started watcher is safe."""
    watcher = FileWatcher()
    await watcher.stop()  # Should not raise
