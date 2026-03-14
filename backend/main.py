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
    await init_db()
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
