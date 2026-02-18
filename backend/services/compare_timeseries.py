"""
Year-over-year comparison: stock value and real estate equity at end of each year.
Uses one Alpha Vantage call for stock; real estate is computed per year.
"""

from backend.services.alpha_vantage import get_daily_adjusted, get_price_on_or_before
from backend.services.real_estate import compute_hypothetical_real_estate


def _year_end_date(year: int) -> str:
    return f"{year}-12-31"


def _stock_values_by_year(
    symbol: str,
    invested_amount: float,
    buy_date: str,
    sell_date: str | None,
) -> tuple[list[str], list[float]]:
    """Return (years, values) for stock at end of each year from buy to sell."""
    series = get_daily_adjusted(symbol, "full")
    buy = get_price_on_or_before(series, buy_date)
    if not buy:
        raise ValueError(f"No price data on or before buy date {buy_date} for {symbol}")
    buy_price = buy["close"]
    shares = invested_amount / buy_price
    buy_year = int(buy_date[:4])
    if sell_date:
        sell = get_price_on_or_before(series, sell_date)
        if not sell or sell["date"] < buy["date"]:
            raise ValueError(f"No price data for sell date for {symbol}")
        sell_year = int(sell["date"][:4])
    else:
        sell_year = int(series["dates"][-1][:4])

    years: list[str] = []
    values: list[float] = []
    for y in range(buy_year, sell_year + 1):
        if y == sell_year and sell_date:
            end_date = min(_year_end_date(y), sell_date)
        else:
            end_date = _year_end_date(y)
        if end_date < buy_date:
            continue
        pt = get_price_on_or_before(series, end_date)
        if not pt:
            continue
        years.append(str(y))
        values.append(round(shares * pt["close"], 2))
    return years, values


def _real_estate_values_by_year(
    purchase_price: float,
    down_payment_percent: float,
    annual_interest_rate: float,
    buy_date: str,
    as_of_date: str,
    annual_appreciation_percent: float,
) -> tuple[list[str], list[float]]:
    """Return (years, equity values) at end of each year from buy to as_of."""
    buy_year = int(buy_date[:4])
    as_of_year = int(as_of_date[:4])
    years: list[str] = []
    values: list[float] = []
    for y in range(buy_year, as_of_year + 1):
        if y == as_of_year:
            end_date = min(_year_end_date(y), as_of_date)
        else:
            end_date = _year_end_date(y)
        if end_date < buy_date:
            continue
        result = compute_hypothetical_real_estate(
            purchase_price=purchase_price,
            down_payment_percent=down_payment_percent,
            annual_interest_rate=annual_interest_rate,
            buy_date=buy_date,
            as_of_date=end_date,
            annual_appreciation_percent=annual_appreciation_percent,
        )
        years.append(str(y))
        values.append(result["equityAtAsOf"])
    return years, values


def get_compare_time_series(
    *,
    symbol: str | None = None,
    invested_amount: float | None = None,
    stock_buy: str | None = None,
    stock_sell: str | None = None,
    purchase_price: float | None = None,
    down_payment_percent: float | None = None,
    annual_interest_rate: float | None = None,
    re_buy_date: str | None = None,
    as_of_date: str | None = None,
    annual_appreciation_percent: float = 0.0,
) -> dict:
    """
    Return year-over-year values for stock and/or real estate.
    Returns { years: [], stock: { values: [] } or None, realEstate: { values: [] } or None }.
    """
    out: dict = {"years": [], "stock": None, "realEstate": None}
    stock_years: list[str] = []
    stock_vals: list[float] = []
    re_years: list[str] = []
    re_vals: list[float] = []

    has_stock = symbol and invested_amount and invested_amount > 0 and stock_buy
    has_re = (
        purchase_price and purchase_price > 0
        and down_payment_percent is not None
        and annual_interest_rate is not None
        and re_buy_date
        and as_of_date
    )

    if has_stock:
        stock_years, stock_vals = _stock_values_by_year(
            symbol=symbol,
            invested_amount=invested_amount,
            buy_date=stock_buy,
            sell_date=stock_sell,
        )
        out["stock"] = {"values": stock_vals}
    if has_re:
        re_years, re_vals = _real_estate_values_by_year(
            purchase_price=purchase_price,
            down_payment_percent=down_payment_percent,
            annual_interest_rate=annual_interest_rate,
            buy_date=re_buy_date,
            as_of_date=as_of_date,
            annual_appreciation_percent=annual_appreciation_percent,
        )
        out["realEstate"] = {"values": re_vals}

    # Align years: union of both, sorted
    all_years = sorted(set(stock_years) | set(re_years), key=int)
    out["years"] = all_years

    # If both series exist, pad with None so chart can show both (same length as all_years)
    if out["stock"]:
        year_to_stock = dict(zip(stock_years, stock_vals))
        out["stock"]["values"] = [year_to_stock.get(y) for y in all_years]
    if out["realEstate"]:
        year_to_re = dict(zip(re_years, re_vals))
        out["realEstate"]["values"] = [year_to_re.get(y) for y in all_years]

    return out
