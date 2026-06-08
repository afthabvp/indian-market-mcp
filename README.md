<p align="center">
  <h1 align="center">Indian Market MCP</h1>
  <p align="center">
    The most comprehensive <a href="https://modelcontextprotocol.io">Model Context Protocol</a> server for the Indian stock market.
    <br />
    <strong>68 tools. Zero API keys. One install.</strong>
  </p>
  <p align="center">
    <a href="#quick-start">Quick Start</a> &bull;
    <a href="#all-63-tools">All Tools</a> &bull;
    <a href="#broker-mode">Broker Mode</a> &bull;
    <a href="#remote-http-server">Deploy</a> &bull;
    <a href="#examples">Examples</a>
  </p>
</p>

---

Covers **NSE, BSE, MCX, Mutual Funds, F&O, ETFs, IPOs, Sovereign Gold Bonds, Commodities, Currency, Technical Analysis, Stock Screener, Company Financials, Candlestick Patterns, News & Sentiment** — plus optional broker integration for live trading via Angel One or Zerodha.

### Why this over other Indian market MCPs?

| Feature | indian-market-mcp | Tapetide | bshada/nse-bse | NseKit | Zerodha Official |
|---|:---:|:---:|:---:|:---:|:---:|
| Total tools | **63** | 26 | 60 | 100+ | ~20 |
| API key required | **No** | No | No | No | Yes |
| Stocks + History | **Yes** | Yes | Yes | Yes | Yes |
| F&O / Option Chain | **Yes** | No | Yes | Yes | No |
| PCR + Max Pain | **Yes** | No | No | No | No |
| Mutual Funds | **Yes** | No | No | No | Partial |
| Commodities (MCX) | **Yes** | No | No | No | No |
| Currency (INR pairs) | **Yes** | No | No | No | No |
| Sovereign Gold Bonds | **Yes** | No | No | No | No |
| Stock Screener | **Yes** | Yes | No | No | No |
| Company Financials | **Yes** | Yes | No | No | No |
| Candlestick Patterns | **Yes** | Yes | No | No | No |
| News & Sentiment | **Yes** | Yes | No | No | No |
| Shareholding Pattern | **Yes** | Yes | No | No | No |
| Technical Analysis | **Yes** | Yes | No | No | No |
| Order Placement | **Yes** | No | No | No | Yes |
| Portfolio / Holdings | **Yes** | No | No | No | Yes |
| Market Depth | **Yes** | No | No | No | Yes |
| Multi-broker support | **Yes** | No | No | No | No |

---

## Quick Start

### Option 1: Use the hosted server (zero install)

```json
{
  "mcpServers": {
    "indian-market": {
      "type": "url",
      "url": "https://indian-market-mcp-wweh.onrender.com/mcp"
    }
  }
}
```

### Option 2: Local (stdio)

```bash
uvx indian-market-mcp
```

### Option 3: Self-host HTTP

```bash
MCP_TRANSPORT=http uvx indian-market-mcp
# Server at http://localhost:8000/mcp
```

### Option 4: Docker

```bash
docker build -t indian-market-mcp .
docker run -p 8000:8000 indian-market-mcp
```

---

## Connect to Your AI Tool

### Claude Code

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "indian-market": {
      "command": "uvx",
      "args": ["indian-market-mcp"]
    }
  }
}
```

### Claude Desktop

Go to **Settings > MCP Servers > Add** and use the same config above. Or for a remote server:

```json
{
  "mcpServers": {
    "indian-market": {
      "type": "url",
      "url": "https://your-server.com/mcp"
    }
  }
}
```

### Cursor

Add to `.cursor/mcp.json` in your project:

```json
{
  "mcpServers": {
    "indian-market": {
      "command": "uvx",
      "args": ["indian-market-mcp"]
    }
  }
}
```

### VS Code (Copilot)

Add to your VS Code `settings.json`:

```json
{
  "mcp": {
    "servers": {
      "indian-market": {
        "command": "uvx",
        "args": ["indian-market-mcp"]
      }
    }
  }
}
```

### Windsurf / Cline / Any MCP Client

Use stdio config (`command` + `args`) or remote URL (`https://your-server.com/mcp`) depending on what your client supports.

---

## Examples

Ask your AI assistant in natural language:

### Stocks
```
"What's the price of Reliance?"
"Show me top gainers today"
"Get historical data for TCS from Jan to June 2025"
"Which stocks hit 52-week high today?"
"Search for stocks related to EV"
```

