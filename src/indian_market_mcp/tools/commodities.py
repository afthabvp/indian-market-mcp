from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from ..sources import mcx


def register(mcp: FastMCP):

    @mcp.tool()
    async def get_commodity_price(commodity: str) -> dict:
        """Get live price for a commodity — GOLD, SILVER, CRUDE_OIL, NATURAL_GAS, COPPER, ALUMINIUM, ZINC, LEAD, NICKEL, COTTON.
        Example: get_commodity_price("GOLD")"""
        return await mcx.get_commodity_price(commodity)

    @mcp.tool()
    async def get_all_commodity_prices() -> list[dict]:
        """Get live prices for all supported commodities."""
        return await mcx.get_all_commodities()

    @mcp.tool()
    async def get_commodity_history(commodity: str, period: str = "1mo") -> dict:
        """Get historical price data for a commodity.
        Periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max.
        Example: get_commodity_history("GOLD", "6mo")"""
        return await mcx.get_commodity_history(commodity, period)
