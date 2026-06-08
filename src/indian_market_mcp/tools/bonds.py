from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from ..sources import nse


def register(mcp: FastMCP):

    @mcp.tool()
    async def get_sovereign_gold_bonds() -> dict:
        """Get all Sovereign Gold Bonds (SGBs) listed on NSE with prices and maturity dates."""
        return await nse.get_sgb_list()

    @mcp.tool()
    async def get_sgb_quote(symbol: str) -> dict:
        """Get detailed quote for a specific Sovereign Gold Bond.
        Example: get_sgb_quote("SGBJAN30IX")"""
        data = await nse.get_quote(symbol)
        info = data.get("priceInfo", {})
        return {
            "symbol": symbol.upper(),
            "name": data.get("info", {}).get("companyName", ""),
            "price": info.get("lastPrice"),
            "change": info.get("change"),
            "change_percent": info.get("pChange"),
            "day_high": info.get("intraDayHighLow", {}).get("max"),
            "day_low": info.get("intraDayHighLow", {}).get("min"),
            "week_52_high": info.get("weekHighLow", {}).get("max"),
            "week_52_low": info.get("weekHighLow", {}).get("min"),
        }

    @mcp.tool()
    async def get_sgb_history(
        symbol: str,
        from_date: str = "",
        to_date: str = "",
    ) -> dict:
        """Get historical price data for a Sovereign Gold Bond.
        Example: get_sgb_history("SGBJAN30IX", "01-01-2025", "01-06-2025")"""
        return await nse.get_historical(symbol, "SG", from_date, to_date)
