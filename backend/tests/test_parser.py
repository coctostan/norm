from backend.parser import parse_project_md, parse_roadmap_md, parse_state_md

SAMPLE_STATE = """\
# Project State

## Current Position

Milestone: v0.1 Foundation (v0.1.0)
Phase: 3 of 4 (Frontend Shell)
Plan: 03-01 complete
Status: Loop complete, ready for next PLAN
Last activity: 2026-03-13 — Completed frontend shell

Progress:
- v0.1 Foundation: [████████░░] 75%
- Phase 3: [██████████] 100%

## Loop Position

Current loop state:
```
PLAN ──▶ APPLY ──▶ UNIFY
  ✓        ✓        ✓     [Loop complete - ready for next PLAN]
```

## Accumulated Context

### Decisions
| Decision | Phase | Impact |
|----------|-------|--------|
| FastAPI + SvelteKit | Init | Full-stack with WebSocket |
| aiosqlite direct | Phase 1 | Simpler for cache layer |

### Blockers/Concerns
- Deployment config missing
- Test coverage at 0%

### Git State
Last commit: abc1234
"""


SAMPLE_STATE_NO_BLOCKERS = """\
# Project State

## Current Position

Milestone: v0.1 Foundation (v0.1.0)
Phase: 2 of 4 (API)
Plan: 02-01 complete
Status: Ready

## Loop Position

Current loop state:
```
PLAN ──▶ APPLY ──▶ UNIFY
  ✓        ○        ○     [Plan created]
```

## Accumulated Context

### Decisions
| Decision | Phase | Impact |
|----------|-------|--------|

### Blockers/Concerns
- None active
"""


SAMPLE_ROADMAP = """\
# Roadmap: NORM

## Current Milestone

**v0.1 Foundation** (v0.1.0)
Status: 🚧 In Progress
Phases: 2 of 4 complete

## Phases

| Phase | Name | Plans | Status | Completed |
|-------|------|-------|--------|-----------|
| 1 | Backend Core | 3 | ✅ Complete | 2026-03-13 |
| 2 | API & WebSocket | 1 | ✅ Complete | 2026-03-13 |
| 3 | Frontend Shell | 1 | Planning | - |
| 4 | Detail Views | 3 planned | Not started | - |
"""


SAMPLE_PROJECT = """\
# NORM — Notifier & Observer for Running Milestones

## What This Is

A real-time monitoring dashboard.

## Current State

| Attribute | Value |
|-----------|-------|
| Version | 0.1.0-alpha |
| Status | In Development |
| Last Updated | 2026-03-13 |
"""


class TestParseStateMd:
    def test_parses_milestone(self):
        state = parse_state_md(SAMPLE_STATE)
        assert state.milestone == "v0.1 Foundation (v0.1.0)"

    def test_parses_phase_info(self):
        state = parse_state_md(SAMPLE_STATE)
        assert state.phase_number == 3
        assert state.phase_total == 4
        assert state.phase_name == "Frontend Shell"

    def test_parses_plan_and_status(self):
        state = parse_state_md(SAMPLE_STATE)
        assert state.plan == "03-01 complete"
        assert state.status == "Loop complete, ready for next PLAN"

    def test_parses_loop_position_all_complete(self):
        state = parse_state_md(SAMPLE_STATE)
        assert state.loop.plan is True
        assert state.loop.apply is True
        assert state.loop.unify is True
        assert "Loop complete" in state.loop.description

    def test_parses_loop_position_partial(self):
        state = parse_state_md(SAMPLE_STATE_NO_BLOCKERS)
        assert state.loop.plan is True
        assert state.loop.apply is False
        assert state.loop.unify is False

    def test_parses_progress(self):
        state = parse_state_md(SAMPLE_STATE)
        assert state.progress_milestone == 75.0
        assert state.progress_phase == 100.0

    def test_parses_last_activity(self):
        state = parse_state_md(SAMPLE_STATE)
        assert state.last_activity == "2026-03-13 — Completed frontend shell"

    def test_parses_blockers(self):
        state = parse_state_md(SAMPLE_STATE)
        assert len(state.blockers) == 2
        assert "Deployment config missing" in state.blockers
        assert "Test coverage at 0%" in state.blockers

    def test_no_blockers_when_none(self):
        state = parse_state_md(SAMPLE_STATE_NO_BLOCKERS)
        assert len(state.blockers) == 0

    def test_parses_decisions(self):
        state = parse_state_md(SAMPLE_STATE)
        assert len(state.decisions) == 2
        assert state.decisions[0]["decision"] == "FastAPI + SvelteKit"
        assert state.decisions[0]["phase"] == "Init"

    def test_empty_content(self):
        state = parse_state_md("")
        assert state.milestone == ""
        assert state.phase_number == 0
        assert len(state.blockers) == 0
        assert len(state.decisions) == 0


class TestParseRoadmapMd:
    def test_parses_milestone_name(self):
        roadmap = parse_roadmap_md(SAMPLE_ROADMAP)
        assert roadmap.milestone_name == "v0.1 Foundation"
        assert roadmap.milestone_version == "v0.1.0"

    def test_parses_milestone_status(self):
        roadmap = parse_roadmap_md(SAMPLE_ROADMAP)
        assert "In Progress" in roadmap.milestone_status

    def test_parses_phases(self):
        roadmap = parse_roadmap_md(SAMPLE_ROADMAP)
        assert len(roadmap.phases) == 4
        assert roadmap.phases[0].number == 1
        assert roadmap.phases[0].name == "Backend Core"
        assert roadmap.phases[0].plan_count == 3
        assert roadmap.phases[0].status == "✅ Complete"
        assert roadmap.phases[0].completed_date == "2026-03-13"

    def test_phase_not_started(self):
        roadmap = parse_roadmap_md(SAMPLE_ROADMAP)
        phase4 = roadmap.phases[3]
        assert phase4.name == "Detail Views"
        assert phase4.completed_date is None

    def test_empty_content(self):
        roadmap = parse_roadmap_md("")
        assert roadmap.milestone_name == ""
        assert len(roadmap.phases) == 0


class TestParseProjectMd:
    def test_parses_name_and_description(self):
        project = parse_project_md(SAMPLE_PROJECT)
        assert project.name == "NORM"
        assert project.description == "Notifier & Observer for Running Milestones"

    def test_parses_version(self):
        project = parse_project_md(SAMPLE_PROJECT)
        assert project.version == "0.1.0-alpha"

    def test_parses_status(self):
        project = parse_project_md(SAMPLE_PROJECT)
        assert project.status == "In Development"

    def test_parses_last_updated(self):
        project = parse_project_md(SAMPLE_PROJECT)
        assert project.last_updated == "2026-03-13"

    def test_empty_content(self):
        project = parse_project_md("")
        assert project.name == ""
        assert project.version == ""
