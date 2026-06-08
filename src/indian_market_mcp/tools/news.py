from __future__ import annotations

import httpx
from xml.etree import ElementTree
from mcp.server.fastmcp import FastMCP
from ..sources import nse
from ..sources.cache import cached


GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"


def register(mcp: FastMCP):

    @cached(ttl=300)
    async def _fetch_google_news(query: str, limit: int = 10) -> list[dict]:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                GOOGLE_NEWS_RSS,
                params={"q": query, "hl": "en-IN", "gl": "IN", "ceid": "IN:en"},
            )
            resp.raise_for_status()

        root = ElementTree.fromstring(resp.text)
        items = root.findall(".//item")
        results = []
        for item in items[:limit]:
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub_date = item.findtext("pubDate", "")
            source = item.findtext("source", "")
            results.append({
                "title": title,
                "link": link,
                "published": pub_date,
                "source": source,
            })
        return results

    @mcp.tool()
    async def get_market_news(limit: int = 10) -> list[dict]:
        """Get latest Indian stock market news from Google News.
        Example: get_market_news(15)"""
        return await _fetch_google_news("Indian stock market NSE BSE", limit)

    @mcp.tool()
    async def get_stock_news(symbol: str, limit: int = 10) -> list[dict]:
        """Get latest news for a specific stock.
        Example: get_stock_news("RELIANCE", 10)"""
        return await _fetch_google_news(f"{symbol} NSE stock", limit)

    @mcp.tool()
    async def get_sector_news(sector: str, limit: int = 10) -> list[dict]:
        """Get latest news for a sector — IT, Banking, Pharma, Auto, FMCG etc.
        Example: get_sector_news("Banking", 10)"""
        return await _fetch_google_news(f"India {sector} sector stocks", limit)

    @mcp.tool()
    async def get_nse_announcements(symbol: str = "") -> dict:
        """Get official NSE corporate announcements/filings.
        If symbol is provided, get announcements for that stock.
        Otherwise get latest announcements across all stocks.
        Example: get_nse_announcements("TCS")"""
        return await nse.get_announcements(symbol=symbol)

    @mcp.tool()
    async def get_board_meetings(symbol: str) -> dict:
        """Get upcoming and past board meeting dates for a stock.
        Example: get_board_meetings("RELIANCE")"""
        return await nse.get_board_meetings(symbol)
