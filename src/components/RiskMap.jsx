import RiskMapInner from "./RiskMapInner";

export default function RiskMap({
  locations = [],
  activeLayers = ["risk"],
  onSelect,
  focus,
  height = 520,
  showLegend = true,
}) {
  return (
    <div
      className="overflow-hidden rounded-2xl border border-border bg-white"
      style={{ height }}
    >
      <RiskMapInner
        locations={locations}
        activeLayers={activeLayers}
        onSelect={onSelect}
        focus={focus}
        showLegend={showLegend}
      />
    </div>
  );
}