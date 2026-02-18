"""
Compare API: run stock and real estate hypotheticals in one request.
Returns both results so the frontend can show side-by-side (and we use one stock API call).
Also time-series for year-over-year chart.
"""

from flask import Blueprint, request, jsonify

from backend.services.returns import compute_hypothetical_return
from backend.services.real_estate import compute_hypothetical_real_estate
from backend.services.compare_timeseries import get_compare_time_series

compare_bp = Blueprint("compare", __name__, url_prefix="/api/compare")


@compare_bp.route("", methods=["GET"])
def compare():
    """
    GET with optional stock params: symbol, investedAmount, buyDate, sellDate
    and optional real estate params: purchasePrice, downPaymentPercent, annualInterestRate,
    buyDate (re), asOfDate, annualAppreciationPercent.
    Returns { stock: {...} or null, realEstate: {...} or null }.
    At least one set of params must be provided.
    """
    out = {"stock": None, "realEstate": None}

    # Stock params
    symbol = (request.args.get("symbol") or "").strip().upper()
    invested_amount = request.args.get("investedAmount", type=float)
    stock_buy = (request.args.get("buyDate") or "").strip()
    stock_sell = (request.args.get("sellDate") or "").strip() or None

    # Real estate params (use reBuyDate/reAsOfDate to avoid clashing with stock buyDate/sellDate)
    purchase_price = request.args.get("purchasePrice", type=float)
    down_payment_percent = request.args.get("downPaymentPercent", type=float)
    annual_interest_rate = request.args.get("annualInterestRate", type=float)
    re_buy_date = (request.args.get("reBuyDate") or request.args.get("buyDate") or "").strip()
    as_of_date = (request.args.get("asOfDate") or "").strip()
    annual_appreciation = request.args.get("annualAppreciationPercent", type=float) or 0.0

    has_stock = symbol and invested_amount and invested_amount > 0 and stock_buy
    has_re = (
        purchase_price and purchase_price > 0
        and down_payment_percent is not None
        and annual_interest_rate is not None
        and re_buy_date
        and as_of_date
    )

    if not has_stock and not has_re:
        return jsonify({
            "error": (
                "Provide either stock params (symbol, investedAmount, buyDate [, sellDate]) "
                "or real estate params (purchasePrice, downPaymentPercent, annualInterestRate, "
                "buyDate, asOfDate), or both."
            ),
        }), 400

    errors = []

    if has_stock:
        try:
            out["stock"] = compute_hypothetical_return(
                symbol=symbol,
                invested_amount=invested_amount,
                buy_date=stock_buy,
                sell_date=stock_sell,
            )
        except ValueError as e:
            errors.append(f"Stock: {e}")

    if has_re:
        try:
            out["realEstate"] = compute_hypothetical_real_estate(
                purchase_price=purchase_price,
                down_payment_percent=down_payment_percent,
                annual_interest_rate=annual_interest_rate,
                buy_date=re_buy_date,
                as_of_date=as_of_date,
                annual_appreciation_percent=annual_appreciation,
            )
        except ValueError as e:
            errors.append(f"Real estate: {e}")

    if errors:
        return jsonify({"error": "; ".join(errors), "partial": out}), 400

    return jsonify(out)


@compare_bp.route("/time-series", methods=["GET"])
def compare_time_series():
    """
    GET same params as /api/compare. Returns year-over-year values for charting:
    { years: ["2020","2021",...], stock: { values: [...] }, realEstate: { values: [...] } }.
    """
    symbol = (request.args.get("symbol") or "").strip().upper()
    invested_amount = request.args.get("investedAmount", type=float)
    stock_buy = (request.args.get("buyDate") or "").strip()
    stock_sell = (request.args.get("sellDate") or "").strip() or None
    purchase_price = request.args.get("purchasePrice", type=float)
    down_payment_percent = request.args.get("downPaymentPercent", type=float)
    annual_interest_rate = request.args.get("annualInterestRate", type=float)
    re_buy_date = (request.args.get("reBuyDate") or request.args.get("buyDate") or "").strip()
    as_of_date = (request.args.get("asOfDate") or "").strip()
    annual_appreciation = request.args.get("annualAppreciationPercent", type=float) or 0.0

    has_stock = symbol and invested_amount and invested_amount > 0 and stock_buy
    has_re = (
        purchase_price and purchase_price > 0
        and down_payment_percent is not None
        and annual_interest_rate is not None
        and re_buy_date
        and as_of_date
    )
    if not has_stock and not has_re:
        return jsonify({
            "error": "Provide stock params and/or real estate params (same as Compare).",
        }), 400

    try:
        out = get_compare_time_series(
            symbol=symbol if has_stock else None,
            invested_amount=invested_amount if has_stock else None,
            stock_buy=stock_buy if has_stock else None,
            stock_sell=stock_sell if has_stock else None,
            purchase_price=purchase_price if has_re else None,
            down_payment_percent=down_payment_percent if has_re else None,
            annual_interest_rate=annual_interest_rate if has_re else None,
            re_buy_date=re_buy_date if has_re else None,
            as_of_date=as_of_date if has_re else None,
            annual_appreciation_percent=annual_appreciation,
        )
        return jsonify(out)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
