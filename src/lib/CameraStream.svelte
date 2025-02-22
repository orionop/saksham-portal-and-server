<script lang="ts">
  import { onMount } from 'svelte';

  export let cameraId: string;
  export let coordinates: { lat: number; lng: number };
  export let gasConcentration: number;
  export let personDetected: boolean;
  export let hideGas: boolean;
  
  $: statusColor = personDetected ? 'bg-green-500' : 'bg-red-500';
  $: gasLevel = gasConcentration > 50 ? 'High' : gasConcentration > 25 ? 'Medium' : 'Low';
  $: gasColor = gasConcentration > 50 ? 'bg-red-500' : gasConcentration > 25 ? 'bg-yellow-500' : 'bg-green-500';
  $: show = hideGas === false;

  // Format coordinates to cardinal directions
  $: formattedCoordinates = formatCoordinates(coordinates);

  function formatCoordinates(coords: { lat: number; lng: number }) {
    const latDir = coords.lat >= 0 ? 'N' : 'S';
    const lngDir = coords.lng >= 0 ? 'E' : 'W';
    return `${Math.abs(coords.lat).toFixed(4)}°${latDir}, ${Math.abs(coords.lng).toFixed(4)}°${lngDir}`;
  }

  // Replace these URLs with your actual camera stream URLs
  const getStreamUrl = (id: string) => {
    return `http://saksham.local:7090/camera${id}`;
  };

  let imgElement: HTMLImageElement;
  
  // onMount(() => {
  //   // Simulate a live stream by updating the image
  //   // Replace this with your actual stream connection logic
  //   const updateImage = () => {
  //     // For demonstration, we're using a placeholder service
  //     // Replace this with your actual camera stream URL
  //     imgElement.src = `https://picsum.photos/800/450?random=${Date.now()}`;
  //   };

  //   // Update every 1 second to simulate live feed
  //   const interval = setInterval(updateImage, 1000);
  //   updateImage();

  //   return () => {
  //     clearInterval(interval);
  //   };
  // });
</script>

<div class="camera-container">
  <div class="camera-header">
    <h2 class="camera-title">{cameraId === '1' ? 'RVR' : 'AIR'} Camera</h2>
    <span class="camera-id">ID: {cameraId}</span>
  </div>
  
  <div class="camera-stream">
    <img
      src={getStreamUrl(cameraId)}
      alt="Camera {cameraId} Stream"
      class="stream-image"
    />
  </div>
  
  <div class="data-container">
    <div class="data-item">
      <span class="label">Location:</span>
      <span class="value">{formattedCoordinates}</span>
    </div>
    
    {#if show}
    <div class="data-item">
      <span class="label">Gas Concentration:</span>
      <span class="pill {gasColor}">{gasLevel} ({gasConcentration}ppm)</span>
    </div>
    
    <div class="data-item">
      <span class="label">Person Detected:</span>
      <span class="pill {statusColor}">{personDetected ? 'Yes' : 'No'}</span>
    </div>
    {/if}
    
  </div>
</div>

<style>
  .camera-container {
    background: #f4f4f4;
    border-radius: 8px;
    padding: 1rem;
  }
  
  .camera-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e2e2e2;
  }

  .camera-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0;
  }

  .camera-id {
    font-size: 0.875rem;
    color: #666;
    padding: 0.25rem 0.5rem;
    background: #e2e2e2;
    border-radius: 4px;
  }
  
  .camera-stream {
    background: #2a2a2a;
    height: 270px;
    border-radius: 4px;
    margin-bottom: 1rem;
    overflow: hidden;
  }
  
  .stream-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .data-container {
    display: grid;
    gap: 0.5rem;
  }
  
  .data-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .label {
    font-weight: 500;
    color: #666;
  }
  
  .value {
    font-family: monospace;
    background: #e2e2e2;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.875rem;
  }
  
  .pill {
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    color: white;
    font-size: 0.875rem;
  }
  
  :global(.bg-red-500) {
    background-color: #ef4444;
  }
  
  :global(.bg-yellow-500) {
    background-color: #eab308;
  }
  
  :global(.bg-green-500) {
    background-color: #22c55e;
  }
</style>