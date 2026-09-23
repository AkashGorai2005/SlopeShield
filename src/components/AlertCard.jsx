import { Link } from "@/lib/navigation";
import { ArrowUpRight, CloudRain, Clock, Check, TrendingUp } from "lucide-react";
import { useState } from "react";

import { formatDelta, formatPercent, formatRainfall, formatRelative } from "@/utils/formatters";
import { riskChipClass, riskColor, riskLabel } from "@/utils/riskUtils";
import { resolveAlert } from "@/services/api";

export default function AlertCard({ warning, onResolved }) {
  const [resolving, setResolving] = useState(false);
  const [resolveError, setResolveError] = useState("");

  async function handleResolve() {
    setResolving(true);
    setResolveError("");
    try {
      await resolveAlert(warning.id);
      onResolved?.();
    } catch (error) {
      setResolveError(error.message || "Could not resolve alert");
    } finally {
      setResolving(false);
    }
  }

  return (
    <article className="panel p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-foreground">{warning.location}</p>
          <p className="eyebrow mt-0.5">Priority monitoring area</p>
        </div>
        <span
          className={`shrink-0 rounded border px-2 py-0.5 text-[11px] font-medium ${riskChipClass(warning.riskLevel)}`}
        >
          {riskLabel(warning.riskLevel)}
        </span>
      </div>

      <div className="mt-3 grid grid-cols-3 gap-2 border-y border-border py-3 text-xs">
        <div>
          <p className="flex items-center gap-1 text-muted-foreground">
            <CloudRain className="h-3 w-3" /> Rainfall
          </p>
          <p className="mt-0.5 text-sm font-medium">{formatRainfall(warning.rainfall)}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Probability</p>
          <p className="mt-0.5 text-sm font-medium" style={{ color: riskColor(warning.riskLevel) }}>
            {formatPercent(warning.probability)}
          </p>
        </div>
        <div>
          <p className="flex items-center gap-1 text-muted-foreground">
            <TrendingUp className="h-3 w-3" /> Change
          </p>
          <p className="mt-0.5 text-sm font-medium">{formatDelta(warning.change)}</p>
        </div>
      </div>

      <div className="mt-3 flex items-center justify-between">
        <span className="flex items-center gap-1 text-[11px] text-muted-foreground">
          <Clock className="h-3 w-3" /> Estimated {formatRelative(warning.timestamp)}
        </span>
        <Link
          to="/location/$id"
          params={{ id: warning.locationId }}
          className="inline-flex items-center gap-1 text-xs font-medium text-forest hover:underline"
        >
          Details <ArrowUpRight className="h-3 w-3" />
        </Link>
      </div>
      <div className="mt-3 rounded-md border border-border bg-surface px-3 py-2 text-xs text-muted-foreground">
        <span className="font-medium text-deep">Recommended action:</span> {warning.recommendedAction || "Continue monitoring."}
      </div>
      {warning.status === "active" && (
        <button
          type="button"
          onClick={handleResolve}
          disabled={resolving}
          className="mt-3 inline-flex items-center gap-1 rounded-md border border-border px-3 py-1.5 text-xs font-medium text-deep hover:bg-secondary disabled:opacity-60"
        >
          <Check className="h-3.5 w-3.5" /> {resolving ? "Resolving..." : "Mark resolved"}
        </button>
      )}
      {resolveError && <p className="mt-2 text-xs text-risk-high">{resolveError}</p>}
    </article>
  );
}
