import aiosqlite

from backend.config import settings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    path TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'active',
    last_synced TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS project_state (
    project_id INTEGER UNIQUE NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    milestone TEXT,
    phase_number INTEGER,
    phase_total INTEGER,
    phase_name TEXT,
    plan TEXT,
    status TEXT,
    loop_plan BOOLEAN DEFAULT 0,
    loop_apply BOOLEAN DEFAULT 0,
    loop_unify BOOLEAN DEFAULT 0,
    loop_description TEXT,
    progress_milestone REAL,
    progress_phase REAL,
    last_activity TEXT,
    blockers_json TEXT DEFAULT '[]',
    decisions_json TEXT DEFAULT '[]',
    project_name TEXT,
    project_description TEXT,
    project_version TEXT,
    project_status TEXT,
    roadmap_milestone_name TEXT,
    roadmap_milestone_version TEXT,
    roadmap_milestone_status TEXT,
    synced_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS project_phases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    phase_number INTEGER NOT NULL,
    name TEXT,
    plan_count INTEGER,
    status TEXT,
    completed_date TEXT,
    UNIQUE(project_id, phase_number)
);
"""


async def init_db():
    async with aiosqlite.connect(settings.database_path) as db:
        await db.executescript(_SCHEMA)
        await db.commit()


async def get_db():
    db = await aiosqlite.connect(settings.database_path)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()
