<script lang="ts">
  import { onMount } from 'svelte';
  import 'leaflet/dist/leaflet.css';
  import L from 'leaflet';
  import arrowIcon from '../assets/arrow.svg';

  export let height = '400px';
  export let cameras = [
    { id: '1', coordinates: { lat: 51.505, lng: -0.09 } },
    { id: '2', coordinates: { lat: 51.506, lng: -0.10 } }
  ];
  
  let mapElement: HTMLElement;
  
  onMount(() => {
    const map = L.map(mapElement).setView([51.505, -0.09], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Create custom icons for each camera with larger size
    const cameraIcon1 = L.icon({
      iconUrl: arrowIcon,
      iconSize: [48, 48], // Increased from 32x32 to 48x48
      iconAnchor: [24, 48], // Adjusted anchor point for larger size
      popupAnchor: [0, -48], // Adjusted popup anchor for larger size
      className: 'camera-marker camera-1'
    });

    const cameraIcon2 = L.icon({
      iconUrl: arrowIcon,
      iconSize: [48, 48], // Increased from 32x32 to 48x48
      iconAnchor: [24, 48], // Adjusted anchor point for larger size
      popupAnchor: [0, -48], // Adjusted popup anchor for larger size
      className: 'camera-marker camera-2'
    });

    // Add markers for each camera
    cameras.forEach((camera, index) => {
      const icon = index === 0 ? cameraIcon1 : cameraIcon2;
      const marker = L.marker([camera.coordinates.lat, camera.coordinates.lng], {
        icon: icon
      }).addTo(map);
      
      marker.bindPopup(`Camera ${camera.id}`);
    });

    // Add legend
    const legend = L.control({ position: 'bottomright' });
    
    legend.onAdd = function() {
      const div = L.DomUtil.create('div', 'legend');
      div.innerHTML = `
        <div class="legend-item">
          <img src="${arrowIcon}" class="legend-icon camera-1" alt="Camera 1" />
          <span>RVR</span>
        </div>
        <div class="legend-item">
          <img src="${arrowIcon}" class="legend-icon camera-2" alt="Camera 2" />
          <span>AIR</span>
        </div>
      `;
      return div;
    };
    
    legend.addTo(map);
  });
</script>

<div bind:this={mapElement} style="height: {height}"></div>

<style>
  div {
    width: 100%;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 1rem;
  }

  :global(.camera-marker.camera-1) {
    filter: hue-rotate(120deg); /* Green tint */
  }

  :global(.camera-marker.camera-2) {
    filter: hue-rotate(240deg); /* Blue tint */
  }

  :global(.legend) {
    background: white;
    padding: 10px;
    border-radius: 4px;
    box-shadow: 0 1px 5px rgba(0,0,0,0.2);
  }

  :global(.legend-item) {
    display: flex;
    align-items: center;
    margin: 5px 0;
  }

  :global(.legend-icon) {
    width: 24px;
    height: 24px;
    margin-right: 8px;
  }

  :global(.legend-icon.camera-1) {
    filter: hue-rotate(120deg); /* Green tint */
  }

  :global(.legend-icon.camera-2) {
    filter: hue-rotate(240deg); /* Blue tint */
  }
</style>