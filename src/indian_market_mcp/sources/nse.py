from __future__ import annotations

import asyncio
from urllib.parse import urlencode
from curl_cffi.requests import AsyncSession
from .cache import cached

BASE = "https://www.nseindia.com"
API = f"{BASE}/api"

_session: AsyncSession | None = None
_initialized = False


async def _get_session() -> AsyncSession:
    global _session, _initialized
    if _session is None:
        _session = AsyncSession(impersonate="chrome")
    if not _initialized:
        await _session.get(BASE)
        _initialized = True
        await asyncio.sleep(1)
    return _session


async def _fetch(path: str, params: dict | None = None) -> dict:
    session = await _get_session()
    url = f"{API}/{path}"
    if params:
        url = f"{url}?{urlencode(params)}"
    resp = await session.get(url)
    if resp.status_code == 403:
        global _initialized
        _initialized = False
        session = await _get_session()
        resp = await session.get(url)
    if resp.status_code != 200:
        raise Exception(f"NSE API error {resp.status_code} for {path}")
    return resp.json()


# ── Stock Quote (NSE blocked → use yfinance) ─────────────────

@cached(ttl=60)
async def get_quote(symbol: str) -> dict:
    try:
        return await _fetch("quote-equity", {"symbol": symbol.upper()})
    except Exception:
        return await _yf_quote(symbol)


async def _yf_quote(symbol: str) -> dict:
    import yfinance as yf
    ticker = yf.Ticker(f"{symbol.upper()}.NS")
    info = ticker.info
    return {
        "info": {
            "companyName": info.get("longName", info.get("shortName", "")),
            "industry": info.get("industry", ""),
            "symbol": symbol.upper(),
        },
        "priceInfo": {
            "lastPrice": info.get("regularMarketPrice") or info.get("currentPrice"),
            "change": info.get("regularMarketChange"),
            "pChange": info.get("regularMarketChangePercent"),
            "open": info.get("regularMarketOpen") or info.get("open"),
            "close": info.get("regularMarketPreviousClose") or info.get("previousClose"),
            "intraDayHighLow": {
                "max": info.get("regularMarketDayHigh") or info.get("dayHigh"),
                "min": info.get("regularMarketDayLow") or info.get("dayLow"),
            },
            "weekHighLow": {
                "max": info.get("fiftyTwoWeekHigh"),
                "min": info.get("fiftyTwoWeekLow"),
            },
        },
        "securityWiseDP": {
            "quantityTraded": info.get("regularMarketVolume") or info.get("volume"),
        },
    }


# ── Search (NSE blocked → use yfinance) ──────────────────────

@cached(ttl=120)
async def search_stock(query: str) -> dict:
    try:
        return await _fetch("search/autocomplete", {"q": query})
    except Exception:
        return _yf_search(query)


def _yf_search(query: str) -> dict:
    import yfinance as yf
    results = []
    for suffix in [".NS", ".BO"]:
        try:
            t = yf.Ticker(f"{query.upper()}{suffix}")
            info = t.info
            if info.get("regularMarketPrice") or info.get("currentPrice"):
                results.append({
                    "symbol": info.get("symbol", "").replace(".NS", "").replace(".BO", ""),
                    "symbol_info": info.get("longName", info.get("shortName", "")),
                })
        except Exception:
            pass
    return {"symbols": results}


# ── Derivative Quote (NSE blocked → use yfinance for basic) ──

@cached(ttl=60)
async def get_quote_derivative(symbol: str) -> dict:
    try:
        return await _fetch("quote-derivative", {"symbol": symbol.upper()})
    except Exception:
        return {"stocks": [], "info": {"symbol": symbol.upper()}, "error": "Derivative data temporarily unavailable from NSE. Try during market hours."}


# ── Option Chain (NSE blocked → return helpful error) ────────

@cached(ttl=120)
async def get_option_chain_index(symbol: str) -> dict:
    try:
        return await _fetch("option-chain-indices", {"symbol": symbol.upper()})
    except Exception:
        return {"records": {"expiryDates": [], "underlyingValue": None, "strikePrices": [], "data": []}, "filtered": {"CE": {"totOI": 0}, "PE": {"totOI": 0}, "data": []}, "error": "Option chain temporarily unavailable from NSE. Works during market hours."}


@cached(ttl=120)
async def get_option_chain_equity(symbol: str) -> dict:
    try:
        return await _fetch("option-chain-equities", {"symbol": symbol.upper()})
    except Exception:
        return {"records": {"expiryDates": [], "data": []}, "filtered": {"CE": {"totOI": 0}, "PE": {"totOI": 0}, "data": []}, "error": "Option chain temporarily unavailable from NSE. Works during market hours."}


# ── Index Data (NSE blocked → extract from allIndices) ───────

@cached(ttl=60)
async def get_index_data(index: str) -> dict:
    try:
        return await _fetch("equity-stockIndices", {"index": index})
    except Exception:
        all_data = await get_all_indices()
        for idx in all_data.get("data", []):
            if idx.get("index", "").upper() == index.upper():
                return {
                    "metadata": {
                        "last": idx.get("last"),
                        "open": idx.get("open"),
                        "high": idx.get("high"),
                        "low": idx.get("low"),
                        "previousClose": idx.get("previousClose"),
                        "change": idx.get("variation"),
                        "percChange": idx.get("percentChange"),
                    },
                    "advance": {},
                    "data": [],
                }
        return {"metadata": {}, "data": [], "error": f"Index {index} not found"}


