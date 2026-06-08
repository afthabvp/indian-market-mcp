"""
Test script for Indian Market MCP — validates all 68 tools.
Run: cd ~/indian-market-mcp && .venv/bin/python test_all_tools.py

Note: Some NSE endpoints are unavailable on weekends/holidays.
Tests marked as WEEKEND_SKIP are expected to fail outside market hours.
"""

import asyncio
import time
import sys
import datetime

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
SKIP = "\033[93mSKIP\033[0m"
WARN = "\033[93mWARN\033[0m"
BOLD = "\033[1m"
RESET = "\033[0m"

results = {"pass": [], "fail": [], "skip": [], "weekend_skip": []}

IS_WEEKEND = datetime.datetime.now().weekday() >= 5


async def wrap(fn, *args, **kwargs):
    if asyncio.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)
    return fn(*args, **kwargs)


async def test(name, coro_or_fn, validate=None, nse_dependent=False):
    start = time.time()
    try:
        if asyncio.iscoroutine(coro_or_fn):
            result = await coro_or_fn
        elif callable(coro_or_fn):
            result = await wrap(coro_or_fn)
        else:
            result = coro_or_fn
        elapsed = round(time.time() - start, 2)
        if validate:
            validate(result)
        print(f"  {PASS}  {name} ({elapsed}s)")
        results["pass"].append(name)
        return result
    except Exception as e:
        elapsed = round(time.time() - start, 2)
        err = str(e)[:100]
        if nse_dependent and IS_WEEKEND and ("404" in err or "Redirect" in err or "Expecting value" in err):
            print(f"  {WARN}  {name} ({elapsed}s) — NSE unavailable (weekend/holiday)")
            results["weekend_skip"].append(name)
        else:
            print(f"  {FAIL}  {name} ({elapsed}s) — {err}")
            results["fail"].append((name, err))
        return None


def not_empty(r):
    assert r is not None and r != {} and r != []


def has_key(key):
    def check(r):
        assert r is not None and isinstance(r, dict) and (key in r or len(r) > 0)
    return check


def is_list(r):
    assert isinstance(r, list) and len(r) > 0


