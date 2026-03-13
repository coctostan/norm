from datetime import datetime

import aiosqlite


async def create_project(db: aiosqlite.Connection, name: str, path: str) -> dict:
    cursor = await db.execute(
        "INSERT INTO projects (name, path) VALUES (?, ?)",
        (name, path),
    )
    await db.commit()
    row = await db.execute_fetchall("SELECT * FROM projects WHERE id = ?", (cursor.lastrowid,))
    return dict(row[0])


async def get_project(db: aiosqlite.Connection, project_id: int) -> dict | None:
    rows = await db.execute_fetchall("SELECT * FROM projects WHERE id = ?", (project_id,))
    return dict(rows[0]) if rows else None


async def list_projects(db: aiosqlite.Connection) -> list[dict]:
    rows = await db.execute_fetchall("SELECT * FROM projects ORDER BY created_at DESC")
    return [dict(row) for row in rows]


async def delete_project(db: aiosqlite.Connection, project_id: int) -> bool:
    cursor = await db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    await db.commit()
    return cursor.rowcount > 0


async def update_project_sync_time(db: aiosqlite.Connection, project_id: int) -> None:
    await db.execute(
        "UPDATE projects SET last_synced = ? WHERE id = ?",
        (datetime.now().isoformat(), project_id),
    )
    await db.commit()
