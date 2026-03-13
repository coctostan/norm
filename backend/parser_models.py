from pydantic import BaseModel


class LoopPosition(BaseModel):
    plan: bool = False
    apply: bool = False
    unify: bool = False
    description: str = ""


class PhaseProgress(BaseModel):
    number: int
    name: str
    plan_count: int | None = None
    status: str = "Not started"
    completed_date: str | None = None


class ParsedState(BaseModel):
    milestone: str = ""
    phase_number: int = 0
    phase_total: int = 0
    phase_name: str = ""
    plan: str = ""
    status: str = ""
    loop: LoopPosition = LoopPosition()
    progress_milestone: float | None = None
    progress_phase: float | None = None
    last_activity: str | None = None
    blockers: list[str] = []
    decisions: list[dict] = []


class ParsedRoadmap(BaseModel):
    milestone_name: str = ""
    milestone_version: str = ""
    milestone_status: str = ""
    phases: list[PhaseProgress] = []


class ParsedProject(BaseModel):
    name: str = ""
    description: str = ""
    version: str = ""
    status: str = ""
    last_updated: str | None = None


class ProjectFullState(BaseModel):
    state: ParsedState | None = None
    roadmap: ParsedRoadmap | None = None
    project: ParsedProject | None = None
    synced_at: str = ""
