from __future__ import annotations

import yfinance as yf
import httpx
from .cache import cached

COMMODITY_SYMBOLS = {
    "GOLD": "GC=F",
    "SILVER": "SI=F",
    "CRUDE_OIL": "CL=F",
    "NATURAL_GAS": "NG=F",
    "COPPER": "HG=F",
    "ALUMINIUM": "ALI=F",
    "ZINC": "ZNC=F",
    "LEAD": "LEAD=F",
    "NICKEL": "NI=F",
    "COTTON": "CT=F",
}

CURRENCY_SYMBOLS = {
    "USDINR": "USDINR=X",
    "EURINR": "EURINR=X",
    "GBPINR": "GBPINR=X",
    "JPYINR": "JPYINR=X",
}

METALS_DEV_URL = "https://api.metals.dev/v1/latest"


@cached(ttl=120)
async def get_commodity_price(commodity: str) -> dict:
    symbol = COMMODITY_SYMBOLS.get(commodity.upper())
    if not symbol:
        return {"error": f"Unknown commodity: {commodity}. Available: {list(COMMODITY_SYMBOLS.keys())}"}

    ticker = yf.Ticker(symbol)
    info = ticker.info
    return {
        "commodity": commodity.upper(),
        "symbol": symbol,
        "price": info.get("regularMarketPrice"),
        "previous_close": info.get("regularMarketPreviousClose"),
        "day_high": info.get("regularMarketDayHigh"),
        "day_low": info.get("regularMarketDayLow"),
        "change": info.get("regularMarketChange"),
        "change_percent": info.get("regularMarketChangePercent"),
        "currency": info.get("currency", "USD"),
    }


@cached(ttl=120)
async def get_currency_rate(pair: str) -> dict:
    symbol = CURRENCY_SYMBOLS.get(pair.upper())
    if not symbol:
        return {"error": f"Unknown pair: {pair}. Available: {list(CURRENCY_SYMBOLS.keys())}"}

    ticker = yf.Ticker(symbol)
    info = ticker.info
    return {
        "pair": pair.upper(),
        "rate": info.get("regularMarketPrice"),
        "previous_close": info.get("regularMarketPreviousClose"),
        "day_high": info.get("regularMarketDayHigh"),
        "day_low": info.get("regularMarketDayLow"),
        "change": info.get("regularMarketChange"),
        "change_percent": info.get("regularMarketChangePercent"),
    }


@cached(ttl=300)
async def get_commodity_history(commodity: str, period: str = "1mo") -> dict:
    symbol = COMMODITY_SYMBOLS.get(commodity.upper())
    if not symbol:
        return {"error": f"Unknown commodity: {commodity}"}

    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)
    records = []
    for idx, row in df.iterrows():
        records.append({
            "date": idx.strftime("%Y-%m-%d"),
            "open": round(row["Open"], 2),
            "high": round(row["High"], 2),
            "low": round(row["Low"], 2),
            "close": round(row["Close"], 2),
            "volume": int(row["Volume"]),
        })
    return {"commodity": commodity.upper(), "period": period, "data": records}


@cached(ttl=300)
async def get_currency_history(pair: str, period: str = "1mo") -> dict:
    symbol = CURRENCY_SYMBOLS.get(pair.upper())
    if not symbol:
        return {"error": f"Unknown pair: {pair}"}

    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)
    records = []
    for idx, row in df.iterrows():
        records.append({
            "date": idx.strftime("%Y-%m-%d"),
            "open": round(row["Open"], 4),
            "high": round(row["High"], 4),
            "low": round(row["Low"], 4),
            "close": round(row["Close"], 4),
        })
    return {"pair": pair.upper(), "period": period, "data": records}


@cached(ttl=120)
async def get_all_commodities() -> list[dict]:
    results = []
    for name, symbol in COMMODITY_SYMBOLS.items():
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            results.append({
                "commodity": name,
                "price": info.get("regularMarketPrice"),
                "change_percent": info.get("regularMarketChangePercent"),
                "currency": info.get("currency", "USD"),
            })
        except Exception:
            results.append({"commodity": name, "error": "Failed to fetch"})
    return results


@cached(ttl=120)
async def get_all_currencies() -> list[dict]:
    results = []
    for name, symbol in CURRENCY_SYMBOLS.items():
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            results.append({
                "pair": name,
                "rate": info.get("regularMarketPrice"),
                "change_percent": info.get("regularMarketChangePercent"),
            })
        except Exception:
            results.append({"pair": name, "error": "Failed to fetch"})
    return results
