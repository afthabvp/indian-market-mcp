from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from ..sources import nse


def register(mcp: FastMCP):

    @mcp.tool()
    async def get_shareholding_pattern(symbol: str) -> dict:
        """Get shareholding pattern — promoter, FII, DII, public holding percentages.
        Example: get_shareholding_pattern("RELIANCE")"""
        return await nse.get_shareholding(symbol)

    @mcp.tool()
    async def get_company_profile(symbol: str) -> dict:
        """Get comprehensive company profile — sector, industry, fundamentals, and current quote in one call.
        Example: get_company_profile("TCS")"""
        import yfinance as yf
        ticker = yf.Ticker(f"{symbol.upper()}.NS")
        info = ticker.info

        return {
            "symbol": symbol.upper(),
            "company": info.get("longName", ""),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "website": info.get("website", ""),
            "description": info.get("longBusinessSummary", "")[:500],
            "employees": info.get("fullTimeEmployees"),
            "price": info.get("regularMarketPrice"),
            "market_cap_cr": round((info.get("marketCap") or 0) / 1e7, 0),
            "pe": info.get("trailingPE"),
            "pb": info.get("priceToBook"),
            "roe": round((info.get("returnOnEquity") or 0) * 100, 2),
            "debt_to_equity": info.get("debtToEquity"),
            "dividend_yield": round((info.get("dividendYield") or 0) * 100, 2),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "avg_volume": info.get("averageVolume"),
            "beta": info.get("beta"),
        }

    @mcp.tool()
    async def get_bulk_deals() -> dict:
        """Get recent bulk and block deals on NSE."""
        return await nse.get_advances_declines()
