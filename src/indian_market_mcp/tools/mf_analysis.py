from __future__ import annotations

import math
from mcp.server.fastmcp import FastMCP
from ..sources import amfi


def _calc_returns(nav_data: list[dict]) -> dict:
    if not nav_data:
        return {}

    try:
        current = float(nav_data[0]["nav"])
    except (ValueError, KeyError):
        return {}

    periods = {
        "1M": 22, "3M": 66, "6M": 132,
        "1Y": 252, "2Y": 504, "3Y": 756,
        "5Y": 1260, "7Y": 1764, "10Y": 2520,
    }
    returns = {}
    for label, days in periods.items():
        if len(nav_data) > days:
            try:
                old = float(nav_data[days]["nav"])
                if old > 0:
                    if days <= 252:
                        returns[label] = round(((current - old) / old) * 100, 2)
                    else:
                        years = days / 252
                        cagr = (pow(current / old, 1 / years) - 1) * 100
                        returns[label] = round(cagr, 2)
            except (ValueError, KeyError, IndexError):
                pass
    return returns


def _calc_risk_metrics(nav_data: list[dict], period_days: int = 756) -> dict:
    data = nav_data[:min(period_days, len(nav_data))]
    if len(data) < 30:
        return {}

    navs = []
    for d in data:
        try:
            navs.append(float(d["nav"]))
        except (ValueError, KeyError):
            continue

    if len(navs) < 30:
        return {}

    daily_returns = []
    for i in range(1, len(navs)):
        if navs[i - 1] > 0:
            daily_returns.append((navs[i] - navs[i - 1]) / navs[i - 1])

    if not daily_returns:
        return {}

    mean_return = sum(daily_returns) / len(daily_returns)
    variance = sum((r - mean_return) ** 2 for r in daily_returns) / len(daily_returns)
    std_dev = math.sqrt(variance)
    annualized_volatility = round(std_dev * math.sqrt(252) * 100, 2)

    annualized_return = mean_return * 252
    risk_free_rate = 0.065
    sharpe = round((annualized_return - risk_free_rate) / (std_dev * math.sqrt(252)), 2) if std_dev > 0 else 0

    peak = navs[0]
    max_dd = 0
    for nav in navs:
        if nav > peak:
            peak = nav
        dd = (peak - nav) / peak
        if dd > max_dd:
            max_dd = dd

    negative_returns = [r for r in daily_returns if r < 0]
    downside_dev = 0
    if negative_returns:
        downside_dev = math.sqrt(sum(r ** 2 for r in negative_returns) / len(negative_returns))
    sortino = round((annualized_return - risk_free_rate) / (downside_dev * math.sqrt(252)), 2) if downside_dev > 0 else 0

    return {
        "volatility_annual": annualized_volatility,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "max_drawdown": round(max_dd * 100, 2),
        "negative_days_pct": round(len(negative_returns) / len(daily_returns) * 100, 1),
    }


def _calc_rolling_returns(nav_data: list[dict], roll_years: int = 3) -> dict:
    roll_days = roll_years * 252
    if len(nav_data) < roll_days + 252:
        return {}

    rolling = []
    for i in range(0, len(nav_data) - roll_days, 22):
        try:
            end_nav = float(nav_data[i]["nav"])
            start_nav = float(nav_data[i + roll_days]["nav"])
            if start_nav > 0:
                cagr = (pow(end_nav / start_nav, 1 / roll_years) - 1) * 100
                rolling.append(round(cagr, 2))
        except (ValueError, KeyError, IndexError):
            continue

    if not rolling:
        return {}

    return {
        "avg_rolling_return": round(sum(rolling) / len(rolling), 2),
        "best_rolling_return": max(rolling),
        "worst_rolling_return": min(rolling),
        "positive_periods_pct": round(sum(1 for r in rolling if r > 0) / len(rolling) * 100, 1),
        "periods_analyzed": len(rolling),
    }


