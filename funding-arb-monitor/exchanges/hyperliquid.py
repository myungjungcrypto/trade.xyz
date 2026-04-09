import logging
import time
from typing import Optional

import requests

from config import HYPERLIQUID_INFO_URL, HYPERLIQUID_SYMBOLS
from exchanges.base import ExchangeBase

logger = logging.getLogger(__name__)


class HyperliquidFunding(ExchangeBase):
    """trade.xyz (Hyperliquid) perpetual funding rates for oil contracts.

    Funding period: every 1 hour (24 times/day).
    trade.xyz applies 0.5x multiplier on Hyperliquid's baseline formula.
    Symbols: WTIOIL, BRENTOIL.
    """

    name = "trade.xyz"

    def __init__(self):
        self.info_url = HYPERLIQUID_INFO_URL
        self.symbols = HYPERLIQUID_SYMBOLS
        self.session = requests.Session()

    def get_funding_rate_24h(self, symbol: str) -> Optional[float]:
        coin = self.symbols.get(symbol)
        if not coin:
            logger.warning(f"[trade.xyz] Unknown symbol: {symbol}")
            return None

        # 24 hours ago in milliseconds
        now_ms = int(time.time() * 1000)
        start_ms = now_ms - (24 * 60 * 60 * 1000)

        payload = {
            "type": "fundingHistory",
            "coin": coin,
            "startTime": start_ms,
        }

        try:
            resp = self.session.post(
                self.info_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            logger.error(f"[trade.xyz] API error for {coin}: {e}")
            return None

        if not data:
            logger.warning(f"[trade.xyz] No funding data for {coin}")
            return None

        # Sum all hourly funding rates, convert to percentage
        total = sum(float(entry.get("fundingRate", 0)) for entry in data)
        total_pct = total * 100

        logger.info(
            f"[trade.xyz] {symbol} ({coin}): "
            f"{len(data)} payments, 24h cumulative = {total_pct:+.4f}%"
        )
        return total_pct

    def get_current_funding_rate(self, symbol: str) -> Optional[float]:
        """Fetch the current/predicted funding rate (not historical)."""
        coin = self.symbols.get(symbol)
        if not coin:
            return None

        payload = {"type": "metaAndAssetCtxs"}

        try:
            resp = self.session.post(
                self.info_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            logger.error(f"[trade.xyz] Meta API error: {e}")
            return None

        # data[0] = meta (universe), data[1] = asset contexts
        if not isinstance(data, list) or len(data) < 2:
            return None

        universe = data[0].get("universe", [])
        contexts = data[1]

        for i, asset in enumerate(universe):
            if asset.get("name") == coin and i < len(contexts):
                funding = float(contexts[i].get("funding", 0))
                return funding * 100

        return None
