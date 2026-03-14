export interface DashboardProject {
	id: number;
	name: string;
	path: string;
	status: string;
	last_synced: string | null;
	created_at: string;
	milestone: string | null;
	phase_number: number | null;
	phase_total: number | null;
	phase_name: string | null;
	loop_plan: boolean;
	loop_apply: boolean;
	loop_unify: boolean;
	progress_milestone: number | null;
	progress_phase: number | null;
	plan_status: string | null;
	last_activity: string | null;
	blocker_count: number;
}

export interface LoopPosition {
	plan: boolean;
	apply: boolean;
	unify: boolean;
	description: string;
}

export interface PhaseProgress {
	number: number;
	name: string;
	plan_count: number | null;
	status: string;
	completed_date: string | null;
}

export interface ParsedState {
	milestone: string;
	phase_number: number;
	phase_total: number;
	phase_name: string;
	plan: string;
	status: string;
	loop: LoopPosition;
	progress_milestone: number | null;
	progress_phase: number | null;
	last_activity: string | null;
	blockers: string[];
	decisions: Record<string, string>[];
}

export interface ParsedRoadmap {
	milestone_name: string;
	milestone_version: string;
	milestone_status: string;
	phases: PhaseProgress[];
}

export interface ParsedProject {
	name: string;
	description: string;
	version: string;
	status: string;
	last_updated: string | null;
}

export interface ProjectStateResponse {
	state: ParsedState | null;
	roadmap: ParsedRoadmap | null;
	project: ParsedProject | null;
	synced_at: string;
}
