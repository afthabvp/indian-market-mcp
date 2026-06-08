from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from ..sources import mcx


def register(mcp: FastMCP):

    @mcp.tool()
    async def get_currency_rate(pair: str) -> dict:
        """Get live exchange rate — USDINR, EURINR, GBPINR, JPYINR.
        Example: get_currency_rate("USDINR")"""
        return await mcx.get_currency_rate(pair)

    @mcp.tool()
    async def get_all_currency_rates() -> list[dict]:
        """Get live rates for all supported INR currency pairs."""
        return await mcx.get_all_currencies()

    @mcp.tool()
    async def get_currency_history(pair: str, period: str = "1mo") -> dict:
        """Get historical exchange rate data. Periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max.
        Example: get_currency_history("USDINR", "6mo")"""
        return await mcx.get_currency_history(pair, period)
