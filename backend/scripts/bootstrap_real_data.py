"""Build a reproducible real-source feature dataset for SLOPESHIELD NER.

Sources:
- NASA Global Landslide Catalog export (historical rainfall-triggered events)
- OpenTopoData SRTM endpoint (elevation)
- Open-Meteo archive (event-day precipitation)

The negative class is a background sample, not proof that a location never had a
landslide. The generated metadata says so explicitly.

The historical_landslides feature represents the number of other NASA GLC
events within 25 km of the sample location. For positive samples, the current
event itself is excluded to avoid directly leaking the target into the feature.
"""

from pathlib import Path
import math
import random
import time

import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

RAW.mkdir(parents=True, exist_ok=True)
PROCESSED.mkdir(parents=True, exist_ok=True)


NASA_CSV = (
    "https://data.nasa.gov/docs/legacy/Global_Landslide_Catalog_Export/"
    "Global_Landslide_Catalog_Export_rows.csv"
)

NASA_FEATURE_SERVER = (
    "https://maps.nccs.nasa.gov/server/rest/services/"
    "global_landslide_catalog/glc_viewer_service/FeatureServer"
)

NER = (20.0, 30.0, 88.0, 98.5)

HISTORICAL_RADIUS_KM = 25.0


def _normalise_nasa_records(records):
    """Flatten ArcGIS records into the dataframe shape used by the pipeline."""
    rows = []

    for rec in records:
        attrs = dict(rec.get("attributes") or {})
        geom = rec.get("geometry") or {}

        existing_keys = {str(k).lower() for k in attrs}

        if "latitude" not in existing_keys and geom.get("y") is not None:
            attrs["latitude"] = geom.get("y")

        if "longitude" not in existing_keys and geom.get("x") is not None:
            attrs["longitude"] = geom.get("x")

        rows.append(attrs)

    return pd.DataFrame(rows)


def download_nasa_feature_server():
    """Fetch the NER bounding box from NASA's ArcGIS GLC service."""
    root = None
    last_root_error = None

    for attempt in range(3):
        try:
            root = requests.get(
                NASA_FEATURE_SERVER,
                params={"f": "json"},
                timeout=45,
                headers={"User-Agent": "SLOPESHIELD-NER/1.0"},
            )
            root.raise_for_status()
            break

        except Exception as exc:
            last_root_error = exc

            if attempt < 2:
                time.sleep(2 ** attempt)

    if root is None:
        raise RuntimeError(
            f"NASA FeatureServer connection failed: {last_root_error}"
        )

    meta = root.json()
    layers = meta.get("layers") or []

    if not layers:
        raise RuntimeError(
            "NASA FeatureServer responded but exposed no layers."
        )

    bbox = f"{NER[2]},{NER[0]},{NER[3]},{NER[1]}"

    last_error = None

    for layer in layers:
        layer_id = layer.get("id")

        if layer_id is None:
            continue

        query_url = f"{NASA_FEATURE_SERVER}/{layer_id}/query"

        try:
            params = {
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "true",
                "geometry": bbox,
                "geometryType": "esriGeometryEnvelope",
                "inSR": "4326",
                "spatialRel": "esriSpatialRelIntersects",
                "outSR": "4326",
                "resultRecordCount": 2000,
                "f": "json",
            }

            r = requests.get(
                query_url,
                params=params,
                timeout=90,
            )

            r.raise_for_status()

            payload = r.json()

            if payload.get("error"):
                raise RuntimeError(payload["error"])

            records = payload.get("features") or []

            if records:
                df = _normalise_nasa_records(records)

                if not df.empty:
                    target = RAW / "nasa_global_landslides.csv"
                    df.to_csv(target, index=False)

                    return (
                        target,
                        f"{NASA_FEATURE_SERVER}/{layer_id}",
                    )

        except Exception as exc:
            last_error = exc

    raise RuntimeError(
        "NASA FeatureServer returned no NER records. "
        f"Last error: {last_error}"
    )


def download_nasa():
    """Prefer NASA FeatureServer; fall back to legacy CSV if needed."""
    target = RAW / "nasa_global_landslides.csv"

    if target.exists():
        return target, "cached"

    try:
        return download_nasa_feature_server()

    except Exception as feature_error:
        print(
            f"NASA FeatureServer unavailable: {feature_error}"
        )
        print(
            "Trying the legacy NASA CSV export as a fallback..."
        )

        r = requests.get(
            NASA_CSV,
            timeout=120,
        )

        r.raise_for_status()

        target.write_bytes(r.content)

        return target, NASA_CSV


def pick_col(df, candidates):
    lower = {
        str(c).lower(): c
        for c in df.columns
    }

    for c in candidates:
        if c.lower() in lower:
            return lower[c.lower()]

    return None


