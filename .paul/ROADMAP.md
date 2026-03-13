# Roadmap: NORM

## Overview

NORM — Notifier & Observer for Running Milestones. A real-time monitoring dashboard for PALS projects. Built as a companion tool that reads `.paul/` state files and presents a unified web UI with live updates. The journey starts with a solid backend foundation, adds API/WebSocket layer, builds the frontend shell, then polishes detail views and testing.

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

## Phase Details

### Phase 1: Backend Core

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
- [ ] 01-01: FastAPI scaffolding + SQLite schema + Project registry
- [ ] 01-02: Markdown parser for PALS state files
- [ ] 01-03: File watcher with change detection

### Phase 2: API & WebSocket

**Goal:** REST endpoints for project data and WebSocket server for real-time push updates
**Depends on:** Phase 1 (backend core running, data indexed)
**Research:** Unlikely (FastAPI native WebSocket support)

**Scope:**
- REST API endpoints for project list, project detail, phase data
- WebSocket server for real-time state change notifications
- API response models and serialization
- Connection management and reconnection handling

**Plans:**
- [ ] 02-01: TBD (defined during /paul:plan)

### Phase 3: Frontend Shell

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
- [ ] 03-01: TBD (defined during /paul:plan)

### Phase 4: Detail Views & Polish

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
- [ ] 04-01: TBD (defined during /paul:plan)

---
*Roadmap created: 2026-03-13*
*Last updated: 2026-03-13*
