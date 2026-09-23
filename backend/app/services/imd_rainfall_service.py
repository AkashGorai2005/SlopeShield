"""
SLOPESHIELD NER - official IMD rainfall adapter.

Primary rainfall source:
- IMD district-wise rainfall API for district locations.
- IMD Gangtok Today's Weather Report for Gangtok/Gyalshing station coverage.

Open-Meteo remains the caller's fallback when IMD cannot provide a value.

Notes:
- IMD daily rainfall is measured from 0830 IST to 0830 IST.
- IMD "Weekly Actual" is used as the closest official 7-day accumulation field.
  It is not a rolling 168-hour total.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from html import unescape
from typing import Any

import requests

IMD_DISTRICT_API = "https://mausam.imd.gov.in/api/districtwise_rainfall_api.php"
IMD_DISTRICT_PAGE = (
    "https://mausam.imd.gov.in/responsive/rainfallinformation.php?msg=M"
)
IMD_GANGTOK_TODAY = (
    "https://mausam.imd.gov.in/imd_latest/contents/Todaysweather_mc.php?id=20"
)
REQUEST_TIMEOUT = 15
USER_AGENT = "SLOPESHIELD-NER/1.0"

# Names used by SLOPESHIELD -> IMD district names.
DISTRICT_ALIASES = {
    "aizawl": "AIZAWL",
    "lunglei": "LUNGLEI",
    "shillong": "EAST KHASI HILLS",
    "cherrapunji": "EAST KHASI HILLS",
    "haflong": "DIMA HASAO",
    "guwahati": "KAMRUP METRO",
    "itanagar": "PAPUM PARE",
    "tawang": "TAWANG",
    "kohima": "KOHIMA",
    "dimapur": "DIMAPUR",
    "imphal": "IMPHAL WEST",
    "churachandpur": "CHURACHANDPUR",
    "agartala": "WEST TRIPURA",
    # Sikkim is handled by the station report below.
    "gangtok": "GANGTOK",
    "pelling": "GYALSHING",
}


def _get(url: str) -> requests.Response:
    response = requests.get(
        url,
        timeout=REQUEST_TIMEOUT,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    return response


def _number(value: Any) -> float:
    if value is None:
        return 0.0
    match = re.search(r"-?\d+(?:\.\d+)?", str(value).replace(",", ""))
    return float(match.group(0)) if match else 0.0


def _parse_date(value: Any) -> datetime | None:
    if not value:
        return None
    raw = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            pass
    return None


def _normalise(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", " ", value.upper()).strip()


def _fetch_nwic_csv() -> str:
    """Fetch the current official IMD district CSV from NWIC."""
    page = _get(
        "https://www.nwdp.nwic.gov.in/en/dataset/rainfall-daily-imd/resource/8752174f-1d17-4aaf-8058-2eb396f50157"
    ).text
    # Prefer the resource download link exposed by the official page.
    links = re.findall(r"(?:href|url)=[\"\']([^\"\']+\.csv(?:\?[^\"\']*)?)", page, flags=re.I)
    links += re.findall(r"https?://[^\"\'\s<>]+\.csv(?:\?[^\"\'\s<>]*)?", page, flags=re.I)
    for link in links:
        if link.startswith("/"):
            link = "https://www.nwdp.nwic.gov.in" + link
        if link.startswith("http"):
            response = _get(link)
            return response.text
    raise RuntimeError("Official NWIC IMD rainfall CSV download link not found")


def _csv_district_rainfall(district: str) -> dict:
    import csv
    from io import StringIO

    csv_text = _fetch_nwic_csv()
    rows = csv.DictReader(StringIO(csv_text))
    target = _normalise(district)
    matches = [r for r in rows if _normalise(r.get("District", "")) == target]
    if not matches:
        raise RuntimeError(f"IMD/NWIC district not found: {district}")

    # The official dataset can contain multiple dates. Use the newest row.
    row = max(matches, key=lambda r: _parse_date(r.get("Date")) or datetime.min)
    observed = _parse_date(row.get("Date")) or datetime.utcnow()
    return {
        "observed_at": observed,
        "rainfall_1h": 0.0,
        "rainfall_24h": max(0.0, _number(row.get("Daily Actual"))),
        "rainfall_7d": max(0.0, _number(row.get("Weekly Actual"))),
        "temperature": 0.0,
        "humidity": 0.0,
        "wind_speed": 0.0,
        "source": "IMD/NWIC",
        "source_detail": "National Water Data Portal - IMD Rainfall DistrictWise Daily CSV",
        "rainfall_window": "0830 IST previous day to 0830 IST current day",
    }


def _sikkim_report() -> str:
    return _get(IMD_GANGTOK_TODAY).text


def _sikkim_station_rainfall(station: str) -> dict:
    html = _sikkim_report()

    # Convert HTML to simple text while preserving table row boundaries.
    text = re.sub(r"(?is)<br\s*/?>", "\n", html)
    text = re.sub(r"(?is)</tr>", "\n", text)
    text = re.sub(r"(?is)</t[dh]>", " | ", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", unescape(text))

    station_re = re.escape(station.upper())
    match = re.search(
        rf"{station_re}\s*\|\s*[^|]*\|\s*[^|]*\|\s*[^|]*\|\s*[^|]*"
        rf"\|\s*[^|]*\|\s*[^|]*\|\s*([^|]+)",
        text,
        flags=re.I,
    )
    if not match:
        raise RuntimeError(f"IMD Sikkim station {station} not found")

    rainfall = _number(match.group(1))

    date_match = re.search(r"Date:\s*(\d{4}-\d{2}-\d{2})", text)
    observed = (
        datetime.strptime(date_match.group(1), "%Y-%m-%d")
        if date_match
        else datetime.utcnow()
    )

    return {
        "observed_at": observed,
        "rainfall_1h": 0.0,
        "rainfall_24h": max(0.0, rainfall),
        # The current station page gives the latest daily value only.
        # Use 24h for the 7d feature rather than inventing a 7-day value.
        "rainfall_7d": max(0.0, rainfall),
        "temperature": 0.0,
        "humidity": 0.0,
        "wind_speed": 0.0,
        "source": "IMD",
        "source_detail": "IMD Gangtok Today's Weather Report",
        "rainfall_window": "0830 IST previous day to 0830 IST current day",
    }


def fetch_rainfall(location_name: str) -> dict:
    """
    Fetch current official IMD rainfall for a SLOPESHIELD location.

    Gangtok -> GANGTOK station.
    Pelling -> GYALSINGH station.
    Other locations -> IMD district-wise rainfall API.
    """
    key = _normalise(location_name)

    if key == "GANGTOK":
        return _sikkim_station_rainfall("GANGTOK")

    if key == "PELLING":
        return _sikkim_station_rainfall("GYALSINGH")

    district = DISTRICT_ALIASES.get(location_name.strip().lower())
    if not district:
        raise RuntimeError(f"No IMD district mapping configured for {location_name}")

    return _csv_district_rainfall(district)