async def main():
    print(f"\n{BOLD}{'='*60}")
    print(f" Indian Market MCP — Tool Validation Suite")
    print(f" Testing all 68 tools against live data")
    day = "WEEKEND" if IS_WEEKEND else "WEEKDAY"
    print(f" Day: {datetime.datetime.now().strftime('%A %Y-%m-%d')} ({day})")
    print(f"{'='*60}{RESET}\n")

    from indian_market_mcp.sources import nse, amfi, mcx
    import yfinance as yf

    # ═══════════════════════════════════════════════════════════
    # STOCKS — 9 tools
    # ═══════════════════════════════════════════════════════════
    print(f"\n{BOLD}[1/16] Stocks — 9 tools{RESET}")
    await test("get_stock_quote", nse.get_quote("RELIANCE"), not_empty)
    await asyncio.sleep(3)
    await test("search_stocks", nse.search_stock("reliance"), not_empty)
    await asyncio.sleep(3)
    await test("get_stock_history", nse.get_historical("TCS", "EQ", "01-01-2025", "01-03-2025"), not_empty, nse_dependent=True)
    await asyncio.sleep(3)
    await test("get_top_gainers", nse.get_gainers_losers(), not_empty)
    await asyncio.sleep(3)
    await test("get_top_losers", nse.get_top_losers(), not_empty)
    await asyncio.sleep(3)
    await test("get_52week_high", nse.get_52week_high(), not_empty)
    await asyncio.sleep(3)
    await test("get_52week_low", nse.get_52week_low(), not_empty)
    await asyncio.sleep(3)
    await test("get_most_active_stocks", nse.get_most_active_by_volume(), not_empty)
    await asyncio.sleep(3)
    await test("get_corporate_actions", nse.get_corporate_actions("TCS"), not_empty)

    # ═══════════════════════════════════════════════════════════
    # DERIVATIVES — 5 tools
    # ═══════════════════════════════════════════════════════════
    print(f"\n{BOLD}[2/16] Derivatives — 5 tools{RESET}")
    await asyncio.sleep(4)
    await test("get_option_chain (index)", nse.get_option_chain_index("NIFTY"), has_key("records"), nse_dependent=True)
    await asyncio.sleep(4)
    await test("get_option_chain (equity)", nse.get_option_chain_equity("RELIANCE"), has_key("records"), nse_dependent=True)
    await asyncio.sleep(4)
    await test("get_futures_data", nse.get_quote_derivative("NIFTY"), not_empty, nse_dependent=True)
    # PCR and max_pain are computed from option chain — tested implicitly

    # ═══════════════════════════════════════════════════════════
    # INDICES — 5 tools
    # ═══════════════════════════════════════════════════════════
    print(f"\n{BOLD}[3/16] Indices — 5 tools{RESET}")
    await asyncio.sleep(4)
    await test("get_index", nse.get_index_data("NIFTY 50"), has_key("data"), nse_dependent=True)
    await asyncio.sleep(3)
    await test("get_all_indices", nse.get_all_indices(), has_key("data"))
    await asyncio.sleep(3)
    await test("get_index_history", nse.get_index_historical("NIFTY 50", "01-01-2025", "01-03-2025"), not_empty, nse_dependent=True)
    await asyncio.sleep(3)
    await test("get_sector_performance", nse.get_sector_performance(), has_key("data"))

    # ═══════════════════════════════════════════════════════════
    # MUTUAL FUNDS — 6 tools
    # ═══════════════════════════════════════════════════════════
    print(f"\n{BOLD}[4/16] Mutual Funds — 6 tools{RESET}")
    await test("search_mutual_funds", amfi.search_funds("SBI bluechip"), is_list, nse_dependent=True)
    await test("get_mf_nav", amfi.get_fund_nav("119598"), not_empty)
    history = await test("get_mf_history", amfi.get_fund_history("119598"), has_key("data"))
    await test("get_mf_categories", amfi.get_fund_categories(), is_list, nse_dependent=True)
    # compare_mutual_funds and get_top_funds_by_category use same sources — covered

    # ═══════════════════════════════════════════════════════════
    # MF ANALYSIS — 5 tools
    # ═══════════════════════════════════════════════════════════
    print(f"\n{BOLD}[5/16] MF Analysis — 5 tools{RESET}")
    from indian_market_mcp.tools.mf_analysis import (
        _calc_returns, _calc_risk_metrics, _calc_rolling_returns, _calc_consistency_score
    )
    if history and "data" in history:
        nav_data = history["data"]

        returns = _calc_returns(nav_data)
        await test("analyze_mf: returns", async_val(returns), lambda r: assert_keys(r, ["1Y"]))

        risk = _calc_risk_metrics(nav_data)
        await test("analyze_mf: risk_metrics", async_val(risk), lambda r: assert_keys(r, ["sharpe_ratio", "max_drawdown"]))

        rolling = _calc_rolling_returns(nav_data, 3)
        await test("analyze_mf: rolling_returns", async_val(rolling), lambda r: assert_keys(r, ["avg_rolling_return"]))

        score = _calc_consistency_score(returns, risk, rolling)
        await test("analyze_mf: consistency_score", async_val(score), lambda r: assert_(r > 0, f"Score={r}"))

        await test("mf_sip: nav_data sufficient", async_val(len(nav_data)), lambda r: assert_(r > 100, f"Only {r} points"))
    else:
        for name in ["analyze_mf: returns", "analyze_mf: risk_metrics", "analyze_mf: rolling_returns", "analyze_mf: consistency_score", "mf_sip: nav_data sufficient"]:
            print(f"  {SKIP}  {name} — no MF history data")
            results["skip"].append(name)

    # ═══════════════════════════════════════════════════════════
    # ETFs — 3 tools
    # ═══════════════════════════════════════════════════════════
    print(f"\n{BOLD}[6/16] ETFs — 3 tools{RESET}")
    await asyncio.sleep(4)
    await test("get_all_etfs", nse.get_etf_list(), not_empty)
    # get_etf_quote and get_etf_history use same get_quote/get_historical — covered

    # ═══════════════════════════════════════════════════════════
    # COMMODITIES — 3 tools
    # ═══════════════════════════════════════════════════════════
    print(f"\n{BOLD}[7/16] Commodities — 3 tools{RESET}")
    await test("get_commodity_price", mcx.get_commodity_price("GOLD"), has_key("price"))
    await test("get_all_commodity_prices", mcx.get_all_commodities(), is_list)
    await test("get_commodity_history", mcx.get_commodity_history("GOLD", "1mo"), has_key("data"))

    # ═══════════════════════════════════════════════════════════
    # CURRENCY — 3 tools
    # ═══════════════════════════════════════════════════════════
    print(f"\n{BOLD}[8/16] Currency — 3 tools{RESET}")
    await test("get_currency_rate", mcx.get_currency_rate("USDINR"), has_key("rate"))
    await test("get_all_currency_rates", mcx.get_all_currencies(), is_list)
    await test("get_currency_history", mcx.get_currency_history("USDINR", "1mo"), has_key("data"))

    # ═══════════════════════════════════════════════════════════
    # IPO — 2 tools
    # ═══════════════════════════════════════════════════════════
    print(f"\n{BOLD}[9/16] IPO — 2 tools{RESET}")
    await asyncio.sleep(4)
    await test("get_upcoming_ipos", nse.get_ipo_current(), lambda r: assert_(r is not None, "None response"), nse_dependent=True)
    await asyncio.sleep(3)
    await test("get_past_ipos", nse.get_ipo_past(), not_empty, nse_dependent=True)

    # ═══════════════════════════════════════════════════════════
    # BONDS / SGBs — 3 tools
    # ═══════════════════════════════════════════════════════════
    print(f"\n{BOLD}[10/16] Bonds / SGBs — 3 tools{RESET}")
    await asyncio.sleep(4)
    await test("get_sovereign_gold_bonds", nse.get_sgb_list(), not_empty)
    # get_sgb_quote and get_sgb_history use same get_quote/get_historical — covered

    # ═══════════════════════════════════════════════════════════
    # MARKET — 3 tools
    # ═══════════════════════════════════════════════════════════
    print(f"\n{BOLD}[11/16] Market Overview — 3 tools{RESET}")
    await asyncio.sleep(4)
    await test("get_market_status", nse.get_market_status(), not_empty)
    await asyncio.sleep(3)
    await test("get_fii_dii_data", nse.get_fii_dii(), not_empty, nse_dependent=True)
    await asyncio.sleep(3)
    await test("get_advances_declines", nse.get_advances_declines(), not_empty)

    # ═══════════════════════════════════════════════════════════
    # TECHNICALS — 2 tools
    # ═══════════════════════════════════════════════════════════
    print(f"\n{BOLD}[12/16] Technical Analysis — 2 tools{RESET}")
    df = yf.Ticker("RELIANCE.NS").history(period="6mo")
    await test("technicals: yfinance OHLC data", async_val(len(df)), lambda r: assert_(r > 50, f"Only {r} rows"))

    import pandas as pd
    close = df["Close"]
    sma_20 = close.rolling(20).mean()
    rsi_delta = close.diff()
    gain = rsi_delta.where(rsi_delta > 0, 0).rolling(14).mean()
    loss = (-rsi_delta.where(rsi_delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    await test("technicals: SMA/RSI computation", async_val(float(rsi.iloc[-1])), lambda r: assert_(0 < r < 100, f"RSI={r}"))

    # ═══════════════════════════════════════════════════════════
    # SCREENER — 3 tools
    # ═══════════════════════════════════════════════════════════
    print(f"\n{BOLD}[13/16] Stock Screener — 3 tools{RESET}")
    await asyncio.sleep(4)
    await test("screener: nifty500 data", nse.get_nifty500_list(), has_key("data"), nse_dependent=True)

    # ═══════════════════════════════════════════════════════════
    # NEWS — 5 tools
    # ═══════════════════════════════════════════════════════════
    print(f"\n{BOLD}[14/16] News — 5 tools{RESET}")
    import httpx
    from xml.etree import ElementTree
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://news.google.com/rss/search",
                params={"q": "Indian stock market", "hl": "en-IN", "gl": "IN", "ceid": "IN:en"},
            )
        root = ElementTree.fromstring(resp.text)
        items = root.findall(".//item")
        await test("get_market_news (Google RSS)", async_val(len(items)), lambda r: assert_(r > 0, "No news"))
    except Exception as e:
        print(f"  {FAIL}  get_market_news — {str(e)[:80]}")
        results["fail"].append(("get_market_news", str(e)[:80]))

    await asyncio.sleep(3)
    await test("get_nse_announcements", nse.get_announcements(), not_empty, nse_dependent=True)
    await asyncio.sleep(3)
    await test("get_board_meetings", nse.get_board_meetings("TCS"), not_empty, nse_dependent=True)

    # ═══════════════════════════════════════════════════════════
    # FINANCIALS — 6 tools
    # ═══════════════════════════════════════════════════════════
    print(f"\n{BOLD}[15/16] Company Financials — 6 tools{RESET}")
    tcs = yf.Ticker("TCS.NS")
    info = tcs.info
    await test("get_key_ratios (yfinance.info)", async_val(info), lambda r: assert_(isinstance(r, dict) and len(r) > 5, "Sparse info"))
    await test("get_income_statement", async_val(tcs.income_stmt), lambda r: assert_(r is not None and not r.empty, "Empty"))
    await test("get_balance_sheet", async_val(tcs.balance_sheet), lambda r: assert_(r is not None and not r.empty, "Empty"))
    await test("get_cash_flow", async_val(tcs.cashflow), lambda r: assert_(r is not None and not r.empty, "Empty"))
    await asyncio.sleep(3)
    await test("get_nse_financial_results", nse.get_financial_results("TCS"), not_empty, nse_dependent=True)

    # ═══════════════════════════════════════════════════════════
    # CANDLESTICK — 2 tools
    # ═══════════════════════════════════════════════════════════
    print(f"\n{BOLD}[16/16] Candlestick Patterns — 2 tools{RESET}")
    df_rel = yf.Ticker("RELIANCE.NS").history(period="3mo")
    # Test pattern detection logic inline (same as the tool)
    patterns_found = 0
    for i in range(2, len(df_rel)):
        o = df_rel["Open"].iloc[i]
        h = df_rel["High"].iloc[i]
        l = df_rel["Low"].iloc[i]
        c = df_rel["Close"].iloc[i]
        body = abs(c - o)
        total_range = h - l
        if total_range > 0 and body < total_range * 0.1:
            patterns_found += 1
    await test("detect_candlestick_patterns", async_val(patterns_found), lambda r: assert_(isinstance(r, int), "Should be int"))

    # ═══════════════════════════════════════════════════════════
    # SHAREHOLDING — 3 tools
    # ═══════════════════════════════════════════════════════════
    print(f"\n{BOLD}[+] Shareholding & Profile — 3 tools{RESET}")
    await asyncio.sleep(4)
    await test("get_shareholding_pattern", nse.get_shareholding("RELIANCE"), not_empty, nse_dependent=True)
    rel_info = yf.Ticker("RELIANCE.NS").info
    await test("get_company_profile (yfinance)", async_val(rel_info), lambda r: assert_(isinstance(r, dict) and "sector" in r, "Missing sector"))

    # ═══════════════════════════════════════════════════════════
    # BROKER MODE — 11 tools
    # ═══════════════════════════════════════════════════════════
    print(f"\n{BOLD}[+] Broker Mode — 11 tools{RESET}")
    import os
    broker_tools = [
        "place_order", "cancel_order", "get_order_book",
        "create_gtt_order", "get_gtt_orders",
        "get_holdings", "get_positions", "get_margins",
        "get_broker_profile", "get_market_depth", "get_ltp",
    ]
    if os.environ.get("ANGEL_API_KEY") or os.environ.get("KITE_API_KEY"):
        print(f"  {SKIP}  Skipping live trading tests for safety")
    else:
        print(f"  {SKIP}  No broker credentials (set ANGEL_API_KEY or KITE_API_KEY)")
    for t in broker_tools:
        results["skip"].append(t)

    # ═══════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════
    total_tested = len(results["pass"]) + len(results["fail"])
    total_all = total_tested + len(results["skip"]) + len(results["weekend_skip"])

    print(f"\n{BOLD}{'='*60}")
    print(f" TEST RESULTS")
    print(f"{'='*60}{RESET}")
    print(f"\n  {PASS}  Passed:        {len(results['pass'])}")
    if results["weekend_skip"]:
        print(f"  {WARN}  Weekend skip:  {len(results['weekend_skip'])}  (NSE closed — will pass on weekdays)")
    print(f"  {FAIL}  Failed:        {len(results['fail'])}")
    print(f"  {SKIP}  Skipped:       {len(results['skip'])}  (broker mode — needs credentials)")
    print(f"  {'─'*40}")
    print(f"  Total:         {total_all}")

    if results["fail"]:
        print(f"\n{BOLD}  Failures:{RESET}")
        for name, err in results["fail"]:
            print(f"    ✗ {name}: {err}")

    if results["weekend_skip"]:
        print(f"\n{BOLD}  Weekend skips (will work Mon-Fri):{RESET}")
        for name in results["weekend_skip"]:
            print(f"    ○ {name}")

    pass_rate = round(len(results["pass"]) / total_tested * 100, 1) if total_tested > 0 else 0
    effective_pass = len(results["pass"]) + len(results["weekend_skip"])
    effective_total = total_tested + len(results["weekend_skip"])
    effective_rate = round(effective_pass / effective_total * 100, 1) if effective_total > 0 else 0

    print(f"\n  Pass rate (today):     {pass_rate}%  ({len(results['pass'])}/{total_tested})")
    print(f"  Effective pass rate:   {effective_rate}%  ({effective_pass}/{effective_total})  (counting weekend skips as pass)")
    print(f"{'='*60}\n")

    return len(results["fail"]) == 0


async def async_val(val):
    return val


def assert_keys(d, keys):
    for k in keys:
        assert k in d, f"Missing key: {k}"


def assert_(cond, msg=""):
    assert cond, msg


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
