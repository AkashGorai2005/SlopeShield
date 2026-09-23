"""Quick connectivity test for the NASA Global Landslide Catalog source."""
from bootstrap_real_data import download_nasa_feature_server, NER

try:
    path, url = download_nasa_feature_server()
    print(f"NASA source OK")
    print(f"Source: {url}")
    print(f"Saved: {path}")
except Exception as exc:
    print("NASA source FAILED")
    print(type(exc).__name__ + ":", exc)
    raise SystemExit(1)
