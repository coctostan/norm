import json
from datetime import datetime

import aiosqlite

from backend.parser_models import ProjectFullState


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


async def upsert_project_state(
    db: aiosqlite.Connection, project_id: int, parsed: ProjectFullState
) -> None:
    state = parsed.state
    project = parsed.project
    roadmap = parsed.roadmap

    await db.execute(
        """INSERT OR REPLACE INTO project_state (
            project_id, milestone, phase_number, phase_total, phase_name,
            plan, status, loop_plan, loop_apply, loop_unify, loop_description,
            progress_milestone, progress_phase, last_activity,
            blockers_json, decisions_json,
            project_name, project_description, project_version, project_status,
            roadmap_milestone_name, roadmap_milestone_version, roadmap_milestone_status,
            synced_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            project_id,
            state.milestone if state else None,
            state.phase_number if state else None,
            state.phase_total if state else None,
            state.phase_name if state else None,
            state.plan if state else None,
            state.status if state else None,
            state.loop.plan if state else False,
            state.loop.apply if state else False,
            state.loop.unify if state else False,
            state.loop.description if state else "",
            state.progress_milestone if state else None,
            state.progress_phase if state else None,
            state.last_activity if state else None,
            json.dumps(state.blockers) if state else "[]",
            json.dumps(state.decisions) if state else "[]",
            project.name if project else None,
            project.description if project else None,
            project.version if project else None,
            project.status if project else None,
            roadmap.milestone_name if roadmap else None,
            roadmap.milestone_version if roadmap else None,
            roadmap.milestone_status if roadmap else None,
            parsed.synced_at,
        ),
    )
    await db.commit()


async def upsert_project_phases(db: aiosqlite.Connection, project_id: int, phases: list) -> None:
    await db.execute("DELETE FROM project_phases WHERE project_id = ?", (project_id,))
    for phase in phases:
        await db.execute(
            """INSERT INTO project_phases (
                project_id, phase_number, name, plan_count, status, completed_date
            ) VALUES (?, ?, ?, ?, ?, ?)""",
            (
                project_id,
                phase.number,
                phase.name,
                phase.plan_count,
                phase.status,
                phase.completed_date,
            ),
        )
    await db.commit()


async def get_project_state(db: aiosqlite.Connection, project_id: int) -> dict | None:
    rows = await db.execute_fetchall(
        "SELECT * FROM project_state WHERE project_id = ?", (project_id,)
    )
    if not rows:
        return None
    row = dict(rows[0])
    row["blockers_json"] = json.loads(row.get("blockers_json") or "[]")
    row["decisions_json"] = json.loads(row.get("decisions_json") or "[]")
    return row


async def get_project_phases(db: aiosqlite.Connection, project_id: int) -> list[dict]:
    rows = await db.execute_fetchall(
        "SELECT * FROM project_phases WHERE project_id = ? ORDER BY phase_number",
        (project_id,),
    )
    return [dict(row) for row in rows]


async def get_dashboard_projects(db: aiosqlite.Connection) -> list[dict]:
    rows = await db.execute_fetchall(
        """SELECT
            p.id, p.name, p.path, p.status, p.last_synced, p.created_at,
            s.milestone, s.phase_number, s.phase_total, s.phase_name,
            s.loop_plan, s.loop_apply, s.loop_unify,
            s.progress_milestone, s.progress_phase,
            s.plan AS plan_status, s.last_activity,
            s.blockers_json
        FROM projects p
        LEFT JOIN project_state s ON p.id = s.project_id
        ORDER BY p.created_at DESC"""
    )
    result = []
    for row in rows:
        d = dict(row)
        blockers_json = d.pop("blockers_json", None)
        blockers = json.loads(blockers_json) if blockers_json else []
        d["blocker_count"] = len(blockers)
        # Coerce NULL booleans from LEFT JOIN to False
        for key in ("loop_plan", "loop_apply", "loop_unify"):
            if d.get(key) is None:
                d[key] = False
        result.append(d)
    return result
