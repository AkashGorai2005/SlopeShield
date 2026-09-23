import { CloudRain, Droplets, Thermometer, Wind } from "lucide-react";

import { formatRainfall } from "@/utils/formatters";

export default function WeatherCard({ weather, status }) {
  const rows = [
    { icon: Thermometer, label: "Temperature", value: weather.temperature == null ? "—" : `${weather.temperature}°C` },
    { icon: Droplets, label: "Humidity", value: weather.humidity == null ? "—" : `${weather.humidity}%` },
    { icon: Wind, label: "Wind", value: weather.wind == null ? "—" : `${weather.wind} km/h` },
  ];

  return (
    <div className="panel p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="eyebrow">Rainfall status</p>
          <p className="mt-1 text-sm font-medium text-foreground">{weather.condition}</p>
          <p className="text-xs text-muted-foreground">{weather.place}</p>
        </div>
        <CloudRain className="h-6 w-6 text-sage" />
      </div>

      <p className="mt-4 font-display text-4xl leading-none text-deep">
        {formatRainfall(weather.rainfall24h)}
        <span className="ml-2 text-sm text-muted-foreground">last 24h</span>
      </p>

      <dl className="mt-4 grid grid-cols-3 gap-2 border-t border-border pt-3">
        {rows.map(({ icon: Icon, label, value }) => (
          <div key={label}>
            <dt className="flex items-center gap-1 text-[11px] text-muted-foreground">
              <Icon className="h-3 w-3" /> {label}
            </dt>
            <dd className="mt-0.5 text-sm font-medium">{value}</dd>
          </div>
        ))}
      </dl>

      {status && (
        <p className="mt-3 rounded-md bg-surface px-3 py-2 text-[11px] text-muted-foreground">
          7-day accumulation {formatRainfall(status.last7d)} · {status.intensity}. {status.note}
        </p>
      )}
    </div>
  );
}
