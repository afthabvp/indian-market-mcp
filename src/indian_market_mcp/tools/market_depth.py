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
    async def get_market_depth(symbol: str, exchange: str = "NSE", token: str = "") -> dict:
        """Get Level 2/3 market depth — top 5 or 20 bid/ask orders with quantities.
        Requires broker credentials for full depth.
        - exchange: NSE, BSE, MCX
        Example: get_market_depth("RELIANCE", "NSE")"""
        broker = _get_broker()
        if not broker:
            return {"error": "No broker configured. Set ANGEL_API_KEY or KITE_API_KEY env vars for market depth."}

        if broker == "angel":
            from ..sources.broker import angel
            if not token:
                return {"error": "Angel One requires symbol token. Use search_stocks to find it."}
            return await angel.get_market_depth(exchange, symbol, token)
        else:
            from ..sources.broker import zerodha
            instrument = f"{exchange}:{symbol.upper()}"
            return await zerodha.get_market_depth([instrument])

    @mcp.tool()
    async def get_ltp(symbol: str, exchange: str = "NSE", token: str = "") -> dict:
        """Get Last Traded Price via broker API (faster than NSE scraping).
        Requires broker credentials.
        Example: get_ltp("RELIANCE", "NSE")"""
        broker = _get_broker()
        if not broker:
            return {"error": "No broker configured."}

        if broker == "angel":
            from ..sources.broker import angel
            if not token:
                return {"error": "Angel One requires symbol token."}
            return await angel.get_ltp(exchange, symbol, token)
        else:
            from ..sources.broker import zerodha
            instrument = f"{exchange}:{symbol.upper()}"
            return await zerodha.get_ltp([instrument])
