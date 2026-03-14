<script lang="ts">
	import { wsStore } from '$lib/stores/websocket.svelte.js';
	import ProjectCard from '$lib/components/project-card.svelte';

	let sortedProjects = $derived(
		[...wsStore.projects].sort((a, b) => {
			if (a.blocker_count !== b.blocker_count) return b.blocker_count - a.blocker_count;
			const aTime = a.last_activity ?? '';
			const bTime = b.last_activity ?? '';
			return bTime.localeCompare(aTime);
		})
	);
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<h2 class="text-lg font-semibold">Dashboard</h2>
		<div class="flex items-center gap-2 text-sm text-muted-foreground">
			<span
				class="inline-block h-2 w-2 rounded-full {wsStore.connected
					? 'bg-emerald-500'
					: 'bg-yellow-500'}"
			></span>
			{wsStore.connected ? 'Connected' : 'Connecting...'}
		</div>
	</div>

	{#if sortedProjects.length === 0}
		<div class="flex min-h-[300px] items-center justify-center">
			<p class="text-muted-foreground">
				{wsStore.connected ? 'No projects monitored yet' : 'Connecting to server...'}
			</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
			{#each sortedProjects as project (project.id)}
				<ProjectCard {project} />
			{/each}
		</div>
	{/if}
</div>
