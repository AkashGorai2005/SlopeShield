export default function StatCard({ label, value, unit, hint, icon: Icon, tone = "default" }) {
  const tones = {
    default: "text-deep",
    sage: "text-forest",
    warn: "text-risk-high",
    danger: "text-risk-critical",
  };

  return (
    <div className="panel p-4">
      <div className="flex items-start justify-between gap-3">
        <span className="eyebrow">{label}</span>
        {Icon && <Icon className="h-4 w-4 text-sage" />}
      </div>
      <p className={`mt-2 font-display text-3xl leading-none ${tones[tone] ?? tones.default}`}>
        {value}
        {unit && <span className="ml-1 text-base text-muted-foreground">{unit}</span>}
      </p>
      {hint && <p className="mt-2 text-xs text-muted-foreground">{hint}</p>}
    </div>
  );
}
