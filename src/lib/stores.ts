import { writable } from 'svelte/store';

export type CameraData = {
  id: string;
  coordinates: { lat: number; lng: number };
  gasConcentration: number;
  personDetected: boolean;
  lastUpdate: string;
};

type CameraStore = {
  [key: string]: CameraData;
};

export const cameraStore = writable<CameraStore>({
  "1": {
    id: "1",
    coordinates: { lat: 51.505, lng: -0.09 },
    gasConcentration: 25,
    personDetected: false,
    lastUpdate: new Date().toISOString()
  },
  "2": {
    id: "2",
    coordinates: { lat: 51.506, lng: -0.10 },
    gasConcentration: 55,
    personDetected: false,
    lastUpdate: new Date().toISOString()
  }
});