### Derivatives & Options
```
"Show me NIFTY 50 option chain"
"What's the Put-Call Ratio for Bank Nifty?"
"Calculate max pain for NIFTY"
"Get futures data for Reliance"
"Show open interest across all expiries for NIFTY"
```

### Mutual Funds
```
"Search for SBI Bluechip mutual fund"
"Compare SBI Bluechip vs Axis Bluechip — 1Y returns"
"Get NAV history for scheme code 119598"
"Show me top equity mutual fund categories"
```

### Screener
```
"Find stocks with PE < 15 and ROE > 20%"
"Screen for penny stocks under Rs 50"
"Show me large cap value stocks"
"Find stocks near their 52-week high"
"Screen IT sector stocks with high dividend yield"
```

### Technical Analysis
```
"Get technical indicators for RELIANCE — RSI, MACD, Bollinger"
"What are the support and resistance levels for TCS?"
"Detect candlestick patterns for INFY in the last 3 months"
"Scan RELIANCE, TCS, INFY for Bullish Engulfing patterns"
```

### Financials
```
"Show me TCS income statement"
"Get quarterly balance sheet for Reliance"
"What are the key financial ratios for HDFC Bank?"
"Compare TCS with its industry peers"
```

### Commodities & Currency
```
"What's the gold price right now?"
"Get silver price history for last 6 months"
"What's the USD/INR exchange rate?"
"Show me all commodity prices"
```

### Market & News
```
"Is the market open right now?"
"Show FII/DII data for today"
"Get latest market news"
"Show me news about Reliance"
"What's happening in the banking sector?"
"Get upcoming IPOs"
```

### Bonds
```
"Show all Sovereign Gold Bond prices"
"Get price history for SGBJAN30IX"
```

### Broker Mode (with credentials)
```
"Buy 10 shares of Reliance at market price"
"Show my portfolio holdings"
"What's my available margin?"
"Create a GTT order for TCS at Rs 3500"
"Show my open positions"
```

---

## All 68 Tools

### Stocks (NSE/BSE) — 9 tools

| Tool | Description |
|------|-------------|
| `get_stock_quote` | Live price, volume, day high/low, 52-week range, market cap |
| `search_stocks` | Fuzzy search stocks by name or symbol |
| `get_stock_history` | Historical OHLC candle data with date range |
| `get_top_gainers` | Today's top gaining stocks on NSE |
| `get_top_losers` | Today's top losing stocks on NSE |
| `get_52week_high` | All stocks at their 52-week high |
| `get_52week_low` | All stocks at their 52-week low |
| `get_most_active_stocks` | Most traded stocks by volume or value |
| `get_corporate_actions` | Dividends, stock splits, bonus issues, rights |

### Derivatives (F&O) — 5 tools

| Tool | Description |
|------|-------------|
| `get_option_chain` | Full option chain — strike prices, premiums, OI, change in OI, IV. Works for indices (NIFTY, BANKNIFTY) and stocks |
| `get_pcr` | Put-Call Ratio with bullish/bearish interpretation |
| `get_max_pain` | Max pain strike price calculation — where option writers face minimum loss |
| `get_futures_data` | Futures contracts with lot size, expiry dates, OI, price |
| `get_oi_data` | Open Interest data across all expiries and strike prices |

### Indices — 5 tools

| Tool | Description |
|------|-------------|
| `get_index` | Live index value with advances/declines (NIFTY 50, BANK NIFTY, NIFTY IT, etc.) |
| `get_index_constituents` | All stocks in an index with live prices |
| `get_all_indices` | Every NSE index with current value and change |
| `get_index_history` | Historical data for any index with date range |
| `get_sector_performance` | All sectoral indices ranked by performance |

### Mutual Funds — 6 tools

| Tool | Description |
|------|-------------|
| `search_mutual_funds` | Search 47,000+ schemes by name, AMC, or category |
| `get_mf_nav` | Latest NAV for any mutual fund scheme |
| `get_mf_history` | Full historical NAV data or filtered by date range |
| `get_mf_categories` | All fund categories — Equity, Debt, Hybrid, etc. |
| `compare_mutual_funds` | Side-by-side comparison — NAV, returns (1M, 3M, 6M, 1Y) |
| `get_top_funds_by_category` | Top performing funds in any category |

### ETFs — 3 tools

| Tool | Description |
|------|-------------|
| `get_all_etfs` | Every ETF listed on NSE — Gold, Debt, Equity, International |
| `get_etf_quote` | Detailed quote for a specific ETF |
| `get_etf_history` | Historical price data for any ETF |

### Commodities (MCX) — 3 tools

