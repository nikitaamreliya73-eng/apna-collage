from bot.client import BinanceTestnetClient, BinanceAPIException, NetworkException
from bot.validators import validate_symbol, validate_side, validate_order_type, validate_quantity, validate_price
from typing import Dict, Any, Tuple

def create_order(client: BinanceTestnetClient, symbol: str, side: str, order_type: str, quantity: float, price: float = None) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validates input and interacts with the Binance API to place an order.
    Returns: (is_success, message, response_data)
    """
    try:
        # 1. Validate inputs
        symbol = validate_symbol(symbol)
        side = validate_side(side)
        order_type = validate_order_type(order_type)
        quantity = validate_quantity(quantity)
        price = validate_price(order_type, price)

        # 2. Print summary
        summary = f"Validating {order_type} {side} order for {quantity} {symbol}"
        if order_type == "LIMIT":
            summary += f" at price {price}"
        print(f"\n--- Order Summary ---\n{summary}\n---------------------\n")

        # 3. Place order via client
        response = client.place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price
        )
        
        return True, "Order placed successfully.", response

    except ValueError as e:
        return False, f"Validation Error: {str(e)}", {}
    except BinanceAPIException as e:
        return False, f"API Error [{e.error_code}]: {str(e)}", {}
    except NetworkException as e:
        return False, f"Network/Retries Exhausted: {str(e)}", {}
    except Exception as e:
        return False, f"Unexpected Error: {str(e)}", {}
