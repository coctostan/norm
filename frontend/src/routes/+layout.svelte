<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { wsStore } from '$lib/stores/websocket.svelte.js';

	let { children } = $props();

	onMount(() => {
		wsStore.connect();
		return () => wsStore.disconnect();
	});
</script>

<svelte:head>
	<title>NORM — Project Monitor</title>
</svelte:head>

<div class="min-h-screen bg-background text-foreground">
	<header class="border-b border-border px-6 py-4">
		<div class="mx-auto max-w-7xl">
			<h1 class="text-xl font-bold tracking-tight">NORM</h1>
			<p class="text-sm text-muted-foreground">Notifier & Observer for Running Milestones</p>
		</div>
	</header>

	<main class="mx-auto max-w-7xl px-6 py-6">
		{@render children()}
	</main>
</div>
