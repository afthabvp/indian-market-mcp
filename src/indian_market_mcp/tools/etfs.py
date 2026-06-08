from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from ..sources import nse


def register(mcp: FastMCP):

    @mcp.tool()
    async def get_all_etfs() -> list[dict]:
        """Get all ETFs listed on NSE with their prices and NAV — Gold ETFs, Debt ETFs, Equity ETFs etc."""
        data = await nse.get_etf_list()
        etfs = []
        for item in data.get("data", []):
            etfs.append({
                "symbol": item.get("symbol"),
                "name": item.get("meta", {}).get("companyName", ""),
                "last_price": item.get("lastPrice"),
                "change": item.get("change"),
                "change_percent": item.get("pChange"),
                "day_high": item.get("dayHigh"),
                "day_low": item.get("dayLow"),
                "previous_close": item.get("previousClose"),
            })
        return etfs

    @mcp.tool()
    async def get_etf_quote(symbol: str) -> dict:
        """Get detailed quote for a specific ETF.
        Example: get_etf_quote("GOLDBEES") or get_etf_quote("NIFTYBEES")"""
        data = await nse.get_quote(symbol)
        info = data.get("priceInfo", {})
        meta = data.get("info", {})
        return {
            "symbol": symbol.upper(),
            "name": meta.get("companyName", ""),
            "price": info.get("lastPrice"),
            "change": info.get("change"),
            "change_percent": info.get("pChange"),
            "open": info.get("open"),
            "close": info.get("close"),
            "day_high": info.get("intraDayHighLow", {}).get("max"),
            "day_low": info.get("intraDayHighLow", {}).get("min"),
            "week_52_high": info.get("weekHighLow", {}).get("max"),
            "week_52_low": info.get("weekHighLow", {}).get("min"),
        }

    @mcp.tool()
    async def get_etf_history(
        symbol: str,
        from_date: str = "",
        to_date: str = "",
    ) -> dict:
        """Get historical data for an ETF. Dates in DD-MM-YYYY format.
        Example: get_etf_history("GOLDBEES", "01-01-2025", "01-06-2025")"""
        return await nse.get_historical(symbol, "EQ", from_date, to_date)
