const API_BASE = import.meta.env.VITE_API_BASE_URL || `${window.location.protocol}//${window.location.hostname}:8000/api`;

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  } catch (error) {
    if (error?.name === "AbortError") throw new Error(`SLOPESHIELD API request timed out: ${path}`);
    throw new Error(`SLOPESHIELD API is not running at ${API_BASE}. Start run_SLOPESHIELD.bat and keep the API window open.`);
  }
  if (!response.ok) {
    const message = await response.text().catch(() => "Request failed");
    throw new Error(message || `API request failed: ${response.status}`);
  }
  const type = response.headers.get("content-type") || "";
  return type.includes("application/json") ? response.json() : response.text();
}

export const getLocations = () => request("/locations");
export const getLocation = (id) => request(`/locations/${id}`);
export const getRiskData = () => request("/data/risk");
export const getRainfallData = () => request("/data/rainfall");
export const getWarnings = (status = "active") => request(`/alerts?status=${status}`);
export const resolveAlert = (id) => request(`/alerts/${String(id).replace(/^w-/, "")}/resolve`, { method: "PATCH" });
export const getSummary = () => request("/data/summary");
export const getMapLayers = () => request("/data/layers");
export const getHistorical = () => request("/data/historical");
export const getDataStatus = () => request("/data/status");
export const getWeather = (locationId) => request(`/data/weather/${locationId}`);
export const getWeatherHistory = (locationId, days = 7) => request(`/data/weather/${locationId}/history?days=${days}`);
export const simulateRisk = (locationId, rainfall) => request("/predictions/simulate", { method: "POST", body: JSON.stringify({ locationId, rainfall }) });
export const login = (name, email) => request("/auth/login", { method: "POST", body: JSON.stringify({ name, email }) });
export const getModelStatus = () => request("/predictions/status");
export const runMonitoringCycle = () => request("/monitoring/cycle", { method: "POST" });
export const getSystemStatus = () => request("/status");
export const getReportSummary = () => request("/reports/summary");
export const downloadReportCsv = () => `${API_BASE}/reports/csv`;
export const reportHtmlUrl = () => `${API_BASE}/reports/html`;
export const reportPdfUrl = () => `${API_BASE}/reports/pdf`;
export const problemsPdfUrl = () => `${API_BASE}/reports/problems-pdf`;

export default { getLocations, getLocation, getRiskData, getRainfallData, getWarnings, resolveAlert, getSummary, getMapLayers, getHistorical, getDataStatus, getWeather, getWeatherHistory, simulateRisk, runMonitoringCycle, login, getModelStatus, getSystemStatus, getReportSummary, downloadReportCsv, reportHtmlUrl, reportPdfUrl, problemsPdfUrl };
