#!/usr/bin/env python3
"""Oil Funding vs Backwardation Monitor.

Compares perpetual funding income against futures backwardation (roll) costs
for crude oil (WTI/Brent) to evaluate carry trade profitability.

Usage:
    python main.py          # Run with scheduler (hourly)
    python main.py --once   # Single execution
"""

import argparse
import logging
import signal
import sys
import os

# Add project root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import SCHEDULE_INTERVAL_MIN


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def run_once():
    from monitor import run_monitor
    run_monitor()


def run_scheduled():
    from apscheduler.schedulers.blocking import BlockingScheduler
    from monitor import run_monitor

    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_monitor,
        "interval",
        minutes=SCHEDULE_INTERVAL_MIN,
        id="funding_monitor",
        next_run_time=None,  # Don't run immediately, we'll run manually first
    )

    def shutdown(signum, frame):
        logging.info("Shutting down scheduler...")
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Run once immediately
    logging.info("Running initial check...")
    run_monitor()

    logging.info(f"Scheduler started. Running every {SCHEDULE_INTERVAL_MIN} minutes.")
    scheduler.start()


def main():
    parser = argparse.ArgumentParser(
        description="Oil Funding vs Backwardation Monitor"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (no scheduler)",
    )
    args = parser.parse_args()

    setup_logging()

    if args.once:
        run_once()
    else:
        run_scheduled()


if __name__ == "__main__":
    main()