@cached(ttl=300)
async def get_all_indices() -> dict:
    return await _fetch("allIndices")


# ── FII/DII (NSE blocked → use moneycontrol or return empty) ─

@cached(ttl=120)
async def get_fii_dii() -> dict:
    try:
        return await _fetch("fipiitrddata")
    except Exception:
        return {"error": "FII/DII data temporarily unavailable from NSE. Try during market hours."}


@cached(ttl=300)
async def get_market_status() -> dict:
    return await _fetch("marketStatus")


@cached(ttl=120)
async def get_gainers_losers() -> dict:
    return await _fetch("live-analysis-variations", {"index": "gainers"})


@cached(ttl=120)
async def get_top_losers() -> dict:
    return await _fetch("live-analysis-variations", {"index": "losers"})


@cached(ttl=300)
async def get_advances_declines() -> dict:
    return await _fetch("market-data-pre-open", {"key": "ALL"})


@cached(ttl=600)
async def get_ipo_current() -> dict:
    return await _fetch("all-upcoming-issues", {"type": "ipo"})


@cached(ttl=600)
async def get_ipo_past() -> dict:
    try:
        return await _fetch("all-past-issues", {"type": "ipo"})
    except Exception:
        return {"data": [], "error": "Past IPO data temporarily unavailable."}


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
    try:
        return await _fetch("currency-derivatives-data")
    except Exception:
        return {"error": "Currency derivatives data temporarily unavailable."}


@cached(ttl=300)
async def get_historical(symbol: str, series: str = "EQ", from_date: str = "", to_date: str = "") -> dict:
    params = {"symbol": symbol.upper(), "series": f'["{series}"]'}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    try:
        return await _fetch("historical/cm/equity", params)
    except Exception:
        return _yf_historical(symbol, from_date, to_date)


def _yf_historical(symbol: str, from_date: str = "", to_date: str = "") -> dict:
    import yfinance as yf
    ticker = yf.Ticker(f"{symbol.upper()}.NS")
    kwargs = {"period": "6mo"}
    if from_date and to_date:
        parts_from = from_date.split("-")
        parts_to = to_date.split("-")
        if len(parts_from) == 3 and len(parts_to) == 3:
            kwargs = {
                "start": f"{parts_from[2]}-{parts_from[1]}-{parts_from[0]}",
                "end": f"{parts_to[2]}-{parts_to[1]}-{parts_to[0]}",
            }
    df = ticker.history(**kwargs)
    data = []
    for idx, row in df.iterrows():
        data.append({
            "CH_TIMESTAMP": idx.strftime("%Y-%m-%d"),
            "CH_OPENING_PRICE": round(row["Open"], 2),
            "CH_TRADE_HIGH_PRICE": round(row["High"], 2),
            "CH_TRADE_LOW_PRICE": round(row["Low"], 2),
            "CH_CLOSING_PRICE": round(row["Close"], 2),
            "CH_TOT_TRADED_QTY": int(row["Volume"]),
        })
    return {"data": data}


@cached(ttl=300)
async def get_index_historical(index: str, from_date: str = "", to_date: str = "") -> dict:
    params = {"indexType": index}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    try:
        return await _fetch("historical/indicesHistory", params)
    except Exception:
        return {"data": {"indexCloseOnlineRecords": []}, "error": "Index history temporarily unavailable."}


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


# ── Corporate endpoints (some blocked → graceful fallback) ───

@cached(ttl=600)
async def get_shareholding(symbol: str) -> dict:
    try:
        return await _fetch("corporates-shareholding", {"index": "equities", "symbol": symbol.upper()})
    except Exception:
        return {"error": "Shareholding data temporarily unavailable from NSE."}


@cached(ttl=600)
async def get_board_meetings(symbol: str) -> dict:
    try:
        return await _fetch("corporates-boardMeetings", {"index": "equities", "symbol": symbol.upper()})
    except Exception:
        return {"error": "Board meetings data temporarily unavailable from NSE."}


@cached(ttl=600)
async def get_announcements(index: str = "equities", symbol: str = "") -> dict:
    params = {"index": index}
    if symbol:
        params["symbol"] = symbol.upper()
    try:
        return await _fetch("corporates-announcements", params)
    except Exception:
        return {"error": "Announcements data temporarily unavailable from NSE."}


@cached(ttl=300)
async def get_nifty500_list() -> dict:
    try:
        return await _fetch("equity-stockIndices", {"index": "NIFTY 500"})
    except Exception:
        return await get_all_indices()


@cached(ttl=600)
async def get_financial_results(symbol: str) -> dict:
    try:
        return await _fetch("corporates-financial-results-data", {"index": "equities", "symbol": symbol.upper()})
    except Exception:
        return {"error": "Financial results temporarily unavailable from NSE."}
