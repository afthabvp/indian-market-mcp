from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from ..sources import nse


def register(mcp: FastMCP):

    @mcp.tool()
    async def get_option_chain(symbol: str, is_index: bool = True) -> dict:
        """Get full option chain for an index or stock — strike prices, premiums, OI, change in OI, IV.
        For indices: NIFTY, BANKNIFTY, FINNIFTY. For stocks: any NSE symbol.
        Example: get_option_chain("NIFTY") or get_option_chain("RELIANCE", is_index=False)"""
        if is_index:
            data = await nse.get_option_chain_index(symbol)
        else:
            data = await nse.get_option_chain_equity(symbol)

        records = data.get("records", {})
        filtered = data.get("filtered", {})
        return {
            "symbol": symbol.upper(),
            "expiry_dates": records.get("expiryDates", []),
            "underlying_value": records.get("underlyingValue"),
            "strikePrices": records.get("strikePrices", []),
            "total_ce_oi": filtered.get("CE", {}).get("totOI"),
            "total_pe_oi": filtered.get("PE", {}).get("totOI"),
            "total_ce_volume": filtered.get("CE", {}).get("totVol"),
            "total_pe_volume": filtered.get("PE", {}).get("totVol"),
            "data": filtered.get("data", [])[:50],
        }

    @mcp.tool()
    async def get_pcr(symbol: str) -> dict:
        """Get Put-Call Ratio for an index.
        Example: get_pcr("NIFTY")"""
        data = await nse.get_option_chain_index(symbol)
        filtered = data.get("filtered", {})
        ce_oi = filtered.get("CE", {}).get("totOI", 0)
        pe_oi = filtered.get("PE", {}).get("totOI", 0)
        pcr = round(pe_oi / ce_oi, 4) if ce_oi else 0
        return {
            "symbol": symbol.upper(),
            "pcr": pcr,
            "total_ce_oi": ce_oi,
            "total_pe_oi": pe_oi,
            "interpretation": "Bullish" if pcr > 1 else "Bearish" if pcr < 0.7 else "Neutral",
        }

    @mcp.tool()
    async def get_max_pain(symbol: str) -> dict:
        """Calculate max pain strike price for an index option.
        Max pain is the strike price where option writers (sellers) face minimum losses.
        Example: get_max_pain("NIFTY")"""
        data = await nse.get_option_chain_index(symbol)
        records = data.get("filtered", {}).get("data", [])
        if not records:
            return {"error": "No option chain data available"}

        strikes = {}
        for row in records:
            ce = row.get("CE", {})
            pe = row.get("PE", {})
            strike = row.get("strikePrice")
            if strike:
                strikes[strike] = {
                    "ce_oi": ce.get("openInterest", 0),
                    "pe_oi": pe.get("openInterest", 0),
                }

        min_pain = float("inf")
        max_pain_strike = 0

        for target_strike in strikes:
            total_pain = 0
            for strike, oi_data in strikes.items():
                ce_pain = max(0, target_strike - strike) * oi_data["ce_oi"]
                pe_pain = max(0, strike - target_strike) * oi_data["pe_oi"]
                total_pain += ce_pain + pe_pain
            if total_pain < min_pain:
                min_pain = total_pain
                max_pain_strike = target_strike

        return {
            "symbol": symbol.upper(),
            "max_pain_strike": max_pain_strike,
            "underlying": data.get("records", {}).get("underlyingValue"),
        }

    @mcp.tool()
    async def get_futures_data(symbol: str) -> dict:
        """Get futures data — lot size, expiry, OI, price for a stock or index.
        Example: get_futures_data("NIFTY") or get_futures_data("RELIANCE")"""
        data = await nse.get_quote_derivative(symbol)
        stocks = data.get("stocks", [])
        futures = [s for s in stocks if s.get("metadata", {}).get("instrumentType") in ("Stock Futures", "Index Futures")]
        result = []
        for f in futures[:6]:
            meta = f.get("metadata", {})
            market = f.get("marketDeptOrderBook", {}).get("tradeInfo", {})
            result.append({
                "expiry": meta.get("expiryDate"),
                "last_price": meta.get("lastPrice"),
                "change": meta.get("change"),
                "change_percent": meta.get("pChange"),
                "open_interest": market.get("openInterest"),
                "change_in_oi": market.get("changeinOpenInterest"),
                "lot_size": meta.get("marketLot"),
            })
        return {"symbol": symbol.upper(), "futures": result}

    @mcp.tool()
    async def get_oi_data(symbol: str) -> dict:
        """Get Open Interest data for all expiries of a derivative.
        Example: get_oi_data("NIFTY")"""
        data = await nse.get_quote_derivative(symbol)
        stocks = data.get("stocks", [])
        result = []
        for s in stocks:
            meta = s.get("metadata", {})
            trade = s.get("marketDeptOrderBook", {}).get("tradeInfo", {})
            result.append({
                "instrument": meta.get("instrumentType"),
                "expiry": meta.get("expiryDate"),
                "strike": meta.get("strikePrice"),
                "option_type": meta.get("optionType"),
                "last_price": meta.get("lastPrice"),
                "oi": trade.get("openInterest"),
                "change_in_oi": trade.get("changeinOpenInterest"),
                "volume": trade.get("noOfTrades"),
            })
        return {"symbol": symbol.upper(), "data": result}
