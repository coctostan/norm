"""Tests for watcher resilience — missing directories, sync failures, graceful recovery."""

import os
from unittest.mock import AsyncMock, patch

import pytest

from backend.watcher import FileWatcher, sync_project_by_path


@pytest.fixture
def watcher():
    return FileWatcher(on_sync=AsyncMock())


class TestGetWatchPathsMissingDirs:
    """_get_watch_paths should only return directories that exist."""

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_projects(self, watcher, tmp_path):
        """No active projects → empty dict."""
        with patch("backend.watcher.aiosqlite") as mock_aiosqlite:
            mock_db = AsyncMock()
            mock_db.row_factory = None
            mock_db.__aenter__ = AsyncMock(return_value=mock_db)
            mock_db.__aexit__ = AsyncMock(return_value=False)
            mock_aiosqlite.connect.return_value = mock_db

            with patch("backend.watcher.list_projects", return_value=[]):
                paths = await watcher._get_watch_paths()
                assert paths == {}

    @pytest.mark.asyncio
    async def test_skips_nonexistent_paul_dirs(self, watcher, tmp_path):
        """Projects whose .paul/ dir doesn't exist are excluded."""
        fake_project = {"id": 1, "path": str(tmp_path / "nonexistent")}

        with patch("backend.watcher.aiosqlite") as mock_aiosqlite:
            mock_db = AsyncMock()
            mock_db.row_factory = None
            mock_db.__aenter__ = AsyncMock(return_value=mock_db)
            mock_db.__aexit__ = AsyncMock(return_value=False)
            mock_aiosqlite.connect.return_value = mock_db

            with patch("backend.watcher.list_projects", return_value=[fake_project]):
                paths = await watcher._get_watch_paths()
                assert paths == {}

    @pytest.mark.asyncio
    async def test_includes_existing_paul_dirs(self, watcher, tmp_path):
        """Projects with valid .paul/ dirs are included."""
        project_dir = tmp_path / "myproject"
        paul_dir = project_dir / ".paul"
        paul_dir.mkdir(parents=True)

        fake_project = {"id": 42, "path": str(project_dir)}

        with patch("backend.watcher.aiosqlite") as mock_aiosqlite:
            mock_db = AsyncMock()
            mock_db.row_factory = None
            mock_db.__aenter__ = AsyncMock(return_value=mock_db)
            mock_db.__aexit__ = AsyncMock(return_value=False)
            mock_aiosqlite.connect.return_value = mock_db

            with patch("backend.watcher.list_projects", return_value=[fake_project]):
                paths = await watcher._get_watch_paths()
                assert str(paul_dir) in paths
                assert paths[str(paul_dir)] == 42


class TestSyncProjectResiliency:
    """sync_project_by_path should handle errors gracefully."""

    @pytest.mark.asyncio
    async def test_sync_returns_false_on_parse_error(self, tmp_path):
        """If parsing fails, sync returns False without crashing."""
        mock_db = AsyncMock()
        mock_db.execute_fetchall = AsyncMock(return_value=[(1,)])

        with patch("backend.watcher.parse_project_state", side_effect=FileNotFoundError("gone")):
            result = await sync_project_by_path(mock_db, str(tmp_path))
            assert result is False

    @pytest.mark.asyncio
    async def test_sync_returns_false_on_os_error(self, tmp_path):
        """If OS-level error occurs during parsing, sync returns False."""
        mock_db = AsyncMock()
        mock_db.execute_fetchall = AsyncMock(return_value=[(1,)])

        with patch("backend.watcher.parse_project_state", side_effect=OSError("Permission denied")):
            result = await sync_project_by_path(mock_db, str(tmp_path))
            assert result is False


class TestWatcherLifecycle:
    """Watcher start/stop resilience."""

    @pytest.mark.asyncio
    async def test_stop_is_idempotent(self, watcher):
        """Calling stop() multiple times doesn't crash."""
        await watcher.stop()
        await watcher.stop()

    @pytest.mark.asyncio
    async def test_stop_after_start(self, watcher):
        """Start then stop completes cleanly."""
        with patch.object(watcher, "_watch_loop", new_callable=AsyncMock):
            await watcher.start()
            assert watcher._task is not None
            await watcher.stop()
