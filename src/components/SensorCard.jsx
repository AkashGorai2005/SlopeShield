import { CircuitBoard } from "lucide-react";

export default function SensorCard() {
  return (
    <div className="rounded-lg border border-dashed border-border bg-surface p-4">
      <div className="flex items-center gap-2 text-muted-foreground"><CircuitBoard className="h-4 w-4" /><span className="text-sm font-medium text-foreground">Field sensors</span></div>
      <p className="mt-2 text-xs text-muted-foreground">Not used in SLOPESHIELD NER. This SIH implementation is software-only and uses weather, terrain, geospatial and historical datasets rather than ESP32/IoT hardware.</p>
    </div>
  );
}
