export default function LoadingState({ label = "Loading data…", rows = 3 }) {
  return (
    <div className="panel p-6" role="status" aria-live="polite">
      <p className="text-sm text-muted-foreground">{label}</p>
      <div className="mt-4 space-y-3">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="h-3 animate-pulse rounded bg-muted" style={{ width: `${90 - i * 18}%` }} />
        ))}
      </div>
    </div>
  );
}