def _calc_consistency_score(returns: dict, risk: dict, rolling: dict) -> float:
    score = 0
    max_score = 0

    if "3Y" in returns:
        max_score += 25
        r = returns["3Y"]
        if r > 20:
            score += 25
        elif r > 15:
            score += 20
        elif r > 12:
            score += 15
        elif r > 8:
            score += 10
        elif r > 0:
            score += 5

    if "1Y" in returns:
        max_score += 15
        r = returns["1Y"]
        if r > 25:
            score += 15
        elif r > 15:
            score += 12
        elif r > 10:
            score += 8
        elif r > 0:
            score += 4

    if "5Y" in returns:
        max_score += 20
        r = returns["5Y"]
        if r > 18:
            score += 20
        elif r > 14:
            score += 16
        elif r > 10:
            score += 12
        elif r > 5:
            score += 6

    if risk.get("sharpe_ratio"):
        max_score += 15
        s = risk["sharpe_ratio"]
        if s > 1.5:
            score += 15
        elif s > 1.0:
            score += 12
        elif s > 0.5:
            score += 8
        elif s > 0:
            score += 4

    if risk.get("max_drawdown"):
        max_score += 10
        dd = risk["max_drawdown"]
        if dd < 10:
            score += 10
        elif dd < 20:
            score += 7
        elif dd < 30:
            score += 4

    if rolling.get("positive_periods_pct"):
        max_score += 15
        pp = rolling["positive_periods_pct"]
        if pp > 95:
            score += 15
        elif pp > 85:
            score += 12
        elif pp > 70:
            score += 8
        elif pp > 50:
            score += 4

    return round(score / max_score * 100, 1) if max_score > 0 else 0


