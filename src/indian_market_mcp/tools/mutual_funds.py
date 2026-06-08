from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from ..sources import amfi


def register(mcp: FastMCP):

    @mcp.tool()
    async def search_mutual_funds(query: str) -> list[dict]:
        """Search mutual funds by name, AMC, or category.
        Example: search_mutual_funds("SBI Bluechip") or search_mutual_funds("axis flexi cap")"""
        return await amfi.search_funds(query)

    @mcp.tool()
    async def get_mf_nav(scheme_code: str) -> dict:
        """Get latest NAV for a mutual fund by scheme code.
        Example: get_mf_nav("119598")"""
        return await amfi.get_fund_nav(scheme_code)

    @mcp.tool()
    async def get_mf_history(
        scheme_code: str,
        from_date: str = "",
        to_date: str = "",
    ) -> dict:
        """Get historical NAV data for a mutual fund. Dates in YYYY-MM-DD format.
        Returns full history if no dates specified.
        Example: get_mf_history("119598", "2025-01-01", "2025-06-01")"""
        if from_date and to_date:
            return await amfi.get_fund_history_range(scheme_code, from_date, to_date)
        return await amfi.get_fund_history(scheme_code)

    @mcp.tool()
    async def get_mf_categories() -> list[str]:
        """Get all mutual fund categories — Equity, Debt, Hybrid, Solution Oriented etc."""
        return await amfi.get_fund_categories()

    @mcp.tool()
    async def compare_mutual_funds(scheme_codes: list[str]) -> list[dict]:
        """Compare multiple mutual funds side by side. Pass a list of scheme codes.
        Example: compare_mutual_funds(["119598", "120503"])"""
        results = []
        for code in scheme_codes[:5]:
            nav_data = await amfi.get_fund_nav(code)
            history = await amfi.get_fund_history(code)

            meta = nav_data.get("meta", {})
            data_points = history.get("data", [])

            current_nav = float(data_points[0]["nav"]) if data_points else 0
            returns = {}
            period_map = {"1M": 22, "3M": 66, "6M": 132, "1Y": 252}
            for label, days in period_map.items():
                if len(data_points) > days:
                    old_nav = float(data_points[days]["nav"])
                    if old_nav:
                        returns[label] = round(((current_nav - old_nav) / old_nav) * 100, 2)

            results.append({
                "scheme_code": code,
                "fund_name": meta.get("scheme_name", ""),
                "fund_house": meta.get("fund_house", ""),
                "scheme_type": meta.get("scheme_type", ""),
                "current_nav": current_nav,
                "returns": returns,
            })
        return results

    @mcp.tool()
    async def get_top_funds_by_category(category: str, limit: int = 10) -> list[dict]:
        """Get top mutual funds in a category.
        Example: get_top_funds_by_category("Equity Scheme")"""
        all_navs = await amfi.get_all_navs()
        cat_lower = category.lower()
        filtered = [f for f in all_navs if cat_lower in f["category"].lower()]
        return filtered[:limit]
