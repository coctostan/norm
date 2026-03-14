<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { wsStore } from '$lib/stores/websocket.svelte.js';
	import ConnectionStatus from '$lib/components/ConnectionStatus.svelte';

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
	<ConnectionStatus />
	<header class="border-b border-border/50 bg-background/80 px-6 py-3 backdrop-blur-sm">
		<div class="mx-auto flex max-w-7xl items-baseline gap-3">
			<h1 class="text-lg font-bold tracking-tight">NORM</h1>
			<p class="text-xs text-muted-foreground">Notifier & Observer for Running Milestones</p>
		</div>
	</header>

	<main class="mx-auto max-w-7xl px-6 py-6">
		{@render children()}
	</main>
</div>
