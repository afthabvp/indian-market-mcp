from __future__ import annotations

import yfinance as yf
from mcp.server.fastmcp import FastMCP
from ..sources import nse


def _safe_dict(df) -> list[dict]:
    if df is None or df.empty:
        return []
    records = []
    for col in df.columns:
        entry = {"period": col.strftime("%Y-%m-%d") if hasattr(col, "strftime") else str(col)}
        for idx in df.index:
            val = df.at[idx, col]
            if hasattr(val, "item"):
                val = val.item()
            entry[str(idx)] = val
        records.append(entry)
    return records


def register(mcp: FastMCP):

    @mcp.tool()
    async def get_income_statement(symbol: str, quarterly: bool = False) -> dict:
        """Get income statement (P&L) — revenue, expenses, net income, EPS.
        Set quarterly=True for quarterly results.
        Example: get_income_statement("TCS") or get_income_statement("RELIANCE", quarterly=True)"""
        ticker = yf.Ticker(f"{symbol.upper()}.NS")
        if quarterly:
            data = _safe_dict(ticker.quarterly_income_stmt)
        else:
            data = _safe_dict(ticker.income_stmt)
        return {"symbol": symbol.upper(), "quarterly": quarterly, "data": data}

    @mcp.tool()
    async def get_balance_sheet(symbol: str, quarterly: bool = False) -> dict:
        """Get balance sheet — assets, liabilities, equity, debt.
        Example: get_balance_sheet("INFY")"""
        ticker = yf.Ticker(f"{symbol.upper()}.NS")
        if quarterly:
            data = _safe_dict(ticker.quarterly_balance_sheet)
        else:
            data = _safe_dict(ticker.balance_sheet)
        return {"symbol": symbol.upper(), "quarterly": quarterly, "data": data}

    @mcp.tool()
    async def get_cash_flow(symbol: str, quarterly: bool = False) -> dict:
        """Get cash flow statement — operating, investing, financing cash flows.
        Example: get_cash_flow("HDFCBANK")"""
        ticker = yf.Ticker(f"{symbol.upper()}.NS")
        if quarterly:
            data = _safe_dict(ticker.quarterly_cashflow)
        else:
            data = _safe_dict(ticker.cashflow)
        return {"symbol": symbol.upper(), "quarterly": quarterly, "data": data}

    @mcp.tool()
    async def get_key_ratios(symbol: str) -> dict:
        """Get key financial ratios — PE, PB, ROE, ROCE, debt/equity, dividend yield, EPS, market cap.
        Example: get_key_ratios("RELIANCE")"""
        ticker = yf.Ticker(f"{symbol.upper()}.NS")
        info = ticker.info
        return {
            "symbol": symbol.upper(),
            "company": info.get("shortName", ""),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "market_cap_cr": round((info.get("marketCap") or 0) / 1e7, 0),
            "enterprise_value_cr": round((info.get("enterpriseValue") or 0) / 1e7, 0),
            "pe_trailing": info.get("trailingPE"),
            "pe_forward": info.get("forwardPE"),
            "pb": info.get("priceToBook"),
            "ps": info.get("priceToSalesTrailing12Months"),
            "peg": info.get("pegRatio"),
            "ev_ebitda": info.get("enterpriseToEbitda"),
            "roe": round((info.get("returnOnEquity") or 0) * 100, 2),
            "roa": round((info.get("returnOnAssets") or 0) * 100, 2),
            "debt_to_equity": info.get("debtToEquity"),
            "current_ratio": info.get("currentRatio"),
            "quick_ratio": info.get("quickRatio"),
            "eps_trailing": info.get("trailingEps"),
            "eps_forward": info.get("forwardEps"),
            "dividend_yield": round((info.get("dividendYield") or 0) * 100, 2),
            "dividend_per_share": info.get("dividendRate"),
            "payout_ratio": round((info.get("payoutRatio") or 0) * 100, 2),
            "revenue_growth": round((info.get("revenueGrowth") or 0) * 100, 2),
            "earnings_growth": round((info.get("earningsGrowth") or 0) * 100, 2),
            "profit_margin": round((info.get("profitMargins") or 0) * 100, 2),
            "operating_margin": round((info.get("operatingMargins") or 0) * 100, 2),
            "gross_margin": round((info.get("grossMargins") or 0) * 100, 2),
            "beta": info.get("beta"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "avg_volume": info.get("averageVolume"),
            "shares_outstanding": info.get("sharesOutstanding"),
            "float_shares": info.get("floatShares"),
            "book_value": info.get("bookValue"),
        }

    @mcp.tool()
    async def get_peer_comparison(symbol: str) -> list[dict]:
        """Compare a stock with its industry peers — PE, PB, market cap, ROE side by side.
        Example: get_peer_comparison("TCS")"""
        ticker = yf.Ticker(f"{symbol.upper()}.NS")
        info = ticker.info
        industry = info.get("industry", "")
        sector = info.get("sector", "")

        data = await nse.get_nifty500_list()
        stocks = data.get("data", [])

        peers = []
        for s in stocks:
            sym = s.get("symbol", "")
            if sym == symbol.upper():
                continue
            try:
                t = yf.Ticker(f"{sym}.NS")
                i = t.info
                if i.get("industry") == industry or i.get("sector") == sector:
                    peers.append({
                        "symbol": sym,
                        "company": i.get("shortName", ""),
                        "price": i.get("regularMarketPrice"),
                        "pe": i.get("trailingPE"),
                        "pb": i.get("priceToBook"),
                        "market_cap_cr": round((i.get("marketCap") or 0) / 1e7, 0),
                        "roe": round((i.get("returnOnEquity") or 0) * 100, 2),
                        "debt_to_equity": i.get("debtToEquity"),
                    })
            except Exception:
                continue
            if len(peers) >= 8:
                break

        return peers

    @mcp.tool()
    async def get_nse_financial_results(symbol: str) -> dict:
        """Get quarterly/annual financial results filed with NSE.
        Example: get_nse_financial_results("RELIANCE")"""
        return await nse.get_financial_results(symbol)
