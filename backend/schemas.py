from datetime import datetime

from pydantic import BaseModel

from backend.parser_models import ParsedProject, ParsedRoadmap, ParsedState


class ProjectCreate(BaseModel):
    name: str
    path: str


class ProjectResponse(BaseModel):
    id: int
    name: str
    path: str
    status: str
    last_synced: datetime | None = None
    created_at: datetime


class ProjectList(BaseModel):
    projects: list[ProjectResponse]
    count: int


class ProjectStateResponse(BaseModel):
    state: ParsedState | None = None
    roadmap: ParsedRoadmap | None = None
    project: ParsedProject | None = None
    synced_at: str = ""


class DashboardProject(BaseModel):
    id: int
    name: str
    path: str
    status: str
    last_synced: datetime | None = None
    created_at: datetime
    milestone: str | None = None
    phase_number: int | None = None
    phase_total: int | None = None
    phase_name: str | None = None
    loop_plan: bool = False
    loop_apply: bool = False
    loop_unify: bool = False
    progress_milestone: float | None = None
    progress_phase: float | None = None
    plan_status: str | None = None
    last_activity: str | None = None
    blocker_count: int = 0


class DashboardResponse(BaseModel):
    projects: list[DashboardProject]
    count: int
