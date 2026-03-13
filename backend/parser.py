import os
import re
from datetime import datetime, timezone

from backend.parser_models import (
    LoopPosition,
    ParsedProject,
    ParsedRoadmap,
    ParsedState,
    PhaseProgress,
    ProjectFullState,
)


def parse_state_md(content: str) -> ParsedState:
    state = ParsedState()

    # Milestone
    m = re.search(r"^Milestone:\s*(.+)$", content, re.MULTILINE)
    if m:
        state.milestone = m.group(1).strip()

    # Phase: N of M (Name)
    m = re.search(r"^Phase:\s*(\d+)\s+of\s+(\d+)\s*\(([^)]+)\)", content, re.MULTILINE)
    if m:
        state.phase_number = int(m.group(1))
        state.phase_total = int(m.group(2))
        state.phase_name = m.group(3).strip()

    # Plan
    m = re.search(r"^Plan:\s*(.+)$", content, re.MULTILINE)
    if m:
        state.plan = m.group(1).strip()

    # Status
    m = re.search(r"^Status:\s*(.+)$", content, re.MULTILINE)
    if m:
        state.status = m.group(1).strip()

    # Loop position from code block
    loop_block = re.search(r"```\s*\n(.*?PLAN.*?UNIFY.*?\n.*?)```", content, re.DOTALL)
    if loop_block:
        loop_text = loop_block.group(1)
        # Find the line with ✓/○ markers
        marker_line = ""
        for line in loop_text.split("\n"):
            if "✓" in line or "○" in line:
                marker_line = line
                break
        if marker_line:
            # Extract markers in order: plan, apply, unify
            markers = re.findall(r"[✓○]", marker_line)
            if len(markers) >= 3:
                state.loop = LoopPosition(
                    plan=markers[0] == "✓",
                    apply=markers[1] == "✓",
                    unify=markers[2] == "✓",
                )
            # Description is in brackets at end
            desc_match = re.search(r"\[(.+?)\]", marker_line)
            if desc_match:
                state.loop.description = desc_match.group(1).strip()

    # Progress percentages
    for line in content.split("\n"):
        if "Foundation:" in line or "Milestone:" in line.lower():
            pct = re.search(r"(\d+)%", line)
            if pct and state.progress_milestone is None:
                state.progress_milestone = float(pct.group(1))
        if re.search(r"Phase\s+\d+:", line):
            pct = re.search(r"(\d+)%", line)
            if pct:
                state.progress_phase = float(pct.group(1))

    # Last activity
    m = re.search(r"^Last activity:\s*(.+)$", content, re.MULTILINE)
    if m:
        state.last_activity = m.group(1).strip()

    # Blockers
    blockers_section = re.search(
        r"###\s*Blockers/Concerns\s*\n(.*?)(?=\n###|\n##|\n---|\Z)",
        content,
        re.DOTALL,
    )
    if blockers_section:
        section_text = blockers_section.group(1).strip()
        if section_text and "none" not in section_text.lower():
            for line in section_text.split("\n"):
                line = line.strip()
                if line.startswith("- ") and line != "- None":
                    state.blockers.append(line[2:].strip())

    # Decisions table
    decisions_section = re.search(
        r"###\s*Decisions\s*\n(.*?)(?=\n###|\n##|\n---|\Z)",
        content,
        re.DOTALL,
    )
    if decisions_section:
        table_text = decisions_section.group(1).strip()
        rows = table_text.split("\n")
        for row in rows:
            if "|" in row and not row.strip().startswith("|--") and "Decision" not in row:
                cols = [c.strip() for c in row.split("|") if c.strip()]
                if len(cols) >= 3:
                    state.decisions.append(
                        {"decision": cols[0], "phase": cols[1], "impact": cols[2]}
                    )

    return state


def parse_roadmap_md(content: str) -> ParsedRoadmap:
    roadmap = ParsedRoadmap()

    # Milestone name and version: **v0.1 Foundation** (v0.1.0)
    m = re.search(r"\*\*(.+?)\*\*\s*\(([^)]+)\)", content)
    if m:
        roadmap.milestone_name = m.group(1).strip()
        roadmap.milestone_version = m.group(2).strip()

    # Milestone status
    m = re.search(r"^Status:\s*(.+)$", content, re.MULTILINE)
    if m:
        roadmap.milestone_status = m.group(1).strip()

    # Phases table: | Phase | Name | Plans | Status | Completed |
    table_match = re.search(
        r"\|\s*Phase\s*\|\s*Name\s*\|.*?\n\|[-|\s]+\n(.*?)(?=\n\n|\n##|\Z)",
        content,
        re.DOTALL,
    )
    if table_match:
        for row in table_match.group(1).strip().split("\n"):
            cols = [c.strip() for c in row.split("|") if c.strip()]
            if len(cols) >= 4:
                try:
                    phase_num = int(cols[0])
                except ValueError:
                    continue
                plan_count = None
                try:
                    plan_count = int(cols[2])
                except ValueError:
                    if cols[2].upper() != "TBD":
                        plan_count = None

                roadmap.phases.append(
                    PhaseProgress(
                        number=phase_num,
                        name=cols[1],
                        plan_count=plan_count,
                        status=cols[3],
                        completed_date=cols[4] if len(cols) > 4 and cols[4] != "-" else None,
                    )
                )

    return roadmap


def parse_project_md(content: str) -> ParsedProject:
    project = ParsedProject()

    # Name and description from H1: # NAME — Description
    m = re.search(r"^#\s+(.+?)(?:\s*—\s*(.+))?$", content, re.MULTILINE)
    if m:
        project.name = m.group(1).strip()
        if m.group(2):
            project.description = m.group(2).strip()

    # Version from table row
    m = re.search(r"\|\s*Version\s*\|\s*(.+?)\s*\|", content)
    if m:
        project.version = m.group(1).strip()

    # Status from table row
    m = re.search(r"\|\s*Status\s*\|\s*(.+?)\s*\|", content)
    if m:
        project.status = m.group(1).strip()

    # Last Updated from table row or footer
    m = re.search(r"\|\s*Last Updated\s*\|\s*(.+?)\s*\|", content)
    if m:
        project.last_updated = m.group(1).strip()
    else:
        m = re.search(r"\*Last updated:\s*(.+?)\*", content)
        if m:
            project.last_updated = m.group(1).strip()

    return project


async def parse_project_state(project_path: str) -> ProjectFullState:
    paul_dir = os.path.join(project_path, ".paul")
    now = datetime.now(timezone.utc).isoformat()

    state = None
    roadmap = None
    project = None

    # Parse STATE.md
    state_path = os.path.join(paul_dir, "STATE.md")
    try:
        with open(state_path) as f:
            state = parse_state_md(f.read())
    except (FileNotFoundError, PermissionError):
        pass

    # Parse ROADMAP.md
    roadmap_path = os.path.join(paul_dir, "ROADMAP.md")
    try:
        with open(roadmap_path) as f:
            roadmap = parse_roadmap_md(f.read())
    except (FileNotFoundError, PermissionError):
        pass

    # Parse PROJECT.md
    project_path_file = os.path.join(paul_dir, "PROJECT.md")
    try:
        with open(project_path_file) as f:
            project = parse_project_md(f.read())
    except (FileNotFoundError, PermissionError):
        pass

    return ProjectFullState(
        state=state,
        roadmap=roadmap,
        project=project,
        synced_at=now,
    )
