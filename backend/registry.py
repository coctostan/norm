import os

from fastapi import APIRouter, Depends, HTTPException

from backend.config import save_config
from backend.database import get_db
from backend.watcher import sync_project_by_path
from backend.models import (
    create_project,
    delete_project,
    get_dashboard_projects,
    get_project,
    get_project_phases,
    get_project_state,
    list_projects,
    update_project_sync_time,
    upsert_project_phases,
    upsert_project_state,
)
from backend.parser import parse_project_state
from backend.schemas import (
    DashboardResponse,
    ProjectCreate,
    ProjectList,
    ProjectResponse,
    ProjectStateResponse,
)

router = APIRouter(prefix="/api/projects", tags=["projects"])
dashboard_router = APIRouter(tags=["dashboard"])


@dashboard_router.get("/api/dashboard", response_model=DashboardResponse)
async def get_dashboard(db=Depends(get_db)):
    projects = await get_dashboard_projects(db)
    return DashboardResponse(projects=projects, count=len(projects))


@router.post("/", response_model=ProjectResponse, status_code=201)
async def register_project(project: ProjectCreate, db=Depends(get_db)):
    paul_dir = os.path.join(project.path, ".paul")
    if not os.path.isdir(paul_dir):
        raise HTTPException(
            status_code=422,
            detail=f"No .paul/ directory found at: {project.path}",
        )

    abs_path = os.path.abspath(project.path)
    try:
        result = await create_project(db, project.name, abs_path)
    except Exception as e:
        if "UNIQUE constraint" in str(e):
            raise HTTPException(
                status_code=409,
                detail=f"Project already registered at: {abs_path}",
            )
        raise

    # Persist to config file
    all_projects = await list_projects(db)
    save_config(all_projects)

    # Auto-sync so project details are available immediately
    await sync_project_by_path(db, abs_path)

    return result


@router.get("/", response_model=ProjectList)
async def get_projects(db=Depends(get_db)):
    projects = await list_projects(db)
    return ProjectList(projects=projects, count=len(projects))


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project_detail(project_id: int, db=Depends(get_db)):
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}", status_code=204)
async def remove_project(project_id: int, db=Depends(get_db)):
    deleted = await delete_project(db, project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")

    # Persist to config file
    all_projects = await list_projects(db)
    save_config(all_projects)


@router.post("/{project_id}/sync", response_model=ProjectStateResponse)
async def sync_project(project_id: int, db=Depends(get_db)):
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    parsed = await parse_project_state(project["path"])
    await upsert_project_state(db, project_id, parsed)
    if parsed.roadmap and parsed.roadmap.phases:
        await upsert_project_phases(db, project_id, parsed.roadmap.phases)
    await update_project_sync_time(db, project_id)

    return ProjectStateResponse(
        state=parsed.state,
        roadmap=parsed.roadmap,
        project=parsed.project,
        synced_at=parsed.synced_at,
    )


@router.get("/{project_id}/state", response_model=ProjectStateResponse)
async def get_project_state_endpoint(project_id: int, db=Depends(get_db)):
    project = await get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    cached = await get_project_state(db, project_id)
    if not cached:
        raise HTTPException(
            status_code=404, detail="Project state not synced yet. Run POST /sync first."
        )

    phases_data = await get_project_phases(db, project_id)

    from backend.parser_models import (
        LoopPosition,
        ParsedProject,
        ParsedRoadmap,
        ParsedState,
        PhaseProgress,
    )

    state = ParsedState(
        milestone=cached.get("milestone") or "",
        phase_number=cached.get("phase_number") or 0,
        phase_total=cached.get("phase_total") or 0,
        phase_name=cached.get("phase_name") or "",
        plan=cached.get("plan") or "",
        status=cached.get("status") or "",
        loop=LoopPosition(
            plan=bool(cached.get("loop_plan")),
            apply=bool(cached.get("loop_apply")),
            unify=bool(cached.get("loop_unify")),
            description=cached.get("loop_description") or "",
        ),
        progress_milestone=cached.get("progress_milestone"),
        progress_phase=cached.get("progress_phase"),
        last_activity=cached.get("last_activity"),
        blockers=cached.get("blockers_json") or [],
        decisions=cached.get("decisions_json") or [],
    )

    roadmap = ParsedRoadmap(
        milestone_name=cached.get("roadmap_milestone_name") or "",
        milestone_version=cached.get("roadmap_milestone_version") or "",
        milestone_status=cached.get("roadmap_milestone_status") or "",
        phases=[
            PhaseProgress(
                number=p["phase_number"],
                name=p.get("name") or "",
                plan_count=p.get("plan_count"),
                status=p.get("status") or "",
                completed_date=p.get("completed_date"),
            )
            for p in phases_data
        ],
    )

    project_info = ParsedProject(
        name=cached.get("project_name") or "",
        description=cached.get("project_description") or "",
        version=cached.get("project_version") or "",
        status=cached.get("project_status") or "",
    )

    return ProjectStateResponse(
        state=state,
        roadmap=roadmap,
        project=project_info,
        synced_at=cached.get("synced_at") or "",
    )
