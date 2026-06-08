from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from ..sources import nse


def register(mcp: FastMCP):

    @mcp.tool()
    async def get_stock_quote(symbol: str) -> dict:
        """Get live stock quote from NSE — price, volume, day high/low, 52-week range, market cap.
        Example: get_stock_quote("RELIANCE")"""
        data = await nse.get_quote(symbol)
        info = data.get("priceInfo", {})
        meta = data.get("info", {})
        return {
            "symbol": symbol.upper(),
            "company": meta.get("companyName", ""),
            "industry": meta.get("industry", ""),
            "price": info.get("lastPrice"),
            "change": info.get("change"),
            "change_percent": info.get("pChange"),
            "open": info.get("open"),
            "close": info.get("close"),
            "day_high": info.get("intraDayHighLow", {}).get("max"),
            "day_low": info.get("intraDayHighLow", {}).get("min"),
            "week_52_high": info.get("weekHighLow", {}).get("max"),
            "week_52_low": info.get("weekHighLow", {}).get("min"),
            "total_traded_volume": data.get("securityWiseDP", {}).get("quantityTraded"),
        }

    @mcp.tool()
    async def search_stocks(query: str) -> list[dict]:
        """Search stocks by name or symbol on NSE.
        Example: search_stocks("reliance") or search_stocks("INFY")"""
        data = await nse.search_stock(query)
        results = []
        for item in data.get("symbols", []):
            results.append({
                "symbol": item.get("symbol", ""),
                "company": item.get("symbol_info", ""),
            })
        return results[:15]

    @mcp.tool()
    async def get_stock_history(
        symbol: str,
        from_date: str = "",
        to_date: str = "",
    ) -> dict:
        """Get historical OHLC data for a stock.
        Dates in DD-MM-YYYY format.
        Example: get_stock_history("TCS", "01-01-2025", "01-06-2025")"""
        return await nse.get_historical(symbol, "EQ", from_date, to_date)

    @mcp.tool()
    async def get_top_gainers() -> list[dict]:
        """Get today's top gaining stocks on NSE."""
        data = await nse.get_gainers_losers()
        return data.get("NIFTY", {}).get("data", [])[:15]

    @mcp.tool()
    async def get_top_losers() -> list[dict]:
        """Get today's top losing stocks on NSE."""
        data = await nse.get_top_losers()
        return data.get("NIFTY", {}).get("data", [])[:15]

    @mcp.tool()
    async def get_52week_high() -> list[dict]:
        """Get stocks at their 52-week high."""
        return await nse.get_52week_high()

    @mcp.tool()
    async def get_52week_low() -> list[dict]:
        """Get stocks at their 52-week low."""
        return await nse.get_52week_low()

    @mcp.tool()
    async def get_most_active_stocks(by: str = "volume") -> list[dict]:
        """Get most active stocks by volume or value.
        Example: get_most_active_stocks("volume") or get_most_active_stocks("value")"""
        if by == "value":
            return await nse.get_most_active_by_value()
        return await nse.get_most_active_by_volume()

    @mcp.tool()
    async def get_corporate_actions(symbol: str) -> dict:
        """Get corporate actions (dividends, splits, bonus) for a stock.
        Example: get_corporate_actions("TCS")"""
        return await nse.get_corporate_actions(symbol)
