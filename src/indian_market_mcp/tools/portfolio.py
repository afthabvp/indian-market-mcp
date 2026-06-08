from __future__ import annotations

import os
from mcp.server.fastmcp import FastMCP


def _get_broker():
    if os.environ.get("ANGEL_API_KEY"):
        return "angel"
    if os.environ.get("KITE_API_KEY"):
        return "zerodha"
    return None


def register(mcp: FastMCP):

    @mcp.tool()
    async def get_holdings() -> dict:
        """Get your portfolio holdings — all stocks you own with buy price, current price, and P&L.
        Requires broker credentials."""
        broker = _get_broker()
        if not broker:
            return {"error": "No broker configured. Set ANGEL_API_KEY or KITE_API_KEY env vars."}

        if broker == "angel":
            from ..sources.broker import angel
            return await angel.get_holdings()
        else:
            from ..sources.broker import zerodha
            return await zerodha.get_holdings()

    @mcp.tool()
    async def get_positions() -> dict:
        """Get open positions — intraday and overnight positions with live P&L.
        Requires broker credentials."""
        broker = _get_broker()
        if not broker:
            return {"error": "No broker configured."}

        if broker == "angel":
            from ..sources.broker import angel
            return await angel.get_positions()
        else:
            from ..sources.broker import zerodha
            return await zerodha.get_positions()

    @mcp.tool()
    async def get_margins() -> dict:
        """Get available margins — cash balance, used margin, and available margin for trading.
        Requires broker credentials."""
        broker = _get_broker()
        if not broker:
            return {"error": "No broker configured."}

        if broker == "angel":
            from ..sources.broker import angel
            return await angel.get_margin()
        else:
            from ..sources.broker import zerodha
            return await zerodha.get_margins()

    @mcp.tool()
    async def get_broker_profile() -> dict:
        """Get your broker account profile — name, client ID, email, registered exchanges.
        Requires broker credentials."""
        broker = _get_broker()
        if not broker:
            return {"error": "No broker configured."}

        if broker == "angel":
            from ..sources.broker import angel
            return await angel.get_profile()
        else:
            from ..sources.broker import zerodha
            return await zerodha.get_profile()
