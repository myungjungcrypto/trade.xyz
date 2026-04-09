import logging
from typing import Optional

import requests

from config import LIGHTER_BASE_URL, LIGHTER_SYMBOLS
from exchanges.base import ExchangeBase

logger = logging.getLogger(__name__)


class LighterFunding(ExchangeBase):
    """Lighter.xyz perpetual funding rates for oil contracts.

    Funding period: every 1 hour.
    API docs: https://apidocs.lighter.xyz/reference/funding-rates
    Note: Market symbols TBD - verify from official docs.
    """

    name = "Lighter"

    def __init__(self):
        self.base_url = LIGHTER_BASE_URL
        self.symbols = LIGHTER_SYMBOLS
        self.session = requests.Session()

    def get_funding_rate_24h(self, symbol: str) -> Optional[float]:
        market_symbol = self.symbols.get(symbol)
        if not market_symbol:
            logger.warning(f"[Lighter] Unknown symbol: {symbol}")
            return None

        # Best-effort: try known endpoint patterns
        # Lighter API structure may vary - attempt with graceful fallback
        url = f"{self.base_url}/api/v1/funding-rates"
        params = {"market": market_symbol}

        try:
            resp = self.session.get(url, params=params, timeout=10)
            if resp.status_code == 404:
                logger.info(
                    f"[Lighter] Funding endpoint not found for {market_symbol}. "
                    "Verify API docs at https://apidocs.lighter.xyz"
                )
                return None
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            logger.warning(
                f"[Lighter] API unavailable for {market_symbol}: {e}. "
                "This is expected until API endpoints are verified."
            )
            return None

        # Parse response - adapt based on actual API format
        # Expected: list of {fundingRate, timestamp} entries
        if not isinstance(data, list):
            # Try alternative response formats
            if isinstance(data, dict):
                rates = data.get("data", data.get("fundingRates", []))
            else:
                logger.warning(f"[Lighter] Unexpected response format for {market_symbol}")
                return None
        else:
            rates = data

        if not rates:
            logger.warning(f"[Lighter] No funding data for {market_symbol}")
            return None

        # Take last 24 entries (hourly) and sum
        recent = rates[-24:] if len(rates) > 24 else rates
        total = sum(
            float(r.get("fundingRate", r.get("funding_rate", r.get("rate", 0))))
            for r in recent
        )
        total_pct = total * 100

        logger.info(
            f"[Lighter] {symbol} ({market_symbol}): "
            f"{len(recent)} payments, 24h cumulative = {total_pct:+.4f}%"
        )
        return total_pct
