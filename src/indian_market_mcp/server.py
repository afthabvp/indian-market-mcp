from __future__ import annotations

import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Indian Market MCP")

from .tools import stocks, derivatives, indices, mutual_funds, etfs
from .tools import commodities, currency, ipo, bonds, market, technicals
from .tools import screener, news, financials, candlestick, shareholding

stocks.register(mcp)
derivatives.register(mcp)
indices.register(mcp)
mutual_funds.register(mcp)
etfs.register(mcp)
commodities.register(mcp)
currency.register(mcp)
ipo.register(mcp)
bonds.register(mcp)
market.register(mcp)
technicals.register(mcp)
screener.register(mcp)
news.register(mcp)
financials.register(mcp)
candlestick.register(mcp)
shareholding.register(mcp)

if os.environ.get("ANGEL_API_KEY") or os.environ.get("KITE_API_KEY"):
    from .tools import trading, portfolio, market_depth
    trading.register(mcp)
    portfolio.register(mcp)
    market_depth.register(mcp)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
