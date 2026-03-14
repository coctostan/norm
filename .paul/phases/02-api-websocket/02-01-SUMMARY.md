---
phase: 02-api-websocket
plan: 01
subsystem: api
tags: [fastapi, websocket, dashboard, real-time, broadcast]

requires:
  - phase: 01-backend-core
    provides: FastAPI server, SQLite schema, project registry, file watcher, markdown parsers

provides:
  - GET /api/dashboard endpoint (all projects with inline state)
  - WebSocket /ws endpoint with connection management
  - Watcher-to-WebSocket broadcast pipeline
  - ConnectionManager singleton for WebSocket state

affects:
  - 03-frontend-shell (consumes dashboard API + WebSocket)

tech-stack:
  added: []
  patterns: [on_sync callback for watcher extensibility, LEFT JOIN for dashboard aggregation]

key-files:
  created: [backend/websocket.py, tests/test_api.py, tests/test_websocket.py]
  modified: [backend/main.py, backend/schemas.py, backend/registry.py, backend/models.py, backend/watcher.py]

key-decisions:
  - "Decision: Separate dashboard_router from projects router for clean URL prefix"
  - "Decision: on_sync as optional async callback rather than event emitter"

patterns-established:
  - "Pattern: Watcher extensibility via on_sync callback — decouples sync from notification"
  - "Pattern: ConnectionManager singleton for WebSocket state management"

duration: ~15min
started: 2026-03-13T12:00:00Z
completed: 2026-03-13T12:15:00Z
---

# Phase 2 Plan 01: Dashboard API + WebSocket + Watcher Integration Summary

**REST dashboard endpoint, WebSocket server with connection management, and watcher→WebSocket broadcast pipeline for real-time state push.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~15 min |
| Tasks | 3 completed |
| Files modified | 7 (2 new source, 2 new test, 3 modified) |
| Tests | 46 total (35 existing + 11 new), all passing |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: Dashboard endpoint returns all projects with state | Pass | LEFT JOIN returns projects with inline state, handles NULL gracefully |
| AC-2: WebSocket connection and message flow | Pass | /ws sends initial_state on connect, receives broadcasts |
| AC-3: WebSocket connection management | Pass | ConnectionManager tracks/removes connections, handles failures |
| AC-4: Watcher broadcasts via WebSocket | Pass | on_sync callback fires after successful sync, broadcasts to all clients |

## Accomplishments

- Dashboard endpoint (`GET /api/dashboard`) returns all projects with inline state in a single efficient query
- WebSocket server at `/ws` with `ConnectionManager` that handles connect/disconnect/broadcast
- File watcher now triggers WebSocket broadcasts via async `on_sync` callback after successful syncs
- 11 new tests covering dashboard API (4) and WebSocket lifecycle (7)

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `backend/websocket.py` | Created | ConnectionManager class + module-level singleton |
| `backend/schemas.py` | Modified | DashboardProject + DashboardResponse models |
| `backend/models.py` | Modified | get_dashboard_projects() with LEFT JOIN query |
| `backend/registry.py` | Modified | dashboard_router + GET /api/dashboard endpoint |
| `backend/main.py` | Modified | WebSocket /ws endpoint, _on_sync callback, watcher wiring |
| `backend/watcher.py` | Modified | on_sync callback parameter + invocation after sync |
| `tests/test_api.py` | Created | 4 dashboard endpoint tests |
| `tests/test_websocket.py` | Created | 7 WebSocket + ConnectionManager tests |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| Separate dashboard_router | Dashboard lives at /api/dashboard, not under /api/projects | Clean URL structure for frontend |
| on_sync as optional async callback | Simpler than event emitter, no new deps, backward compatible | Watcher tests unaffected (defaults to None) |
| Broadcast full project list on change | Simpler than per-project delta messages | Frontend gets complete state on every update |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Auto-fixed | 1 | Essential NULL handling fix |

**Total impact:** Minimal — one NULL coercion fix for LEFT JOIN edge case.

### Auto-fixed Issues

**1. NULL boolean coercion in dashboard query**
- **Found during:** Task 1 (dashboard endpoint)
- **Issue:** LEFT JOIN returns NULL for loop_plan/loop_apply/loop_unify when no state synced
- **Fix:** Added explicit NULL→False coercion in get_dashboard_projects()
- **Verification:** test_dashboard_with_project_no_state passes

### Deferred Items

None.

## Issues Encountered

None.

## Next Phase Readiness

**Ready:**
- Full REST API available for frontend consumption (dashboard + project CRUD + sync + state)
- WebSocket /ws endpoint ready for real-time updates
- Watcher→WebSocket pipeline operational

**Concerns:**
- None

**Blockers:**
- None

---
*Phase: 02-api-websocket, Plan: 01*
*Completed: 2026-03-13*
