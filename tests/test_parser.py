import os

import pytest

from backend.parser import parse_project_md, parse_project_state, parse_roadmap_md, parse_state_md

STATE_MD_FIXTURE = """# Project State

## Project Reference

See: .paul/PROJECT.md (updated 2026-03-13)

**Core value:** Devs managing multiple PALS projects see all work in one place
**Current focus:** v0.1 Foundation — Phase 1: Backend Core

## Current Position

Milestone: v0.1 Foundation (v0.1.0)
Phase: 1 of 4 (Backend Core) — Planning
Plan: 01-02 created, awaiting approval
Status: PLAN created, ready for APPLY
Last activity: 2026-03-13 — Created .paul/phases/01-backend-core/01-02-PLAN.md

Progress:
- v0.1 Foundation: [█░░░░░░░░░] 8%
- Phase 1: [███░░░░░░░] 33% (1/3 plans)

## Loop Position

Current loop state:
```
PLAN ──▶ APPLY ──▶ UNIFY
  ✓        ○        ○     [Plan created, awaiting approval]
```

## Accumulated Context

### Decisions
| Decision | Phase | Impact |
|----------|-------|--------|
| Separate repo from PALS | Init | Read-only companion tool |
| FastAPI + SvelteKit + SQLite | Init | Full-stack with real-time WebSocket |
| aiosqlite direct (no ORM) | Phase 1 | Simpler for cache layer use case |

### Blockers/Concerns
- None active
"""

ROADMAP_MD_FIXTURE = """# Roadmap: NORM

## Current Milestone

**v0.1 Foundation** (v0.1.0)
Status: 🚧 In Progress
Phases: 0 of 4 complete

## Phases

| Phase | Name | Plans | Status | Completed |
|-------|------|-------|--------|-----------|
| 1 | Backend Core | 3 | In progress | - |
| 2 | API & WebSocket | TBD | Not started | - |
| 3 | Frontend Shell | TBD | Not started | - |
| 4 | Detail Views & Polish | TBD | Not started | - |
"""

PROJECT_MD_FIXTURE = """# NORM — Notifier & Observer for Running Milestones

## Current State

| Attribute | Value |
|-----------|-------|
| Version | 0.0.0 |
| Status | Greenfield |
| Last Updated | 2026-03-13 |
"""


def test_parse_state_md_milestone():
    result = parse_state_md(STATE_MD_FIXTURE)
    assert result.milestone == "v0.1 Foundation (v0.1.0)"


def test_parse_state_md_phase():
    result = parse_state_md(STATE_MD_FIXTURE)
    assert result.phase_number == 1
    assert result.phase_total == 4
    assert result.phase_name == "Backend Core"


def test_parse_state_md_plan_and_status():
    result = parse_state_md(STATE_MD_FIXTURE)
    assert "01-02" in result.plan
    assert "PLAN created" in result.status


def test_parse_state_md_loop_position():
    result = parse_state_md(STATE_MD_FIXTURE)
    assert result.loop.plan is True
    assert result.loop.apply is False
    assert result.loop.unify is False
    assert "awaiting approval" in result.loop.description


def test_parse_state_md_progress():
    result = parse_state_md(STATE_MD_FIXTURE)
    assert result.progress_milestone == 8.0
    assert result.progress_phase == 33.0


def test_parse_state_md_last_activity():
    result = parse_state_md(STATE_MD_FIXTURE)
    assert result.last_activity is not None
    assert "2026-03-13" in result.last_activity


def test_parse_state_md_decisions():
    result = parse_state_md(STATE_MD_FIXTURE)
    assert len(result.decisions) >= 3
    assert result.decisions[0]["decision"] == "Separate repo from PALS"


def test_parse_state_md_no_blockers():
    result = parse_state_md(STATE_MD_FIXTURE)
    assert result.blockers == []


def test_parse_state_md_empty_content():
    result = parse_state_md("")
    assert result.milestone == ""
    assert result.phase_number == 0
    assert result.loop.plan is False


def test_parse_roadmap_md_milestone():
    result = parse_roadmap_md(ROADMAP_MD_FIXTURE)
    assert result.milestone_name == "v0.1 Foundation"
    assert result.milestone_version == "v0.1.0"


def test_parse_roadmap_md_status():
    result = parse_roadmap_md(ROADMAP_MD_FIXTURE)
    assert "In Progress" in result.milestone_status


def test_parse_roadmap_md_phases():
    result = parse_roadmap_md(ROADMAP_MD_FIXTURE)
    assert len(result.phases) == 4
    assert result.phases[0].number == 1
    assert result.phases[0].name == "Backend Core"
    assert result.phases[0].plan_count == 3
    assert result.phases[0].status == "In progress"


def test_parse_roadmap_md_tbd_plans():
    result = parse_roadmap_md(ROADMAP_MD_FIXTURE)
    assert result.phases[1].plan_count is None  # TBD


def test_parse_roadmap_md_empty_content():
    result = parse_roadmap_md("")
    assert result.milestone_name == ""
    assert result.phases == []


def test_parse_project_md_name():
    result = parse_project_md(PROJECT_MD_FIXTURE)
    assert result.name == "NORM"
    assert "Notifier" in result.description


def test_parse_project_md_version():
    result = parse_project_md(PROJECT_MD_FIXTURE)
    assert result.version == "0.0.0"


def test_parse_project_md_status():
    result = parse_project_md(PROJECT_MD_FIXTURE)
    assert result.status == "Greenfield"


def test_parse_project_md_last_updated():
    result = parse_project_md(PROJECT_MD_FIXTURE)
    assert result.last_updated == "2026-03-13"


def test_parse_project_md_empty_content():
    result = parse_project_md("")
    assert result.name == ""
    assert result.version == ""


@pytest.mark.asyncio
async def test_parse_project_state_real_project():
    """Test with this project's own .paul/ directory."""
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paul_dir = os.path.join(project_path, ".paul")
    if not os.path.isdir(paul_dir):
        pytest.skip("No .paul/ directory found in project root")

    result = await parse_project_state(project_path)
    assert result.synced_at != ""
    assert result.state is not None
    assert result.roadmap is not None
    assert result.project is not None
    assert result.project.name == "NORM"


@pytest.mark.asyncio
async def test_parse_project_state_missing_paul_dir(tmp_path):
    """Test with a path that has no .paul/ directory."""
    result = await parse_project_state(str(tmp_path))
    assert result.state is None
    assert result.roadmap is None
    assert result.project is None
    assert result.synced_at != ""
