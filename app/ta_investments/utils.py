from decimal import Decimal
from typing import Dict, List

from .models import Loan, Cashflow


def calculate_investment_statistics(loans: List[Loan], cashflows: List[Cashflow]) -> Dict[str, Decimal]:
    total_invested = Decimal(0)
    total_returned = Decimal(0)
    total_interest_earned = Decimal(0)
    total_expected_interest = Decimal(0)

    for loan in loans:
        if loan.is_closed:
            total_invested += loan.invested_amount
            total_returned += loan.invested_amount + loan.realized_irr
            total_interest_earned += loan.realized_irr
            total_expected_interest += loan.expected_interest_amount

    for cashflow in cashflows:
        if cashflow.type == "FUNDING":
            total_invested += cashflow.amount
        elif cashflow.type == "REPAYMENT":
            total_returned += cashflow.amount

    investment_statistics = {
        "total_invested": total_invested,
        "total_returned": total_returned,
        "total_interest_earned": total_interest_earned,
        "total_expected_interest": total_expected_interest,
    }

    return investment_statistics
