export const formatRainfall = (mm) => mm == null ? "No data" : `${Math.round(mm)} mm`;

export const formatPercent = (value, digits = 0) =>
  `${(value <= 1 ? value * 100 : value).toFixed(digits)}%`;

export const formatSlope = (deg) => `${deg}°`;

export const formatElevation = (m) => `${m.toLocaleString("en-IN")} m`;

export const formatDateTime = (iso) =>
  new Date(iso).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });

export const formatRelative = (iso) => {
  const diff = Date.now() - new Date(iso).getTime();
  const h = Math.round(diff / 3_600_000);
  if (h < 1) return "just now";
  if (h < 24) return `${h}h ago`;
  return `${Math.round(h / 24)}d ago`;
};

export const formatDelta = (value) =>
  value === 0 ? "no change" : `${value > 0 ? "+" : ""}${Math.round(value * 100)} pts`;
