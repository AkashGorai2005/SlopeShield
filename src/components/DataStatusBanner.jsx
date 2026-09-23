import { Database, ShieldCheck, TriangleAlert } from "lucide-react";
import { useProjectData } from "@/context/ProjectDataContext";

export default function DataStatusBanner() {
  const { dataStatus, systemStatus, error } = useProjectData();

  if (!dataStatus && !error) return null;

  if (error) {
    return (
      <div className="mb-5 rounded-2xl border border-red-200 bg-red-50/90 px-4 py-3 text-xs text-red-900">
        <div className="font-semibold">Some backend data could not be loaded.</div>
        <div className="mt-1 break-words">{error}</div>
      </div>
    );
  }

  const real = ["database", "real-source"].includes(dataStatus.mode);
  const trained = Boolean(systemStatus?.modelTrained);

  return (
    <div
      className={`mb-5 flex flex-wrap items-center justify-between gap-3 rounded-2xl border px-4 py-3 text-xs ${
        real && trained ? "border-emerald-200 bg-emerald-50/80" : "border-amber-200 bg-amber-50/80"
      }`}
    >
      <div className="flex items-center gap-2">
        {real && trained ? (
          <ShieldCheck className="h-4 w-4 text-emerald-700" />
        ) : (
          <TriangleAlert className="h-4 w-4 text-amber-700" />
        )}

        <span className="font-medium text-deep">
          {real ? "Real backend dataset loaded" : "Reference catalogue mode"}
        </span>

        <span className="text-muted-foreground">
          {trained ? "· trained ML model active" : "· trained ML model unavailable"}
        </span>
      </div>

      <span className="flex items-center gap-1 text-muted-foreground">
        <Database className="h-3.5 w-3.5" />
          Historical inventory: {dataStatus.historicalDataAvailable ? "loaded" : "not loaded"}
      </span>
    </div>
  );
}
