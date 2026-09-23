import { MapPin, Mountain, CloudRain, TrendingUp } from "lucide-react";

export default function LocationPanel({ location }) {
  if (!location) {
    return (
      <div className="rounded-2xl border border-border bg-white p-5">
        <p className="text-sm text-muted-foreground">
          Select a monitoring location to view its details.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-border bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4 text-primary" />
            <h3 className="font-semibold text-deep">{location.name}</h3>
          </div>

          <p className="mt-1 text-xs text-muted-foreground">
            {location.state}
          </p>
        </div>

        <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium capitalize text-deep">
          {location.riskLevel}
        </span>
      </div>

      <div className="mt-5 grid grid-cols-2 gap-3">
        <div className="rounded-xl bg-slate-50 p-3">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <CloudRain className="h-3.5 w-3.5" />
            Rainfall
          </div>
          <p className="mt-1 font-semibold text-deep">
            {location.rainfall} mm
          </p>
        </div>

        <div className="rounded-xl bg-slate-50 p-3">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Mountain className="h-3.5 w-3.5" />
            Elevation
          </div>
          <p className="mt-1 font-semibold text-deep">
            {location.elevation} m
          </p>
        </div>

        <div className="rounded-xl bg-slate-50 p-3">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <TrendingUp className="h-3.5 w-3.5" />
            Slope
          </div>
          <p className="mt-1 font-semibold text-deep">
            {location.slope}°
          </p>
        </div>

        <div className="rounded-xl bg-slate-50 p-3">
          <p className="text-xs text-muted-foreground">Model probability</p>
          <p className="mt-1 font-semibold text-deep">
            {typeof location.probability === "number"
              ? `${(location.probability * 100).toFixed(1)}%`
              : "—"}
          </p>
        </div>
      </div>

      <p className="mt-2 text-[11px] text-muted-foreground">
        Backend-connected monitoring data from the configured source layers and model pipeline.
      </p>
    </div>
  );
}