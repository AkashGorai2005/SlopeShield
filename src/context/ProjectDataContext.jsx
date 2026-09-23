import { createContext, useContext, useEffect, useState } from "react";
import {
  getDataStatus,
  getLocations,
  getHistorical,
  getMapLayers,
  getRainfallData,
  getRiskData,
  getSummary,
  getSystemStatus,
  getWarnings,
} from "@/services/api";

const ProjectDataContext = createContext(null);

const endpoints = [
  "locations",
  "risk data",
  "rainfall data",
  "summary",
  "warnings",
  "map layers",
  "historical data",
  "data status",
  "system status",
];

function responseValue(result, fallback) {
  return result?.status === "fulfilled" ? result.value : fallback;
}

function errorMessage(results) {
  const failures = results
    .map((result, index) => ({ result, index }))
    .filter(({ result }) => result.status === "rejected")
    .map(({ result, index }) => `${endpoints[index]}: ${result.reason?.message || "request failed"}`);

  return failures.length > 0 ? failures.join(" | ") : null;
}

export function ProjectDataProvider({ children }) {
  const [state, setState] = useState({
    loading: true,
    error: null,
    locations: [],
    risk: null,
    rainfall: null,
    summary: null,
    warnings: [],
    mapLayers: [],
    historical: [],
    dataStatus: null,
    systemStatus: null,
  });

  useEffect(() => {
    let cancelled = false;

    const load = () => Promise.allSettled([
      getLocations(),
      getRiskData(),
      getRainfallData(),
      getSummary(),
      getWarnings(),
      getMapLayers(),
      getHistorical(),
      getDataStatus(),
      getSystemStatus(),
    ]).then((results) => {
      if (cancelled) return;

      const locationsResponse = responseValue(results[0], []);
      const historicalResponse = responseValue(results[6], { points: [] });

      setState({
        loading: false,
        error: errorMessage(results),
        locations: Array.isArray(locationsResponse)
          ? locationsResponse
          : locationsResponse?.locations || [],
        risk: responseValue(results[1], null),
        rainfall: responseValue(results[2], null),
        summary: responseValue(results[3], null),
        warnings: responseValue(results[4], []),
        mapLayers: responseValue(results[5], []),
        historical: Array.isArray(historicalResponse)
          ? historicalResponse
          : historicalResponse?.points || [],
        dataStatus: responseValue(results[7], null),
        systemStatus: responseValue(results[8], null),
        refresh: load,
      });
    });

    load();
    const refresh = window.setInterval(load, 60000);

    return () => {
      cancelled = true;
      window.clearInterval(refresh);
    };
  }, []);

  return (
    <ProjectDataContext.Provider value={state}>
      {children}
    </ProjectDataContext.Provider>
  );
}

export function useProjectData() {
  return useContext(ProjectDataContext);
}