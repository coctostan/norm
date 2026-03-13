# NORM — Notifier & Observer for Running Milestones

## What This Is

A real-time monitoring dashboard for PALS projects. NORM watches `.paul/STATE.md` and related files across multiple projects and presents a unified view of project status, phase progress, loop positions, blockers, and activity — all in a web UI with live updates.

## Core Value

Developers managing multiple PALS projects can see the state of all their work in one place without switching terminals.

## Current State

| Attribute | Value |
|-----------|-------|
| Version | 0.0.0 |
| Status | Greenfield |
| Last Updated | 2026-03-13 |

## Requirements

### Active (In Progress)

- [ ] Project registry — add/remove PALS project paths to monitor
- [ ] Multi-project dashboard — cards showing phase, loop position, progress for each project
- [ ] Project detail view — roadmap, recent activity, decisions, blockers
- [ ] Real-time updates — WebSocket push when STATE.md changes
- [ ] Blocker/alert surfacing — highlight projects with active blockers at top level
- [ ] Dark mode — monitoring tools should be dark-first

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
*Last updated: 2026-03-13*
