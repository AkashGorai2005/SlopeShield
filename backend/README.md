# SLOPESHIELD NER backend

FastAPI backend for the software-only SIH landslide monitoring system.

## One-command Windows startup
From the project root, run `run_SLOPESHIELD.bat`.

## Real-source pipeline
Run `backend/scripts/run_real_pipeline.bat`. It downloads the public NASA Global Landslide Catalog export, samples SRTM elevation/slope through OpenTopoData, retrieves event-day precipitation from Open-Meteo, creates a background sample, trains Random Forest + XGBoost, evaluates both, and saves the selected model.

The negative class is explicitly documented as a spatial background sample. It is **not** proof of landslide absence. The slope is point-sampled from SRTM elevations, not a full raster DEM derivative. Do not report the resulting metrics as field-validated accuracy.

## API
- `/docs` Swagger UI
- `/health`
- `/api/status`
- `/api/data/status`
- `/api/locations`
- `/api/data/risk`
- `/api/data/rainfall`
- `/api/data/historical`
- `/api/monitoring/cycle` (POST; fetches Open-Meteo, recalculates the trained model, persists predictions and alerts)
- `/api/data/weather/{location_id}`
- `/api/predictions/simulate`
- `/api/predictions/status`
- `/api/reports/csv`
- `/api/reports/html`

No ESP32, IoT device, physical sensor, or sensor simulator is used.
