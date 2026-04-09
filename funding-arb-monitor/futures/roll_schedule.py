import logging
from datetime import date, timedelta
from typing import Optional

from config import ROLL_DAYS

logger = logging.getLogger(__name__)


def _get_business_days_in_month(year: int, month: int) -> list[date]:
    """Return all business days (Mon-Fri) in a given month."""
    if month == 12:
        next_month_start = date(year + 1, 1, 1)
    else:
        next_month_start = date(year, month + 1, 1)

    current = date(year, month, 1)
    business_days = []
    while current < next_month_start:
        if current.weekday() < 5:  # Mon=0 .. Fri=4
            business_days.append(current)
        current += timedelta(days=1)
    return business_days


def get_roll_info(ref_date: Optional[date] = None) -> dict:
    """Determine if the current date is within the BD5~BD10 roll window.

    trade.xyz oracle roll schedule:
    - Monthly, from Business Day 5 to Business Day 10
    - 5-day linear transition between contract months

    Args:
        ref_date: Reference date (default: today)

    Returns:
        {
            "in_roll_window": True/False,
            "roll_days": 5,           # total roll period
            "roll_day_number": 2,     # current day within roll (1-based)
            "roll_days_remaining": 3,
            "roll_start": date,       # BD5
            "roll_end": date,         # BD10
            "from_month": "Apr 2026", # rolling from
            "to_month": "May 2026",   # rolling to
            "roll_progress_pct": 40.0,
        }
    """
    if ref_date is None:
        ref_date = date.today()

    year, month = ref_date.year, ref_date.month
    bdays = _get_business_days_in_month(year, month)

    if len(bdays) < 10:
        logger.warning(f"Month {year}-{month:02d} has fewer than 10 business days")
        return {"in_roll_window": False, "roll_days": ROLL_DAYS}

    # BD5 = index 4 (0-based), BD10 = index 9
    roll_start = bdays[4]   # BD5
    roll_end = bdays[9]     # BD10

    month_names = [
        "", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]

    # Determine from/to contract months
    from_month_str = f"{month_names[month]} {year}"
    if month == 12:
        to_month_str = f"{month_names[1]} {year + 1}"
    else:
        to_month_str = f"{month_names[month + 1]} {year}"

    in_window = roll_start <= ref_date <= roll_end

    if not in_window:
        return {
            "in_roll_window": False,
            "roll_days": ROLL_DAYS,
            "roll_start": roll_start,
            "roll_end": roll_end,
            "from_month": from_month_str,
            "to_month": to_month_str,
        }

    # Calculate position within the roll window
    # BD5~BD10 = 6 business days, but roll is spread over ROLL_DAYS
    roll_bdays = [d for d in bdays[4:10] if d <= roll_end]
    day_in_window = 0
    for i, d in enumerate(roll_bdays):
        if d <= ref_date:
            day_in_window = i + 1

    # Map to ROLL_DAYS scale
    roll_day_number = min(day_in_window, ROLL_DAYS)
    roll_days_remaining = max(0, ROLL_DAYS - roll_day_number)
    progress = (roll_day_number / ROLL_DAYS) * 100

    result = {
        "in_roll_window": True,
        "roll_days": ROLL_DAYS,
        "roll_day_number": roll_day_number,
        "roll_days_remaining": roll_days_remaining,
        "roll_start": roll_start,
        "roll_end": roll_end,
        "from_month": from_month_str,
        "to_month": to_month_str,
        "roll_progress_pct": progress,
    }

    logger.info(
        f"[Roll] In roll window: day {roll_day_number}/{ROLL_DAYS} "
        f"({from_month_str} -> {to_month_str}), {roll_days_remaining} days remaining"
    )
    return result
