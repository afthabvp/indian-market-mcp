from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from ..sources import nse


def register(mcp: FastMCP):

    @mcp.tool()
    async def get_market_status() -> dict:
        """Get current market status — open, closed, or pre-market for all segments (equity, derivatives, currency)."""
        return await nse.get_market_status()

    @mcp.tool()
    async def get_fii_dii_data() -> dict:
        """Get Foreign Institutional Investor (FII) and Domestic Institutional Investor (DII) buy/sell data for today."""
        return await nse.get_fii_dii()

    @mcp.tool()
    async def get_advances_declines() -> dict:
        """Get market breadth — number of advancing, declining, and unchanged stocks."""
        return await nse.get_advances_declines()
