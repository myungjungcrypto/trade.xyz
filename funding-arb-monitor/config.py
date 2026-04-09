import os
from dotenv import load_dotenv

load_dotenv()

# --- Telegram ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# --- Roll Schedule ---
ROLL_DAYS = int(os.getenv("ROLL_DAYS", "5"))

# --- Scheduler ---
SCHEDULE_INTERVAL_MIN = int(os.getenv("SCHEDULE_INTERVAL_MIN", "60"))

# --- Symbol Mappings ---
# Internal name -> exchange-specific symbol
BINANCE_SYMBOLS = {
    "WTI": "CLUSDT",
    "BRENT": "BZUSDT",
}

HYPERLIQUID_SYMBOLS = {
    "WTI": "WTIOIL",
    "BRENT": "BRENTOIL",
}

LIGHTER_SYMBOLS = {
    "WTI": "WTIOIL",      # TBD - verify from lighter docs
    "BRENT": "BRENTOIL",  # TBD - verify from lighter docs
}

# --- CME Futures (Yahoo Finance tickers) ---
# Month code mapping: F=Jan, G=Feb, H=Mar, J=Apr, K=May, M=Jun,
#                     N=Jul, Q=Aug, U=Sep, V=Oct, X=Nov, Z=Dec
CME_MONTH_CODES = {
    1: "F", 2: "G", 3: "H", 4: "J", 5: "K", 6: "M",
    7: "N", 8: "Q", 9: "U", 10: "V", 11: "X", 12: "Z",
}

CME_TICKERS = {
    "WTI": {"root": "CL", "front": "CL=F", "exchange": "NYM"},
    "BRENT": {"root": "BZ", "front": "BZ=F", "exchange": "NYM"},
}

# --- API Endpoints ---
BINANCE_BASE_URL = "https://fapi.binance.com"
HYPERLIQUID_INFO_URL = "https://api.hyperliquid.xyz/info"
LIGHTER_BASE_URL = "https://api.lighter.xyz"  # TBD - verify actual base URL

# --- Assets to monitor ---
ASSETS = ["WTI", "BRENT"]
