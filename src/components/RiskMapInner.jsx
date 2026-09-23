import "leaflet/dist/leaflet.css";
import { CircleMarker, MapContainer, Marker, Popup, TileLayer, Tooltip, useMap } from "react-leaflet";
import L from "leaflet";
import { useEffect } from "react";

import { formatElevation, formatRainfall, formatPercent, formatSlope } from "@/utils/formatters";
import { DEFAULT_ZOOM, NORTHEAST_CENTER, TILE_LAYERS, riskRadius } from "@/utils/mapUtils";
import { riskColor, riskLabel } from "@/utils/riskUtils";

function FlyTo({ location }) {
  const map = useMap();
  useEffect(() => {
    if (location) map.flyTo([location.latitude, location.longitude], 10, { duration: 0.8 });
  }, [location, map]);
  return null;
}

const historyIcon = L.divIcon({
  className: "",
  html: '<span style="display:block;width:9px;height:9px;border-radius:2px;background:#5b6b57;border:1.5px solid #fff;transform:rotate(45deg)"></span>',
  iconSize: [9, 9],
});

export default function RiskMapInner({
  locations,
  historicalLandslides = [],
  activeLayers = ["risk", "historical"],
  onSelect,
  focus = null,
  zoom = DEFAULT_ZOOM,
  scrollWheelZoom = true,
}) {
  const showTerrain = activeLayers.includes("slope") || activeLayers.includes("elevation");
  const tiles = showTerrain ? TILE_LAYERS.terrain : TILE_LAYERS.base;

  return (
    <MapContainer
      center={NORTHEAST_CENTER}
      zoom={zoom}
      scrollWheelZoom={scrollWheelZoom}
      className="h-full w-full"
      attributionControl
    >
      <TileLayer key={tiles.url} url={tiles.url} attribution={tiles.attribution} />
      <FlyTo location={focus} />

      {activeLayers.includes("rainfall") &&
        locations.map((l) => (
          <CircleMarker
            key={`rain-${l.id}`}
            center={[l.latitude, l.longitude]}
            radius={10 + l.rainfall / 12}
            pathOptions={{ color: "#4c7fa8", weight: 1, fillColor: "#7fb0cf", fillOpacity: 0.16 }}
          />
        ))}

      {activeLayers.includes("risk") &&
        locations.map((l) => (
          <CircleMarker
            key={l.id}
            center={[l.latitude, l.longitude]}
            radius={riskRadius(l.probability)}
            pathOptions={{
              color: riskColor(l.riskLevel),
              weight: 2,
              fillColor: riskColor(l.riskLevel),
              fillOpacity: 0.28,
            }}
            eventHandlers={{ click: () => onSelect && onSelect(l) }}
          >
            <Tooltip direction="top" offset={[0, -6]}>
              <span className="text-xs font-medium">
                {l.name} · {riskLabel(l.riskLevel)}
              </span>
            </Tooltip>
            <Popup>
              <div className="min-w-[190px] text-xs">
                <p className="text-sm font-semibold">{l.name}</p>
                <p className="text-muted-foreground">{l.state}</p>
                <dl className="mt-2 space-y-0.5">
                  <div className="flex justify-between gap-4">
                    <dt>Risk</dt>
                    <dd style={{ color: riskColor(l.riskLevel) }}>{riskLabel(l.riskLevel)}</dd>
                  </div>
                  <div className="flex justify-between gap-4">
                    <dt>Probability</dt>
                    <dd>{formatPercent(l.probability)}</dd>
                  </div>
                  <div className="flex justify-between gap-4">
                    <dt>Rainfall 24h</dt>
                    <dd>{formatRainfall(l.rainfall)}</dd>
                  </div>
                  {activeLayers.includes("slope") && (
                    <div className="flex justify-between gap-4">
                      <dt>Slope</dt>
                      <dd>{formatSlope(l.slope)}</dd>
                    </div>
                  )}
                  {activeLayers.includes("elevation") && (
                    <div className="flex justify-between gap-4">
                      <dt>Elevation</dt>
                      <dd>{formatElevation(l.elevation)}</dd>
                    </div>
                  )}
                  {activeLayers.includes("landcover") && (
                    <div className="flex justify-between gap-4">
                      <dt>Land cover</dt>
                      <dd className="text-right">{l.landCover}</dd>
                    </div>
                  )}
                  {activeLayers.includes("geology") && (
                    <div className="flex justify-between gap-4">
                      <dt>Geology</dt>
                      <dd className="text-right">{l.geology}</dd>
                    </div>
                  )}
                </dl>
                <p className="mt-2 text-[10px] text-muted-foreground">
                  Backend data from the configured monitoring and scientific source layers.
                </p>
              </div>
            </Popup>
          </CircleMarker>
        ))}

      {activeLayers.includes("historical") &&
        historicalLandslides.map((h) => (
          <Marker key={h.id} position={[h.latitude, h.longitude]} icon={historyIcon}>
            <Tooltip direction="top">
              <span className="text-xs">
                {h.place} · {h.year} · {h.severity}
              </span>
            </Tooltip>
            <Popup>
              <div className="min-w-[190px] text-xs">
                <p className="text-sm font-semibold">Historical landslide</p>
                <p className="mt-1 text-muted-foreground">{h.place || h.state || "Recorded event"}</p>
                <dl className="mt-2 space-y-0.5">
                  <div className="flex justify-between gap-4"><dt>Event ID</dt><dd>{h.id}</dd></div>
                  <div className="flex justify-between gap-4"><dt>Date</dt><dd>{h.date || h.year || "Unavailable"}</dd></div>
                  <div className="flex justify-between gap-4"><dt>Severity</dt><dd>{h.severity || "Unavailable"}</dd></div>
                  <div className="flex justify-between gap-4"><dt>Source</dt><dd>{h.source || "PostgreSQL"}</dd></div>
                </dl>
              </div>
            </Popup>
          </Marker>
        ))}
    </MapContainer>
  );
}