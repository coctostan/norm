import type { DashboardProject } from '$lib/types.js';

class WebSocketStore {
	projects = $state<DashboardProject[]>([]);
	connected = $state(false);
	reconnecting = $state(false);
	lastUpdated = $state<Date | null>(null);

	private ws: WebSocket | null = null;
	private reconnectDelay = 1000;
	private maxReconnectDelay = 30000;
	private shouldReconnect = true;

	connect() {
		this.shouldReconnect = true;
		this.createConnection();
	}

	disconnect() {
		this.shouldReconnect = false;
		if (this.ws) {
			this.ws.close();
			this.ws = null;
		}
		this.connected = false;
		this.reconnecting = false;
	}

	private createConnection() {
		// In dev mode, connect directly to backend (Vite proxy doesn't reliably handle WebSocket upgrades)
		// In production, backend serves everything so relative path works
		const wsUrl = import.meta.env.DEV
			? 'ws://localhost:8000/ws'
			: `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;

		this.ws = new WebSocket(wsUrl);

		this.ws.onopen = () => {
			this.connected = true;
			this.reconnecting = false;
			this.reconnectDelay = 1000;
		};

		this.ws.onmessage = (event) => {
			const data = JSON.parse(event.data);

			if (data.type === 'ping') {
				return;
			}

			if (data.type === 'initial_state' || data.type === 'project_updated') {
				this.projects = data.projects;
				this.lastUpdated = new Date();
			}
		};

		this.ws.onclose = () => {
			this.connected = false;
			this.ws = null;

			if (this.shouldReconnect) {
				this.reconnecting = true;
				setTimeout(() => {
					this.createConnection();
					this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
				}, this.reconnectDelay);
			}
		};

		this.ws.onerror = () => {
			this.ws?.close();
		};
	}
}

export const wsStore = new WebSocketStore();
