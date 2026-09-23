import { riskColor, riskLabel } from "@/utils/riskUtils";

export default function RiskCard({ level, count, total, note }) {
  const pct = total ? Math.round((count / total) * 100) : 0;

  return (
    <div className="panel p-4">
      <div className="flex items-center gap-2">
        <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: riskColor(level) }} />
        <span className="text-sm font-medium text-foreground">{riskLabel(level)} risk</span>
      </div>
      <p className="mt-3 font-display text-4xl leading-none text-deep">{count}</p>
      <p className="mt-1 text-xs text-muted-foreground">{note ?? "monitored areas"}</p>
      <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full"
          style={{ width: `${pct}%`, backgroundColor: riskColor(level) }}
        />
      </div>
      <p className="mt-1.5 text-[11px] text-muted-foreground">{pct}% of monitored areas</p>
    </div>
  );
}
