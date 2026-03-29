# Binance Futures Testnet Trading Bot

A robust, production-quality CLI trading bot that interacts with the Binance Futures Testnet API. It allows users to confidently place MARKET and LIMIT orders using a clean architecture and automated retry mechanisms.

## Features
- **Order Types**: Place MARKET and LIMIT orders.
- **Support**: Supports both BUY (Long) and SELL (Short) sides.
- **Robustness**: Automated retry mechanisms on network errors and temporary Binance server issues (via `tenacity`).
- **Safety**: Robust regex and type validations before any HTTP requests are sent.
- **Logging**: Captures request payloads, response data, and stack traces into `logs/app.log`.

## Setup Instructions

1. **Clone or Download the Project**

2. **Create a Virtual Environment**
   ```cmd
   python -m venv venv
   venv\\Scripts\\activate
   ```

3. **Install Dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   - Copy the `.env.example` file to `.env`:
     ```cmd
     copy .env.example .env
     ```
   - Open `.env` and fill in your Binance Testnet API credentials.

## How to Obtain Binance Testnet API keys

1. Go to the [Binance Futures Testnet](https://testnet.binancefuture.com/).
2. Log in with your Binance account or create a simulated account on the testnet explicitly.
3. Once logged in, scroll to the bottom of the page or check the API keys section in your profile to \"Generate API Key\".
4. Note your **API Key** and **Secret Key**, and paste them into your `.env` file!

## Usage and CLI Commands

Run the entry point `cli.py` passing the required arguments.

### Help Command
View all available valid arguments:
```cmd
python cli.py --help
```

### Examples

**Place a MARKET BUY Order**
```cmd
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

**Place a LIMIT SELL Order**
```cmd
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 30000
```

## Architecture
- `cli.py`: The entry point utilizing `click` for command line parsing.
- `bot/client.py`: Core REST client wrapped with `tenacity` retries and HMAC SHA256 signing specific for Binance.
- `bot/validators.py`: Argument validation ensuring sane defaults prior to API transmission.
- `bot/orders.py`: The core domain logic orchestrating validation -> placement.
- `bot/logging_config.py`: File and console log configuration.

## Assumptions
- Uses Python 3.7+ conventions (type hints).
- Binance Testnet URL (`https://testnet.binancefuture.com`) remains reliable.
- GTC (Good Til Cancelled) is acceptable for all LIMIT orders.
