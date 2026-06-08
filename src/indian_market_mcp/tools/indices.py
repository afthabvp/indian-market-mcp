from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from ..sources import nse


def register(mcp: FastMCP):

    @mcp.tool()
    async def get_index(name: str) -> dict:
        """Get live data for an NSE index — value, change, advances/declines.
        Common indices: NIFTY 50, NIFTY BANK, NIFTY NEXT 50, NIFTY IT, NIFTY FINANCIAL SERVICES.
        Example: get_index("NIFTY 50")"""
        data = await nse.get_index_data(name)
        metadata = data.get("metadata", {})
        advance = data.get("advance", {})
        return {
            "index": name,
            "last": metadata.get("last"),
            "open": metadata.get("open"),
            "high": metadata.get("high"),
            "low": metadata.get("low"),
            "previous_close": metadata.get("previousClose"),
            "change": metadata.get("change"),
            "change_percent": metadata.get("percChange"),
            "advances": advance.get("advances"),
            "declines": advance.get("declines"),
            "unchanged": advance.get("unchanged"),
            "constituents_count": len(data.get("data", [])),
        }

    @mcp.tool()
    async def get_index_constituents(name: str) -> list[dict]:
        """Get all stocks in an index with their live prices.
        Example: get_index_constituents("NIFTY 50")"""
        data = await nse.get_index_data(name)
        stocks = []
        for s in data.get("data", []):
            stocks.append({
                "symbol": s.get("symbol"),
                "company": s.get("meta", {}).get("companyName", ""),
                "last_price": s.get("lastPrice"),
                "change": s.get("change"),
                "change_percent": s.get("pChange"),
                "day_high": s.get("dayHigh"),
                "day_low": s.get("dayLow"),
            })
        return stocks

    @mcp.tool()
    async def get_all_indices() -> list[dict]:
        """Get all NSE indices with current values — Nifty 50, Bank Nifty, sectoral indices etc."""
        data = await nse.get_all_indices()
        indices = []
        for idx in data.get("data", []):
            indices.append({
                "index": idx.get("index"),
                "last": idx.get("last"),
                "change": idx.get("variation"),
                "change_percent": idx.get("percentChange"),
                "open": idx.get("open"),
                "high": idx.get("high"),
                "low": idx.get("low"),
                "previous_close": idx.get("previousClose"),
            })
        return indices

    @mcp.tool()
    async def get_index_history(
        index: str,
        from_date: str = "",
        to_date: str = "",
    ) -> dict:
        """Get historical data for an NSE index. Dates in DD-MM-YYYY format.
        Example: get_index_history("NIFTY 50", "01-01-2025", "01-06-2025")"""
        return await nse.get_index_historical(index, from_date, to_date)

    @mcp.tool()
    async def get_sector_performance() -> list[dict]:
        """Get performance of all sectoral indices — IT, Bank, Pharma, Auto, FMCG etc."""
        data = await nse.get_sector_performance()
        sectors = []
        for idx in data.get("data", []):
            name = idx.get("index", "")
            if "NIFTY" in name.upper():
                sectors.append({
                    "sector": name,
                    "last": idx.get("last"),
                    "change_percent": idx.get("percentChange"),
                })
        return sorted(sectors, key=lambda x: float(x.get("change_percent") or 0), reverse=True)
