import { FlaskConical, Info, LoaderCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { simulateRisk } from "@/services/api";
import { formatPercent, formatRainfall } from "@/utils/formatters";
import { riskChipClass, riskLabel } from "@/utils/riskUtils";

export default function WhatIfSimulation({ location }) {
  const [rainfall, setRainfall] = useState(location.rainfall);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => { setRainfall(location.rainfall); setResult(null); }, [location.id, location.rainfall]);
  useEffect(() => {
    let active = true;
    setLoading(true); setError("");
    const timer = setTimeout(() => simulateRisk(location.id, rainfall)
      .then((data) => active && setResult(data))
      .catch((e) => active && setError(e.message || "Simulation failed"))
      .finally(() => active && setLoading(false)), 180);
    return () => { active = false; clearTimeout(timer); };
  }, [location.id, rainfall]);

  const simulated = result?.probability ?? location.probability;
  const simulatedLevel = result?.riskLevel ?? location.riskLevel;
  return (
    <section className="panel p-5">
      <header className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2"><FlaskConical className="h-4 w-4 text-forest" /><h3 className="text-base text-deep">What-if simulation</h3></div>
        <span className={`rounded border px-2 py-0.5 text-[11px] font-medium ${riskChipClass(simulatedLevel)}`}>{riskLabel(simulatedLevel)}</span>
      </header>
      <div className="mt-5">
        <div className="flex items-center justify-between text-xs text-muted-foreground"><span>Scenario 24h rainfall</span><span className="font-medium text-foreground">{formatRainfall(rainfall)}</span></div>
        <input type="range" min={0} max={500} step={5} value={rainfall} onChange={(e) => setRainfall(Number(e.target.value))} className="mt-2 w-full accent-[var(--color-forest)]" />
        <div className="flex justify-between text-[11px] text-muted-foreground"><span>0 mm</span><span>500 mm</span></div>
      </div>
      <dl className="mt-5 grid gap-3 sm:grid-cols-2">
        <div className="rounded-md bg-surface px-3 py-2"><dt className="text-[11px] text-muted-foreground">Current rainfall</dt><dd className="mt-0.5 text-sm font-medium">{formatRainfall(location.rainfall)}</dd></div>
        <div className="rounded-md bg-sage-soft px-3 py-2"><dt className="text-[11px] text-deep/70">Scenario rainfall</dt><dd className="mt-0.5 text-sm font-medium text-deep">{formatRainfall(rainfall)}</dd></div>
        <div className="rounded-md bg-surface px-3 py-2"><dt className="text-[11px] text-muted-foreground">Current risk</dt><dd className="mt-0.5 text-sm font-medium">{riskLabel(location.riskLevel)}</dd></div>
        <div className="rounded-md bg-sage-soft px-3 py-2"><dt className="text-[11px] text-deep/70">Simulated risk</dt><dd className="mt-0.5 text-sm font-medium text-deep">{riskLabel(simulatedLevel)}</dd></div>
        <div className="rounded-md bg-surface px-3 py-2"><dt className="text-[11px] text-muted-foreground">Current probability</dt><dd className="mt-0.5 text-sm font-medium">{formatPercent(location.probability)}</dd></div>
        <div className="rounded-md bg-sage-soft px-3 py-2"><dt className="text-[11px] text-deep/70">Simulated probability</dt><dd className="mt-0.5 text-sm font-medium text-deep">{loading ? <LoaderCircle className="inline h-4 w-4 animate-spin" /> : formatPercent(simulated)}</dd></div>
      </dl>
      {result?.factors?.length ? <p className="mt-4 text-xs text-muted-foreground">Main factors: {result.factors.join(" · ")}</p> : null}
      <button onClick={() => setRainfall(location.rainfall)} className="mt-4 rounded-md border border-border px-3 py-1.5 text-xs font-medium hover:bg-secondary">Reset to current rainfall</button>
      <p className="mt-4 flex gap-2 rounded-md border border-border bg-surface px-3 py-2 text-[11px] text-muted-foreground"><Info className="mt-0.5 h-3.5 w-3.5 shrink-0" />Model-based scenario simulation using the trained Random Forest model. Results are estimates and are not guaranteed future predictions.</p>
      {error && <p className="mt-2 text-xs text-risk-high">{error}</p>}
    </section>
  );
}
