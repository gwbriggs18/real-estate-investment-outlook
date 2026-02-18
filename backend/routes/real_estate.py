"""
Real estate API routes: value by address (RentCast), hypothetical return (mortgage + equity).
"""

from flask import Blueprint, request, jsonify

from backend.services.real_estate import compute_hypothetical_real_estate
from backend.services.rentcast import get_value_by_address

real_estate_bp = Blueprint(
    "real_estate", __name__, url_prefix="/api/real-estate"
)


@real_estate_bp.route("/hypothetical", methods=["GET"])
def hypothetical():
    """
    GET ?purchasePrice=&downPaymentPercent=&annualInterestRate=&buyDate=&asOfDate=
    Optional: annualAppreciationPercent=0, loanTermYears=30
    """
    try:
        purchase_price = request.args.get("purchasePrice", type=float)
        down_payment_percent = request.args.get("downPaymentPercent", type=float)
        annual_interest_rate = request.args.get("annualInterestRate", type=float)
        buy_date = (request.args.get("buyDate") or "").strip()
        as_of_date = (request.args.get("asOfDate") or "").strip()
        annual_appreciation = request.args.get(
            "annualAppreciationPercent", type=float
        ) or 0.0
        loan_term_years = request.args.get("loanTermYears", type=int) or 30

        if (
            purchase_price is None
            or purchase_price <= 0
            or down_payment_percent is None
            or annual_interest_rate is None
            or not buy_date
            or not as_of_date
        ):
            return jsonify({
                "error": (
                    "Missing or invalid: purchasePrice (positive), "
                    "downPaymentPercent, annualInterestRate, buyDate (YYYY-MM-DD), "
                    "asOfDate (YYYY-MM-DD)"
                ),
            }), 400

        result = compute_hypothetical_real_estate(
            purchase_price=purchase_price,
            down_payment_percent=down_payment_percent,
            annual_interest_rate=annual_interest_rate,
            buy_date=buy_date,
            as_of_date=as_of_date,
            annual_appreciation_percent=annual_appreciation,
            loan_term_years=loan_term_years,
        )
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@real_estate_bp.route("/value", methods=["GET"])
def value_by_address():
    """
    GET ?address=Street, City, State, Zip
    Returns current AVM value estimate for that address (RentCast; 50 free requests/month).
    """
    try:
        address = (request.args.get("address") or "").strip()
        if not address:
            return jsonify({
                "error": "Missing address. Use format: Street, City, State, Zip",
            }), 400
        result = get_value_by_address(address)
        return jsonify(result)
    except ValueError as e:
        status = 503 if "API key" in str(e) or "RENTCAST" in str(e) else 400
        return jsonify({"error": str(e)}), status
