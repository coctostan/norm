---
phase: 01-backend-core
plan: 01
subsystem: infra
tags: [fastapi, sqlite, aiosqlite, pydantic, uvicorn, github-actions, ruff, ci-cd]

requires: []
provides:
  - FastAPI server with health check endpoint
  - SQLite projects table with async CRUD
  - Project registry REST API with .paul/ path validation
  - GitHub repo with CI pipeline and branch protection ruleset
  - Conventional commit and trunk-based branching conventions
affects:
  - 01-backend-core (plans 02, 03 build on this foundation)
  - 02-api-websocket (extends these endpoints)

tech-stack:
  added: [fastapi, uvicorn, aiosqlite, pydantic, pydantic-settings, pyyaml, watchfiles, ruff, pytest, httpx]
  patterns: ["aiosqlite direct (no ORM) for cache layer", "pydantic-settings with NORM_ env prefix", "FastAPI lifespan for DB init"]

key-files:
  created: [backend/main.py, backend/database.py, backend/models.py, backend/registry.py, backend/schemas.py, backend/config.py, pyproject.toml, .github/workflows/ci.yml, norm.yaml]
  modified: []

key-decisions:
  - "Decision: Made repo public for free-tier branch protection rulesets"
  - "Decision: aiosqlite direct instead of SQLAlchemy — simpler for cache use case"
  - "Decision: Added .claude/skills/ to .gitignore — embedded git repos"

patterns-established:
  - "Pattern: Conventional commits (feat:, fix:, chore:, docs:, ci:)"
  - "Pattern: Branch naming phase-{NN}/{plan-NN}-{slug}"
  - "Pattern: PR required to merge to main, CI must pass, 0 approvals"

duration: ~20min
started: 2026-03-13T18:45:00Z
completed: 2026-03-13T19:15:00Z
---

# Phase 1 Plan 01: Backend Scaffolding Summary

**FastAPI server with SQLite project registry, GitHub repo with CI/CD and branch protection — NORM's complete backend foundation.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~20min |
| Started | 2026-03-13T18:45:00Z |
| Completed | 2026-03-13T19:15:00Z |
| Tasks | 5 completed |
| Files created | 11 |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: FastAPI Server Starts | Pass | uvicorn starts, GET /health returns {"status": "ok"} |
| AC-2: SQLite Database Initializes | Pass | norm.db created with projects table on startup |
| AC-3: Project Registry CRUD | Pass | POST/GET/DELETE all verified with curl |
| AC-4: Path Validation | Pass | Invalid paths return 422 with clear message |
| AC-5: GitHub Repo with CI/CD | Pass | CI workflow defined, triggers on push and PR |
| AC-6: Branch Protection | Pass | Ruleset created via gh api — PR required, CI must pass |

## Accomplishments

- Standing FastAPI server with async SQLite database layer (no ORM, aiosqlite direct)
- Full CRUD project registry API with .paul/ path validation and duplicate detection (409)
- GitHub repo (public) with CI pipeline (ruff lint + format + pytest) and branch protection ruleset

## Task Commits

| Task | Commit | Type | Description |
|------|--------|------|-------------|
| All tasks | `747ed27` | feat | Initial project scaffolding with FastAPI, SQLite, and project registry |

Note: Initial commit bundled all tasks (greenfield project). Future plans will use per-task or per-plan commits.

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `pyproject.toml` | Created | Python project config, dependencies, ruff/pytest config |
| `backend/__init__.py` | Created | Package marker |
| `backend/main.py` | Created | FastAPI app, lifespan, health check, CORS, router mount |
| `backend/config.py` | Created | pydantic-settings with NORM_ env prefix |
| `backend/database.py` | Created | aiosqlite init_db() and get_db() async generator |
| `backend/models.py` | Created | SQL CRUD functions for projects table |
| `backend/schemas.py` | Created | Pydantic request/response models |
| `backend/registry.py` | Created | /api/projects router with path validation |
| `norm.yaml` | Created | Example config (projects list + settings) |
| `.gitignore` | Created | Python, DB, IDE, OS, future frontend ignores |
| `.github/workflows/ci.yml` | Created | CI pipeline — ruff + pytest on push/PR |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| Public repo | Free-tier GitHub doesn't support rulesets on private repos | Repo is now public at github.com/coctostan/norm |
| aiosqlite direct (no ORM) | SQLite is a cache layer, not primary storage — ORM overhead not justified | Simpler code, fewer deps, but manual SQL |
| .claude/skills/ in .gitignore | Skills dirs are embedded git repos, cause submodule warnings | Skills not tracked in repo |
| Python 3.14 venv (local) / 3.12 CI | Local machine has 3.14, CI uses 3.12 — both >=3.11 requirement | pyproject.toml targets >=3.11 for compatibility |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-fixed | 2 | Minor — build config fixes |
| Scope additions | 1 | Added 409 duplicate detection to registry |
| Deferred | 0 | — |

**Total impact:** Essential fixes, no scope creep.

### Auto-fixed Issues

**1. Build backend incompatibility**
- **Found during:** Task 2 (Python scaffolding)
- **Issue:** `setuptools.backends._legacy:_Backend` doesn't exist in current setuptools
- **Fix:** Changed to `setuptools.build_meta`
- **Verification:** `pip install -e ".[dev]"` succeeds

**2. ruff format violation**
- **Found during:** Task 4 verification
- **Issue:** `backend/models.py` had a line exceeding format rules
- **Fix:** Ran `ruff format backend/`
- **Verification:** `ruff format --check backend/` passes

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| `python` not found (macOS) | Used `python3` — system has 3.14.3 via Homebrew |
| Rulesets require GitHub Pro on private repos | Made repo public |
| .claude/skills/ embedded git repo warnings | Added to .gitignore, removed from staging |

## Next Phase Readiness

**Ready:**
- FastAPI server running and tested
- SQLite schema established with async CRUD
- Project registry API ready for consumers (Plan 01-02 parser, Plan 01-03 watcher)
- CI/CD pipeline ready for PR-based workflow

**Concerns:**
- CI hasn't actually run yet (no PR created) — will validate on first feature branch PR
- norm.yaml config file exists but isn't used by the app yet (API-only registry)

**Blockers:**
- None

---
*Phase: 01-backend-core, Plan: 01*
*Completed: 2026-03-13*
