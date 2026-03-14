# Roadmap: NORM

## Overview

NORM — Notifier & Observer for Running Milestones. A real-time monitoring dashboard for PALS projects. Built as a companion tool that reads `.paul/` state files and presents a unified web UI with live updates. The journey starts with a solid backend foundation, adds API/WebSocket layer, builds the frontend shell, then polishes detail views and testing.

## Current Milestone

**v0.2 Operational** (v0.2.0)
Status: 🚧 In Progress
Phases: 1 of 3 complete

## Milestones

### v0.1 Foundation (v0.1.0) — ✅ Complete

| Phase | Name | Plans | Status | Completed |
|-------|------|-------|--------|-----------|
| 1 | Backend Core | 3 | ✅ Complete | 2026-03-13 |
| 2 | API & WebSocket | 1 | ✅ Complete | 2026-03-13 |
| 3 | Frontend Shell | 1 | ✅ Complete | 2026-03-13 |
| 4 | Detail Views & Polish | 3 | ✅ Complete | 2026-03-14 |

### v0.2 Operational (v0.2.0) — 🚧 In Progress

| Phase | Name | Plans | Status | Completed |
|-------|------|-------|--------|-----------|
| 5 | Startup & Registration | 1 | ✅ Complete | 2026-03-14 |
| 6 | E2E Validation & Bug Fixes | TBD | Not started | - |
| 7 | Resilience & Polish | TBD | Not started | - |

## Phase Details

### Phase 1: Backend Core (v0.1)

**Goal:** Standing FastAPI server with SQLite schema, markdown parser, file watcher, and project registry
**Depends on:** Nothing (first phase)
**Research:** Unlikely (established patterns)

**Scope:**
- FastAPI server scaffolding with async support
- SQLite schema for project index/cache
- Markdown parser for STATE.md, ROADMAP.md, PROJECT.md
- File watcher (watchfiles) for real-time change detection
- Project registry — add/remove PALS project paths

**Plans:**
- [x] 01-01: FastAPI scaffolding + SQLite schema + Project registry
- [x] 01-02: Markdown parser for PALS state files
- [x] 01-03: File watcher with change detection

### Phase 2: API & WebSocket (v0.1)

**Goal:** REST endpoints for project data and WebSocket server for real-time push updates
**Depends on:** Phase 1 (backend core running, data indexed)
**Research:** Unlikely (FastAPI native WebSocket support)

**Scope:**
- REST API endpoints for project list, project detail, phase data
- WebSocket server for real-time state change notifications
- API response models and serialization
- Connection management and reconnection handling

**Plans:**
- [x] 02-01: Dashboard API + WebSocket server + watcher integration

### Phase 3: Frontend Shell (v0.1)

**Goal:** SvelteKit app with dashboard layout, project cards, and live WebSocket updates
**Depends on:** Phase 2 (API available to consume)
**Research:** Likely (shadcn-svelte + LayerChart integration patterns)
**Research topics:** shadcn-svelte component composition, LayerChart for progress visualization, WebSocket client with Svelte 5 runes

**Scope:**
- SvelteKit app scaffolding with shadcn-svelte and Tailwind
- Dashboard layout with project card grid
- Project cards showing phase, loop position, progress, last activity
- WebSocket client for real-time updates via $state runes
- Lucide icons integration

**Plans:**
- [x] 03-01: SvelteKit scaffolding + shadcn-svelte + WebSocket store + dashboard cards

### Phase 4: Detail Views & Polish (v0.1)

**Goal:** Project detail page, roadmap visualization, blocker alerts, dark mode polish, end-to-end testing
**Depends on:** Phase 3 (dashboard shell functional)
**Research:** Unlikely (building on established patterns from Phase 3)

**Scope:**
- Project detail page — roadmap, phase breakdown, decisions, blockers
- Blocker/alert surfacing at dashboard level
- Dark mode polish (Grafana density, Linear polish, Vercel dark)
- End-to-end testing
- Performance tuning for 10+ projects

**Plans:**
- [x] 04-01: Project detail page + blocker alert surfacing
- [x] 04-02: Dark mode polish + production adapter config
- [x] 04-03: Backend + frontend test suites (29 + 10 tests)

### Phase 5: Startup & Registration (v0.2)

**Goal:** Single-command startup and easy project registration with persistent config
**Depends on:** Phase 4 (all foundation code complete)
**Research:** Unlikely (shell scripting + config file patterns)

**Scope:**
- Unified run script (dev mode: concurrent backend + frontend dev servers)
- Production mode (serve built frontend from backend)
- CLI for project add/remove with persistent config
- Config file persistence (projects survive restart)

**Plans:**
- [x] 05-01: Config file persistence + startup scripts (dev + prod)

### Phase 6: E2E Validation & Bug Fixes (v0.2)

**Goal:** Validate the full system works end-to-end with real PALS projects
**Depends on:** Phase 5 (startup script works, projects registered)
**Research:** Unlikely (testing existing code with real data)

**Scope:**
- Register real PALS projects and verify dashboard populates
- Smoke test full loop: file change → watcher → parser → API → WebSocket → UI update
- Fix integration bugs discovered during real-world usage
- Validate detail page renders correctly with live project data

**Plans:**
- TBD (defined during /paul:plan)

### Phase 7: Resilience & Polish (v0.2)

**Goal:** Production-grade error handling, graceful shutdown, and performance validation
**Depends on:** Phase 6 (system works end-to-end, bugs fixed)
**Research:** Unlikely (established error handling patterns)

**Scope:**
- WebSocket reconnection edge cases (server restart, network blip)
- Watcher recovery (watched directory deleted/moved)
- Graceful shutdown (clean up connections, stop watchers)
- Performance validation with 5-10+ concurrent projects
- Error boundaries in frontend (connection lost, API errors)

**Plans:**
- TBD (defined during /paul:plan)

---
*Roadmap created: 2026-03-13*
*Last updated: 2026-03-14 — Phase 5 complete*
