<script lang="ts">
  import Map from './lib/Map.svelte';
  import CameraStream from './lib/CameraStream.svelte';
  import DataStream from './lib/DataStream.svelte';
  import { cameraStore } from './lib/stores';

  $: cameras = Object.values($cameraStore);
</script>

<main>
  <div class="container">
    <h1>Sasksham Ground Control</h1>
    
    <div class="dashboard-grid">
      <div class="cameras-column">
        <div class="cameras-grid">
          <CameraStream 
            cameraId="1"
            coordinates={$cameraStore["1"].coordinates}
            gasConcentration={$cameraStore["1"].gasConcentration}
            personDetected={$cameraStore["1"].personDetected}
            hideGas={false}
          />
          
          <CameraStream 
            cameraId="2"
            coordinates={$cameraStore["2"].coordinates}
            gasConcentration={$cameraStore["2"].gasConcentration}
            personDetected={$cameraStore["2"].personDetected}
            hideGas={true}
          />
        </div>
      </div>
      
      <div class="map-container">
        <Map height="100%" {cameras} />
      </div>
    </div>

    <DataStream />
  </div>
</main>

<style>
  .container {
    width: 100%;
    max-width: 1600px;
    margin: 0 auto;
    padding: 2rem;
  }

  h1 {
    font-size: 2rem;
    margin-bottom: 2rem;
    color: #333;
  }

  .dashboard-grid {
    display: grid;
    grid-template-columns: minmax(300px, 1fr) 2fr;
    gap: 2rem;
    margin-bottom: 2rem;
    min-height: 800px;
  }

  .cameras-column {
    display: flex;
    flex-direction: column;
  }

  .cameras-grid {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .map-container {
    background: #f4f4f4;
    border-radius: 8px;
    overflow: hidden;
  }

  @media (max-width: 1024px) {
    .dashboard-grid {
      grid-template-columns: 1fr;
    }

    .map-container {
      height: 600px;
    }
  }

  :global(body) {
    margin: 0;
    padding: 0;
    min-height: 100vh;
    background-color: #ffffff;
    color: #213547;
  }
</style>