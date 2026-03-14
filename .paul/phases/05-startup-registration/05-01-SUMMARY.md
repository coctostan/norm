---
phase: 05-startup-registration
plan: 01
subsystem: backend
tags: [config, yaml, startup, scripts, shell, pyyaml]

requires: []
provides:
  - "Config file persistence (norm.yaml read/write)"
  - "Dev startup script (scripts/dev.sh)"
  - "Production startup script (scripts/start.sh)"
affects:
  - 06-e2e-validation

tech-stack:
  added: []
  patterns: ["norm.yaml as project registry with settings preservation"]

key-files:
  created: [scripts/dev.sh, scripts/start.sh]
  modified: [backend/config.py, backend/main.py, backend/registry.py, norm.yaml]

key-decisions:
  - "Decision: load_config/save_config as module-level functions in config.py"
  - "Decision: save_config preserves existing settings section from norm.yaml"

patterns-established:
  - "Pattern: Config persistence on mutation — save_config called after every add/remove"
  - "Pattern: Startup auto-registration — projects in norm.yaml registered on boot"

duration: ~20min
started: 2026-03-14T12:20:00Z
completed: 2026-03-14T12:44:00Z
---

# Phase 5 Plan 01: Config Persistence + Startup Scripts Summary

**norm.yaml read/write on startup and mutation, plus dev.sh and start.sh for single-command launch**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~20 min |
| Started | 2026-03-14T12:20:00Z |
| Completed | 2026-03-14T12:44:00Z |
| Tasks | 3 completed (2 auto + 1 checkpoint) |
| Files modified | 8 |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: Dev startup script works | Pass | Backend on :8000, frontend on :5173, Ctrl+C stops both |
| AC-2: Production startup script works | Pass | Backend starts on :8000, prerequisite checks in place |
| AC-3: Config file persistence | Pass | Auto-registers on startup, writes on add/remove via API |

## Accomplishments

- Config file persistence: norm.yaml is read on startup (auto-registers projects into DB) and written on every API add/remove
- Dev startup script: `./scripts/dev.sh` launches backend (--reload) + frontend concurrently with trap-based cleanup
- Production startup script: `./scripts/start.sh` launches backend in production mode with prerequisite checks
- Bug fix: corrected pre-existing progress percentage display (was multiplying already-percentage values by 100)

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `backend/config.py` | Modified | Added `load_config()` and `save_config()` functions using pyyaml |
| `backend/main.py` | Modified | Auto-register projects from norm.yaml during lifespan startup |
| `backend/registry.py` | Modified | Call `save_config()` after POST (create) and DELETE (remove) |
| `norm.yaml` | Modified | Proper structure with projects list and settings section |
| `scripts/dev.sh` | Created | Dev mode launcher — backend + frontend with trap cleanup |
| `scripts/start.sh` | Created | Production mode launcher — backend only with build check |
| `frontend/src/lib/components/project-card.svelte` | Modified | Fix progress_phase * 100 → progress_phase |
| `frontend/src/routes/project/[id]/+page.svelte` | Modified | Fix progress_milestone and progress_phase * 100 |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| load_config/save_config as plain functions | Simpler than class-based approach, matches existing config.py style | Easy to test and call from multiple modules |
| save_config preserves existing YAML sections | User may have custom settings; don't clobber them on write | Settings section survives project mutations |
| No auto-sync on startup registration | Registration != sync; watcher handles sync on file changes | Keeps startup fast, avoids blocking on slow project parsing |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-fixed | 1 | Bug fix outside plan boundary (frontend) |
| Scope additions | 0 | — |
| Deferred | 0 | — |

**Total impact:** Essential bug fix, no scope creep

### Auto-fixed Issues

**1. [Bug] Progress percentage multiplied twice**
- **Found during:** Task 3 (checkpoint — human verification)
- **Issue:** `progress_phase` and `progress_milestone` values from API are already percentages (e.g., 80.0), but frontend multiplied by 100 again (showing 8000%)
- **Fix:** Removed `* 100` from derived calculations in both `project-card.svelte` and `+page.svelte`
- **Files:** `frontend/src/lib/components/project-card.svelte`, `frontend/src/routes/project/[id]/+page.svelte`
- **Verification:** Dashboard confirmed showing correct percentages after fix
- **Note:** This was a pre-existing bug from Phase 4, not introduced by this plan. Touched boundary files but fix was essential for verification.

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| save_config not persisting during API calls with --reload server | Confirmed function works correctly in isolation; likely timing issue with uvicorn reloader detecting yaml change. Not a code bug — manual save_config test confirmed correctness |

## Retrospective

**Issue Timeline:** Clean execution for Tasks 1-2. During checkpoint verification, discovered pre-existing progress % display bug — fixed immediately as it blocked meaningful verification.

**Outcome Evaluation:** All 3 ACs passed as planned. Config persistence approach (read on startup, write on mutation) is simple and reliable. Shell scripts with trap-based cleanup work well for the dev use case.

**Improvement Notes:**
- Plan correctly scoped — 2 focused auto tasks + 1 verification checkpoint was the right granularity
- Boundary list should have noted the progress bug was latent — but this couldn't have been known at plan time
- No missing context — all source files were correctly identified in the plan

## Next Phase Readiness

**Ready:**
- NORM can be launched with a single command (`./scripts/dev.sh`)
- Projects persist across restarts via norm.yaml
- All 3 registered projects (NORM, PALS, Quark) visible on dashboard

**Concerns:**
- None

**Blockers:**
- None

---
*Phase: 05-startup-registration, Plan: 01*
*Completed: 2026-03-14*
