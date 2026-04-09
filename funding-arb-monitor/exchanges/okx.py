import logging
from typing import Optional

from exchanges.base import ExchangeBase

logger = logging.getLogger(__name__)


class OKXFunding(ExchangeBase):
    """OKX perpetual funding rates - STUB.

    OKX does not currently offer WTI/Brent oil perpetual contracts.
    This module is kept as a placeholder for future expansion.
    """

    name = "OKX"

    def get_funding_rate_24h(self, symbol: str) -> Optional[float]:
        logger.info(f"[OKX] Oil perpetuals not available (requested: {symbol})")
        return None
