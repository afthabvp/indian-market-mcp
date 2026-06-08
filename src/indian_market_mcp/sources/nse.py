from __future__ import annotations

import httpx
from .cache import cached

BASE = "https://www.nseindia.com"
API = f"{BASE}/api"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": BASE,
}

_client: httpx.AsyncClient | None = None
_cookies: httpx.Cookies | None = None


async def _get_client() -> httpx.AsyncClient:
    global _client, _cookies
    if _client is None or _cookies is None:
        _client = httpx.AsyncClient(headers=HEADERS, timeout=30, follow_redirects=True)
        resp = await _client.get(BASE)
        _cookies = resp.cookies
    return _client


async def _refresh_cookies() -> None:
    global _cookies
    client = await _get_client()
    r = await client.get(BASE)
    _cookies = r.cookies


async def _fetch(path: str, params: dict | None = None) -> dict:
    client = await _get_client()
    resp = await client.get(f"{API}/{path}", params=params, cookies=_cookies)
    if resp.status_code == 403:
        await _refresh_cookies()
        resp = await client.get(f"{API}/{path}", params=params, cookies=_cookies)
    resp.raise_for_status()
    return resp.json()


@cached(ttl=60)
async def get_quote(symbol: str) -> dict:
    return await _fetch("quote-equity", {"symbol": symbol.upper()})


@cached(ttl=60)
async def get_quote_derivative(symbol: str) -> dict:
    return await _fetch("quote-derivative", {"symbol": symbol.upper()})


@cached(ttl=120)
async def get_option_chain_index(symbol: str) -> dict:
    return await _fetch("option-chain-indices", {"symbol": symbol.upper()})


@cached(ttl=120)
async def get_option_chain_equity(symbol: str) -> dict:
    return await _fetch("option-chain-equities", {"symbol": symbol.upper()})


@cached(ttl=300)
async def get_market_status() -> dict:
    return await _fetch("marketStatus")


@cached(ttl=120)
async def get_gainers_losers() -> dict:
    return await _fetch("live-analysis-variations", {"index": "gainers"})


@cached(ttl=120)
async def get_top_losers() -> dict:
    return await _fetch("live-analysis-variations", {"index": "losers"})


@cached(ttl=60)
async def get_index_data(index: str) -> dict:
    return await _fetch("equity-stockIndices", {"index": index.upper()})


@cached(ttl=300)
async def get_all_indices() -> dict:
    return await _fetch("allIndices")


@cached(ttl=120)
async def get_fii_dii() -> dict:
    return await _fetch("fipiitrddata")


@cached(ttl=300)
async def get_advances_declines() -> dict:
    return await _fetch("market-data-pre-open", {"key": "ALL"})


@cached(ttl=600)
async def get_ipo_current() -> dict:
    return await _fetch("all-upcoming-issues", {"type": "ipo"})


@cached(ttl=600)
async def get_ipo_past() -> dict:
    return await _fetch("all-past-issues", {"type": "ipo"})


@cached(ttl=300)
async def get_etf_list() -> dict:
    return await _fetch("etf")


@cached(ttl=300)
async def get_corporate_actions(symbol: str) -> dict:
    return await _fetch("corporates-corporateActions", {"index": "equities", "symbol": symbol.upper()})


@cached(ttl=600)
async def get_sgb_list() -> dict:
    return await _fetch("sovereign-gold-bonds")


@cached(ttl=300)
async def get_currency_data() -> dict:
    return await _fetch("currency-derivatives-data")


@cached(ttl=120)
async def search_stock(query: str) -> dict:
    return await _fetch("search/autocomplete", {"q": query})


@cached(ttl=300)
async def get_historical(symbol: str, series: str = "EQ", from_date: str = "", to_date: str = "") -> dict:
    params = {"symbol": symbol.upper(), "series": f'["{series}"]'}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    return await _fetch("historical/cm/equity", params)


@cached(ttl=300)
async def get_index_historical(index: str, from_date: str = "", to_date: str = "") -> dict:
    params = {"indexType": index}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    return await _fetch("historical/indicesHistory", params)


@cached(ttl=120)
async def get_sector_performance() -> dict:
    return await _fetch("allIndices")


@cached(ttl=120)
async def get_52week_high() -> dict:
    return await _fetch("live-analysis-52Week", {"index": "high"})


@cached(ttl=120)
async def get_52week_low() -> dict:
    return await _fetch("live-analysis-52Week", {"index": "low"})


@cached(ttl=120)
async def get_most_active_by_volume() -> dict:
    return await _fetch("live-analysis-most-active-securities", {"index": "volume"})


@cached(ttl=120)
async def get_most_active_by_value() -> dict:
    return await _fetch("live-analysis-most-active-securities", {"index": "value"})
