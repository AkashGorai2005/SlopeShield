export const RISK_ORDER = ["low", "moderate", "high", "critical"];

export const RISK_META = {
  low: { label: "Low", hex: "#3f8f5b", chip: "bg-risk-low-soft text-risk-low border-risk-low/25" },
  moderate: {
    label: "Moderate",
    hex: "#d3a017",
    chip: "bg-risk-moderate-soft text-risk-moderate border-risk-moderate/30",
  },
  high: {
    label: "High",
    hex: "#dd7326",
    chip: "bg-risk-high-soft text-risk-high border-risk-high/30",
  },
  critical: {
    label: "Critical",
    hex: "#c4362f",
    chip: "bg-risk-critical-soft text-risk-critical border-risk-critical/30",
  },
};

export const riskLabel = (level) => RISK_META[level]?.label ?? "Unknown";
export const riskColor = (level) => RISK_META[level]?.hex ?? "#8a8f8a";
export const riskChipClass = (level) => RISK_META[level]?.chip ?? "bg-muted text-muted-foreground";

export const probabilityToRisk = (p) => {
  if (p >= 0.75) return "critical";
  if (p >= 0.55) return "high";
  if (p >= 0.3) return "moderate";
  return "low";
};

// Simple, transparent frontend-only scenario calculation (no ML involved).
export const simulateProbability = (location, scenarioRainfall) => {
  const base = location.probability;
  const ratio = scenarioRainfall / Math.max(location.rainfall, 1);
  const slopeFactor = 0.6 + location.slope / 90;
  const historyFactor = 1 + Math.min(location.historicalLandslides, 50) / 250;
  const value = base * Math.pow(ratio, 0.55 * slopeFactor) * historyFactor;
  return Math.max(0.02, Math.min(0.99, Number(value.toFixed(2))));
};

export const trendLabel = (trend) =>
  ({ increasing: "Increasing", decreasing: "Decreasing", stable: "Stable" })[trend] ?? "—";
