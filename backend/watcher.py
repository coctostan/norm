import asyncio
import logging
import os
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any

import aiosqlite
from watchfiles import Change, awatch

from backend.config import settings
from backend.models import (
    list_projects,
    update_project_sync_time,
    upsert_project_phases,
    upsert_project_state,
)
from backend.parser import parse_project_state

logger = logging.getLogger(__name__)

OnSyncCallback = Callable[[str], Coroutine[Any, Any, None]]

MONITORED_FILES = {"STATE.md", "ROADMAP.md", "PROJECT.md"}


def _is_monitored(path: str) -> bool:
    """Check if a changed file is one we care about."""
    return Path(path).name in MONITORED_FILES


def _path_to_project_path(changed_path: str) -> str | None:
    """Extract project root from a .paul/ file path.

    Given '/some/project/.paul/STATE.md', returns '/some/project'.
    """
    p = Path(changed_path)
    if p.parent.name == ".paul":
        return str(p.parent.parent)
    return None


async def sync_project_by_path(db: aiosqlite.Connection, project_path: str) -> bool:
    """Run sync for a project identified by its filesystem path.

    Returns True if sync succeeded, False otherwise.
    """
    rows = await db.execute_fetchall(
        "SELECT id FROM projects WHERE path = ? AND status = 'active'",
        (project_path,),
    )
    if not rows:
        logger.warning("No active project found for path: %s", project_path)
        return False

    project_id = rows[0][0]
    try:
        parsed = await parse_project_state(project_path)
        await upsert_project_state(db, project_id, parsed)
        if parsed.roadmap and parsed.roadmap.phases:
            await upsert_project_phases(db, project_id, parsed.roadmap.phases)
        await update_project_sync_time(db, project_id)
        logger.info("Synced project %s (id=%d)", project_path, project_id)
        return True
    except Exception:
        logger.exception("Failed to sync project %s", project_path)
        return False


class FileWatcher:
    """Watches .paul/ directories for registered projects and triggers sync on changes."""

    def __init__(self, on_sync: OnSyncCallback | None = None) -> None:
        self._task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()
        self._on_sync = on_sync

    async def start(self) -> None:
        """Start the file watcher as a background task."""
        self._stop_event.clear()
        self._task = asyncio.create_task(self._watch_loop())
        logger.info("File watcher started")

    async def stop(self) -> None:
        """Stop the file watcher gracefully."""
        if self._task and not self._task.done():
            self._stop_event.set()
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("File watcher stopped")

    async def _get_watch_paths(self) -> dict[str, int]:
        """Get mapping of .paul/ directory paths to project IDs for all active projects."""
        async with aiosqlite.connect(settings.database_path) as db:
            db.row_factory = aiosqlite.Row
            projects = await list_projects(db)

        paths = {}
        for project in projects:
            paul_dir = os.path.join(project["path"], ".paul")
            if os.path.isdir(paul_dir):
                paths[paul_dir] = project["id"]
        return paths

    async def _watch_loop(self) -> None:
        """Main watch loop — monitors .paul/ directories and triggers sync on changes."""
        while not self._stop_event.is_set():
            try:
                watch_paths = await self._get_watch_paths()
                if not watch_paths:
                    logger.debug("No projects to watch, waiting 5s...")
                    try:
                        await asyncio.wait_for(self._stop_event.wait(), timeout=5.0)
                        break
                    except asyncio.TimeoutError:
                        continue

                # Filter to paths that still exist (directory may have been removed between checks)
                paul_dirs = [p for p in watch_paths if os.path.isdir(p)]
                if not paul_dirs:
                    logger.warning("All watched directories missing, waiting 5s...")
                    try:
                        await asyncio.wait_for(self._stop_event.wait(), timeout=5.0)
                        break
                    except asyncio.TimeoutError:
                        continue

                if len(paul_dirs) < len(watch_paths):
                    missing = set(watch_paths) - set(paul_dirs)
                    logger.warning("Skipping missing directories: %s", missing)

                logger.info("Watching %d project(s): %s", len(paul_dirs), paul_dirs)

                async for changes in awatch(
                    *paul_dirs,
                    debounce=settings.watch_debounce_ms,
                    stop_event=self._stop_event,
                    recursive=False,
                ):
                    synced_paths: set[str] = set()
                    for change_type, changed_path in changes:
                        if change_type != Change.modified and change_type != Change.added:
                            continue
                        if not _is_monitored(changed_path):
                            continue
                        project_path = _path_to_project_path(changed_path)
                        if project_path and project_path not in synced_paths:
                            try:
                                async with aiosqlite.connect(settings.database_path) as db:
                                    db.row_factory = aiosqlite.Row
                                    synced = await sync_project_by_path(db, project_path)
                            except (OSError, FileNotFoundError):
                                logger.warning(
                                    "Directory disappeared during sync: %s", project_path
                                )
                                synced = False
                            if synced and self._on_sync:
                                try:
                                    await self._on_sync(project_path)
                                except Exception:
                                    logger.exception("on_sync callback failed for %s", project_path)
                            synced_paths.add(project_path)

                    # After processing a batch of changes, refresh watch paths
                    # in case projects were added/removed
                    new_paths = await self._get_watch_paths()
                    if set(new_paths.keys()) != set(watch_paths.keys()):
                        logger.info("Project list changed, restarting watch...")
                        break  # Break inner loop to restart awatch with new paths

            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Watcher error, restarting in 5s...")
                try:
                    await asyncio.wait_for(self._stop_event.wait(), timeout=5.0)
                    break
                except asyncio.TimeoutError:
                    continue
