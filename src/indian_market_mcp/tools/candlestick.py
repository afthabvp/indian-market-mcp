from __future__ import annotations

import yfinance as yf
import pandas as pd
from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP):

    def _get_df(symbol: str, period: str = "3mo") -> pd.DataFrame:
        ticker = yf.Ticker(f"{symbol.upper()}.NS")
        return ticker.history(period=period)

    def _detect_patterns(df: pd.DataFrame) -> list[dict]:
        if len(df) < 3:
            return []

        patterns = []
        for i in range(2, len(df)):
            o = df["Open"].iloc[i]
            h = df["High"].iloc[i]
            l = df["Low"].iloc[i]
            c = df["Close"].iloc[i]
            date = df.index[i].strftime("%Y-%m-%d")

            prev_o = df["Open"].iloc[i - 1]
            prev_c = df["Close"].iloc[i - 1]
            prev_h = df["High"].iloc[i - 1]
            prev_l = df["Low"].iloc[i - 1]

            body = abs(c - o)
            upper_shadow = h - max(o, c)
            lower_shadow = min(o, c) - l
            total_range = h - l

            if total_range == 0:
                continue

            prev_body = abs(prev_c - prev_o)

            # Doji
            if body < total_range * 0.1:
                patterns.append({"date": date, "pattern": "Doji", "signal": "Neutral/Reversal"})

            # Hammer (bullish)
            if lower_shadow > body * 2 and upper_shadow < body * 0.5 and c > o:
                patterns.append({"date": date, "pattern": "Hammer", "signal": "Bullish"})

            # Inverted Hammer
            if upper_shadow > body * 2 and lower_shadow < body * 0.5 and c > o:
                patterns.append({"date": date, "pattern": "Inverted Hammer", "signal": "Bullish"})

            # Hanging Man (bearish)
            if lower_shadow > body * 2 and upper_shadow < body * 0.5 and c < o:
                patterns.append({"date": date, "pattern": "Hanging Man", "signal": "Bearish"})

            # Shooting Star
            if upper_shadow > body * 2 and lower_shadow < body * 0.5 and c < o:
                patterns.append({"date": date, "pattern": "Shooting Star", "signal": "Bearish"})

            # Bullish Engulfing
            if prev_c < prev_o and c > o and o <= prev_c and c >= prev_o and body > prev_body:
                patterns.append({"date": date, "pattern": "Bullish Engulfing", "signal": "Bullish"})

            # Bearish Engulfing
            if prev_c > prev_o and c < o and o >= prev_c and c <= prev_o and body > prev_body:
                patterns.append({"date": date, "pattern": "Bearish Engulfing", "signal": "Bearish"})

            # Morning Star (3 candle)
            if i >= 2:
                pp_o = df["Open"].iloc[i - 2]
                pp_c = df["Close"].iloc[i - 2]
                pp_body = abs(pp_c - pp_o)
                if pp_c < pp_o and pp_body > total_range * 0.5 and prev_body < pp_body * 0.3 and c > o and body > pp_body * 0.5:
                    patterns.append({"date": date, "pattern": "Morning Star", "signal": "Bullish"})

            # Evening Star (3 candle)
            if i >= 2:
                pp_o = df["Open"].iloc[i - 2]
                pp_c = df["Close"].iloc[i - 2]
                pp_body = abs(pp_c - pp_o)
                if pp_c > pp_o and pp_body > total_range * 0.5 and prev_body < pp_body * 0.3 and c < o and body > pp_body * 0.5:
                    patterns.append({"date": date, "pattern": "Evening Star", "signal": "Bearish"})

            # Marubozu (strong candle, no shadows)
            if upper_shadow < body * 0.05 and lower_shadow < body * 0.05:
                signal = "Bullish" if c > o else "Bearish"
                patterns.append({"date": date, "pattern": f"{signal} Marubozu", "signal": signal})

            # Three White Soldiers
            if i >= 2:
                pp_o = df["Open"].iloc[i - 2]
                pp_c = df["Close"].iloc[i - 2]
                if pp_c > pp_o and prev_c > prev_o and c > o and c > prev_c and prev_c > pp_c:
                    patterns.append({"date": date, "pattern": "Three White Soldiers", "signal": "Bullish"})

            # Three Black Crows
            if i >= 2:
                pp_o = df["Open"].iloc[i - 2]
                pp_c = df["Close"].iloc[i - 2]
                if pp_c < pp_o and prev_c < prev_o and c < o and c < prev_c and prev_c < pp_c:
                    patterns.append({"date": date, "pattern": "Three Black Crows", "signal": "Bearish"})

        return patterns

    @mcp.tool()
    async def detect_candlestick_patterns(symbol: str, period: str = "3mo") -> dict:
        """Detect candlestick patterns for a stock — Doji, Hammer, Engulfing, Morning Star, Evening Star, Marubozu, Three White Soldiers, Three Black Crows, and more.
        Periods: 1mo, 3mo, 6mo, 1y.
        Example: detect_candlestick_patterns("RELIANCE", "3mo")"""
        df = _get_df(symbol, period)
        if df.empty:
            return {"error": f"No data found for {symbol}"}

        patterns = _detect_patterns(df)

        recent = patterns[-20:] if len(patterns) > 20 else patterns

        bullish = sum(1 for p in recent if p["signal"] == "Bullish")
        bearish = sum(1 for p in recent if p["signal"] == "Bearish")

        return {
            "symbol": symbol.upper(),
            "period": period,
            "total_patterns_found": len(patterns),
            "recent_patterns": recent,
            "summary": {
                "bullish_signals": bullish,
                "bearish_signals": bearish,
                "bias": "Bullish" if bullish > bearish else "Bearish" if bearish > bullish else "Neutral",
            },
        }

    @mcp.tool()
    async def scan_patterns_bulk(
        symbols: list[str],
        pattern_filter: str = "",
    ) -> list[dict]:
        """Scan multiple stocks for candlestick patterns. Optionally filter by pattern name.
        Example: scan_patterns_bulk(["RELIANCE", "TCS", "INFY"], "Bullish Engulfing")"""
        results = []
        for sym in symbols[:20]:
            try:
                df = _get_df(sym, "1mo")
                if df.empty:
                    continue
                patterns = _detect_patterns(df)
                if pattern_filter:
                    patterns = [p for p in patterns if pattern_filter.lower() in p["pattern"].lower()]
                if patterns:
                    results.append({
                        "symbol": sym.upper(),
                        "latest_pattern": patterns[-1],
                        "pattern_count": len(patterns),
                    })
            except Exception:
                continue
        return results
