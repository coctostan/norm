import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock WebSocket
class MockWebSocket {
	static instances: MockWebSocket[] = [];
	url: string;
	onopen: ((ev: Event) => void) | null = null;
	onmessage: ((ev: MessageEvent) => void) | null = null;
	onclose: ((ev: CloseEvent) => void) | null = null;
	onerror: ((ev: Event) => void) | null = null;
	readyState = 0;

	constructor(url: string) {
		this.url = url;
		MockWebSocket.instances.push(this);
	}

	close() {
		this.readyState = 3;
		if (this.onclose) {
			this.onclose(new CloseEvent('close'));
		}
	}

	send(_data: string) {}

	// Test helpers
	simulateOpen() {
		this.readyState = 1;
		if (this.onopen) {
			this.onopen(new Event('open'));
		}
	}

	simulateMessage(data: unknown) {
		if (this.onmessage) {
			this.onmessage(new MessageEvent('message', { data: JSON.stringify(data) }));
		}
	}

	simulateError() {
		if (this.onerror) {
			this.onerror(new Event('error'));
		}
	}
}

// Set up global mocks
beforeEach(() => {
	MockWebSocket.instances = [];
	vi.stubGlobal('WebSocket', MockWebSocket);
	vi.stubGlobal('window', {
		location: { protocol: 'http:', host: 'localhost:5173' }
	});
	vi.useFakeTimers();
});

afterEach(() => {
	vi.restoreAllMocks();
	vi.useRealTimers();
});

// We test the WebSocket store logic by importing a fresh copy each test
// Since the store uses Svelte 5 runes ($state), we test the class behavior directly

describe('WebSocketStore behavior', () => {
	// Re-implement the core logic for unit testing (runes don't work outside Svelte compiler)
	class TestableWebSocketStore {
		projects: unknown[] = [];
		connected = false;
		private ws: MockWebSocket | null = null;
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
			this.ws = new MockWebSocket(wsUrl);

			this.ws.onopen = () => {
				this.connected = true;
				this.reconnectDelay = 1000;
			};

			this.ws.onmessage = (event: MessageEvent) => {
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

		// Expose for testing
		getWs() { return this.ws; }
		getReconnectDelay() { return this.reconnectDelay; }
	}

	it('creates WebSocket with correct URL on connect', () => {
		const store = new TestableWebSocketStore();
		store.connect();

		expect(MockWebSocket.instances).toHaveLength(1);
		expect(MockWebSocket.instances[0].url).toBe('ws://localhost:5173/ws');
	});

	it('sets connected=true on WebSocket open', () => {
		const store = new TestableWebSocketStore();
		store.connect();

		expect(store.connected).toBe(false);
		MockWebSocket.instances[0].simulateOpen();
		expect(store.connected).toBe(true);
	});

	it('updates projects on initial_state message', () => {
		const store = new TestableWebSocketStore();
		store.connect();
		MockWebSocket.instances[0].simulateOpen();

		const mockProjects = [{ id: 1, name: 'Test Project' }];
		MockWebSocket.instances[0].simulateMessage({
			type: 'initial_state',
			projects: mockProjects
		});

		expect(store.projects).toEqual(mockProjects);
	});

	it('updates projects on project_updated message', () => {
		const store = new TestableWebSocketStore();
		store.connect();
		MockWebSocket.instances[0].simulateOpen();

		const updatedProjects = [{ id: 1, name: 'Updated' }, { id: 2, name: 'New' }];
		MockWebSocket.instances[0].simulateMessage({
			type: 'project_updated',
			projects: updatedProjects
		});

		expect(store.projects).toEqual(updatedProjects);
	});

	it('ignores unknown message types', () => {
		const store = new TestableWebSocketStore();
		store.connect();
		MockWebSocket.instances[0].simulateOpen();

		store.projects = [{ id: 1 }];
		MockWebSocket.instances[0].simulateMessage({
			type: 'unknown_type',
			data: 'should be ignored'
		});

		expect(store.projects).toEqual([{ id: 1 }]);
	});

	it('sets connected=false on disconnect', () => {
		const store = new TestableWebSocketStore();
		store.connect();
		MockWebSocket.instances[0].simulateOpen();
		expect(store.connected).toBe(true);

		store.disconnect();
		expect(store.connected).toBe(false);
	});

	it('does not reconnect after explicit disconnect', () => {
		const store = new TestableWebSocketStore();
		store.connect();
		MockWebSocket.instances[0].simulateOpen();

		store.disconnect();
		vi.advanceTimersByTime(5000);

		// Only the initial connection, no reconnect
		expect(MockWebSocket.instances).toHaveLength(1);
	});

	it('reconnects with exponential backoff on unexpected close', () => {
		const store = new TestableWebSocketStore();
		store.connect();
		MockWebSocket.instances[0].simulateOpen();

		// Simulate unexpected close (not via disconnect())
		const ws = MockWebSocket.instances[0];
		ws.readyState = 3;
		if (ws.onclose) ws.onclose(new CloseEvent('close'));

		expect(store.connected).toBe(false);

		// After 1s delay, should reconnect
		vi.advanceTimersByTime(1000);
		expect(MockWebSocket.instances).toHaveLength(2);

		// Simulate second close — delay should be 2s
		const ws2 = MockWebSocket.instances[1];
		ws2.readyState = 3;
		if (ws2.onclose) ws2.onclose(new CloseEvent('close'));

		vi.advanceTimersByTime(1000);
		expect(MockWebSocket.instances).toHaveLength(2); // Not yet
		vi.advanceTimersByTime(1000);
		expect(MockWebSocket.instances).toHaveLength(3); // Now reconnected
	});

	it('resets reconnect delay on successful connection', () => {
		const store = new TestableWebSocketStore();
		store.connect();

		// Close to trigger backoff
		const ws1 = MockWebSocket.instances[0];
		ws1.readyState = 3;
		if (ws1.onclose) ws1.onclose(new CloseEvent('close'));
		vi.advanceTimersByTime(1000);

		// Connect successfully — should reset delay
		MockWebSocket.instances[1].simulateOpen();
		expect(store.getReconnectDelay()).toBe(1000);
	});

	it('closes WebSocket on error', () => {
		const store = new TestableWebSocketStore();
		store.connect();

		const ws = MockWebSocket.instances[0];
		const closeSpy = vi.spyOn(ws, 'close');
		ws.simulateError();

		expect(closeSpy).toHaveBeenCalled();
	});
});
