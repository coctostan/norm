from datetime import datetime

from pydantic import BaseModel


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
