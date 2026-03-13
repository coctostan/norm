---
phase: 01-backend-core
plan: 03
subsystem: backend
tags: [watchfiles, file-watcher, async, real-time, change-detection, aiosqlite]

requires:
  - "01-02: Markdown parsers, cache upsert functions, sync flow"
provides:
  - FileWatcher class with async start/stop lifecycle
  - sync_project_by_path() standalone sync function
  - Filename filter for STATE.md/ROADMAP.md/PROJECT.md
  - App lifespan integration (watcher starts/stops with server)
affects:
  - 02-api-websocket (watcher will emit WebSocket notifications on sync)
  - 03-frontend-shell (real-time updates depend on watcher triggering syncs)

tech-stack:
  added: [watchfiles]
  patterns: ["Background asyncio.Task for long-running watcher", "stop_event for graceful shutdown", "Dynamic watch path refresh on project list change"]

key-files:
  created: [backend/watcher.py, tests/test_watcher.py]
  modified: [backend/main.py, backend/config.py]

key-decisions:
  - "Decision: Per-change DB connection rather than shared connection — simpler lifecycle, no stale connection issues"

patterns-established:
  - "Pattern: FileWatcher uses stop_event + task.cancel() for graceful shutdown"
  - "Pattern: Watch loop refreshes project list after each batch of changes to handle add/remove"
  - "Pattern: Filename filter via set membership, not glob — explicit and fast"

duration: ~8min
started: 2026-03-13T21:00:00Z
completed: 2026-03-13T21:08:00Z
---

# Phase 1 Plan 03: File Watcher Summary

**Async file watcher using watchfiles that monitors .paul/ directories and triggers automatic sync when STATE.md, ROADMAP.md, or PROJECT.md change — NORM now has real-time change detection.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~8min |
| Started | 2026-03-13T21:00:00Z |
| Completed | 2026-03-13T21:08:00Z |
| Tasks | 3 completed |
| Files created | 2 |
| Files modified | 2 |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: Watcher detects file changes | Pass | watchfiles.awatch monitors .paul/ dirs, debounce 1000ms |
| AC-2: Watcher triggers sync on change | Pass | sync_project_by_path() calls parse_project_state + upsert, tested with real tmp .paul/ |
| AC-3: Watcher only monitors relevant files | Pass | _is_monitored() filters to STATE.md/ROADMAP.md/PROJECT.md only, 6 filter tests pass |
| AC-4: Watcher lifecycle tied to app | Pass | Starts in lifespan setup, stops in teardown, stored on app.state |
| AC-5: Watcher handles project list changes | Pass | Watch loop breaks and restarts with new paths when project list changes |

## Accomplishments

- FileWatcher class with async start/stop lifecycle using watchfiles rust-backed OS notifications
- sync_project_by_path() standalone function reusing parser + cache logic from Plan 01-02
- Filename filter restricting sync triggers to STATE.md, ROADMAP.md, PROJECT.md only
- 14 new tests (35 total), all passing, lint clean

## Task Commits

| Task | Commit | Type | Description |
|------|--------|------|-------------|
| All tasks | uncommitted | feat | File watcher module, lifespan integration, tests |

Note: Work is uncommitted on feature/01-03-file-watcher branch. Will be committed during phase transition.

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `backend/watcher.py` | Created | FileWatcher class, sync_project_by_path(), _is_monitored(), _path_to_project_path() |
| `tests/test_watcher.py` | Created | 14 tests: filter helpers, sync integration, watcher lifecycle |
| `backend/main.py` | Modified | Added watcher to lifespan context manager (start on init, stop on shutdown) |
| `backend/config.py` | Modified | Added watch_debounce_ms setting (default 1000) |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| Per-change DB connection | Avoids stale connections in long-running watcher, simpler than connection pooling | Slightly more overhead per sync, but correct and simple |
| Default 1000ms debounce | Responsive enough for monitoring, avoids excessive syncs on rapid edits | Configurable via NORM_WATCH_DEBOUNCE_MS env var |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-fixed | 0 | — |
| Scope additions | 0 | — |
| Deferred | 0 | — |

**Total impact:** None — plan executed exactly as written.

## Issues Encountered

None — straightforward implementation.

## Next Phase Readiness

**Ready:**
- Phase 1 complete: FastAPI server, SQLite schema, markdown parsers, file watcher, project registry
- All 35 tests passing, lint clean
- Backend can register projects, parse state files, cache state, and detect changes in real-time
- Phase 2 (API & WebSocket) can build directly on this foundation

**Concerns:**
- None

**Blockers:**
- None

---
*Phase: 01-backend-core, Plan: 03*
*Completed: 2026-03-13*
