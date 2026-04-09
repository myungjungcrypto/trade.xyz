# Funding Arb Monitor

Oil (WTI/Brent) perpetual funding vs backwardation carry trade monitor.

## Quick Start
```bash
cd funding-arb-monitor
pip install -r requirements.txt
cp .env.example .env  # edit if Telegram notifications desired
python main.py --once  # single run
python main.py         # scheduled (hourly)
```

## Architecture
- `exchanges/` - Exchange adapters (Binance, Hyperliquid/trade.xyz, Lighter, OKX stub)
- `futures/` - CME futures spreads via yfinance + roll schedule logic
- `monitor.py` - Core comparison logic and output formatting
- `notifier.py` - Optional Telegram alerts
- `config.py` - All configuration via env vars

## Key APIs
- Binance: `GET /fapi/v1/fundingRate` (CLUSDT, BZUSDT) - 4h funding
- Hyperliquid: `POST /info` fundingHistory (WTIOIL, BRENTOIL) - 1h funding
- Lighter: funding-rates endpoint (TBD symbols) - 1h funding
- Yahoo Finance (yfinance): CME WTI (CL) and Brent (BZ) front-month spreads
