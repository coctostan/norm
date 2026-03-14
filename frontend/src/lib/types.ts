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
