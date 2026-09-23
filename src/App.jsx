import { useEffect, useState } from "react";
import { BrowserRouter, Route, Routes, useParams } from "react-router-dom";

import Home from "@/pages/Home";
import Login from "@/pages/Login";
import AppLayout from "@/components/AppLayout";
import RiskCard from "@/components/RiskCard";
import RiskChart from "@/components/RiskChart";
import RiskMap from "@/components/RiskMap";
import AlertCard from "@/components/AlertCard";
import WeatherCard from "@/components/WeatherCard";
import LayerControl from "@/components/LayerControl";
import LocationPanel from "@/components/LocationPanel";
import WhatIfSimulation from "@/components/WhatIfSimulation";
import DataStatusBanner from "@/components/DataStatusBanner";
import EmptyState from "@/components/EmptyState";
import { downloadReportCsv, getWarnings, problemsPdfUrl, reportHtmlUrl, reportPdfUrl, runMonitoringCycle } from "@/services/api";
import { SidebarProvider } from "@/hooks/useSidebar";
import { Link } from "@/lib/navigation";
import { AuthProvider, useAuth } from "@/lib/auth";
import { useProjectData, ProjectDataProvider } from "@/context/ProjectDataContext";
import { RISK_ORDER, riskLabel } from "@/utils/riskUtils";
import { formatDateTime, formatPercent, formatRainfall } from "@/utils/formatters";

function GuestPrompt({ feature = "this feature" }) {
  return (
    <AppLayout
      title="Detailed monitoring"
      description="Public overview only. Sign in to unlock the full operational view."
    >
      <div className="glass-panel mx-auto max-w-2xl rounded-2xl p-8 text-center">
        <p className="eyebrow">Access restricted</p>
        <h2 className="mt-2 text-3xl text-deep">Sign in to unlock {feature}.</h2>
        <p className="mt-3 text-sm text-muted-foreground">
          The public experience remains available, and the full dashboard intelligence is reserved for
          authenticated users in the demo workflow.
        </p>
        <div className="mt-6 flex justify-center gap-3">
          <Link
            to="/login"
            className="rounded-md bg-forest px-5 py-2.5 text-sm font-medium text-white shadow-sm"
          >
            Sign In
          </Link>
          <Link
            to="/risk-map"
            className="rounded-md border border-border bg-white/50 px-5 py-2.5 text-sm font-medium text-deep"
          >
            View Public Map
          </Link>
        </div>
      </div>
    </AppLayout>
  );
}

function RequireAuth({ children, feature }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <GuestPrompt feature={feature} />;
}

