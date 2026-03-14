<script lang="ts">
	import * as Card from '$lib/components/ui/card/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import { Progress } from '$lib/components/ui/progress/index.js';
	import { Separator } from '$lib/components/ui/separator/index.js';

	let { data } = $props();

	let state = $derived(data.state);
	let roadmap = $derived(data.roadmap);
	let project = $derived(data.project);

	let milestoneProgress = $derived(
		state?.progress_milestone != null ? Math.round(state.progress_milestone) : 0
	);

	let phaseProgress = $derived(
		state?.progress_phase != null ? Math.round(state.progress_phase) : 0
	);

	function phaseStatusVariant(status: string): 'default' | 'outline' | 'secondary' | 'destructive' {
		if (status.toLowerCase().includes('complete')) return 'default';
		if (status.toLowerCase().includes('progress')) return 'secondary';
		return 'outline';
	}
</script>

<svelte:head>
	<title>{project?.name ?? 'Project'} — NORM</title>
</svelte:head>

<div class="space-y-4">
	<!-- Header -->
	<div class="flex items-start justify-between">
		<div>
			<a href="/" class="text-xs text-muted-foreground hover:text-foreground">&larr; Dashboard</a>
			<h2 class="mt-1 text-xl font-bold">{project?.name ?? 'Unknown Project'}</h2>
			{#if project?.description}
				<p class="mt-1 text-sm text-muted-foreground">{project.description}</p>
			{/if}
		</div>
		{#if project?.version}
			<Badge variant="outline" class="text-xs">{project.version}</Badge>
		{/if}
	</div>

	<!-- Status Bar -->
	{#if state}
		<Card.Root class="border-l-2 border-l-primary">
			<Card.Content class="pt-4">
				<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
					<!-- Milestone -->
					<div class="space-y-1">
						<p class="text-xs font-medium text-muted-foreground">Milestone</p>
						<p class="text-sm font-semibold">{state.milestone || 'None'}</p>
					</div>

					<!-- Current Phase -->
					<div class="space-y-1">
						<p class="text-xs font-medium text-muted-foreground">Phase</p>
						<p class="text-sm font-semibold">
							{#if state.phase_number && state.phase_total}
								{state.phase_number} of {state.phase_total} — {state.phase_name || ''}
							{:else}
								No phase data
							{/if}
						</p>
					</div>

					<!-- Plan Status -->
					<div class="space-y-1">
						<p class="text-xs font-medium text-muted-foreground">Plan</p>
						<p class="text-sm font-semibold">{state.plan || state.status || 'None'}</p>
					</div>

					<!-- Loop Position -->
					<div class="space-y-1">
						<p class="text-xs font-medium text-muted-foreground">Loop</p>
						<div class="flex items-center gap-2">
							<Badge variant={state.loop.plan ? 'default' : 'outline'} class="text-xs">Plan</Badge>
							<span class="text-muted-foreground">›</span>
							<Badge variant={state.loop.apply ? 'default' : 'outline'} class="text-xs">Apply</Badge>
							<span class="text-muted-foreground">›</span>
							<Badge variant={state.loop.unify ? 'default' : 'outline'} class="text-xs">Unify</Badge>
						</div>
					</div>
				</div>

				<!-- Progress Bars -->
				<div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
					<div class="space-y-1.5">
						<div class="flex items-center justify-between">
							<p class="text-xs font-medium text-muted-foreground">Milestone Progress</p>
							<span class="text-xs text-muted-foreground">{milestoneProgress}%</span>
						</div>
						<Progress value={milestoneProgress} max={100} />
					</div>
					<div class="space-y-1.5">
						<div class="flex items-center justify-between">
							<p class="text-xs font-medium text-muted-foreground">Phase Progress</p>
							<span class="text-xs text-muted-foreground">{phaseProgress}%</span>
						</div>
						<Progress value={phaseProgress} max={100} />
					</div>
				</div>
			</Card.Content>
		</Card.Root>
	{/if}

	<!-- Blockers -->
	{#if state && state.blockers.length > 0}
		<Card.Root class="border-destructive">
			<Card.Header>
				<Card.Title class="text-destructive">
					Blockers ({state.blockers.length})
				</Card.Title>
			</Card.Header>
			<Card.Content>
				<ul class="space-y-2">
					{#each state.blockers as blocker}
						<li class="flex items-start gap-2 text-sm">
							<span class="mt-0.5 text-destructive">&#x2022;</span>
							<span>{blocker}</span>
						</li>
					{/each}
				</ul>
			</Card.Content>
		</Card.Root>
	{/if}

	<!-- Roadmap Phases -->
	{#if roadmap && roadmap.phases.length > 0}
		<Card.Root>
			<Card.Header>
				<Card.Title>Roadmap</Card.Title>
				<Card.Description>
					{roadmap.milestone_name}
					{#if roadmap.milestone_version}
						({roadmap.milestone_version})
					{/if}
					{#if roadmap.milestone_status}
						— {roadmap.milestone_status}
					{/if}
				</Card.Description>
			</Card.Header>
			<Card.Content>
				<div class="relative ml-3 border-l border-border/60">
					{#each roadmap.phases as phase, i}
						{@const isCurrent = state?.phase_number === phase.number}
						<div
							class="relative flex items-center justify-between py-2 pl-6 pr-2 {isCurrent
								? 'bg-accent/50 rounded-r-md'
								: ''}"
						>
							<div class="absolute -left-3 flex h-6 w-6 items-center justify-center rounded-full text-xs font-medium {
								phase.status.toLowerCase().includes('complete')
									? 'bg-primary text-primary-foreground'
									: isCurrent
										? 'bg-secondary text-secondary-foreground'
										: 'bg-muted text-muted-foreground'
							}">
								{#if phase.status.toLowerCase().includes('complete')}
									&#x2713;
								{:else}
									{phase.number}
								{/if}
							</div>
							<div>
								<p class="text-sm font-medium">{phase.name}</p>
								{#if phase.completed_date}
									<p class="text-xs text-muted-foreground">Completed {phase.completed_date}</p>
								{/if}
							</div>
							<div class="flex items-center gap-2">
								{#if phase.plan_count != null}
									<span class="text-xs text-muted-foreground">
										{phase.plan_count} plan{phase.plan_count !== 1 ? 's' : ''}
									</span>
								{/if}
								<Badge variant={phaseStatusVariant(phase.status)} class="text-xs">
									{phase.status}
								</Badge>
							</div>
						</div>
					{/each}
				</div>
			</Card.Content>
		</Card.Root>
	{/if}

	<!-- Decisions -->
	{#if state && state.decisions.length > 0}
		<Card.Root>
			<Card.Header>
				<Card.Title>Decisions</Card.Title>
			</Card.Header>
			<Card.Content>
				<div class="overflow-x-auto">
					<table class="w-full text-xs">
						<thead>
							<tr class="border-b border-border text-left">
								<th class="pb-1.5 pr-3 font-medium text-muted-foreground">Decision</th>
								<th class="pb-1.5 pr-3 font-medium text-muted-foreground">Rationale</th>
								<th class="pb-1.5 pr-3 font-medium text-muted-foreground">Date</th>
								<th class="pb-1.5 font-medium text-muted-foreground">Status</th>
							</tr>
						</thead>
						<tbody>
							{#each state.decisions as decision}
								<tr class="border-b border-border/50">
									<td class="py-1.5 pr-3">{decision.decision ?? ''}</td>
									<td class="py-1.5 pr-3 text-muted-foreground">{decision.rationale ?? ''}</td>
									<td class="py-1.5 pr-3 text-muted-foreground whitespace-nowrap">{decision.date ?? ''}</td>
									<td class="py-1.5">
										{#if decision.status}
											<Badge variant="outline" class="text-xs">{decision.status}</Badge>
										{/if}
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</Card.Content>
		</Card.Root>
	{/if}

	<!-- Last Activity & Sync -->
	<div class="flex items-center justify-between text-xs text-muted-foreground">
		{#if state?.last_activity}
			<span>Last activity: {state.last_activity}</span>
		{:else}
			<span></span>
		{/if}
		{#if data.synced_at}
			<span>Synced: {data.synced_at}</span>
		{/if}
	</div>
</div>
