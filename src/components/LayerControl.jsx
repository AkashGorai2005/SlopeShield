import { Layers } from "lucide-react";

export default function LayerControl({ layers, active, onToggle, className = "" }) {
  return (
    <div className={`panel p-3 ${className}`}>
      <p className="mb-2 flex items-center gap-1.5 eyebrow">
        <Layers className="h-3.5 w-3.5" /> Data layers
      </p>
      <ul className="space-y-1">
        {layers.map((layer) => {
          const checked = active.includes(layer.id);
          return (
            <li key={layer.id}>
              <label className="flex cursor-pointer items-start gap-2.5 rounded-md px-2 py-1.5 hover:bg-secondary">
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() => onToggle(layer.id)}
                  className="mt-0.5 h-3.5 w-3.5 accent-[var(--color-forest)]"
                />
                <span className="min-w-0">
                  <span className="block text-xs font-medium text-foreground">{layer.name}</span>
                  <span className="block text-[11px] text-muted-foreground">{layer.description}</span>
                </span>
              </label>
            </li>
          );
        })}
      </ul>
      <p className="mt-2 border-t border-border pt-2 text-[11px] text-muted-foreground">
        Layers are labelled with their configured source; unavailable layers are never replaced with invented readings.
      </p>
    </div>
  );
}
