# SLOPESHIELD NER data methodology

## Sources wired into the project
1. NASA Global Landslide Catalog export — historical rainfall-triggered landslide event inventory.
2. Open-Meteo Historical Weather API — event-day precipitation.
3. OpenTopoData SRTM endpoint — point elevation and a 3x3 point-sampled slope approximation.
4. Bhuvan/ISRO is documented as the intended contextual land-cover/geospatial source; it is not silently converted into model features without a verified downloadable layer.

## Model
Features currently supported by the trained pipeline: rainfall_24h, rainfall_7d, elevation, slope, historical_landslides.
Both Random Forest and XGBoost are trained; the better holdout F1 is selected. Evaluation includes accuracy, precision, recall, F1, ROC-AUC and confusion matrix.

## Scientific safeguards
- No invented live readings.
- No invented accuracy.
- Background samples are labelled as background, not confirmed negatives.
- Risk classes are an operational classification of model probability, not a government hazard declaration.
- If an official IMD feed or authoritative DEM/LULC/geology dataset is available, configure it and regenerate the dataset before final SIH claims.
