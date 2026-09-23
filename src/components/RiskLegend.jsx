import { RISK_ORDER, riskColor, riskLabel } from "@/utils/riskUtils";

export default function RiskLegend({ compact = false, className = "" }) {
  return (
    <div className={`panel p-3 ${className}`}>
      {!compact && <p className="eyebrow mb-2">Risk classification</p>}
      <ul className={compact ? "flex flex-wrap gap-3" : "space-y-1.5"}>
        {RISK_ORDER.map((level) => (
          <li key={level} className="flex items-center gap-2 text-xs text-muted-foreground">
            <span className="h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: riskColor(level) }} />
            <span className="text-foreground">{riskLabel(level)}</span>
          </li>
        ))}
      </ul>
      {!compact && <p className="mt-3 border-t border-border pt-2 text-[11px] text-muted-foreground">Classes are produced by the configured SLOPESHIELD model/risk engine. Source and model state are shown above each operational view.</p>}
    </div>
  );
}
