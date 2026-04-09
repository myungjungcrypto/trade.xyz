import logging
import time
from typing import Optional

import requests

from config import BINANCE_BASE_URL, BINANCE_SYMBOLS
from exchanges.base import ExchangeBase

logger = logging.getLogger(__name__)


class BinanceFunding(ExchangeBase):
    """Binance USDT-M perpetual funding rates for oil contracts.

    Funding period: every 4 hours (6 times/day).
    Symbols: CLUSDT (WTI), BZUSDT (Brent).
    Note: Korean IPs get HTTP 451 - run from AWS EC2.
    """

    name = "Binance"

    def __init__(self):
        self.base_url = BINANCE_BASE_URL
        self.symbols = BINANCE_SYMBOLS
        self.session = requests.Session()

    def get_funding_rate_24h(self, symbol: str) -> Optional[float]:
        exchange_symbol = self.symbols.get(symbol)
        if not exchange_symbol:
            logger.warning(f"[Binance] Unknown symbol: {symbol}")
            return None

        # Fetch last 6 funding payments (4h * 6 = 24h)
        url = f"{self.base_url}/fapi/v1/fundingRate"
        params = {
            "symbol": exchange_symbol,
            "limit": 6,
        }

        try:
            resp = self.session.get(url, params=params, timeout=10)
            if resp.status_code == 451:
                logger.warning("[Binance] HTTP 451 - Korean IP blocked. Use EC2.")
                return None
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            logger.error(f"[Binance] API error for {exchange_symbol}: {e}")
            return None

        if not data:
            logger.warning(f"[Binance] No funding data for {exchange_symbol}")
            return None

        # Sum funding rates and convert to percentage
        total = sum(float(entry["fundingRate"]) for entry in data)
        total_pct = total * 100

        logger.info(
            f"[Binance] {symbol} ({exchange_symbol}): "
            f"{len(data)} payments, 24h cumulative = {total_pct:+.4f}%"
        )
        return total_pct
