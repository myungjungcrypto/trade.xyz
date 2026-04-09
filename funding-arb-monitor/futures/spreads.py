import logging
from datetime import datetime, date
from typing import Optional

import yfinance as yf

from config import CME_MONTH_CODES, CME_TICKERS

logger = logging.getLogger(__name__)


def _get_next_two_months(ref_date: date) -> tuple[tuple[int, int], tuple[int, int]]:
    """Return (year, month) for front month and next month futures.

    Front month is the current month if before ~15th, otherwise next month.
    Simplified: use current month as front, next month as second.
    """
    y, m = ref_date.year, ref_date.month

    front = (y, m)
    if m == 12:
        second = (y + 1, 1)
    else:
        second = (y, m + 1)

    return front, second


def _build_yahoo_ticker(root: str, year: int, month: int, exchange: str) -> str:
    """Build Yahoo Finance ticker for a specific futures month.

    Example: CLK26.NYM for WTI May 2026
    """
    month_code = CME_MONTH_CODES[month]
    year_suffix = str(year)[-2:]
    return f"{root}{month_code}{year_suffix}.{exchange}"


def _get_price(ticker: str) -> Optional[float]:
    """Fetch the latest closing price for a Yahoo Finance ticker."""
    try:
        data = yf.download(ticker, period="5d", progress=False, auto_adjust=True)
        if data.empty:
            return None
        # Get the most recent close price
        close = data["Close"].iloc[-1]
        # Handle case where close might be a Series (multi-ticker)
        if hasattr(close, "item"):
            return float(close.item())
        return float(close)
    except Exception as e:
        logger.error(f"yfinance error for {ticker}: {e}")
        return None


def get_cme_spread(asset: str, ref_date: Optional[date] = None) -> Optional[dict]:
    """Calculate front-month vs next-month spread for a CME oil contract.

    Args:
        asset: "WTI" or "BRENT"
        ref_date: Reference date (default: today)

    Returns:
        Dict with spread info, or None if data unavailable.
        {
            "asset": "WTI",
            "front_month": "May 2026",
            "next_month": "Jun 2026",
            "front_price": 65.20,
            "next_price": 64.50,
            "spread_pct": -1.07,  # negative = backwardation
            "state": "backwardation",
            "front_ticker": "CLK26.NYM",
            "next_ticker": "CLM26.NYM",
        }
    """
    if ref_date is None:
        ref_date = date.today()

    ticker_info = CME_TICKERS.get(asset)
    if not ticker_info:
        logger.error(f"Unknown CME asset: {asset}")
        return None

    root = ticker_info["root"]
    exchange = ticker_info["exchange"]

    (y1, m1), (y2, m2) = _get_next_two_months(ref_date)

    front_ticker = _build_yahoo_ticker(root, y1, m1, exchange)
    next_ticker = _build_yahoo_ticker(root, y2, m2, exchange)

    logger.info(f"[CME] Fetching {asset}: {front_ticker} vs {next_ticker}")

    # Also try the generic front-month ticker as fallback
    front_price = _get_price(front_ticker)
    if front_price is None:
        logger.info(f"[CME] Trying generic front ticker: {ticker_info['front']}")
        front_price = _get_price(ticker_info["front"])
        if front_price is None:
            logger.warning(f"[CME] No price data for {asset} front month")
            return None

    next_price = _get_price(next_ticker)
    if next_price is None:
        logger.warning(f"[CME] No price data for {asset} next month ({next_ticker})")
        return None

    spread_pct = (next_price - front_price) / front_price * 100
    state = "backwardation" if spread_pct < 0 else "contango"

    month_names = [
        "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]

    result = {
        "asset": asset,
        "front_month": f"{month_names[m1]} {y1}",
        "next_month": f"{month_names[m2]} {y2}",
        "front_price": front_price,
        "next_price": next_price,
        "spread_pct": spread_pct,
        "state": state,
        "front_ticker": front_ticker,
        "next_ticker": next_ticker,
    }

    logger.info(
        f"[CME] {asset}: {result['front_month']} vs {result['next_month']} = "
        f"{spread_pct:+.2f}% ({state})"
    )
    return result


def get_all_spreads(assets: list[str]) -> dict[str, Optional[dict]]:
    """Fetch CME spreads for all given assets."""
    results = {}
    for asset in assets:
        try:
            results[asset] = get_cme_spread(asset)
        except Exception as e:
            logger.error(f"[CME] Failed to fetch {asset} spread: {e}")
            results[asset] = None
    return results
