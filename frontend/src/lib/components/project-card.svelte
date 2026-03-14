<script lang="ts">
	import { goto } from '$app/navigation';
	import type { DashboardProject } from '$lib/types.js';
	import * as Card from '$lib/components/ui/card/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Progress } from '$lib/components/ui/progress/index.js';

	let { project }: { project: DashboardProject } = $props();

	let phaseLabel = $derived(
		project.phase_number && project.phase_total
			? `Phase ${project.phase_number} of ${project.phase_total}`
			: 'No phase data'
	);

	let phaseProgress = $derived(
		project.progress_phase != null ? Math.round(project.progress_phase) : 0
	);
</script>

<Card.Root
	class="flex cursor-pointer flex-col transition-all hover:border-foreground/25 hover:shadow-md hover:shadow-black/20"
	onclick={() => goto(`/project/${project.id}`)}
	role="link"
	tabindex={0}
	onkeydown={(e: KeyboardEvent) => { if (e.key === 'Enter') goto(`/project/${project.id}`); }}
>
	<Card.Header class="pb-2">
		<div class="flex items-start justify-between">
			<div>
				<Card.Title class="text-base">{project.name}</Card.Title>
				<Card.Description>
					{phaseLabel}
					{#if project.phase_name}
						— {project.phase_name}
					{/if}
				</Card.Description>
			</div>
			{#if project.blocker_count > 0}
				<Badge variant="destructive" class="ml-2 shrink-0">
					{project.blocker_count} blocker{project.blocker_count > 1 ? 's' : ''}
				</Badge>
			{/if}
		</div>
	</Card.Header>

	<Card.Content class="flex-1 space-y-3">
		<!-- Loop Position -->
		<div class="space-y-1">
			<p class="text-xs font-medium text-muted-foreground">Loop</p>
			<div class="flex items-center gap-1.5">
				<Badge variant={project.loop_plan ? 'default' : 'outline'} class="text-xs">
					Plan
				</Badge>
				<span class="text-muted-foreground">›</span>
				<Badge variant={project.loop_apply ? 'default' : 'outline'} class="text-xs">
					Apply
				</Badge>
				<span class="text-muted-foreground">›</span>
				<Badge variant={project.loop_unify ? 'default' : 'outline'} class="text-xs">
					Unify
				</Badge>
			</div>
		</div>

		<!-- Progress -->
		<div class="space-y-1">
			<div class="flex items-center justify-between">
				<p class="text-xs font-medium text-muted-foreground">Phase Progress</p>
				<span class="text-xs text-muted-foreground">{phaseProgress}%</span>
			</div>
			<Progress value={phaseProgress} max={100} />
		</div>
	</Card.Content>

	<Card.Footer>
		{#if project.last_activity}
			<p class="text-xs text-muted-foreground">{project.last_activity}</p>
		{:else}
			<p class="text-xs text-muted-foreground">No recent activity</p>
		{/if}
	</Card.Footer>
</Card.Root>
