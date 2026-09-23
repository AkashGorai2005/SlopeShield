"""Prepare a training CSV from a feature table supplied by the data team.
No synthetic rows are generated.
"""
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data'/'raw'
OUT=ROOT/'data'/'processed'/'training.csv'
REQUIRED=['latitude','longitude','rainfall_24h','rainfall_7d','elevation','slope','historical_landslides','target']

def main():
    source=RAW/'feature_table.csv'
    if not source.exists(): raise SystemExit(f'Missing {source}. Supply a real feature table; nothing will be fabricated.')
    df=pd.read_csv(source)
    missing=[c for c in REQUIRED if c not in df.columns]
    if missing: raise SystemExit(f'Missing columns: {missing}')
    OUT.parent.mkdir(parents=True,exist_ok=True)
    df[REQUIRED].drop_duplicates().to_csv(OUT,index=False)
    print(f'Prepared {len(df)} real rows -> {OUT}')

if __name__=='__main__': main()