def elevation_and_slope(lat, lon):
    """
    Sample a 3x3 SRTM grid around the point.

    Elevation comes from the center point.
    Slope is a point-sampled central-difference approximation.
    """
    step = 0.0025

    pts = [
        (lat + dy, lon + dx)
        for dy, dx in [
            (-step, -step),
            (-step, 0),
            (-step, step),
            (0, -step),
            (0, 0),
            (0, step),
            (step, -step),
            (step, 0),
            (step, step),
        ]
    ]

    loc = "|".join(
        f"{a},{b}"
        for a, b in pts
    )

    r = requests.get(
        "https://api.opentopodata.org/v1/srtm30m",
        params={"locations": loc},
        timeout=60,
    )

    r.raise_for_status()

    vals = [
        float(x.get("elevation") or 0)
        for x in r.json().get("results", [])
    ]

    if len(vals) != 9:
        return (
            vals[4] if len(vals) > 4 else 0.0,
            0.0,
        )

    dzdx = (
        (
            (vals[5] + 2 * vals[8] + vals[7])
            - (vals[3] + 2 * vals[6] + vals[0])
        )
        / (
            8
            * step
            * 111200
            * max(math.cos(math.radians(lat)), 0.2)
        )
    )

    dzdy = (
        (
            (vals[6] + 2 * vals[7] + vals[8])
            - (vals[0] + 2 * vals[1] + vals[2])
        )
        / (8 * step * 111200)
    )

    slope = math.degrees(
        math.atan(
            math.sqrt(
                dzdx * dzdx
                + dzdy * dzdy
            )
        )
    )

    return vals[4], round(slope, 2)


def rainfall(lat, lon, date):
    try:
        date = pd.to_datetime(
            date,
            errors="coerce",
        )

        if pd.isna(date):
            return 0.0, 0.0

        end_date = date.strftime("%Y-%m-%d")

        start_date = (
            date - pd.Timedelta(days=6)
        ).strftime("%Y-%m-%d")

        r = requests.get(
            "https://archive-api.open-meteo.com/v1/archive",
            params={
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date,
                "end_date": end_date,
                "daily": "precipitation_sum",
                "timezone": "UTC",
            },
            timeout=60,
        )

        r.raise_for_status()

        vals = (
            r.json()
            .get("daily", {})
            .get("precipitation_sum", [])
        )

        if not vals:
            return 0.0, 0.0

        rainfall_values = [
            float(v)
            for v in vals
            if v is not None
        ]

        if not rainfall_values:
            return 0.0, 0.0

        rainfall_24h = rainfall_values[-1]
        rainfall_7d = sum(rainfall_values)

        return rainfall_24h, rainfall_7d

    except Exception as e:
        print(
            f"Rainfall error for "
            f"{lat}, {lon}, {date}: {e}"
        )

        return 0.0, 0.0


def historical_count(
    lat,
    lon,
    events,
    exclude_event=None,
    reference_date=None,
    radius_km=HISTORICAL_RADIUS_KM,
):
    """
    Count historical landslide events within radius_km.

    exclude_event:
        Optional (latitude, longitude, date) tuple representing the
        current positive event. It is excluded from the count.
    """

    count = 0

    lat_rad = math.radians(lat)

    for event_lat, event_lon, event_date in events:

        if reference_date is not None and event_date >= reference_date:
            continue

        if exclude_event is not None:
            same_location = (
                abs(event_lat - exclude_event[0]) < 1e-9
                and abs(event_lon - exclude_event[1]) < 1e-9
            )

            same_date = event_date == exclude_event[2]

            if same_location and same_date:
                continue

        dlat = math.radians(event_lat - lat)
        dlon = math.radians(event_lon - lon)

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat_rad)
            * math.cos(math.radians(event_lat))
            * math.sin(dlon / 2) ** 2
        )

        a = min(1.0, max(0.0, a))

        distance_km = (
            6371.0
            * 2
            * math.asin(math.sqrt(a))
        )

        if distance_km <= radius_km:
            count += 1

    return count