function Dashboard() {
  const {
    locations,
    risk,
    rainfall,
    warnings,
    refresh,
    historical,
    summary,
  } = useProjectData();
  const [cycleState, setCycleState] = useState("idle");

  const total = locations.length;
  const riskDistribution = risk?.distribution || [];
  const riskTrend = risk?.trend || [];
  const rainfallVsRisk = rainfall?.series || [];

  const [selectedLocationId, setSelectedLocationId] = useState(
    locations[0]?.id || "",
  );

  useEffect(() => {
    if (!selectedLocationId && locations.length > 0) {
      setSelectedLocationId(locations[0].id);
    }
  }, [locations, selectedLocationId]);

  const selectedLocation =
    locations.find(
      (location) => location.id === selectedLocationId,
    ) || locations[0] || null;

  return (
    <AppLayout
      title="Dashboard"
      description="Model-estimated landslide risk overview for monitored areas."
    >
      <DataStatusBanner />

      <div className="mb-4 flex flex-wrap items-center justify-between gap-3 rounded-md border border-border bg-white/70 px-4 py-3">
        <div>
          <p className="text-sm font-medium text-deep">Automatic monitoring</p>
          <p className="text-xs text-muted-foreground">Fetch rainfall, recalculate ML risk, persist predictions and alerts.</p>
        </div>
        <button
          type="button"
          disabled={cycleState === "running"}
          onClick={async () => {
            setCycleState("running");
            try {
              await runMonitoringCycle();
              await refresh?.();
              setCycleState("complete");
            } catch {
              setCycleState("failed");
            }
          }}
          className="rounded-md bg-forest px-4 py-2 text-xs font-medium text-white disabled:opacity-60"
        >
          {cycleState === "running" ? "Running cycle..." : cycleState === "complete" ? "Cycle complete" : cycleState === "failed" ? "Cycle failed" : "Run monitoring cycle"}
        </button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {riskDistribution.map((item) => (
          <RiskCard
            key={item.level}
            level={item.level}
            count={item.count}
            total={total}
          />
        ))}
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-[1.35fr_0.65fr]">
        <RiskMap
          locations={locations}
          historicalLandslides={historical}
          activeLayers={["risk", "historical"]}
          height={460}
          showLegend
        />

        <WeatherCard
          weather={{
            place: "Northeast India",
            condition:
              rainfall?.status?.headline ||
              "Operational weather adapter",
            temperature: null,
            humidity: null,
            wind: null,
            rainfall24h:
              rainfall?.status?.last24h ?? null,
          }}
          status={rainfall?.status}
        />
      </div>
      <p className="mt-2 text-xs text-muted-foreground">
        Historical landslide inventory: {summary?.historicalEvents ?? historical.length} PostgreSQL records shown separately from current model risk.
      </p>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <RiskChart
          type="rainfall-vs-risk"
          data={rainfallVsRisk}
          title="Rainfall vs risk"
          subtitle="Observed rainfall data"
        />

        <RiskChart
          type="risk-trend"
          data={riskTrend}
          title="Risk trend"
          subtitle="Model risk trend"
        />
      </div>

      <section className="mt-6">
        <div className="mb-3">
          <p className="eyebrow">What-if analysis</p>
          <h2 className="mt-1 text-xl text-deep">
            Simulate rainfall impact
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Test how a different 24-hour rainfall value changes the
            trained model's predicted risk.
          </p>
        </div>

        {locations.length > 0 && (
          <div className="panel mb-4 p-4">
            <label
              htmlFor="dashboard-location"
              className="block text-sm font-medium text-deep"
            >
              Monitoring location
            </label>

            <select
              id="dashboard-location"
              value={selectedLocation?.id || ""}
              onChange={(event) =>
                setSelectedLocationId(event.target.value)
              }
              className="mt-2 w-full rounded-md border border-border bg-white px-3 py-2 text-sm text-deep outline-none focus:border-forest"
            >
              {locations.map((location) => (
                <option
                  key={location.id}
                  value={location.id}
                >
                  {location.name} — {location.state}
                </option>
              ))}
            </select>
          </div>
        )}

        {selectedLocation ? (
          <WhatIfSimulation
            location={selectedLocation}
          />
        ) : (
          <div className="panel p-6 text-sm text-muted-foreground">
            No monitored locations are available.
          </div>
        )}
      </section>

      <section className="mt-6">
        <div className="mb-3 flex items-end justify-between">
          <div>
            <p className="eyebrow">
              Early-warning information
            </p>

            <h2 className="mt-1 text-xl text-deep">
              Priority monitoring areas
            </h2>
          </div>

          <Link
            to="/alerts"
            className="text-sm font-medium text-forest hover:underline"
          >
            View all
          </Link>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {warnings.slice(0, 4).map((warning) => (
            <AlertCard
              key={warning.id}
              warning={warning}
            />
          ))}
        </div>
      </section>
    </AppLayout>
  );
}

function RiskMapPage() {
  const { locations, historical, mapLayers } = useProjectData();
  const [layers, setLayers] = useState([]);

  useEffect(() => {
    setLayers(
      mapLayers
        .filter((layer) => layer.default)
        .map((layer) => layer.id),
    );
  }, [mapLayers]);

  const [selected, setSelected] = useState(null);

  return (
    <AppLayout
      title="Risk Map"
      description="Explore model-estimated risk and contextual geographic layers."
    >
      <DataStatusBanner />

      <div className="grid gap-4 lg:grid-cols-[1fr_280px]">
        <div>
          <RiskMap
            locations={locations}
            historicalLandslides={historical}
            activeLayers={layers}
            onSelect={setSelected}
            height={620}
            showLegend
          />
        </div>

        <div className="space-y-4">
          <LayerControl
            layers={mapLayers}
            active={layers}
            onToggle={(id) =>
              setLayers((current) =>
                current.includes(id)
                  ? current.filter((value) => value !== id)
                  : [...current, id],
              )
            }
          />

          {selected && (
            <LocationPanel
              location={selected}
              onClose={() => setSelected(null)}
            />
          )}
        </div>
      </div>
    </AppLayout>
  );
}

