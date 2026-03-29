import re

def validate_symbol(symbol: str) -> str:
    symbol = symbol.upper()
    if not re.match(r"^[A-Z0-9]{2,20}$", symbol):
        raise ValueError(f"Invalid symbol format: {symbol}. Must be 2-20 uppercase alphanumeric characters.")
    return symbol

def validate_side(side: str) -> str:
    side = side.upper()
    if side not in ("BUY", "SELL"):
        raise ValueError(f"Invalid side: {side}. Must be 'BUY' or 'SELL'.")
    return side

def validate_order_type(order_type: str) -> str:
    order_type = order_type.upper()
    if order_type not in ("MARKET", "LIMIT"):
        raise ValueError(f"Invalid order type: {order_type}. Supported types are 'MARKET' and 'LIMIT'.")
    return order_type

def validate_quantity(quantity: float) -> float:
    if quantity <= 0:
        raise ValueError(f"Invalid quantity: {quantity}. Must be greater than 0.")
    return quantity

def validate_price(order_type: str, price: float = None) -> float:
    if order_type == "LIMIT":
        if price is None or price <= 0:
            raise ValueError("Price is required and must be greater than 0 for LIMIT orders.")
        return price
    return price
