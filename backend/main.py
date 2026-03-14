from contextlib import asynccontextmanager

import aiosqlite
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import init_db
from backend.models import get_dashboard_projects
from backend.registry import dashboard_router
from backend.registry import router as projects_router
from backend.watcher import FileWatcher
from backend.websocket import manager


async def _on_sync(project_path: str) -> None:
    """Callback invoked by FileWatcher after a successful sync.

    Fetches updated dashboard data and broadcasts to all WebSocket clients.
    """
    async with aiosqlite.connect(settings.database_path) as db:
        db.row_factory = aiosqlite.Row
        projects = await get_dashboard_projects(db)
    await manager.broadcast({"type": "project_updated", "projects": projects})


@asynccontextmanager
async def lifespan(app: FastAPI):
    import logging
    import os

    from backend.config import load_config
    from backend.models import create_project, list_projects
    from backend.watcher import sync_project_by_path

    logger = logging.getLogger(__name__)

    await init_db()

    # Auto-register projects from norm.yaml
    config_projects = load_config()
    if config_projects:
        async with aiosqlite.connect(settings.database_path) as db:
            db.row_factory = aiosqlite.Row
            existing = await list_projects(db)
            existing_paths = {p["path"] for p in existing}
            for proj in config_projects:
                abs_path = os.path.abspath(proj["path"])
                if abs_path not in existing_paths:
                    try:
                        await create_project(db, proj["name"], abs_path)
                        logger.info("Auto-registered project from config: %s", proj["name"])
                    except Exception:
                        logger.warning("Failed to register project from config: %s", proj["name"])

    # Auto-sync all projects on startup so dashboard shows details immediately
    async with aiosqlite.connect(settings.database_path) as db:
        db.row_factory = aiosqlite.Row
        all_projects = await list_projects(db)
        for proj in all_projects:
            try:
                await sync_project_by_path(db, proj["path"])
            except Exception:
                logger.warning("Failed to sync project on startup: %s", proj["name"])

    watcher = FileWatcher(on_sync=_on_sync)
    await watcher.start()
    app.state.watcher = watcher
    yield
    await watcher.stop()


app = FastAPI(
    title="NORM",
    description="Notifier & Observer for Running Milestones — real-time PALS project monitoring",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects_router)
app.include_router(dashboard_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial state snapshot
        async with aiosqlite.connect(settings.database_path) as db:
            db.row_factory = aiosqlite.Row
            projects = await get_dashboard_projects(db)
        await manager.send_personal(websocket, {"type": "initial_state", "projects": projects})
        # Keep-alive loop — detect disconnects
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