| Tool | Description |
|------|-------------|
| `get_commodity_price` | Live price for Gold, Silver, Crude Oil, Natural Gas, Copper, Aluminium, Zinc, Lead, Nickel, Cotton |
| `get_all_commodity_prices` | All commodity prices in one call |
| `get_commodity_history` | Historical OHLC data. Periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max |

### Currency — 3 tools

| Tool | Description |
|------|-------------|
| `get_currency_rate` | Live exchange rate for USDINR, EURINR, GBPINR, JPYINR |
| `get_all_currency_rates` | All INR currency pair rates |
| `get_currency_history` | Historical exchange rate data with configurable period |

### IPO — 2 tools

| Tool | Description |
|------|-------------|
| `get_upcoming_ipos` | Upcoming and ongoing IPOs with dates, price band, issue size |
| `get_past_ipos` | Recently listed IPOs with listing price and returns |

### Bonds / SGBs — 3 tools

| Tool | Description |
|------|-------------|
| `get_sovereign_gold_bonds` | All Sovereign Gold Bonds listed on NSE with maturity dates |
| `get_sgb_quote` | Detailed quote for a specific SGB tranche |
| `get_sgb_history` | Historical price data for any SGB |

### Market Overview — 3 tools

| Tool | Description |
|------|-------------|
| `get_market_status` | Market open/closed/pre-market status for all segments |
| `get_fii_dii_data` | Foreign & Domestic Institutional Investor buy/sell data |
| `get_advances_declines` | Market breadth — advancing, declining, unchanged stocks |

### Technical Analysis — 2 tools

| Tool | Description |
|------|-------------|
| `get_technical_indicators` | All-in-one: SMA (20/50/200), EMA (12/26/50), RSI 14, MACD, Bollinger Bands, VWAP, trend signal |
| `get_support_resistance` | Pivot point based support (S1/S2/S3) and resistance (R1/R2/R3) levels |

### Stock Screener — 3 tools

| Tool | Description |
|------|-------------|
| `screen_stocks` | Custom screener with filters: price range, % change, volume, sector, near 52w high/low. Sortable results |
| `screen_by_fundamentals` | Screen by PE, PB, ROE, market cap, dividend yield. Uses Yahoo Finance fundamentals |
| `run_preset_screen` | 8 pre-built strategies: `top_gainers`, `top_losers`, `high_volume`, `near_52w_high`, `near_52w_low`, `penny_stocks`, `large_cap_value`, `high_dividend` |

### News & Sentiment — 5 tools

| Tool | Description |
|------|-------------|
| `get_market_news` | Latest Indian stock market news from Google News |
| `get_stock_news` | News for a specific stock |
| `get_sector_news` | News for a sector — IT, Banking, Pharma, Auto, FMCG |
| `get_nse_announcements` | Official NSE corporate announcements and filings |
| `get_board_meetings` | Upcoming and past board meeting dates for any stock |

### Company Financials — 6 tools

| Tool | Description |
|------|-------------|
| `get_income_statement` | P&L statement — revenue, expenses, net income, EPS. Annual or quarterly |
| `get_balance_sheet` | Assets, liabilities, equity, debt. Annual or quarterly |
| `get_cash_flow` | Operating, investing, financing cash flows. Annual or quarterly |
| `get_key_ratios` | 30+ financial ratios: PE, PB, ROE, ROA, debt/equity, margins, growth, EPS, dividend yield, beta, etc. |
| `get_peer_comparison` | Compare any stock with its industry peers on key metrics |
| `get_nse_financial_results` | Quarterly/annual results as filed with NSE |

### Candlestick Patterns — 2 tools

| Tool | Description |
|------|-------------|
| `detect_candlestick_patterns` | Detect 12+ patterns: Doji, Hammer, Inverted Hammer, Hanging Man, Shooting Star, Bullish Engulfing, Bearish Engulfing, Morning Star, Evening Star, Marubozu, Three White Soldiers, Three Black Crows. Includes bullish/bearish bias summary |
| `scan_patterns_bulk` | Scan up to 20 stocks at once for specific patterns. E.g., find all stocks showing Bullish Engulfing |

### Shareholding & Profile — 3 tools

| Tool | Description |
|------|-------------|
| `get_shareholding_pattern` | Promoter, FII, DII, public holding percentages from NSE |
| `get_company_profile` | Full company overview: sector, industry, employees, description, fundamentals |
| `get_bulk_deals` | Recent bulk and block deals on NSE |

---

## Broker Mode

Unlock 11 additional tools for live trading by adding your broker credentials. Both brokers are **free** for API access.

### Angel One (Recommended — completely free)

