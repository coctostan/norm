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
