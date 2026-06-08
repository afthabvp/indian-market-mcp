from __future__ import annotations

import os
from mcp.server.fastmcp import FastMCP


def _get_broker():
    if os.environ.get("ANGEL_API_KEY"):
        return "angel"
    if os.environ.get("KITE_API_KEY"):
        return "zerodha"
    return None


def register(mcp: FastMCP):

    @mcp.tool()
    async def place_order(
        symbol: str,
        exchange: str,
        transaction_type: str,
        order_type: str,
        quantity: int,
        price: float = 0,
        trigger_price: float = 0,
        product_type: str = "DELIVERY",
    ) -> dict:
        """Place a buy/sell order through your broker (Angel One or Zerodha).
        Requires broker env vars to be configured.
        - exchange: NSE, BSE, MCX
        - transaction_type: BUY or SELL
        - order_type: MARKET, LIMIT, SL, SL-M
        - product_type: DELIVERY (CNC), INTRADAY (MIS), MARGIN
        Example: place_order("RELIANCE", "NSE", "BUY", "LIMIT", 10, price=2800)"""
        broker = _get_broker()
        if not broker:
            return {"error": "No broker configured. Set ANGEL_API_KEY or KITE_API_KEY env vars."}

        if broker == "angel":
            from ..sources.broker import angel
            return await angel.place_order(
                symbol=symbol, token="", exchange=exchange,
                transaction_type=transaction_type, order_type=order_type,
                quantity=quantity, price=price, trigger_price=trigger_price,
                product_type=product_type,
            )
        else:
            from ..sources.broker import zerodha
            product_map = {"DELIVERY": "CNC", "INTRADAY": "MIS", "MARGIN": "NRML"}
            return await zerodha.place_order(
                symbol=symbol, exchange=exchange,
                transaction_type=transaction_type, order_type=order_type,
                quantity=quantity, price=price, trigger_price=trigger_price,
                product=product_map.get(product_type, "CNC"),
            )

    @mcp.tool()
    async def cancel_order(order_id: str) -> dict:
        """Cancel a pending order.
        Example: cancel_order("220101000000001")"""
        broker = _get_broker()
        if not broker:
            return {"error": "No broker configured."}

        if broker == "angel":
            from ..sources.broker import angel
            return await angel.cancel_order(order_id)
        else:
            from ..sources.broker import zerodha
            return await zerodha.cancel_order(order_id)

    @mcp.tool()
    async def get_order_book() -> list[dict]:
        """Get all orders placed today — pending, executed, and cancelled."""
        broker = _get_broker()
        if not broker:
            return {"error": "No broker configured."}

        if broker == "angel":
            from ..sources.broker import angel
            return await angel.get_order_book()
        else:
            from ..sources.broker import zerodha
            return await zerodha.get_order_book()

    @mcp.tool()
    async def create_gtt_order(
        symbol: str,
        exchange: str,
        transaction_type: str,
        quantity: int,
        price: float,
        trigger_price: float,
        product_type: str = "DELIVERY",
    ) -> dict:
        """Create a Good Till Triggered (GTT) order — auto-executes when price hits trigger.
        Example: create_gtt_order("RELIANCE", "NSE", "BUY", 10, 2750, 2760)"""
        broker = _get_broker()
        if not broker:
            return {"error": "No broker configured."}

        if broker == "angel":
            from ..sources.broker import angel
            return await angel.create_gtt(
                symbol=symbol, token="", exchange=exchange,
                transaction_type=transaction_type, price=price,
                quantity=quantity, trigger_price=trigger_price,
                product_type=product_type,
            )
        else:
            from ..sources.broker import zerodha
            product_map = {"DELIVERY": "CNC", "INTRADAY": "MIS"}
            return await zerodha.place_gtt(
                trigger_type="single",
                tradingsymbol=symbol,
                exchange=exchange,
                trigger_values=[trigger_price],
                last_price=price,
                orders=[{
                    "exchange": exchange,
                    "tradingsymbol": symbol,
                    "transaction_type": transaction_type,
                    "quantity": quantity,
                    "order_type": "LIMIT",
                    "product": product_map.get(product_type, "CNC"),
                    "price": price,
                }],
            )

    @mcp.tool()
    async def get_gtt_orders() -> list[dict]:
        """Get all active GTT orders."""
        broker = _get_broker()
        if not broker:
            return {"error": "No broker configured."}

        if broker == "angel":
            from ..sources.broker import angel
            return await angel.get_gtt_rules()
        else:
            from ..sources.broker import zerodha
            return await zerodha.get_gtt_triggers()
