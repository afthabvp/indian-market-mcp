from __future__ import annotations

import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "Indian Market MCP",
    host=os.environ.get("MCP_HOST", "0.0.0.0"),
    port=int(os.environ.get("MCP_PORT", "8000")),
)

from .tools import stocks, derivatives, indices, mutual_funds, etfs
from .tools import commodities, currency, ipo, bonds, market, technicals
from .tools import screener, news, financials, candlestick, shareholding, mf_analysis

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
mf_analysis.register(mcp)

if os.environ.get("ANGEL_API_KEY") or os.environ.get("KITE_API_KEY"):
    from .tools import trading, portfolio, market_depth
    trading.register(mcp)
    portfolio.register(mcp)
    market_depth.register(mcp)


def main():
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
