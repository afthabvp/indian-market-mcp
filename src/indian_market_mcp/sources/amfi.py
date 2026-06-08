from __future__ import annotations

import httpx
from .cache import cached

NAV_URL = "https://portal.amfiindia.com/spages/NAVAll.txt"
HISTORY_URL = "https://api.mfapi.in/mf"


@cached(ttl=3600)
async def get_all_navs() -> list[dict]:
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(NAV_URL)
        resp.raise_for_status()

    lines = resp.text.strip().split("\n")
    funds = []
    current_category = ""

    for line in lines:
        line = line.strip()
        if not line or line.startswith("Scheme Code"):
            continue
        parts = line.split(";")
        if len(parts) == 1:
            current_category = line
            continue
        if len(parts) >= 5:
            funds.append({
                "scheme_code": parts[0].strip(),
                "scheme_name": parts[1].strip() if len(parts) > 1 else "",
                "nav": parts[4].strip() if len(parts) > 4 else "",
                "date": parts[5].strip() if len(parts) > 5 else "",
                "category": current_category,
            })
    return funds


async def search_funds(query: str) -> list[dict]:
    all_navs = await get_all_navs()
    q = query.lower()
    return [f for f in all_navs if q in f["scheme_name"].lower()][:20]


@cached(ttl=1800)
async def get_fund_nav(scheme_code: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{HISTORY_URL}/{scheme_code}/latest")
        resp.raise_for_status()
        return resp.json()


@cached(ttl=3600)
async def get_fund_history(scheme_code: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{HISTORY_URL}/{scheme_code}")
        resp.raise_for_status()
        return resp.json()


async def get_fund_history_range(scheme_code: str, from_date: str, to_date: str) -> dict:
    data = await get_fund_history(scheme_code)
    if "data" not in data:
        return data

    filtered = []
    for entry in data["data"]:
        d = entry.get("date", "")
        if from_date <= _parse_date(d) <= to_date:
            filtered.append(entry)

    return {**data, "data": filtered}


def _parse_date(date_str: str) -> str:
    try:
        parts = date_str.split("-")
        if len(parts) == 3:
            months = {
                "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
                "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
                "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
            }
            day, mon, year = parts
            return f"{year}-{months.get(mon, '01')}-{day.zfill(2)}"
    except Exception:
        pass
    return date_str


@cached(ttl=3600)
async def get_fund_categories() -> list[str]:
    all_navs = await get_all_navs()
    return sorted(set(f["category"] for f in all_navs if f["category"]))
