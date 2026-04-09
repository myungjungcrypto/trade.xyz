import logging
from datetime import datetime
from typing import Optional

from config import ASSETS, ROLL_DAYS
from exchanges.binance import BinanceFunding
from exchanges.hyperliquid import HyperliquidFunding
from exchanges.lighter import LighterFunding
from exchanges.okx import OKXFunding
from futures.spreads import get_all_spreads
from futures.roll_schedule import get_roll_info
from notifier import send_telegram

logger = logging.getLogger(__name__)


def run_monitor() -> str:
    """Execute one monitoring cycle and return formatted output."""

    now = datetime.now()
    header = f"===== {now.strftime('%Y-%m-%d %H:%M')} KST ====="

    # --- Initialize exchanges ---
    exchanges = [
        BinanceFunding(),
        HyperliquidFunding(),
        LighterFunding(),
        OKXFunding(),
    ]

    # --- Fetch funding rates ---
    funding_data: dict[str, dict[str, Optional[float]]] = {}
    for ex in exchanges:
        funding_data[ex.name] = ex.get_all_funding_rates(ASSETS)

    # --- Fetch CME spreads ---
    spreads = get_all_spreads(ASSETS)

    # --- Get roll schedule ---
    roll_info = get_roll_info()

    # --- Format output ---
    lines = [header, ""]

    # Section 1: Funding rates
    lines.append("[펀딩률 - 24h 누적]")
    for ex_name, rates in funding_data.items():
        parts = []
        for asset in ASSETS:
            rate = rates.get(asset)
            if rate is not None:
                parts.append(f"{asset}: {rate:+.2f}%")
            else:
                parts.append(f"{asset}: N/A")
        lines.append(f"  {ex_name:<10} {' | '.join(parts)}")
    lines.append("")

    # Section 2: CME spreads
    lines.append("[월물 스프레드]")
    for asset in ASSETS:
        spread = spreads.get(asset)
        if spread:
            state_kr = "백워데이션" if spread["state"] == "backwardation" else "콘탱고"
            lines.append(
                f"  {asset:<6} {spread['front_month']} vs {spread['next_month']}: "
                f"{spread['spread_pct']:+.1f}% ({state_kr})"
            )
        else:
            lines.append(f"  {asset:<6} 데이터 없음")
    lines.append("")

    # Section 3: Roll schedule info
    if roll_info["in_roll_window"]:
        lines.append(
            f"[오라클 롤 스케줄] "
            f"{roll_info['from_month']} → {roll_info['to_month']} "
            f"(Day {roll_info['roll_day_number']}/{roll_info['roll_days']}, "
            f"{roll_info['roll_progress_pct']:.0f}% 완료)"
        )
    else:
        lines.append(
            f"[오라클 롤 스케줄] 롤 기간 아님 "
            f"(다음 롤: BD5 = {roll_info.get('roll_start', 'N/A')})"
        )
    lines.append("")

    # Section 4: Roll cost vs funding comparison
    lines.append("[롤 비용 vs 펀딩]")

    any_profitable = False
    for ex_name, rates in funding_data.items():
        for asset in ASSETS:
            funding = rates.get(asset)
            spread = spreads.get(asset)

            if funding is None or spread is None:
                continue

            if roll_info["in_roll_window"]:
                daily_roll_cost = abs(spread["spread_pct"]) / ROLL_DAYS
            else:
                daily_roll_cost = 0.0

            net_pnl = funding - daily_roll_cost if funding < 0 else funding - daily_roll_cost
            # For carry trade: funding is income (negative funding = you receive)
            # We use absolute funding for comparison
            abs_funding = abs(funding)
            net = abs_funding - daily_roll_cost
            is_profitable = net > 0

            if is_profitable:
                any_profitable = True

            emoji = "✅" if is_profitable else "❌"

            lines.append(f"  {ex_name} {asset}:")
            if roll_info["in_roll_window"]:
                lines.append(
                    f"    일일 롤 비용: {daily_roll_cost:.2f}% "
                    f"({abs(spread['spread_pct']):.1f}% / {ROLL_DAYS}일)"
                )
            else:
                lines.append(f"    일일 롤 비용: 0.00% (롤 기간 아님)")
            lines.append(f"    24h 펀딩:     {abs_funding:.2f}%")
            lines.append(f"    순손익:       {net:+.2f}% {emoji}")
            lines.append("")

    # Section 5: Recommendation
    if any_profitable:
        lines.append("→ 일부 롱 퍼프 캐리 트레이드 수익 가능 조합 있음 ✅")
    else:
        lines.append("→ 현재 롱 퍼프 캐리 트레이드 비추천 ❌")

    output = "\n".join(lines)

    # Print to console
    print(output)

    # Send Telegram if configured
    send_telegram(output)

    return output