```json
{
  "mcpServers": {
    "indian-market": {
      "command": "uvx",
      "args": ["indian-market-mcp[angel]"],
      "env": {
        "ANGEL_API_KEY": "your-api-key",
        "ANGEL_CLIENT_ID": "your-client-id",
        "ANGEL_PASSWORD": "your-password",
        "ANGEL_TOTP_SECRET": "your-totp-secret"
      }
    }
  }
}
```

To get credentials:
1. Open an [Angel One](https://www.angelone.in/) account (free)
2. Go to [SmartAPI](https://smartapi.angelbroking.com/) and generate an API key
3. Set up TOTP in your Angel One app and note the secret

### Zerodha Kite Connect

```json
{
  "mcpServers": {
    "indian-market": {
      "command": "uvx",
      "args": ["indian-market-mcp[zerodha]"],
      "env": {
        "KITE_API_KEY": "your-api-key",
        "KITE_ACCESS_TOKEN": "your-access-token"
      }
    }
  }
}
```

To get credentials:
1. Sign up at [Kite Connect](https://developers.kite.trade/)
2. Create an app and get your API key
3. Generate an access token through the login flow

### Broker Tools (11 additional tools)

| Tool | Description |
|------|-------------|
| `place_order` | Place buy/sell orders — MARKET, LIMIT, SL, SL-M. Supports DELIVERY, INTRADAY, MARGIN |
| `cancel_order` | Cancel any pending order by order ID |
| `get_order_book` | All orders placed today — pending, executed, cancelled |
| `create_gtt_order` | Good Till Triggered — auto-executes when price hits your target |
| `get_gtt_orders` | View all active GTT orders |
| `get_holdings` | Complete portfolio — stocks owned, buy price, current price, P&L |
| `get_positions` | Open intraday and overnight positions with live P&L |
| `get_margins` | Available cash, used margin, and free margin for trading |
| `get_broker_profile` | Account details — name, client ID, registered exchanges |
| `get_market_depth` | Level 2/3 order book — top 5/20 bid-ask with quantities |
| `get_ltp` | Fastest last traded price via broker API |

---

## Remote HTTP Server

Host as a public URL so anyone can use it without installing anything — just like `https://mcp.tapetide.com/mcp`.

### Use the hosted server

```json
{
  "mcpServers": {
    "indian-market": {
      "type": "url",
      "url": "https://indian-market-mcp-wweh.onrender.com/mcp"
    }
  }
}
```

### Self-host with Docker

```bash
docker build -t indian-market-mcp .
docker run -p 8000:8000 indian-market-mcp
# Endpoint: http://localhost:8000/mcp
```

### Self-host without Docker

```bash
MCP_TRANSPORT=http MCP_PORT=8000 uvx indian-market-mcp
```

### Deploy to cloud

| Platform | How |
|----------|-----|
| **Railway** | Connect GitHub repo, add env `MCP_TRANSPORT=http`, deploy |
| **Fly.io** | `fly launch` + `fly deploy` |
| **Google Cloud Run** | `gcloud run deploy --source .` |
| **AWS ECS / Fargate** | Push Docker image, create service |
| **Render** | Connect repo, select Docker, deploy |

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_TRANSPORT` | `stdio` | Set to `http` for Streamable HTTP server |
| `MCP_HOST` | `0.0.0.0` | Host to bind |
| `MCP_PORT` | `8000` | Port to bind |
| `ANGEL_API_KEY` | — | Angel One API key (enables broker mode) |
| `ANGEL_CLIENT_ID` | — | Angel One client ID |
| `ANGEL_PASSWORD` | — | Angel One password |
| `ANGEL_TOTP_SECRET` | — | Angel One TOTP secret |
| `KITE_API_KEY` | — | Zerodha API key (enables broker mode) |
| `KITE_ACCESS_TOKEN` | — | Zerodha access token |

---

## Data Sources

All public market data is free with no API keys or sign-ups:

| Source | Data | Update Frequency |
|--------|------|-----------------|
| [NSE India](https://www.nseindia.com) | Stocks, F&O, option chains, indices, ETFs, IPOs, SGBs, FII/DII, shareholding, corporate actions, announcements | Real-time (with 3-min cache) |
| [AMFI India](https://www.amfiindia.com) | Mutual fund NAVs for 47,000+ schemes, historical NAV | Daily |
| [Yahoo Finance](https://finance.yahoo.com) | Commodities, currencies, historical OHLC, fundamentals, financials, technicals | Real-time |
| [Google News](https://news.google.com) | Market news, stock news, sector news | Real-time |

### Rate limiting & caching

NSE aggressively rate-limits requests (~3 per minute). The server uses intelligent disk-based caching:

| Data Type | Cache TTL |
|-----------|-----------|
| Live quotes | 60 seconds |
| Option chains, gainers/losers | 120 seconds |
| Indices, ETFs, FII/DII | 300 seconds |
| Historical data, MF NAVs | 300–3600 seconds |
| IPOs, SGBs, shareholding | 600 seconds |

Cache is stored at `~/.cache/indian-market-mcp/` (configurable, max 500MB).

---

## Architecture

```
indian-market-mcp/
├── src/indian_market_mcp/
│   ├── server.py                 # FastMCP entry point (stdio + HTTP)
│   ├── tools/                    # 19 tool modules
│   │   ├── stocks.py             # 9 tools — quotes, history, search, gainers/losers
│   │   ├── derivatives.py        # 5 tools — option chain, PCR, max pain, futures, OI
│   │   ├── indices.py            # 5 tools — indices, constituents, sectors
│   │   ├── mutual_funds.py       # 6 tools — NAV, history, compare, categories
│   │   ├── etfs.py               # 3 tools — ETF list, quotes, history
│   │   ├── commodities.py        # 3 tools — gold, silver, crude, natural gas
│   │   ├── currency.py           # 3 tools — USDINR, EURINR, GBPINR, JPYINR
│   │   ├── ipo.py                # 2 tools — upcoming, past IPOs
│   │   ├── bonds.py              # 3 tools — SGBs
│   │   ├── market.py             # 3 tools — status, FII/DII, breadth
│   │   ├── technicals.py         # 2 tools — indicators, support/resistance
│   │   ├── screener.py           # 3 tools — custom, fundamental, preset screens
│   │   ├── news.py               # 5 tools — market, stock, sector news
│   │   ├── financials.py         # 6 tools — P&L, balance sheet, ratios, peers
│   │   ├── candlestick.py        # 2 tools — pattern detection, bulk scan
│   │   ├── shareholding.py       # 3 tools — holding pattern, profile
│   │   ├── trading.py            # 5 tools — orders, GTT (broker mode)
│   │   ├── portfolio.py          # 4 tools — holdings, positions, margins (broker mode)
│   │   └── market_depth.py       # 2 tools — depth, LTP (broker mode)
│   └── sources/                  # Data source layer
│       ├── nse.py                # NSE India scraper with session management
│       ├── amfi.py               # AMFI mutual fund data
│       ├── mcx.py                # Commodities & currency via Yahoo Finance
│       ├── cache.py              # Disk-based caching with TTL
│       └── broker/
│           ├── angel.py          # Angel One SmartAPI integration
│           └── zerodha.py        # Zerodha Kite Connect integration
├── Dockerfile                    # Production container
├── pyproject.toml                # Dependencies and build config
└── LICENSE                       # MIT
```

---

## Development

```bash
# Clone
git clone https://github.com/afthabvp/indian-market-mcp.git
cd indian-market-mcp

# Install all dependencies including broker extras
uv sync --all-extras

# Run in stdio mode (for local MCP clients)
uv run indian-market-mcp

# Run as HTTP server
MCP_TRANSPORT=http uv run indian-market-mcp

# Run with broker mode
ANGEL_API_KEY=xxx ANGEL_CLIENT_ID=xxx ANGEL_PASSWORD=xxx ANGEL_TOTP_SECRET=xxx uv run indian-market-mcp
```

### Running tests

```bash
uv run pytest
```

### Code formatting

```bash
uv run ruff check --fix .
uv run ruff format .
```

---

## Roadmap

- [ ] Publish to PyPI (`pip install indian-market-mcp`)
- [ ] Hosted public server (like mcp.tapetide.com)
- [ ] BSE-specific tools (more granular BSE data)
- [ ] Options Greeks calculator
- [ ] Backtesting tools
- [ ] Watchlist management (persistent)
- [ ] Alert system (price/volume triggers)
- [ ] Tax calculator (STCG/LTCG for holdings)
- [ ] Upstox / Groww broker integration

---

## Contributing

Contributions welcome! Please open an issue first to discuss what you'd like to add.

1. Fork the repo
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes
4. Push and open a PR

---

## Disclaimer

This tool is for **informational and educational purposes only**. It does not constitute financial advice. Always do your own research before making investment decisions. The authors are not responsible for any financial losses incurred through the use of this tool.

Market data is sourced from publicly available APIs and may have delays. Broker mode executes real trades — use with caution.

---

## License

[MIT](LICENSE) — use it however you want.
