from __future__ import annotations

import os
from typing import Any

_kite = None


def _is_configured() -> bool:
    return all([
        os.environ.get("KITE_API_KEY"),
        os.environ.get("KITE_ACCESS_TOKEN"),
    ])


def _get_session():
    global _kite
    if _kite is not None:
        return _kite

    try:
        from kiteconnect import KiteConnect
    except ImportError:
        raise RuntimeError(
            "Zerodha broker mode requires: pip install 'indian-market-mcp[zerodha]'"
        )

    api_key = os.environ["KITE_API_KEY"]
    access_token = os.environ["KITE_ACCESS_TOKEN"]

    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)

    _kite = kite
    return kite


async def get_profile() -> dict:
    return _get_session().profile()


async def get_holdings() -> list[dict]:
    return _get_session().holdings()


async def get_positions() -> dict:
    return _get_session().positions()


async def get_order_book() -> list[dict]:
    return _get_session().orders()


async def place_order(
    symbol: str,
    exchange: str,
    transaction_type: str,
    order_type: str,
    quantity: int,
    price: float = 0,
    trigger_price: float = 0,
    product: str = "CNC",
    variety: str = "regular",
) -> str:
    params = {
        "tradingsymbol": symbol,
        "exchange": exchange,
        "transaction_type": transaction_type,
        "order_type": order_type,
        "quantity": quantity,
        "product": product,
        "variety": variety,
    }
    if price:
        params["price"] = price
    if trigger_price:
        params["trigger_price"] = trigger_price
    return _get_session().place_order(**params)


async def modify_order(order_id: str, variety: str = "regular", **kwargs) -> str:
    return _get_session().modify_order(variety=variety, order_id=order_id, **kwargs)


async def cancel_order(order_id: str, variety: str = "regular") -> str:
    return _get_session().cancel_order(variety=variety, order_id=order_id)


async def get_ltp(instruments: list[str]) -> dict:
    return _get_session().ltp(instruments)


async def get_market_depth(instruments: list[str]) -> dict:
    return _get_session().quote(instruments)


async def get_historical_data(
    instrument_token: int,
    from_date: str,
    to_date: str,
    interval: str = "day",
) -> list[dict]:
    return _get_session().historical_data(
        instrument_token, from_date, to_date, interval
    )


async def get_margins() -> dict:
    return _get_session().margins()


async def get_gtt_triggers() -> list[dict]:
    return _get_session().get_gtts()


async def place_gtt(
    trigger_type: str,
    tradingsymbol: str,
    exchange: str,
    trigger_values: list[float],
    last_price: float,
    orders: list[dict],
) -> int:
    return _get_session().place_gtt(
        trigger_type=trigger_type,
        tradingsymbol=tradingsymbol,
        exchange=exchange,
        trigger_values=trigger_values,
        last_price=last_price,
        orders=orders,
    )
