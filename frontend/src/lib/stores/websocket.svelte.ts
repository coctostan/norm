import type { DashboardProject } from '$lib/types.js';

class WebSocketStore {
	projects = $state<DashboardProject[]>([]);
	connected = $state(false);

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
	}

	private createConnection() {
		const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		const wsUrl = `${protocol}//${window.location.host}/ws`;

		this.ws = new WebSocket(wsUrl);

		this.ws.onopen = () => {
			this.connected = true;
			this.reconnectDelay = 1000;
		};

		this.ws.onmessage = (event) => {
			const data = JSON.parse(event.data);

			if (data.type === 'initial_state' || data.type === 'project_updated') {
				this.projects = data.projects;
			}
		};

		this.ws.onclose = () => {
			this.connected = false;
			this.ws = null;

			if (this.shouldReconnect) {
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
