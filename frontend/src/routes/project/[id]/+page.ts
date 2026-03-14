import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';
import type { ProjectStateResponse } from '$lib/types.js';

export const load: PageLoad = async ({ params, fetch }) => {
	const res = await fetch(`/api/projects/${params.id}/state`);

	if (!res.ok) {
		if (res.status === 404) {
			error(404, 'Project not found or not synced yet');
		}
		error(res.status, 'Failed to load project state');
	}

	const state: ProjectStateResponse = await res.json();

	return {
		projectId: Number(params.id),
		...state
	};
};
