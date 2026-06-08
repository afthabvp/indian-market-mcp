# Indian Market MCP

Full-featured [Model Context Protocol](https://modelcontextprotocol.io) server for Indian stock market data and trading.

Covers **NSE, BSE, MCX, Mutual Funds, F&O, ETFs, IPOs, Sovereign Gold Bonds, Commodities, Currency, Technical Analysis, Stock Screener, Company Financials, Candlestick Patterns, News & Sentiment** — plus optional broker integration for order placement and portfolio tracking.

**63 tools. Zero API keys. One install.**

## Quick Start

```bash
# Run directly (no install needed)
uvx indian-market-mcp

# Or install
pip install indian-market-mcp
```

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

Add to Claude Desktop settings > MCP Servers with the same config.

### Cursor / VS Code

Add to your MCP configuration in editor settings.

## What You Can Ask

```
"What's the price of Reliance?"
"Show me NIFTY 50 option chain"
"Compare SBI Bluechip Fund vs Axis Bluechip Fund"
"Get me gold and silver prices"
"What's the USD/INR rate?"
"Show upcoming IPOs"
"Get technical indicators for TCS"
"What are the top gainers today?"
"Show FII/DII data"
"Get Sovereign Gold Bond prices"
```

## Available Tools (63)

### Stocks (NSE/BSE)
| Tool | Description |
|------|-------------|
| `get_stock_quote` | Live price, volume, 52-week range |
| `search_stocks` | Search by name or symbol |
| `get_stock_history` | Historical OHLC data |
| `get_top_gainers` | Today's top gaining stocks |
| `get_top_losers` | Today's top losing stocks |
| `get_52week_high` | Stocks at 52-week highs |
| `get_52week_low` | Stocks at 52-week lows |
| `get_most_active_stocks` | Most active by volume/value |
| `get_corporate_actions` | Dividends, splits, bonus |

### Derivatives (F&O)
| Tool | Description |
|------|-------------|
| `get_option_chain` | Full option chain with OI, IV |
| `get_pcr` | Put-Call Ratio |
| `get_max_pain` | Max pain strike calculation |
| `get_futures_data` | Futures with lot size, expiry, OI |
| `get_oi_data` | Open Interest across expiries |

### Indices
| Tool | Description |
|------|-------------|
| `get_index` | Live index value + advances/declines |
| `get_index_constituents` | All stocks in an index |
| `get_all_indices` | All NSE indices |
| `get_index_history` | Historical index data |
| `get_sector_performance` | Sectoral index performance |

### Mutual Funds
| Tool | Description |
|------|-------------|
| `search_mutual_funds` | Search by name, AMC, category |
| `get_mf_nav` | Latest NAV |
| `get_mf_history` | Historical NAV (full or date range) |
| `get_mf_categories` | All fund categories |
| `compare_mutual_funds` | Side-by-side comparison with returns |
| `get_top_funds_by_category` | Top funds in a category |

### ETFs
| Tool | Description |
|------|-------------|
| `get_all_etfs` | All NSE-listed ETFs |
| `get_etf_quote` | Detailed ETF quote |
| `get_etf_history` | Historical ETF data |

### Commodities (MCX)
| Tool | Description |
|------|-------------|
| `get_commodity_price` | Gold, Silver, Crude, Natural Gas etc. |
| `get_all_commodity_prices` | All commodity prices |
| `get_commodity_history` | Historical commodity data |

### Currency
| Tool | Description |
|------|-------------|
| `get_currency_rate` | USD/INR, EUR/INR, GBP/INR, JPY/INR |
| `get_all_currency_rates` | All currency pair rates |
| `get_currency_history` | Historical exchange rates |

### IPO
| Tool | Description |
|------|-------------|
| `get_upcoming_ipos` | Upcoming and ongoing IPOs |
| `get_past_ipos` | Recently listed IPOs |

### Bonds / SGBs
| Tool | Description |
|------|-------------|
| `get_sovereign_gold_bonds` | All SGBs on NSE |
| `get_sgb_quote` | Detailed SGB quote |
| `get_sgb_history` | Historical SGB prices |

### Market Overview
| Tool | Description |
|------|-------------|
| `get_market_status` | Market open/closed status |
| `get_fii_dii_data` | FII/DII buy/sell data |
| `get_advances_declines` | Market breadth |

### Technical Analysis
| Tool | Description |
|------|-------------|
| `get_technical_indicators` | SMA, EMA, RSI, MACD, Bollinger, VWAP |
| `get_support_resistance` | Pivot-based S/R levels |

### Stock Screener
| Tool | Description |
|------|-------------|
| `screen_stocks` | Screen by price, change%, volume, sector, 52w proximity |
| `screen_by_fundamentals` | Screen by PE, PB, ROE, market cap, dividend yield |
| `run_preset_screen` | Pre-built screens: top_gainers, near_52w_high, penny_stocks, large_cap_value, high_dividend etc. |

### News & Sentiment
| Tool | Description |
|------|-------------|
| `get_market_news` | Latest Indian market news |
| `get_stock_news` | News for a specific stock |
| `get_sector_news` | News for a sector (IT, Banking, Pharma etc.) |
| `get_nse_announcements` | Official NSE corporate announcements |
| `get_board_meetings` | Board meeting dates |

### Company Financials
| Tool | Description |
|------|-------------|
| `get_income_statement` | P&L — revenue, expenses, net income, EPS |
| `get_balance_sheet` | Assets, liabilities, equity, debt |
| `get_cash_flow` | Operating, investing, financing cash flows |
| `get_key_ratios` | 30+ ratios — PE, PB, ROE, ROCE, margins, growth |
| `get_peer_comparison` | Compare with industry peers |
| `get_nse_financial_results` | Quarterly results filed with NSE |

### Candlestick Patterns
| Tool | Description |
|------|-------------|
| `detect_candlestick_patterns` | Detect 12+ patterns — Doji, Hammer, Engulfing, Morning Star, Evening Star, Marubozu, Three White Soldiers etc. |
| `scan_patterns_bulk` | Scan multiple stocks for specific patterns |

### Shareholding & Profile
| Tool | Description |
|------|-------------|
| `get_shareholding_pattern` | Promoter, FII, DII, public holding % |
| `get_company_profile` | Full company profile with fundamentals |
| `get_bulk_deals` | Recent bulk and block deals |

## Broker Mode (Optional)

Enable trading and portfolio features by adding broker credentials:

### Angel One (Free)

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

### Broker Tools (unlocked with credentials)

| Tool | Description |
|------|-------------|
| `place_order` | Buy/sell stocks, F&O |
| `cancel_order` | Cancel pending orders |
| `get_order_book` | Today's orders |
| `create_gtt_order` | Good Till Triggered orders |
| `get_gtt_orders` | Active GTT orders |
| `get_holdings` | Portfolio holdings with P&L |
| `get_positions` | Open positions |
| `get_margins` | Available trading margins |
| `get_broker_profile` | Account profile |
| `get_market_depth` | Level 2/3 bid-ask depth |
| `get_ltp` | Fast last traded price |

## Data Sources

All public data is free with no API keys required:

| Source | Data |
|--------|------|
| NSE India | Stocks, F&O, indices, ETFs, IPOs, SGBs, FII/DII |
| AMFI | Mutual fund NAVs (47,000+ schemes) |
| Yahoo Finance | Commodities, currencies, historical data, technicals |

## Remote HTTP Server

Host as a URL (like `https://mcp.yourdomain.com/mcp`) so anyone can use it without installing:

### Use the hosted version

```json
{
  "mcpServers": {
    "indian-market": {
      "type": "url",
      "url": "https://mcp.yourdomain.com/mcp"
    }
  }
}
```

### Self-host with Docker

```bash
docker build -t indian-market-mcp .
docker run -p 8000:8000 indian-market-mcp
```

Server runs at `http://localhost:8000/mcp`.

### Self-host without Docker

```bash
MCP_TRANSPORT=http MCP_PORT=8000 uvx indian-market-mcp
```

### Deploy to cloud

Works with any container platform:

| Platform | Command |
|----------|---------|
| **Railway** | Connect GitHub repo, set `MCP_TRANSPORT=http` env var |
| **Fly.io** | `fly launch` then `fly deploy` |
| **Google Cloud Run** | `gcloud run deploy --source .` |
| **AWS ECS / Fargate** | Push Docker image, create service |
| **Render** | Connect repo, set Docker runtime |

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_TRANSPORT` | `stdio` | Set to `http` for remote server |
| `MCP_HOST` | `0.0.0.0` | Host to bind |
| `MCP_PORT` | `8000` | Port to bind |

## Development

```bash
git clone https://github.com/afthabvp/indian-market-mcp.git
cd indian-market-mcp
uv sync --all-extras
uv run indian-market-mcp

# Run as HTTP server locally
MCP_TRANSPORT=http uv run indian-market-mcp
```

## License

MIT
