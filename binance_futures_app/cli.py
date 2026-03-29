import click
import time
from dotenv import load_dotenv

from bot.client import BinanceTestnetClient
from bot.orders import create_order
from bot.logging_config import logger


# 🔹 Main CLI group
@click.group()
def cli():
    """Binance Futures Testnet Trading Bot CLI."""
    load_dotenv()


# 🔹 Manual Trade Command
@cli.command()
@click.option('--symbol', required=True, help="Trading pair symbol (e.g., BTCUSDT).")
@click.option('--side', required=True, type=click.Choice(["BUY", "SELL"], case_sensitive=False), help="Order side (BUY or SELL).")
@click.option('--type', 'order_type', required=True, type=click.Choice(["MARKET", "LIMIT"], case_sensitive=False), help="Order type (MARKET or LIMIT).")
@click.option('--quantity', required=True, type=float, help="Quantity to trade.")
@click.option('--price', type=float, default=None, help="Price for LIMIT orders (required if type is LIMIT).")
def trade(symbol, side, order_type, quantity, price):
    """Place a manual trade on Binance Futures Testnet."""

    side = side.upper()
    order_type = order_type.upper()

    # ✅ Validation
    if quantity <= 0:
        click.secho("Error: Quantity must be greater than 0.", fg="red")
        return

    if order_type == "LIMIT" and price is None:
        click.secho("Error: --price is required for LIMIT orders.", fg="red")
        return

    if order_type == "MARKET" and price is not None:
        click.secho("Warning: Price is ignored for MARKET orders.", fg="yellow")

    try:
        client = BinanceTestnetClient()
    except ValueError as e:
        click.secho(f"Configuration Error: {e}", fg="red")
        return

    click.secho("\nInitiating order placement...", fg="cyan")

    success, message, response = create_order(
        client=client,
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price
    )

    if success:
        click.secho("\n[SUCCESS] " + message, fg="green", bold=True)
        click.secho("\n--- Order Details ---", fg="cyan")

        click.echo(f"Order ID:     {response.get('orderId')}")
        click.echo(f"Status:       {response.get('status')}")
        click.echo(f"Executed Qty: {response.get('executedQty')}")

        avg_price = response.get('avgPrice', response.get('price'))
        click.echo(f"Avg Price:    {avg_price}")

        logger.info(f"Order successful. Order ID: {response.get('orderId')}")

    else:
        click.secho("\n[ERROR] Failed to place order.", fg="red", bold=True)
        click.secho(message, fg="red")
        logger.error(f"Order failed: {message}")


# 🔹 Auto Trade Command (Bonus Feature 🚀)
@cli.command()
def auto_trade():
    """Run a simple auto-trading strategy (Buy then Sell)."""

    try:
        client = BinanceTestnetClient()
    except ValueError as e:
        click.secho(f"Configuration Error: {e}", fg="red")
        return

    symbol = "BTCUSDT"
    quantity = 0.002

    click.secho("\nRunning auto-trade strategy...", fg="cyan")

    # BUY
    click.secho("Placing BUY order...", fg="yellow")
    create_order(client, symbol, "BUY", "MARKET", quantity)

    click.secho("Waiting 5 seconds...", fg="yellow")
    time.sleep(5)

    # SELL
    click.secho("Placing SELL order...", fg="yellow")
    create_order(client, symbol, "SELL", "MARKET", quantity)

    click.secho("\n[SUCCESS] Auto trade completed!", fg="green", bold=True)


# 🔹 Entry point
if __name__ == "__main__":
    cli()