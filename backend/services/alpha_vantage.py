"""
Alpha Vantage API client for historical stock data.
Free tier: 25 requests/day, 5/minute. Get key at https://www.alphavantage.co/support/#api-key
"""

import os
import requests

BASE_URL = "https://www.alphavantage.co/query"


def get_api_key() -> str:
    key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if not key:
        raise ValueError(
            "ALPHA_VANTAGE_API_KEY is not set. "
            "Get a free key at https://www.alphavantage.co/support/#api-key"
        )
    return key


def get_daily_adjusted(symbol: str, outputsize: str = "full") -> dict:
    """
    Fetch daily adjusted time series (split/dividend adjusted) for a symbol.
    Returns dict with keys: symbol, dates (list[str]), closes (list[float]).
    """
    api_key = get_api_key()
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol.upper(),
        "outputsize": outputsize,
        "apikey": api_key,
    }
    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    meta = data.get("Meta Data")
    series = data.get("Time Series (Daily)")
    if not series:
        note = data.get("Note") or data.get("Error Message") or "Unknown error"
        raise ValueError(note)
    dates = sorted(series.keys())
    closes = [float(series[d]["5. adjusted close"]) for d in dates]
    return {"symbol": meta["2. Symbol"], "dates": dates, "closes": closes}


def get_price_on_or_before(series: dict, target_date: str) -> dict | None:
    """Get closing price on or nearest before target_date (YYYY-MM-DD)."""
    dates = series["dates"]
    closes = series["closes"]
    # Want latest date <= target_date (nearest trading day on or before)
    for i in range(len(dates) - 1, -1, -1):
        if dates[i] <= target_date:
            return {"date": dates[i], "close": closes[i]}
    return None
