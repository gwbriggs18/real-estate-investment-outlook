"""
Stock API routes: hypothetical return and historical series.
"""

from flask import Blueprint, request, jsonify

from backend.services.returns import compute_hypothetical_return
from backend.services.alpha_vantage import get_daily_adjusted

stock_bp = Blueprint("stock", __name__, url_prefix="/api/stock")


@stock_bp.route("/hypothetical-return", methods=["GET"])
def hypothetical_return():
    """GET ?symbol=&investedAmount=&buyDate=&sellDate= (optional)."""
    try:
        symbol = (request.args.get("symbol") or "").strip().upper()
        invested_amount = request.args.get("investedAmount", type=float)
        buy_date = (request.args.get("buyDate") or "").strip()
        sell_date = (request.args.get("sellDate") or "").strip() or None
        if not symbol or invested_amount is None or invested_amount <= 0 or not buy_date:
            return jsonify({
                "error": "Missing or invalid: symbol, investedAmount (positive number), buyDate (YYYY-MM-DD)",
            }), 400
        result = compute_hypothetical_return(
            symbol=symbol,
            invested_amount=invested_amount,
            buy_date=buy_date,
            sell_date=sell_date,
        )
        return jsonify(result)
    except ValueError as e:
        status = 503 if "API key" in str(e) else 400
        return jsonify({"error": str(e)}), status


@stock_bp.route("/historical", methods=["GET"])
def historical():
    """GET ?symbol=&from=&to= (optional). Returns daily adjusted close for range."""
    try:
        symbol = (request.args.get("symbol") or "").strip().upper()
        from_date = (request.args.get("from") or "").strip() or None
        to_date = (request.args.get("to") or "").strip() or None
        if not symbol:
            return jsonify({"error": "Missing symbol"}), 400
        series = get_daily_adjusted(symbol, "full")
        dates = series["dates"]
        closes = series["closes"]
        start_idx = 0
        end_idx = len(dates) - 1
        if from_date:
            for i, d in enumerate(dates):
                if d >= from_date:
                    start_idx = i
                    break
        if to_date:
            for i, d in enumerate(dates):
                if d > to_date:
                    end_idx = i - 1
                    break
            else:
                end_idx = len(dates) - 1
        out_dates = dates[start_idx : end_idx + 1]
        out_closes = closes[start_idx : end_idx + 1]
        return jsonify({"symbol": series["symbol"], "dates": out_dates, "closes": out_closes})
    except ValueError as e:
        status = 503 if "API key" in str(e) else 400
        return jsonify({"error": str(e)}), status
