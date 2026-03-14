<script lang="ts">
	import { wsStore } from '$lib/stores/websocket.svelte.js';
	import { slide } from 'svelte/transition';

	let showConnected = $state(false);
	let connectedTimeout: ReturnType<typeof setTimeout> | null = null;

	let wasReconnecting = $state(false);

	$effect(() => {
		if (wsStore.reconnecting) {
			wasReconnecting = true;
		}

		if (wsStore.connected && wasReconnecting) {
			wasReconnecting = false;
			showConnected = true;
			if (connectedTimeout) clearTimeout(connectedTimeout);
			connectedTimeout = setTimeout(() => {
				showConnected = false;
			}, 2000);
		}
	});
</script>

{#if wsStore.reconnecting}
	<div
		transition:slide={{ duration: 200 }}
		class="bg-amber-500/90 py-1 px-4 text-center text-sm text-amber-950"
	>
		<span class="inline-block animate-pulse">Connection lost — reconnecting...</span>
	</div>
{:else if showConnected}
	<div
		transition:slide={{ duration: 200 }}
		class="bg-emerald-500/90 py-1 px-4 text-center text-sm text-emerald-950"
	>
		Connected
	</div>
{/if}
