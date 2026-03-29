import os
import hmac
import hashlib
import time
import requests
from urllib.parse import urlencode
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from typing import Dict, Any

from bot.logging_config import logger

class BinanceAPIException(Exception):
    def __init__(self, message, status_code=None, error_code=None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code

class NetworkException(Exception):
    pass

class BinanceTestnetClient:
    BASE_URL = "https://testnet.binancefuture.com"

    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET")

        if not self.api_key or not self.api_secret:
            raise ValueError("API Key and Secret must be set in environment variables (BINANCE_API_KEY, BINANCE_API_SECRET).")

        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/json"
        })

    def _generate_signature(self, query_string: str) -> str:
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type((NetworkException, requests.exceptions.Timeout, requests.exceptions.ConnectionError))
    )
    def _request(self, method: str, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        params = params or {}
        # Binance requires a timestamp
        params['timestamp'] = int(time.time() * 1000)
        
        # We need to sign the query string before adding the signature to params
        query_string = urlencode(params)
        signature = self._generate_signature(query_string)
        params['signature'] = signature

        url = f"{self.BASE_URL}{endpoint}"
        logger.info(f"Sending {method} request to {url}")
        
        logger.info(f"Payload: {params}")

        try:
            response = self.session.request(method, url, params=params, timeout=10)
            logger.info(f"Response ({response.status_code}): {response.text}")
            
            # Handle Binance API errors
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("msg", "Unknown error")
                    error_code = error_data.get("code", None)
                except ValueError:
                    error_msg = response.text
                    error_code = None

                logger.error(f"Binance API Error {response.status_code}: {error_msg} (Code: {error_code})")
                
                # Categorize 5xx errors or specific network errors for tenacity to retry
                if response.status_code >= 500:
                   raise NetworkException(f"Server error: {response.status_code}")
                
                # Client errors (4xx) shouldn't be retried
                raise BinanceAPIException(error_msg, status_code=response.status_code, error_code=error_code)

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during {method} to {url}: {str(e)}", exc_info=True)
            raise NetworkException(f"Network error: {str(e)}")

    def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None) -> Dict[str, Any]:
        """
        Places a new order on Binance Futures Testnet.
        """
        endpoint = "/fapi/v1/order"
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity
        }
        
        if order_type == "LIMIT":
            params["price"] = price
            params["timeInForce"] = "GTC"  # Good Till Cancel required for LIMIT orders

        return self._request("POST", endpoint, params)
