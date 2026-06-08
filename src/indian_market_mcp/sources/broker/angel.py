from __future__ import annotations

import os
from typing import Any

_smart_api = None


def _is_configured() -> bool:
    return all([
        os.environ.get("ANGEL_API_KEY"),
        os.environ.get("ANGEL_CLIENT_ID"),
        os.environ.get("ANGEL_PASSWORD"),
        os.environ.get("ANGEL_TOTP_SECRET"),
    ])


def _get_session():
    global _smart_api
    if _smart_api is not None:
        return _smart_api

    try:
        from SmartApi import SmartConnect
        import pyotp
    except ImportError:
        raise RuntimeError(
            "Angel One broker mode requires: pip install 'indian-market-mcp[angel]'"
        )

    api_key = os.environ["ANGEL_API_KEY"]
    client_id = os.environ["ANGEL_CLIENT_ID"]
    password = os.environ["ANGEL_PASSWORD"]
    totp_secret = os.environ["ANGEL_TOTP_SECRET"]

    obj = SmartConnect(api_key=api_key)
    totp = pyotp.TOTP(totp_secret).now()
    obj.generateSession(client_id, password, totp)

    _smart_api = obj
    return obj


async def get_profile() -> dict:
    session = _get_session()
    return session.getProfile(session.refresh_token)


async def get_holdings() -> list[dict]:
    session = _get_session()
    return session.holding()


async def get_positions() -> dict:
    session = _get_session()
    return session.position()


async def get_order_book() -> list[dict]:
    session = _get_session()
    return session.orderBook()


async def place_order(
    symbol: str,
    token: str,
    exchange: str,
    transaction_type: str,
    order_type: str,
    quantity: int,
    price: float = 0,
    trigger_price: float = 0,
    product_type: str = "DELIVERY",
    variety: str = "NORMAL",
) -> dict:
    session = _get_session()
    params = {
        "variety": variety,
        "tradingsymbol": symbol,
        "symboltoken": token,
        "transactiontype": transaction_type,
        "exchange": exchange,
        "ordertype": order_type,
        "producttype": product_type,
        "duration": "DAY",
        "quantity": quantity,
    }
    if price:
        params["price"] = price
    if trigger_price:
        params["triggerprice"] = trigger_price
    return session.placeOrder(params)


async def modify_order(order_id: str, **kwargs) -> dict:
    session = _get_session()
    params = {"orderid": order_id, **kwargs}
    return session.modifyOrder(params)


async def cancel_order(order_id: str, variety: str = "NORMAL") -> dict:
    session = _get_session()
    return session.cancelOrder(order_id, variety)


async def get_ltp(exchange: str, symbol: str, token: str) -> dict:
    session = _get_session()
    return session.ltpData(exchange, symbol, token)


async def get_market_depth(exchange: str, symbol: str, token: str) -> dict:
    session = _get_session()
    data = session.getMarketData(
        mode="FULL",
        exchangeTokens={exchange: [token]},
    )
    return data


async def get_candle_data(
    exchange: str,
    token: str,
    interval: str = "ONE_DAY",
    from_date: str = "",
    to_date: str = "",
) -> dict:
    session = _get_session()
    params = {
        "exchange": exchange,
        "symboltoken": token,
        "interval": interval,
        "fromdate": from_date,
        "todate": to_date,
    }
    return session.getCandleData(params)


async def get_margin() -> dict:
    session = _get_session()
    return session.rmsLimit()


async def create_gtt(
    symbol: str,
    token: str,
    exchange: str,
    transaction_type: str,
    price: float,
    quantity: int,
    trigger_price: float,
    product_type: str = "DELIVERY",
) -> dict:
    session = _get_session()
    params = {
        "tradingsymbol": symbol,
        "symboltoken": token,
        "exchange": exchange,
        "transactiontype": transaction_type,
        "producttype": product_type,
        "price": price,
        "qty": quantity,
        "triggerprice": trigger_price,
    }
    return session.gttCreateRule(params)


async def get_gtt_rules() -> list[dict]:
    session = _get_session()
    status_list = ["NEW", "TRIGGERED", "ACTIVE"]
    rules = []
    for status in status_list:
        try:
            result = session.gttLists([status], 1, 50)
            if result:
                rules.extend(result)
        except Exception:
            continue
    return rules
