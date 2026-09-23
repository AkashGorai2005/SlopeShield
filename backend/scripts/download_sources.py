"""Download publicly documented source files without fabricating scientific data."""
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data'/'raw'
RAW.mkdir(parents=True, exist_ok=True)
NASA='https://data.nasa.gov/docs/legacy/Global_Landslide_Catalog_Export/Global_Landslide_Catalog_Export_rows.csv'

def download(url, target):
    r=requests.get(url, timeout=60)
    r.raise_for_status()
    target.write_bytes(r.content)
    print(f'Downloaded {target}')

if __name__=='__main__':
    download(NASA, RAW/'nasa_global_landslides.csv')
