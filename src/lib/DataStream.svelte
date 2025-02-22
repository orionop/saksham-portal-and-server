<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { cameraStore } from './stores';

  type DataLog = {
    timestamp: string;
    cameraId: string;
    gasConcentration: number;
    personDetected: boolean;
    coordinates: { lat: number; lng: number };
  };

  let dataLogs: DataLog[] = [];
  let ws: WebSocket;
  let connectionStatus: 'connected' | 'disconnected' | 'connecting' = 'disconnected';
  let updateFrequency = 0;
  let lastUpdateTime = Date.now();

  const WS_URL = 'ws://localhost:7090/live'; // Replace with your WebSocket URL
  // ws://saksham.local:7090/live - when using rpi
  // Calculate update frequency using exponential moving average
  function updateFrequencyStats() {
    const now = Date.now();
    const timeDiff = now - lastUpdateTime;
    const instantFrequency = 1000 / timeDiff; // Convert to updates per second
    
    // Use exponential moving average with 0.2 smoothing factor
    updateFrequency = updateFrequency * 0.8 + instantFrequency * 0.2;
    lastUpdateTime = now;
  }

  function connectWebSocket() {
    connectionStatus = 'connecting';
    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      connectionStatus = 'connected';
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const newLog: DataLog = JSON.parse(event.data);
        updateFrequencyStats();
        
        // Update the camera store with the latest data
        cameraStore.update(store => ({
          ...store,
          [newLog.cameraId]: {
            id: newLog.cameraId,
            coordinates: newLog.coordinates,
            gasConcentration: newLog.gasConcentration,
            personDetected: newLog.personDetected,
            lastUpdate: newLog.timestamp
          }
        }));
        
        dataLogs = [newLog, ...dataLogs].slice(0, 20); // Keep last 20 records
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onclose = () => {
      connectionStatus = 'disconnected';
      console.log('WebSocket disconnected, attempting to reconnect...');
      setTimeout(connectWebSocket, 5000); // Attempt to reconnect after 5 seconds
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      ws.close();
    };
  }

  onMount(() => {
    connectWebSocket();
  });

  onDestroy(() => {
    if (ws) {
      ws.close();
    }
  });

  function formatCoordinates(coords: { lat: number; lng: number }) {
    const latDir = coords.lat >= 0 ? 'N' : 'S';
    const lngDir = coords.lng >= 0 ? 'E' : 'W';
    return `${Math.abs(coords.lat).toFixed(4)}°${latDir}, ${Math.abs(coords.lng).toFixed(4)}°${lngDir}`;
  }
</script>

<div class="data-stream-container">
  <div class="header">
    <div class="header-main">
      <h2>Live Data Stream</h2>
      <span class="status-indicator" class:connected={connectionStatus === 'connected'}>●</span>
    </div>
    <div class="frequency-display">
      <span class="frequency-label">Update Rate:</span>
      <span class="frequency-value">{updateFrequency.toFixed(1)} updates/sec</span>
    </div>
  </div>
  
  <div class="logs-container">
    {#each dataLogs as log, i}
      <div class="log-entry" style="opacity: {Math.max(0.2, 1 - i * 0.15)}">
        <div class="log-header">
          <span class="timestamp">{new Date(log.timestamp).toLocaleTimeString()}</span>
          <span class="camera-id">{log.cameraId === '1' ? 'RVR' : 'AIR'} Camera</span>
        </div>
        <div class="log-details">
          <span class="coordinates">Location: {formatCoordinates(log.coordinates)}</span>
          <span class="gas">Gas: {log.gasConcentration}ppm</span>
          <span class="person">Person: {log.personDetected ? 'Detected' : 'None'}</span>
        </div>
      </div>
    {/each}
    }
  </div>
</div>

<style>
  .data-stream-container {
    background: #f4f4f4;
    border-radius: 8px;
    padding: 1rem;
    margin-top: 2rem;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e2e2e2;
  }

  .header-main {
    display: flex;
    align-items: center;
  }

  .header h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0;
  }

  .status-indicator {
    margin-left: 1rem;
    color: #666;
    animation: pulse 2s infinite;
  }

  .status-indicator.connected {
    color: #22c55e;
  }

  .frequency-display {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: #e2e2e2;
    padding: 0.5rem 1rem;
    border-radius: 999px;
    font-size: 0.875rem;
  }

  .frequency-label {
    color: #666;
  }

  .frequency-value {
    font-family: monospace;
    font-weight: 600;
    color: #1a1a1a;
  }

  @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
  }

  .logs-container {
    max-height: 400px;
    overflow-y: auto;
  }

  .log-entry {
    background: white;
    border-radius: 4px;
    padding: 0.75rem;
    margin-bottom: 0.5rem;
    transition: opacity 0.3s ease;
  }

  .log-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
  }

  .timestamp {
    color: #666;
  }

  .camera-id {
    font-weight: 500;
    color: #1a1a1a;
  }

  .log-details {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    font-size: 0.875rem;
  }

  .coordinates, .gas, .person {
    background: #f8f8f8;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-family: monospace;
  }
</style>