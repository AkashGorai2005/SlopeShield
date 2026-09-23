from fastapi import APIRouter, HTTPException
from app.services.data_service import get_locations, get_historical, get_risk, get_rainfall, get_summary, data_status
from app.services.weather_service import current, historical
from datetime import date, timedelta

router=APIRouter(prefix="/data",tags=["data"])

@router.get("/risk")
def risk(): return get_risk()

@router.get("/rainfall")
def rainfall(): return get_rainfall()

@router.get("/historical")
def historical_points(): return get_historical()

@router.get("/summary")
def summary(): return get_summary()

@router.get("/status")
def status(): return data_status()

@router.get("/weather/{location_id}")
def weather(location_id: str):
    item=next((x for x in get_locations() if x["id"]==location_id),None)
    if not item: raise HTTPException(404,"Location not found")
    try:
        return {**current(item["latitude"],item["longitude"]),"place":item["name"]}
    except Exception as exc:
        raise HTTPException(503,f"Weather provider unavailable: {exc}")

@router.get("/weather/{location_id}/history")
def weather_history(location_id: str, days: int=7):
    item=next((x for x in get_locations() if x["id"]==location_id),None)
    if not item: raise HTTPException(404,"Location not found")
    days=max(1,min(days,31)); end=date.today(); start=end-timedelta(days=days-1)
    try: return historical(item["latitude"],item["longitude"],start,end)
    except Exception as exc: raise HTTPException(503,f"Weather provider unavailable: {exc}")

@router.get("/layers")
def layers():
    return [
      {"id":"risk","name":"Risk Zones","description":"Model-estimated risk classes","default":True,"source":"SLOPESHIELD model"},
      {"id":"historical","name":"Historical Landslides","description":"NASA Global Landslide Catalog inventory when ingested","default":True,"source":"NASA GLC"},
      {"id":"rainfall","name":"Rainfall","description":"Rainfall attached to monitored points","default":False,"source":"Open-Meteo / configured source"},
      {"id":"slope","name":"Slope","description":"DEM-derived terrain slope when pipeline is run","default":False,"source":"DEM pipeline"},
      {"id":"elevation","name":"Elevation","description":"Elevation sampled from DEM/elevation service","default":False,"source":"SRTM/OpenTopoData"},
      {"id":"landcover","name":"Land Cover","description":"Context layer; connect an authorised raster/WMS source","default":False,"source":"Bhuvan/ISRO or configured source"},
      {"id":"geology","name":"Geology","description":"Context layer; connect an authorised geology source","default":False,"source":"Bhuvan/ISRO or configured source"},
    ]
