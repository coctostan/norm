# NORM — Notifier & Observer for Running Milestones

## What This Is

A real-time monitoring dashboard for PALS projects. NORM watches `.paul/STATE.md` and related files across multiple projects and presents a unified view of project status, phase progress, loop positions, blockers, and activity — all in a web UI with live updates.

## Core Value

Developers managing multiple PALS projects can see the state of all their work in one place without switching terminals.

## Current State

| Attribute | Value |
|-----------|-------|
| Version | 0.2.0-dev |
| Status | v0.2 Operational in progress |
| Last Updated | 2026-03-14 |

## Requirements

### Validated (Shipped)

- [x] Project registry — add/remove PALS project paths to monitor — Phase 1
- [x] Markdown parsing — parse STATE.md, ROADMAP.md, PROJECT.md into structured data — Phase 1
- [x] File watching — detect changes to .paul/ files in real-time via watchfiles — Phase 1
- [x] Dashboard API — all projects with inline state in single endpoint — Phase 2
- [x] Real-time updates — WebSocket push when .paul/ files change — Phase 2
- [x] WebSocket connection management — connect/disconnect/broadcast lifecycle — Phase 2
- [x] Multi-project dashboard — cards showing phase, loop position, progress for each project — Phase 3
- [x] Dark mode — monitoring tools should be dark-first — Phase 3
- [x] Project detail view — roadmap, recent activity, decisions, blockers — Phase 4
- [x] Blocker/alert surfacing — highlight projects with active blockers at top level — Phase 4
- [x] Backend test suite — 29 tests (parser + API) — Phase 4
- [x] Frontend test suite — 10 tests (WebSocket store) — Phase 4
- [x] Unified startup script — single command starts backend + frontend (dev + prod) — Phase 5
- [x] Config file persistence — projects survive restart via norm.yaml — Phase 5
- [x] End-to-end validation — full loop verified with real PALS projects — Phase 6
- [x] Auto-sync on startup/registration — immediate state availability — Phase 6

### Active (In Progress)

- [ ] Error handling & resilience — reconnection, watcher recovery, graceful shutdown
- [ ] Performance validation — smooth operation with 5-10+ projects

### Planned (Next)

- [ ] TUI client — terminal UI consuming the same API
- [ ] Multi-device sync — monitor projects across machines
- [ ] Actionable controls — trigger PAUL commands from the UI

### Out of Scope

- Replacing PALS — NORM reads state, never writes it
- SaaS/hosted version — local tool only for v1
- Non-PALS projects — only monitors `.paul/` convention

## Target Users

**Primary:** Developers using PALS who manage 2-10+ concurrent projects
- Frequently switch between projects
- Want oversight without terminal context-switching
- Need to know which projects have blockers or are stalled

## Context

**Technical Context:**
- PALS stores all state in `.paul/` directories as markdown files
- STATE.md is the single source of truth per project
- No existing tool monitors structured markdown project state
- Research confirmed nothing does even 30% of what NORM needs

## Constraints

### Technical Constraints
- Must not modify PALS files (read-only consumer)
- Must work with any PALS project (parse .paul/ conventions)
- SQLite for index/cache — markdown stays source of truth
- Local-first (no cloud dependency for v1)

### Design Constraints
- Must not look boilerplate/template-y
- Must be intuitive — minimal learning curve
- Dark mode first
- Inspired by: Grafana (panel density), Linear (polish), Vercel (clean dark mode)

## Key Decisions

| Decision | Rationale | Date | Status |
|----------|-----------|------|--------|
| Separate repo from PALS | NORM is a companion tool, not a PALS extension | 2026-03-13 | Active |
| FastAPI + SvelteKit + SQLite | Full-stack control, real-time WebSocket native, lightweight | 2026-03-13 | Active |
| shadcn-svelte for UI components | Anti-boilerplate (own your components), Tailwind-native, Svelte 5 ready | 2026-03-13 | Active |
| LayerChart for visualization | Svelte-native, composable, first-class shadcn-svelte integration | 2026-03-13 | Active |
| File watching over polling | Real-time updates, works locally, fast | 2026-03-13 | Active |
| Build from scratch (not on Dashy/Grafana) | Existing frameworks fight the PALS data model | 2026-03-13 | Active |
| aiosqlite direct (no ORM) | Cache layer, not primary storage — simpler | 2026-03-13 | Active |
| Regex parsing over markdown AST | No new deps, structured md has consistent formatting | 2026-03-13 | Active |
| on_sync callback for watcher extensibility | Decouples sync from notification, backward compatible | 2026-03-13 | Active |
| Broadcast full project list on state change | Simpler than per-project deltas, frontend gets complete state | 2026-03-13 | Active |
| Class-based $state WebSocket store | Svelte 5 runes pattern, cleaner than Svelte stores | 2026-03-13 | Active |
| Vite proxy for /api and /ws in dev | Avoids CORS config, single origin in development | 2026-03-13 | Active |
| No Playwright/e2e for v0.1 | Unit + integration tests sufficient for alpha | 2026-03-14 | Active |
| Testable store mirror class | Svelte 5 $state runes can't run outside compiler | 2026-03-14 | Active |
| load_config/save_config as plain functions | Simple, matches config.py style | 2026-03-14 | Active |
| save_config preserves YAML settings section | User settings survive project mutations | 2026-03-14 | Active |

## Tech Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Backend | FastAPI (Python) | Async, native WebSocket support |
| Database | SQLite (aiosqlite) | Index/cache, markdown stays source of truth |
| File Watching | watchfiles | Async file system monitoring |
| Frontend | SvelteKit | Svelte 5 with runes |
| Styling | Tailwind CSS | Via shadcn-svelte |
| UI Components | shadcn-svelte | Built on Bits UI + Melt UI |
| Charts | LayerChart | Svelte-native, composable SVG |
| Icons | Lucide | 1,600+ icons, shadcn-svelte default |
| Toasts | Svelte Sonner | Part of shadcn-svelte ecosystem |
| Animation | Svelte transitions + AutoAnimate | Built-in + list reorder animations |
| Real-time | Native WebSocket + $state runes | No Socket.io needed for local |

## Success Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Projects monitorable | 10+ | 0 | Not started |
| State refresh latency | <1s | - | Not started |
| MVP usable for daily workflow | Yes | No | Not started |

## Specialized Flows

See: .paul/SPECIAL-FLOWS.md

Quick Reference:
- /sveltekit-svelte5-tailwind → Frontend pages, layouts, routing, Tailwind styling
- /shadcn-svelte → UI components — cards, buttons, dialogs, data tables
- /svelte-skills-kit → Svelte 5 patterns — runes, reactivity, transitions

---
*PROJECT.md — Updated when requirements or context change*
*Last updated: 2026-03-14 after Phase 6 — E2E Validation complete*
