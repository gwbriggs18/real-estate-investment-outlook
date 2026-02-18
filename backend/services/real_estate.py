"""
Hypothetical real estate investment: mortgage math and equity at a given date.
No external API: uses purchase price, down payment %, rate, and optional appreciation.
"""

from datetime import datetime


def round_to(n: float, digits: int) -> float:
    m = 10**digits
    return round(n * m) / m


def _months_between(start_date: str, end_date: str) -> int:
    """Return number of full months from start_date to end_date (YYYY-MM-DD)."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    if end < start:
        return 0
    return (end.year - start.year) * 12 + (end.month - start.month)


def _years_between(start_date: str, end_date: str) -> float:
    """Return fractional years between two dates."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    delta = (end - start).days
    return delta / 365.25


def compute_hypothetical_real_estate(
    *,
    purchase_price: float,
    down_payment_percent: float,
    annual_interest_rate: float,
    buy_date: str,
    as_of_date: str,
    annual_appreciation_percent: float = 0.0,
    loan_term_years: int = 30,
) -> dict:
    """
    Compute hypothetical real estate position at as_of_date.

    Uses a standard 30-year (or loan_term_years) fixed mortgage. No property API;
    optional annual_appreciation_percent applies to estimated value at as_of_date.

    Returns dict with: purchasePrice, downPaymentPercent, downPayment, loanAmount,
    annualInterestRate, monthlyPayment, buyDate, asOfDate, paymentsMade, remainingBalance,
    estimatedValueAtAsOf, equityAtAsOf, totalPrincipalPaid, gainLoss, gainLossPercent
    (gain/loss on the down payment / cash invested).
    """
    if purchase_price <= 0 or down_payment_percent < 0 or down_payment_percent >= 100:
        raise ValueError("Invalid purchase price or down payment percent")
    if annual_interest_rate < 0:
        raise ValueError("Interest rate must be non-negative")

    down_payment = purchase_price * (down_payment_percent / 100.0)
    loan_amount = purchase_price - down_payment
    if loan_amount <= 0:
        raise ValueError("Loan amount would be zero or negative")

    n = loan_term_years * 12
    r = (annual_interest_rate / 100.0) / 12.0
    if r == 0:
        monthly_payment = loan_amount / n
    else:
        monthly_payment = loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)

    months_elapsed = _months_between(buy_date, as_of_date)
    if months_elapsed < 0:
        raise ValueError("as_of_date must be on or after buy_date")
    payments_made = min(months_elapsed, n)

    if r == 0:
        remaining_balance = loan_amount - (loan_amount / n) * payments_made
    else:
        remaining_balance = (
            loan_amount
            * ((1 + r) ** n - (1 + r) ** payments_made)
            / ((1 + r) ** n - 1)
        )
    remaining_balance = max(0.0, remaining_balance)

    years_elapsed = _years_between(buy_date, as_of_date)
    if years_elapsed < 0:
        years_elapsed = 0.0
    estimated_value = purchase_price * (
        (1 + annual_appreciation_percent / 100.0) ** years_elapsed
    )
    equity_at_as_of = estimated_value - remaining_balance
    total_principal_paid = loan_amount - remaining_balance

    # Gain/loss on the cash (down payment) invested
    cost_basis = down_payment
    gain_loss = equity_at_as_of - cost_basis
    gain_loss_percent = (gain_loss / cost_basis * 100.0) if cost_basis else 0.0

    return {
        "purchasePrice": round_to(purchase_price, 2),
        "downPaymentPercent": round_to(down_payment_percent, 2),
        "downPayment": round_to(down_payment, 2),
        "loanAmount": round_to(loan_amount, 2),
        "annualInterestRate": round_to(annual_interest_rate, 2),
        "monthlyPayment": round_to(monthly_payment, 2),
        "buyDate": buy_date,
        "asOfDate": as_of_date,
        "paymentsMade": payments_made,
        "remainingBalance": round_to(remaining_balance, 2),
        "estimatedValueAtAsOf": round_to(estimated_value, 2),
        "equityAtAsOf": round_to(equity_at_as_of, 2),
        "totalPrincipalPaid": round_to(total_principal_paid, 2),
        "gainLoss": round_to(gain_loss, 2),
        "gainLossPercent": round_to(gain_loss_percent, 2),
        "annualAppreciationPercent": round_to(annual_appreciation_percent, 2),
    }
