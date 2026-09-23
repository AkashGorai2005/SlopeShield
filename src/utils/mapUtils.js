export const NORTHEAST_CENTER = [25.6, 92.5];
export const DEFAULT_ZOOM = 6;

export const TILE_LAYERS = {
  terrain: {
    url: "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attribution: "© OpenTopoMap contributors",
  },

  base: {
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution: "© OpenStreetMap contributors",
  },
};

export const NORTHEAST_BOUNDS = [
  [21.8, 87.9],
  [29.5, 97.4],
];

// Marker radius scales with model probability.
export const riskRadius = (probability) =>
  8 + Math.round(probability * 14);

export const formatLatLng = (lat, lng) =>
  `${Math.abs(lat).toFixed(3)}° ${lat >= 0 ? "N" : "S"}, ${
    Math.abs(lng).toFixed(3)
  }° ${lng >= 0 ? "E" : "W"}`;