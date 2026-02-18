"""
Hypothetical investment return logic: given an amount invested on a buy date,
what would it be worth on a sell date using historical (adjusted) prices?
"""

from backend.services.alpha_vantage import get_daily_adjusted, get_price_on_or_before


def round_to(n: float, digits: int) -> float:
    m = 10 ** digits
    return round(n * m) / m


def compute_hypothetical_return(
    *,
    symbol: str,
    invested_amount: float,
    buy_date: str,
    sell_date: str | None = None,
) -> dict:
    """
    Compute hypothetical stock return.
    Returns dict with symbol, buyDate, sellDate, buyPrice, sellPrice, shares,
    costBasis, valueAtSell, gainLoss, gainLossPercent (same keys as JS API).
    """
    series = get_daily_adjusted(symbol, "full")
    buy = get_price_on_or_before(series, buy_date)
    if not buy:
        raise ValueError(f"No price data on or before buy date {buy_date} for {symbol}")

    if sell_date:
        sell = get_price_on_or_before(series, sell_date)
    else:
        sell = {
            "date": series["dates"][-1],
            "close": series["closes"][-1],
        }
    if not sell or sell["date"] < buy["date"]:
        raise ValueError(f"No price data for sell date for {symbol}")

    buy_price = buy["close"]
    sell_price = sell["close"]
    shares = invested_amount / buy_price
    value_at_sell = shares * sell_price
    gain_loss = value_at_sell - invested_amount
    gain_loss_percent = (gain_loss / invested_amount) * 100

    return {
        "symbol": series["symbol"],
        "buyDate": buy["date"],
        "sellDate": sell["date"],
        "buyPrice": round_to(buy_price, 4),
        "sellPrice": round_to(sell_price, 4),
        "shares": round_to(shares, 6),
        "costBasis": round_to(invested_amount, 2),
        "valueAtSell": round_to(value_at_sell, 2),
        "gainLoss": round_to(gain_loss, 2),
        "gainLossPercent": round_to(gain_loss_percent, 2),
    }
