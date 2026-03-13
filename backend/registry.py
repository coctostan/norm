import os

from fastapi import APIRouter, Depends, HTTPException

from backend.database import get_db
from backend.models import create_project, delete_project, get_project, list_projects
from backend.schemas import ProjectCreate, ProjectList, ProjectResponse

router = APIRouter(prefix="/api/projects", tags=["projects"])


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