def register(mcp: FastMCP):

    @mcp.tool()
    async def analyze_mutual_fund(scheme_code: str) -> dict:
        """Deep analysis of a mutual fund — returns across all periods, risk metrics (Sharpe, Sortino, max drawdown, volatility), rolling returns, and a consistency score.
        Use search_mutual_funds first to get the scheme code.
        Example: analyze_mutual_fund("119598")"""
        nav_info = await amfi.get_fund_nav(scheme_code)
        history = await amfi.get_fund_history(scheme_code)
        nav_data = history.get("data", [])
        meta = nav_info.get("meta", {})

        returns = _calc_returns(nav_data)
        risk = _calc_risk_metrics(nav_data)
        rolling_3y = _calc_rolling_returns(nav_data, 3)
        rolling_5y = _calc_rolling_returns(nav_data, 5)
        consistency = _calc_consistency_score(returns, risk, rolling_3y)

        current_nav = float(nav_data[0]["nav"]) if nav_data else 0
        fund_age_days = len(nav_data)
        fund_age_years = round(fund_age_days / 252, 1)

        verdict = "Excellent" if consistency >= 80 else "Good" if consistency >= 60 else "Average" if consistency >= 40 else "Below Average" if consistency >= 20 else "Poor"

        return {
            "scheme_code": scheme_code,
            "fund_name": meta.get("scheme_name", ""),
            "fund_house": meta.get("fund_house", ""),
            "scheme_type": meta.get("scheme_type", ""),
            "scheme_category": meta.get("scheme_category", ""),
            "current_nav": current_nav,
            "fund_age_years": fund_age_years,
            "returns": returns,
            "risk_metrics": risk,
            "rolling_returns_3y": rolling_3y,
            "rolling_returns_5y": rolling_5y,
            "consistency_score": consistency,
            "verdict": verdict,
        }

    @mcp.tool()
    async def find_best_mutual_funds(
        category: str = "",
        investment_horizon: str = "3Y",
        risk_appetite: str = "moderate",
        top_n: int = 10,
    ) -> list[dict]:
        """Find the best mutual funds based on investment horizon and risk appetite.
        Analyzes returns, consistency, risk-adjusted performance, and rolling returns to find hidden gems.

        Parameters:
        - category: Fund category keyword (e.g. "Equity", "Large Cap", "Mid Cap", "Small Cap", "Flexi Cap", "ELSS", "Debt", "Hybrid"). Leave empty for all.
        - investment_horizon: "1Y", "3Y", "5Y", "7Y", "10Y"
        - risk_appetite: "low" (prefers low volatility), "moderate" (balanced), "high" (max returns)
        - top_n: Number of top funds to return

        Example: find_best_mutual_funds("Mid Cap", "3Y", "moderate", 10)
        Example: find_best_mutual_funds("", "5Y", "high", 5)"""
        all_navs = await amfi.get_all_navs()

        direct_funds = [
            f for f in all_navs
            if "direct" in f["scheme_name"].lower()
            and "growth" in f["scheme_name"].lower()
        ]

        if category:
            cat_lower = category.lower()
            direct_funds = [
                f for f in direct_funds
                if cat_lower in f["category"].lower() or cat_lower in f["scheme_name"].lower()
            ]

        direct_funds = direct_funds[:200]

        scored_funds = []
        for fund in direct_funds:
            code = fund["scheme_code"]
            try:
                history = await amfi.get_fund_history(code)
                nav_data = history.get("data", [])

                if len(nav_data) < 252:
                    continue

                returns = _calc_returns(nav_data)
                horizon_return = returns.get(investment_horizon)
                if horizon_return is None:
                    continue

                risk = _calc_risk_metrics(nav_data)
                rolling = _calc_rolling_returns(nav_data, int(investment_horizon.replace("Y", ""))) if investment_horizon in ("3Y", "5Y", "7Y", "10Y") else {}

                consistency = _calc_consistency_score(returns, risk, rolling)

                if risk_appetite == "low":
                    final_score = consistency * 0.4 + (risk.get("sharpe_ratio", 0) * 10) * 0.3 + horizon_return * 0.3
                elif risk_appetite == "high":
                    final_score = horizon_return * 0.5 + consistency * 0.3 + (risk.get("sortino_ratio", 0) * 5) * 0.2
                else:
                    final_score = horizon_return * 0.35 + consistency * 0.35 + (risk.get("sharpe_ratio", 0) * 10) * 0.3

                scored_funds.append({
                    "scheme_code": code,
                    "fund_name": fund["scheme_name"],
                    "category": fund["category"],
                    "current_nav": fund["nav"],
                    f"{investment_horizon}_return": horizon_return,
                    "returns": returns,
                    "sharpe_ratio": risk.get("sharpe_ratio"),
                    "sortino_ratio": risk.get("sortino_ratio"),
                    "max_drawdown": risk.get("max_drawdown"),
                    "volatility": risk.get("volatility_annual"),
                    "rolling_avg": rolling.get("avg_rolling_return"),
                    "rolling_positive_pct": rolling.get("positive_periods_pct"),
                    "consistency_score": consistency,
                    "final_score": round(final_score, 2),
                })

            except Exception:
                continue

        scored_funds.sort(key=lambda x: x["final_score"], reverse=True)
        return scored_funds[:top_n]

    @mcp.tool()
    async def find_hidden_gems(
        category: str = "Mid Cap",
        min_age_years: float = 3,
        top_n: int = 10,
    ) -> list[dict]:
        """Find hidden gem mutual funds — funds with exceptional risk-adjusted returns that are less popular.
        Focuses on:
        - High Sharpe ratio (best returns per unit of risk)
        - High rolling return consistency (positive in 80%+ periods)
        - Low max drawdown (less pain in crashes)
        - Strong 3Y/5Y CAGR

        Example: find_hidden_gems("Small Cap", 3, 10)
        Example: find_hidden_gems("Flexi Cap")"""
        all_navs = await amfi.get_all_navs()

        direct_funds = [
            f for f in all_navs
            if "direct" in f["scheme_name"].lower()
            and "growth" in f["scheme_name"].lower()
        ]

        if category:
            cat_lower = category.lower()
            direct_funds = [
                f for f in direct_funds
                if cat_lower in f["category"].lower() or cat_lower in f["scheme_name"].lower()
            ]

        direct_funds = direct_funds[:150]
        min_data_points = int(min_age_years * 252)

        gems = []
        for fund in direct_funds:
            code = fund["scheme_code"]
            try:
                history = await amfi.get_fund_history(code)
                nav_data = history.get("data", [])

                if len(nav_data) < min_data_points:
                    continue

                returns = _calc_returns(nav_data)
                risk = _calc_risk_metrics(nav_data)
                rolling = _calc_rolling_returns(nav_data, 3)

                sharpe = risk.get("sharpe_ratio", 0)
                sortino = risk.get("sortino_ratio", 0)
                max_dd = risk.get("max_drawdown", 100)
                rolling_positive = rolling.get("positive_periods_pct", 0)
                rolling_avg = rolling.get("avg_rolling_return", 0)
                return_3y = returns.get("3Y", 0)
                return_5y = returns.get("5Y", 0)

                gem_score = 0
                gem_score += min(sharpe * 20, 30)
                gem_score += min(sortino * 10, 20)
                gem_score += max(0, (100 - max_dd)) * 0.2
                gem_score += rolling_positive * 0.15
                gem_score += min(rolling_avg * 0.5, 15)

                if sharpe < 0.5 or return_3y < 8:
                    continue

                nav_info = await amfi.get_fund_nav(code)
                meta = nav_info.get("meta", {})

                gems.append({
                    "scheme_code": code,
                    "fund_name": fund["scheme_name"],
                    "fund_house": meta.get("fund_house", ""),
                    "category": fund["category"],
                    "current_nav": fund["nav"],
                    "fund_age_years": round(len(nav_data) / 252, 1),
                    "returns": returns,
                    "sharpe_ratio": sharpe,
                    "sortino_ratio": sortino,
                    "max_drawdown": max_dd,
                    "volatility": risk.get("volatility_annual"),
                    "rolling_3y_avg": rolling_avg,
                    "rolling_3y_positive_pct": rolling_positive,
                    "gem_score": round(gem_score, 2),
                    "why_gem": _explain_gem(sharpe, sortino, max_dd, rolling_positive, return_3y, return_5y),
                })

            except Exception:
                continue

        gems.sort(key=lambda x: x["gem_score"], reverse=True)
        return gems[:top_n]

    @mcp.tool()
    async def mf_sip_returns(
        scheme_code: str,
        monthly_amount: float = 10000,
        years: int = 3,
    ) -> dict:
        """Calculate what your SIP returns would have been if you had invested in this fund.
        Shows month-by-month investment, units accumulated, and final value.

        Example: mf_sip_returns("119598", 10000, 3)
        Means: Rs 10,000/month SIP for 3 years in scheme 119598"""
        history = await amfi.get_fund_history(scheme_code)
        nav_data = history.get("data", [])
        meta_resp = await amfi.get_fund_nav(scheme_code)
        meta = meta_resp.get("meta", {})

        if not nav_data:
            return {"error": "No NAV data available"}

        months_needed = years * 12
        monthly_navs = {}
        for entry in reversed(nav_data):
            try:
                date = amfi._parse_date(entry["date"])
                month_key = date[:7]
                if month_key not in monthly_navs:
                    monthly_navs[month_key] = float(entry["nav"])
            except (ValueError, KeyError):
                continue

        sorted_months = sorted(monthly_navs.keys())
        if len(sorted_months) < months_needed:
            sorted_months_to_use = sorted_months
        else:
            sorted_months_to_use = sorted_months[-months_needed:]

        total_invested = 0
        total_units = 0
        sip_log = []

        for month in sorted_months_to_use:
            nav = monthly_navs[month]
            if nav <= 0:
                continue
            units = monthly_amount / nav
            total_units += units
            total_invested += monthly_amount
            current_value = total_units * nav
            sip_log.append({
                "month": month,
                "nav": round(nav, 4),
                "units_bought": round(units, 4),
                "cumulative_units": round(total_units, 4),
                "invested": total_invested,
                "value": round(current_value, 2),
            })

        current_nav = float(nav_data[0]["nav"]) if nav_data else 0
        final_value = round(total_units * current_nav, 2)
        total_return = round(((final_value - total_invested) / total_invested) * 100, 2) if total_invested > 0 else 0

        xirr_approx = 0
        if total_invested > 0 and len(sip_log) > 1:
            n_months = len(sip_log)
            xirr_approx = round(((final_value / total_invested) ** (12 / n_months) - 1) * 100, 2)

        return {
            "fund_name": meta.get("scheme_name", ""),
            "scheme_code": scheme_code,
            "monthly_sip": monthly_amount,
            "duration_months": len(sip_log),
            "total_invested": total_invested,
            "current_value": final_value,
            "profit": round(final_value - total_invested, 2),
            "absolute_return_pct": total_return,
            "xirr_approx_pct": xirr_approx,
            "total_units": round(total_units, 4),
            "current_nav": current_nav,
            "avg_nav": round(total_invested / total_units, 4) if total_units > 0 else 0,
            "sip_log_last_6": sip_log[-6:],
        }

    @mcp.tool()
    async def compare_mf_detailed(scheme_codes: list[str]) -> dict:
        """Deep comparison of multiple mutual funds — returns, risk, rolling returns, SIP performance, consistency score.
        Perfect for "which fund should I choose" questions.
        Example: compare_mf_detailed(["119598", "120503", "118989"])"""
        results = []
        for code in scheme_codes[:5]:
            try:
                nav_info = await amfi.get_fund_nav(code)
                history = await amfi.get_fund_history(code)
                nav_data = history.get("data", [])
                meta = nav_info.get("meta", {})

                returns = _calc_returns(nav_data)
                risk = _calc_risk_metrics(nav_data)
                rolling_3y = _calc_rolling_returns(nav_data, 3)

                consistency = _calc_consistency_score(returns, risk, rolling_3y)

                results.append({
                    "scheme_code": code,
                    "fund_name": meta.get("scheme_name", ""),
                    "fund_house": meta.get("fund_house", ""),
                    "category": meta.get("scheme_category", ""),
                    "current_nav": float(nav_data[0]["nav"]) if nav_data else 0,
                    "fund_age_years": round(len(nav_data) / 252, 1),
                    "returns": returns,
                    "risk_metrics": risk,
                    "rolling_3y": rolling_3y,
                    "consistency_score": consistency,
                })
            except Exception:
                continue

        if results:
            best_by_return = max(results, key=lambda x: x["returns"].get("3Y", 0))
            best_by_consistency = max(results, key=lambda x: x["consistency_score"])
            best_by_sharpe = max(results, key=lambda x: (x["risk_metrics"].get("sharpe_ratio") or 0))
            lowest_risk = min(results, key=lambda x: (x["risk_metrics"].get("max_drawdown") or 100))

            summary = {
                "best_returns_3y": best_by_return["fund_name"],
                "most_consistent": best_by_consistency["fund_name"],
                "best_risk_adjusted": best_by_sharpe["fund_name"],
                "lowest_risk": lowest_risk["fund_name"],
            }
        else:
            summary = {}

        return {"funds": results, "summary": summary}


def _explain_gem(sharpe, sortino, max_dd, rolling_positive, return_3y, return_5y):
    reasons = []
    if sharpe > 1.2:
        reasons.append(f"Excellent risk-adjusted returns (Sharpe {sharpe})")
    elif sharpe > 0.8:
        reasons.append(f"Good risk-adjusted returns (Sharpe {sharpe})")
    if max_dd < 15:
        reasons.append(f"Very resilient in crashes (max drawdown only {max_dd}%)")
    if rolling_positive > 90:
        reasons.append(f"Extremely consistent — positive {rolling_positive}% of rolling 3Y periods")
    if return_3y > 20:
        reasons.append(f"Strong 3Y CAGR of {return_3y}%")
    if return_5y and return_5y > 18:
        reasons.append(f"Proven long-term track record (5Y CAGR {return_5y}%)")
    if sortino > 2:
        reasons.append(f"Very low downside risk (Sortino {sortino})")
    return reasons if reasons else ["Solid overall performance across metrics"]
