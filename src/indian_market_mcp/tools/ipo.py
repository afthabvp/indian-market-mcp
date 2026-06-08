from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from ..sources import nse


def register(mcp: FastMCP):

    @mcp.tool()
    async def get_upcoming_ipos() -> dict:
        """Get all upcoming and ongoing IPOs on NSE with dates, price band, and issue size."""
        return await nse.get_ipo_current()

    @mcp.tool()
    async def get_past_ipos() -> dict:
        """Get recently listed IPOs with listing price and performance."""
        return await nse.get_ipo_past()
