from __future__ import annotations

import yfinance as yf
from mcp.server.fastmcp import FastMCP
from ..sources import nse


def register(mcp: FastMCP):

    @mcp.tool()
    async def screen_stocks(
        index: str = "NIFTY 500",
        min_price: float = 0,
        max_price: float = 0,
        min_change_percent: float = -100,
        max_change_percent: float = 100,
        min_volume: float = 0,
        sector: str = "",
        near_52w_high: bool = False,
        near_52w_low: bool = False,
        sort_by: str = "change_percent",
        sort_order: str = "desc",
        limit: int = 20,
    ) -> list[dict]:
        """Screen stocks with multiple filters. Works on any NSE index.
        Filters:
        - min_price/max_price: price range
        - min_change_percent/max_change_percent: % change range
        - min_volume: minimum traded volume
        - sector: filter by sector keyword (e.g. "IT", "Bank", "Pharma")
        - near_52w_high: stocks within 5% of 52-week high
        - near_52w_low: stocks within 5% of 52-week low
        - sort_by: change_percent, price, volume (default: change_percent)
        - sort_order: asc or desc
        Example: screen_stocks(min_price=100, max_price=500, min_change_percent=2, sort_by="change_percent")"""
        data = await nse.get_index_data(index)
        stocks = data.get("data", [])
        results = []

        for s in stocks:
            price = s.get("lastPrice") or 0
            change_pct = s.get("pChange") or 0
            vol = s.get("totalTradedVolume") or 0
            high_52 = s.get("yearHigh") or 0
            low_52 = s.get("yearLow") or 0
            sym = s.get("symbol", "")
            industry = s.get("meta", {}).get("industry", "") if isinstance(s.get("meta"), dict) else ""

            if min_price and price < min_price:
                continue
            if max_price and price > max_price:
                continue
            if change_pct < min_change_percent or change_pct > max_change_percent:
                continue
            if min_volume and vol < min_volume:
                continue
            if sector and sector.lower() not in industry.lower():
                continue
            if near_52w_high and high_52 and price < high_52 * 0.95:
                continue
            if near_52w_low and low_52 and price > low_52 * 1.05:
                continue

            results.append({
                "symbol": sym,
                "price": price,
                "change_percent": round(change_pct, 2),
                "volume": vol,
                "day_high": s.get("dayHigh"),
                "day_low": s.get("dayLow"),
                "week_52_high": high_52,
                "week_52_low": low_52,
                "industry": industry,
            })

        reverse = sort_order == "desc"
        sort_key_map = {
            "change_percent": lambda x: x.get("change_percent", 0),
            "price": lambda x: x.get("price", 0),
            "volume": lambda x: x.get("volume", 0),
        }
        key_fn = sort_key_map.get(sort_by, sort_key_map["change_percent"])
        results.sort(key=key_fn, reverse=reverse)

        return results[:limit]

    @mcp.tool()
    async def screen_by_fundamentals(
        min_pe: float = 0,
        max_pe: float = 0,
        min_pb: float = 0,
        max_pb: float = 0,
        min_market_cap: float = 0,
        min_dividend_yield: float = 0,
        min_roe: float = 0,
        sector: str = "",
        limit: int = 20,
    ) -> list[dict]:
        """Screen stocks by fundamental metrics using Yahoo Finance data.
        Filters: PE ratio, PB ratio, market cap (in Cr), dividend yield (%), ROE (%).
        Example: screen_by_fundamentals(min_pe=5, max_pe=20, min_roe=15, limit=10)
        Note: This is slower as it fetches data per stock. Works best with sector filter."""
        data = await nse.get_nifty500_list()
        stocks = data.get("data", [])
        results = []

        candidates = stocks
        if sector:
            candidates = [s for s in stocks if sector.lower() in (s.get("meta", {}).get("industry", "") if isinstance(s.get("meta"), dict) else "").lower()]
        candidates = candidates[:100]

        for s in candidates:
            sym = s.get("symbol", "")
            try:
                ticker = yf.Ticker(f"{sym}.NS")
                info = ticker.info
            except Exception:
                continue

            pe = info.get("trailingPE") or 0
            pb = info.get("priceToBook") or 0
            mcap = (info.get("marketCap") or 0) / 1e7
            div_yield = (info.get("dividendYield") or 0) * 100
            roe = (info.get("returnOnEquity") or 0) * 100

            if min_pe and pe < min_pe:
                continue
            if max_pe and pe > max_pe:
                continue
            if min_pb and pb < min_pb:
                continue
            if max_pb and pb > max_pb:
                continue
            if min_market_cap and mcap < min_market_cap:
                continue
            if min_dividend_yield and div_yield < min_dividend_yield:
                continue
            if min_roe and roe < min_roe:
                continue

            results.append({
                "symbol": sym,
                "company": info.get("shortName", ""),
                "price": info.get("regularMarketPrice"),
                "pe": round(pe, 2),
                "pb": round(pb, 2),
                "market_cap_cr": round(mcap, 0),
                "dividend_yield": round(div_yield, 2),
                "roe": round(roe, 2),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
            })

            if len(results) >= limit:
                break

        return results

    @mcp.tool()
    async def run_preset_screen(preset: str) -> list[dict]:
        """Run a pre-built screener strategy.
        Presets:
        - "top_gainers" — stocks up > 3% today
        - "top_losers" — stocks down > 3% today
        - "high_volume" — unusual volume (top 20)
        - "near_52w_high" — within 5% of 52-week high
        - "near_52w_low" — within 5% of 52-week low
        - "penny_stocks" — price < 50, sorted by change
        - "large_cap_value" — large caps with PE < 20
        - "high_dividend" — dividend yield > 2%
        Example: run_preset_screen("top_gainers")"""
        presets = {
            "top_gainers": {"min_change_percent": 3, "sort_by": "change_percent", "sort_order": "desc"},
            "top_losers": {"max_change_percent": -3, "sort_by": "change_percent", "sort_order": "asc"},
            "high_volume": {"min_volume": 1, "sort_by": "volume", "sort_order": "desc"},
            "near_52w_high": {"near_52w_high": True, "sort_by": "change_percent", "sort_order": "desc"},
            "near_52w_low": {"near_52w_low": True, "sort_by": "change_percent", "sort_order": "asc"},
            "penny_stocks": {"min_price": 1, "max_price": 50, "sort_by": "change_percent", "sort_order": "desc"},
        }

        if preset in presets:
            return await screen_stocks(**presets[preset])

        fundamental_presets = {
            "large_cap_value": {"min_market_cap": 20000, "max_pe": 20, "limit": 20},
            "high_dividend": {"min_dividend_yield": 2, "limit": 20},
        }

        if preset in fundamental_presets:
            return await screen_by_fundamentals(**fundamental_presets[preset])

        return {"error": f"Unknown preset: {preset}. Available: {list(presets.keys()) + list(fundamental_presets.keys())}"}
