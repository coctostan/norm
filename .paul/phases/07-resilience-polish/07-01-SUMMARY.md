---
phase: 07-resilience-polish
plan: 01
subsystem: backend
tags: [graceful-shutdown, watcher-resilience, websocket-ping, fastapi, asyncio]

requires: []
provides:
  - Graceful shutdown with WebSocket close code 1001
  - Watcher recovery for missing/moved directories
  - Server-side WebSocket ping messages (type: "ping") every 30s idle
affects:
  - 07-02 (frontend must handle "ping" messages from server)

tech-stack:
  added: []
  patterns: [lifespan shutdown flag, per-connection ping via asyncio.wait_for timeout]

key-files:
  created: [tests/test_watcher_resilience.py]
  modified: [backend/main.py, backend/watcher.py]

key-decisions:
  - "Decision: Ping implemented inline in websocket_endpoint via asyncio.wait_for timeout, not as separate ConnectionManager method"
  - "Decision: websocket.py broadcast cleanup already sufficient — no changes needed"

patterns-established:
  - "Pattern: app.state.shutting_down flag for coordinated shutdown across endpoints"
  - "Pattern: asyncio.wait_for with timeout for idle-based ping in WebSocket loops"

duration: ~8min
started: 2026-03-14T17:20:00Z
completed: 2026-03-14T17:28:00Z
---

# Phase 7 Plan 01: Backend Resilience Summary

**Graceful shutdown, watcher directory recovery, and WebSocket ping/pong keep-alive for production-grade backend reliability.**

## Performance

| Metric | Value |
|--------|-------|
| Duration | ~8 min |
| Tasks | 3 completed |
| Files modified | 3 (2 modified, 1 created) |
| Tests | 53 total (46 existing + 7 new) |

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC-1: Graceful Shutdown | Pass | Lifespan cleanup sets shutting_down flag, closes WS connections with 1001, stops watcher |
| AC-2: Watcher Recovery on Missing Directory | Pass | Filters missing dirs before awatch, catches OSError/FileNotFoundError during sync |
| AC-3: WebSocket Ping/Pong Keep-Alive | Pass | 30s idle timeout sends ping message, failed send breaks connection loop |

## Accomplishments

- Graceful shutdown sequence: flag → close WebSocket connections (1001) → stop watcher
- Watcher skips missing .paul/ directories and continues watching remaining projects
- WebSocket endpoint sends ping after 30s idle, detecting stale connections

## Files Created/Modified

| File | Change | Purpose |
|------|--------|---------|
| `backend/main.py` | Modified | Added shutting_down flag, WS close on shutdown, ping/pong in endpoint |
| `backend/watcher.py` | Modified | Directory existence filtering, OSError/FileNotFoundError handling in sync |
| `tests/test_watcher_resilience.py` | Created | 7 tests: missing dirs, sync errors, lifecycle idempotency |

## Decisions Made

| Decision | Rationale | Impact |
|----------|-----------|--------|
| Ping in websocket_endpoint, not ConnectionManager | Per-connection timeout is simpler than background ping task | No separate ping coroutine needed |
| websocket.py unchanged | broadcast() already removes failed connections on send error | Less code changed |

## Deviations from Plan

### Summary

| Type | Count | Impact |
|------|-------|--------|
| Scope reduction | 1 | Minimal — websocket.py already had the needed behavior |

**Total impact:** Minor — Task 3 (WS ping/pong) was partially absorbed into Task 1's websocket_endpoint changes. websocket.py didn't need modification.

### Details

**1. websocket.py not modified**
- **Plan expected:** Separate ping_all() method in ConnectionManager
- **Actual:** Ping implemented per-connection in websocket_endpoint via asyncio.wait_for timeout
- **Reason:** Simpler approach, no background task needed, same outcome
- **Files:** backend/websocket.py untouched (was in plan's files_modified)

## Issues Encountered

None — clean execution.

## Retrospective

**Issue Timeline:** Clean execution — no issues encountered.

**Outcome Evaluation:**
- AC-1 (shutdown): Straightforward lifespan cleanup — plan was well-scoped
- AC-2 (watcher recovery): Existing code already had some resilience; additions were targeted
- AC-3 (ping): Plan suggested ConnectionManager approach but per-connection timeout was better

**Improvement Notes:**
- Plan could have recommended the asyncio.wait_for approach directly after reading the existing websocket_endpoint code
- Good task sizing — 3 tasks for 3 files was right

## Next Phase Readiness

**Ready:**
- Backend sends "ping" messages that 07-02 frontend must handle
- app.state.shutting_down flag available for any future endpoint coordination

**Concerns:**
- None

**Blockers:**
- None — ready for Plan 07-02 (frontend resilience)

---
*Phase: 07-resilience-polish, Plan: 01*
*Completed: 2026-03-14*
