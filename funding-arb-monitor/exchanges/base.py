import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)


class ExchangeBase(ABC):
    """Abstract base class for exchange funding rate adapters."""

    name: str = "unknown"

    @abstractmethod
    def get_funding_rate_24h(self, symbol: str) -> Optional[float]:
        """Return 24h cumulative funding rate as a percentage.

        Args:
            symbol: Internal symbol name ("WTI" or "BRENT")

        Returns:
            Cumulative 24h funding rate in percent, or None if unavailable.
        """
        pass

    def get_all_funding_rates(self, symbols: list[str]) -> dict[str, Optional[float]]:
        """Fetch 24h funding rates for all given symbols."""
        results = {}
        for symbol in symbols:
            try:
                results[symbol] = self.get_funding_rate_24h(symbol)
            except Exception as e:
                logger.error(f"[{self.name}] Failed to fetch {symbol} funding: {e}")
                results[symbol] = None
        return results
