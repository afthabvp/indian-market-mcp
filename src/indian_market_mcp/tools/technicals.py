from __future__ import annotations

import pandas as pd
import yfinance as yf
from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP):

    def _get_df(symbol: str, period: str = "6mo") -> pd.DataFrame:
        nse_symbol = f"{symbol.upper()}.NS"
        ticker = yf.Ticker(nse_symbol)
        df = ticker.history(period=period)
        return df

    @mcp.tool()
    async def get_technical_indicators(symbol: str, period: str = "6mo") -> dict:
        """Get key technical indicators for an NSE stock — SMA, EMA, RSI, MACD, Bollinger Bands, VWAP.
        Periods: 1mo, 3mo, 6mo, 1y, 2y.
        Example: get_technical_indicators("RELIANCE", "6mo")"""
        df = _get_df(symbol, period)
        if df.empty:
            return {"error": f"No data found for {symbol}"}

        close = df["Close"]

        sma_20 = close.rolling(20).mean()
        sma_50 = close.rolling(50).mean()
        sma_200 = close.rolling(200).mean()

        ema_12 = close.ewm(span=12).mean()
        ema_26 = close.ewm(span=26).mean()
        ema_50 = close.ewm(span=50).mean()

        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9).mean()
        macd_hist = macd_line - signal_line

        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        bb_mid = sma_20
        bb_std = close.rolling(20).std()
        bb_upper = bb_mid + (2 * bb_std)
        bb_lower = bb_mid - (2 * bb_std)

        vwap = None
        if "Volume" in df.columns:
            typical_price = (df["High"] + df["Low"] + df["Close"]) / 3
            vwap_val = (typical_price * df["Volume"]).cumsum() / df["Volume"].cumsum()
            vwap = round(float(vwap_val.iloc[-1]), 2)

        last = close.iloc[-1]

        return {
            "symbol": symbol.upper(),
            "price": round(float(last), 2),
            "sma": {
                "sma_20": round(float(sma_20.iloc[-1]), 2) if not sma_20.empty else None,
                "sma_50": round(float(sma_50.iloc[-1]), 2) if not sma_50.empty else None,
                "sma_200": round(float(sma_200.iloc[-1]), 2) if len(sma_200.dropna()) > 0 else None,
            },
            "ema": {
                "ema_12": round(float(ema_12.iloc[-1]), 2),
                "ema_26": round(float(ema_26.iloc[-1]), 2),
                "ema_50": round(float(ema_50.iloc[-1]), 2),
            },
            "rsi_14": round(float(rsi.iloc[-1]), 2) if not rsi.empty else None,
            "macd": {
                "macd_line": round(float(macd_line.iloc[-1]), 2),
                "signal_line": round(float(signal_line.iloc[-1]), 2),
                "histogram": round(float(macd_hist.iloc[-1]), 2),
            },
            "bollinger_bands": {
                "upper": round(float(bb_upper.iloc[-1]), 2) if not bb_upper.empty else None,
                "middle": round(float(bb_mid.iloc[-1]), 2) if not bb_mid.empty else None,
                "lower": round(float(bb_lower.iloc[-1]), 2) if not bb_lower.empty else None,
            },
            "vwap": vwap,
            "trend": "Bullish" if last > float(sma_50.iloc[-1] if not sma_50.empty else last) else "Bearish",
            "rsi_signal": "Overbought" if (rsi.iloc[-1] if not rsi.empty else 50) > 70 else "Oversold" if (rsi.iloc[-1] if not rsi.empty else 50) < 30 else "Neutral",
        }

    @mcp.tool()
    async def get_support_resistance(symbol: str, period: str = "3mo") -> dict:
        """Get support and resistance levels for a stock based on pivot points.
        Example: get_support_resistance("RELIANCE")"""
        df = _get_df(symbol, period)
        if df.empty:
            return {"error": f"No data found for {symbol}"}

        high = float(df["High"].iloc[-1])
        low = float(df["Low"].iloc[-1])
        close = float(df["Close"].iloc[-1])

        pivot = (high + low + close) / 3
        r1 = 2 * pivot - low
        s1 = 2 * pivot - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        r3 = high + 2 * (pivot - low)
        s3 = low - 2 * (high - pivot)

        return {
            "symbol": symbol.upper(),
            "pivot": round(pivot, 2),
            "resistance": {"R1": round(r1, 2), "R2": round(r2, 2), "R3": round(r3, 2)},
            "support": {"S1": round(s1, 2), "S2": round(s2, 2), "S3": round(s3, 2)},
        }