def main():
    source, source_url = download_nasa()

    df = pd.read_csv(source)

    latc = pick_col(
        df,
        ["latitude", "lat"],
    )

    lonc = pick_col(
        df,
        ["longitude", "lon"],
    )

    datec = pick_col(
        df,
        [
            "event_date",
            "event_date_time",
            "date",
        ],
    )

    if not latc or not lonc:
        raise SystemExit(
            "NASA export lacks latitude/longitude columns."
        )

    if not datec:
        raise SystemExit(
            "NASA export lacks an event date column."
        )

    df[latc] = pd.to_numeric(
        df[latc],
        errors="coerce",
    )

    df[lonc] = pd.to_numeric(
        df[lonc],
        errors="coerce",
    )

    NER_STATES = {
        "Assam",
        "Arunachal Pradesh",
        "Arunāchal Pradesh",
        "Manipur",
        "Meghalaya",
        "Meghālaya",
        "Mizoram",
        "Nagaland",
        "Nāgāland",
        "Sikkim",
        "Tripura",
    }

    RAIN_TRIGGERS = [
        "downpour",
        "rain",
        "continuous_rain",
        "monsoon",
        "tropical_cyclone",
    ]

    ner = df[
        df[latc].between(
            NER[0],
            NER[1],
        )
        & df[lonc].between(
            NER[2],
            NER[3],
        )
        & (
            df["country_name"]
            .astype(str)
            .str.strip()
            == "India"
        )
        & (
            df["admin_division_name"]
            .astype(str)
            .str.strip()
            .isin(NER_STATES)
        )
        & (
            df["landslide_trigger"]
            .astype(str)
            .str.strip()
            .str.lower()
            .isin(RAIN_TRIGGERS)
        )
    ].dropna(
        subset=[latc, lonc]
    ).copy()

    ner = ner.drop_duplicates(
        subset=[
            latc,
            lonc,
            datec,
        ]
    )

    ner = ner.head(250).copy()

    if len(ner) < 20:
        raise SystemExit(
            f"Only {len(ner)} NER events found; "
            "refusing to train a tiny model."
        )

    events = []

    for _, r in ner.iterrows():
        parsed_date = pd.to_datetime(
            r[datec],
            errors="coerce",
        )

        if pd.isna(parsed_date):
            continue

        events.append(
            (
                float(r[latc]),
                float(r[lonc]),
                parsed_date.strftime("%Y-%m-%d"),
            )
        )

    if len(events) < 20:
        raise SystemExit(
            f"Only {len(events)} dated NER events found; "
            "refusing to train a tiny model."
        )

    print(
        f"Using {len(events)} NASA NER events."
    )

    print(
        f"Historical feature radius: "
        f"{HISTORICAL_RADIUS_KM} km"
    )

    rows = []

    rng = random.Random(42)

    for i, (lat, lon, d) in enumerate(events):

        if i < 5:
            print(
                "DEBUG:",
                lat,
                lon,
                d,
            )

            print(
                "RAINFALL:",
                rainfall(lat, lon, d),
            )

        e, s = elevation_and_slope(
            lat,
            lon,
        )

        rain_24h, rain_7d = rainfall(
            lat,
            lon,
            d,
        )

        hist_count = historical_count(
            lat,
            lon,
            events,
            exclude_event=(lat, lon, d),
            reference_date=d,
        )

        rows.append(
            {
                "id": f"pos-{i+1}",
                "latitude": lat,
                "longitude": lon,
                "rainfall_24h": rain_24h,
                "rainfall_7d": rain_7d,
                "elevation": e,
                "slope": s,
                "historical_landslides": hist_count,
                "target": 1,
                "data_source": (
                    "NASA_GLC+SRTM+OpenMeteo"
                ),
                "label_note": (
                    "observed NASA GLC event; "
                    "historical count excludes "
                    "current event"
                ),
            }
        )

        nlat = lat
        nlon = lon

        for _ in range(30):
            nlat = (
                lat
                + rng.uniform(0.12, 0.45)
                * rng.choice([-1, 1])
            )

            nlon = (
                lon
                + rng.uniform(0.12, 0.45)
                * rng.choice([-1, 1])
            )

            if (
                NER[0] <= nlat <= NER[1]
                and NER[2] <= nlon <= NER[3]
            ):
                break

        ne, ns = elevation_and_slope(
            nlat,
            nlon,
        )

        nr_24h, nr_7d = rainfall(
            nlat,
            nlon,
            d,
        )

        nhist_count = historical_count(
            nlat,
            nlon,
            events,
            reference_date=d,
        )

        rows.append(
            {
                "id": f"bg-{i+1}",
                "latitude": nlat,
                "longitude": nlon,
                "rainfall_24h": nr_24h,
                "rainfall_7d": nr_7d,
                "elevation": ne,
                "slope": ns,
                "historical_landslides": nhist_count,
                "target": 0,
                "data_source": (
                    "background_sample+"
                    "SRTM+OpenMeteo"
                ),
                "label_note": (
                    "spatial background; "
                    "not verified absence"
                ),
            }
        )

        if i % 10 == 0:
            print(
                f"Processed "
                f"{i+1}/{len(events)} events"
            )

        time.sleep(0.15)

    out = pd.DataFrame(rows)

    out.to_csv(
        PROCESSED / "feature_table.csv",
        index=False,
    )

    out.to_csv(
        PROCESSED / "training.csv",
        index=False,
    )

    pos = out[
        out.target == 1
    ].copy()

    pos["model_source"] = (
        "NASA+SRTM+OpenMeteo"
    )

    pos["probability"] = 0.5

    pos.to_csv(
        PROCESSED / "location_features.csv",
        index=False,
    )

    pd.DataFrame(
        [
            {
                "source": (
                    "NASA Global Landslide Catalog"
                ),
                "role": (
                    "historical event inventory"
                ),
                "url": source_url,
            },
            {
                "source": "OpenTopoData SRTM",
                "role": (
                    "elevation + point-sampled "
                    "slope approximation"
                ),
                "url": (
                    "https://api.opentopodata.org/"
                    "v1/srtm30m"
                ),
            },
            {
                "source": (
                    "Open-Meteo Historical Weather"
                ),
                "role": (
                    "event-day precipitation"
                ),
                "url": (
                    "https://archive-api.open-meteo.com/"
                    "v1/archive"
                ),
            },
        ]
    ).to_csv(
        PROCESSED / "source_manifest.csv",
        index=False,
    )

    print(
        f"Created {len(out)} training rows "
        f"and {len(pos)} real monitoring points."
    )


if __name__ == "__main__":
    main()