function Alerts() {
  const { locations, warnings, refresh } = useProjectData();
  const [view, setView] = useState("active");
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  useEffect(() => {
    if (view !== "history") return;
    setHistoryLoading(true);
    getWarnings("all").then(setHistory).finally(() => setHistoryLoading(false));
  }, [view]);
  const visibleWarnings = view === "active" ? warnings : history;

  return (
    <AppLayout
      title="Early Warning Intelligence"
      description="Areas requiring closer monitoring based on environmental conditions and historical context."
    >
      <div className="mb-4 flex gap-2">
        {[
          ["active", "Active alerts"],
          ["history", "Alert history"],
        ].map(([value, label]) => (
          <button
            key={value}
            type="button"
            onClick={() => setView(value)}
            className={`rounded-md border px-3 py-1.5 text-xs font-medium ${view === value ? "border-forest bg-forest text-white" : "border-border text-deep hover:bg-secondary"}`}
          >
            {label}
          </button>
        ))}
      </div>
      {historyLoading ? (
        <div className="panel p-6 text-sm text-muted-foreground">Loading alert history...</div>
      ) : visibleWarnings.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2">
          {visibleWarnings.map((warning) => (
            <AlertCard
              key={warning.id}
              warning={warning}
              onResolved={() => {
                setHistory((current) => current.filter((item) => item.id !== warning.id));
                refresh?.();
              }}
            />
          ))}
        </div>
      ) : (
        <>
          <EmptyState
            title={view === "active" ? "No active warnings" : "No alert history"}
            description={view === "active" ? "No monitored location is currently classified as High or Critical risk." : "Persisted alerts will appear here after the monitoring engine creates them."}
          />

          {view === "active" && locations.length > 0 && (
            <section className="mt-6">
              <div className="mb-3">
                <p className="eyebrow">DATABASE MONITORING DATA</p>
                <h2 className="mt-1 text-xl text-deep">Current monitored locations</h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  Live location values are shown below even when no alert threshold has been reached.
                </p>
              </div>
              <div className="overflow-hidden rounded-2xl border border-border bg-white/75">
                <div className="hidden grid-cols-[1.5fr_1fr_0.8fr_0.8fr] gap-4 border-b border-border bg-surface px-4 py-3 text-[11px] font-semibold uppercase tracking-[0.08em] text-muted-foreground sm:grid">
                  <span>Location</span>
                  <span>Risk level</span>
                  <span>Probability</span>
                  <span>Rainfall</span>
                </div>
                <div className="divide-y divide-border">
                  {locations.map((location) => (
                    <div key={location.id} className="grid gap-2 px-4 py-3 text-sm sm:grid-cols-[1.5fr_1fr_0.8fr_0.8fr] sm:items-center sm:gap-4">
                      <div>
                        <p className="font-medium text-deep">{location.name}</p>
                        <p className="text-xs text-muted-foreground">{location.state}</p>
                      </div>
                      <span className="w-fit rounded border border-border px-2 py-0.5 text-xs font-medium text-deep">
                        {riskLabel(location.riskLevel)}
                      </span>
                      <span className="text-muted-foreground">{formatPercent(location.probability)}</span>
                      <span className="text-muted-foreground">{formatRainfall(location.rainfall)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          )}
        </>
      )}
    </AppLayout>
  );
}

function AboutPage() {
  return (
    <AppLayout
      title="Understanding the landscape before it becomes a threat."
      description="SlopeShield brings together environmental and historical intelligence to highlight areas requiring closer monitoring."
    >
      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="glass-panel rounded-[28px] p-6 sm:p-8">
          <p className="eyebrow">WHAT IS SlopeShield?</p>

          <p className="mt-4 text-base leading-8 text-foreground/80">
            SlopeShield is an AI-based landslide risk monitoring and decision-support system that
            combines environmental conditions, terrain characteristics, and historical landslide
            information to identify areas needing priority monitoring across Northeast India.
          </p>

          <div className="mt-8 grid gap-3 sm:grid-cols-2">
            {[
              "Rainfall",
              "Terrain",
              "Elevation",
              "Land Cover",
              "Geology",
              "Historical Landslides",
            ].map((item) => (
              <div
                key={item}
                className="rounded-2xl border border-white/70 bg-white/45 px-3 py-2.5 text-sm text-deep"
              >
                {item}
              </div>
            ))}
          </div>
        </div>

        <div className="glass-panel rounded-[28px] p-6 sm:p-8">
          <p className="eyebrow">HOW IT WORKS</p>

          <div className="mt-5 space-y-4 text-sm text-foreground/80">
            <div className="flex items-center gap-3">
              <span className="grid h-8 w-8 place-items-center rounded-full bg-sage-soft text-xs font-semibold text-deep">
                01
              </span>
              <span>Data</span>
            </div>

            <div className="flex items-center gap-3">
              <span className="grid h-8 w-8 place-items-center rounded-full bg-sage-soft text-xs font-semibold text-deep">
                02
              </span>
              <span>Analysis</span>
            </div>

            <div className="flex items-center gap-3">
              <span className="grid h-8 w-8 place-items-center rounded-full bg-sage-soft text-xs font-semibold text-deep">
                03
              </span>
              <span>Risk Intelligence</span>
            </div>

            <div className="flex items-center gap-3">
              <span className="grid h-8 w-8 place-items-center rounded-full bg-sage-soft text-xs font-semibold text-deep">
                04
              </span>
              <span>Priority Monitoring</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 glass-panel rounded-[28px] p-6 sm:p-8">
  <p className="eyebrow">OUR TEAM</p>

  <h3 className="mt-3 text-2xl text-deep">
    HIDDEN VARIABLES
  </h3>

  <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
    {[
      ["Adrija Choudhury", "Frontend"],
      ["Akash Gorai", "Backend"],
      ["Pritam Nandi", "Backend"],
      ["Anindita Maji", "Database"],
      ["Pratima Shaw", "Machine Learning"],
      ["Abhishikta Mishra", "Machine Learning"],
    ].map(([name, role]) => (
      <div
        key={name}
        className="rounded-2xl border border-white/70 bg-white/45 p-4"
      >
        <p className="font-medium text-deep">{name}</p>
        <p className="mt-1 text-xs text-muted-foreground">{role}</p>
      </div>
    ))}
  </div>
</div>
     
    </AppLayout>
  );
}

function Analytics() {
  const { risk, rainfall } = useProjectData();

  const riskDistribution = risk?.distribution || [];
  const rainfallVsRisk = rainfall?.series || [];

  return (
    <AppLayout
      title="Analytics"
      description="Risk, rainfall and contributing-factor views from configured environmental data."
    >
      <DataStatusBanner />

      <div className="grid gap-6 lg:grid-cols-2">
        <RiskChart
          type="distribution"
          data={riskDistribution}
          title="Risk distribution"
        />

        <RiskChart
          type="rainfall-vs-risk"
          data={rainfallVsRisk}
          title="Rainfall vs risk"
        />

        <RiskChart
          type="risk-trend"
          data={risk?.trend || []}
          title="Risk trend"
        />

        <RiskChart
          type="regional"
          data={risk?.regional || []}
          title="Regional comparison"
        />

        <RiskChart
          type="factors"
          data={risk?.factors || []}
          title="Risk factor contribution"
          className="lg:col-span-2"
        />
      </div>
    </AppLayout>
  );
}

function Reports() {
  const { risk } = useProjectData();
  const riskDistribution = risk?.distribution || [];

  return (
    <AppLayout
      title="Reports"
      description="Generate a frontend-only risk assessment preview."
    >
      <div className="panel p-6">
        <p className="eyebrow">Risk assessment report</p>

        <h2 className="mt-2 text-2xl text-deep">
          Northeast India landslide risk report
        </h2>

        <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
          This report is generated by the backend from the currently configured dataset and model state.
          It never claims live data unless the source-status banner says the real-source pipeline is loaded.
        </p>

        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {RISK_ORDER.map((level) => (
            <div
              key={level}
              className="rounded-md border border-border p-4"
            >
              <p className="text-xs text-muted-foreground">
                {riskLabel(level)} areas
              </p>

              <p className="mt-1 font-display text-3xl text-deep">
                {riskDistribution.find(
                  (item) => item.level === level,
                )?.count ?? 0}
              </p>
            </div>
          ))}
        </div>

        <div className="mt-6 flex flex-wrap gap-3">
          <button
            onClick={() => window.print()}
            className="rounded-md bg-forest px-4 py-2 text-sm font-medium text-white"
          >
            Print / Save report
          </button>

          <a
            href={downloadReportCsv()}
            className="rounded-md border border-border bg-white px-4 py-2 text-sm font-medium text-deep"
          >
            Download CSV
          </a>

          <a
            href={reportHtmlUrl()}
            target="_blank"
            rel="noreferrer"
            className="rounded-md border border-border bg-white px-4 py-2 text-sm font-medium text-deep"
          >
            Open HTML report
          </a>

          <a
            href={reportPdfUrl()}
            className="rounded-md border border-border bg-white px-4 py-2 text-sm font-medium text-deep"
          >
            Download PDF
          </a>

          <a
            href={problemsPdfUrl()}
            className="rounded-md border border-border bg-white px-4 py-2 text-sm font-medium text-deep"
          >
            Download Audit PDF
          </a>
        </div>
      </div>
    </AppLayout>
  );
}

function Settings() {
  return (
    <AppLayout
      title="Settings"
      description="Local interface preferences for the SlopeShield application."
    >
      <div className="panel max-w-2xl space-y-5 p-6">
        <div>
          <p className="text-sm font-medium">Appearance</p>
          <p className="mt-1 text-xs text-muted-foreground">
            SlopeShield uses a light environmental theme and source-aware data labels.
          </p>
        </div>

        <div className="border-t border-border pt-5">
          <p className="text-sm font-medium">Data mode</p>
          <p className="mt-1 text-xs text-muted-foreground">
            The dashboard reads from FastAPI. The source-status banner identifies whether real-source data and a trained model are active.
          </p>
        </div>

        <div className="border-t border-border pt-5">
          <p className="text-sm font-medium">Notifications</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Early-warning information is generated from the backend risk state. Browser notification delivery can be enabled by the browser when supported.
          </p>
        </div>
      </div>
    </AppLayout>
  );
}

function LocationDetails() {
  const { id } = useParams();
  const { locations, historical, rainfall } = useProjectData();

  const location = locations.find((item) => item.id === id);

  if (!location) {
    return (
      <AppLayout title="Location not found">
        <p className="text-sm text-muted-foreground">
          No matching monitored location.
        </p>
      </AppLayout>
    );
  }

  return (
    <AppLayout
      title={location.name}
      description={location.state}
    >
      <div className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
        <RiskMap
          locations={locations}
          historicalLandslides={historical}
          focus={location}
          height={480}
          showLegend
        />

        <div className="space-y-6">
          <LocationPanel location={location} />

          <WhatIfSimulation location={location} />

          <RiskChart
            type="location-rainfall"
            data={rainfall?.series || []}
            title="Recent rainfall"
          />
        </div>
      </div>
    </AppLayout>
  );
}

function RecentChanges() {
  const { risk } = useProjectData();
  const recentChanges = risk?.recentChanges || [];

  return (
    <AppLayout
      title="Recent Changes"
      description="Recent model-estimated classification changes returned by the backend."
    >
      <div className="panel divide-y divide-border">
        {recentChanges.map((change) => (
          <div
            key={change.id}
            className="flex flex-wrap items-center justify-between gap-3 p-4"
          >
            <div>
              <p className="text-sm font-medium">{change.location}</p>
              <p className="text-xs text-muted-foreground">
                {formatDateTime(change.at)}
              </p>
            </div>

            <p className="text-sm">
              <span className="font-medium">
                {riskLabel(change.from)}
              </span>{" "}
              →
              <span className="font-medium">
                {" "}
                {riskLabel(change.to)}
              </span>
            </p>
          </div>
        ))}
      </div>
    </AppLayout>
  );
}

function AppContent() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Home />} />
      <Route path="/about" element={<AboutPage />} />

      <Route
        path="/dashboard"
        element={
          <RequireAuth feature="the full dashboard">
            <Dashboard />
          </RequireAuth>
        }
      />

      <Route path="/risk-map" element={<RiskMapPage />} />

      <Route
        path="/alerts"
        element={
          <RequireAuth feature="early-warning information">
            <Alerts />
          </RequireAuth>
        }
      />

      <Route path="/early-warnings" element={<Alerts />} />

      <Route
        path="/analytics"
        element={
          <RequireAuth feature="analytics and trend insights">
            <Analytics />
          </RequireAuth>
        }
      />

      <Route
        path="/reports"
        element={
          <RequireAuth feature="full risk reports">
            <Reports />
          </RequireAuth>
        }
      />

      <Route
        path="/settings"
        element={
          <RequireAuth feature="settings and personalization">
            <Settings />
          </RequireAuth>
        }
      />

      <Route
        path="/changes"
        element={<RecentChanges />}
      />

      <Route
        path="/location/:id"
        element={<LocationDetails />}
      />

      <Route
        path="*"
        element={
          <AppLayout title="Page not found">
            <p className="text-sm text-muted-foreground">
              The requested page does not exist.
            </p>
          </AppLayout>
        }
      />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <ProjectDataProvider>
        <SidebarProvider>
          <BrowserRouter>
            <AppContent />
          </BrowserRouter>
        </SidebarProvider>
      </ProjectDataProvider>
    </AuthProvider>
  );
}