from __future__ import annotations
from datetime import date, timedelta
import requests

OPEN_METEO="https://api.open-meteo.com/v1/forecast"
ARCHIVE="https://archive-api.open-meteo.com/v1/archive"


def _safe_get(url, params):
    r=requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def current(lat: float, lon: float):
    data=_safe_get(OPEN_METEO,{"latitude":lat,"longitude":lon,"current":"temperature_2m,relative_humidity_2m,wind_speed_10m,rain","hourly":"precipitation","forecast_days":2,"timezone":"UTC"})
    hourly=data.get("hourly",{})
    precip=[float(x or 0) for x in hourly.get("precipitation",[])][-24:]
    cur=data.get("current",{})
    return {"temperature":cur.get("temperature_2m"),"humidity":cur.get("relative_humidity_2m"),"wind":cur.get("wind_speed_10m"),"rainfall24h":round(sum(precip),1),"provider":"Open-Meteo","updatedAt":cur.get("time")}


def historical(lat: float, lon: float, start: date, end: date):
    data=_safe_get(ARCHIVE,{"latitude":lat,"longitude":lon,"start_date":start.isoformat(),"end_date":end.isoformat(),"daily":"precipitation_sum","timezone":"UTC"})
    return [{"day":d,"rainfall":float(v or 0)} for d,v in zip(data.get("daily",{}).get("time",[]),data.get("daily",{}).get("precipitation_sum",[]))]
