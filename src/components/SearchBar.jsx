import { useNavigate } from "@/lib/navigation";
import { MapPin, Search } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { useLocations } from "@/hooks/useLocations";
import { riskChipClass, riskLabel } from "@/utils/riskUtils";

export default function SearchBar({ placeholder = "Search a location", onSelect }) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const { locations } = useLocations(query);
  const wrapRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const onClick = (e) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  const choose = (loc) => {
    setQuery("");
    setOpen(false);
    if (onSelect) onSelect(loc);
    else navigate({ to: "/location/$id", params: { id: loc.id } });
  };

  return (
    <div ref={wrapRef} className="relative w-full">
      <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
      <input
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        placeholder={placeholder}
        aria-label="Search locations"
        className="h-10 w-full rounded-md border border-border bg-surface pl-9 pr-3 text-sm text-foreground placeholder:text-muted-foreground focus:border-ring focus:bg-card focus:outline-none focus:ring-2 focus:ring-ring/20"
      />
      {open && query.trim() && (
        <ul className="panel absolute z-[1200] mt-2 max-h-80 w-full overflow-auto p-1">
          {locations.length === 0 && (
            <li className="px-3 py-3 text-sm text-muted-foreground">No matching location.</li>
          )}
          {locations.slice(0, 7).map((loc) => (
            <li key={loc.id}>
              <button
                onClick={() => choose(loc)}
                className="flex w-full items-center justify-between gap-3 rounded-md px-3 py-2 text-left hover:bg-secondary"
              >
                <span className="flex items-center gap-2 text-sm">
                  <MapPin className="h-3.5 w-3.5 text-sage" />
                  <span className="font-medium">{loc.name}</span>
                  <span className="text-muted-foreground">{loc.state}</span>
                </span>
                <span className={`rounded border px-1.5 py-0.5 text-[10px] font-medium ${riskChipClass(loc.riskLevel)}`}>
                  {riskLabel(loc.riskLevel)}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
