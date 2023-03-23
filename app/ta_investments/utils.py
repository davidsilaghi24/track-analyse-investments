import django_filters
import redis
from django.conf import settings
from django.db.models import F, Sum
from ta_investments.models import Cashflow, Loan

redis_conn = redis.Redis(host=settings.REDIS_HOST, port=6379, db=0)


def get_stats_cache_key(user_id):
    return f"user_{user_id}_stats"


def get_investment_stats(user):
    # Check cache
    cache_key = get_stats_cache_key(user.id)
    stats = redis_conn.get(cache_key)
    if stats:
        return stats.decode("utf-8")

    # Number of Loans
    num_loans = Loan.objects.filter(user=user).count()

    # Total invested amount (all loans)
    total_invested_amount = (
        Loan.objects.filter(user=user).aggregate(total_invested_amount=Sum("invested_amount"))["total_invested_amount"]
        or 0
    )

    # Current invested amount (only open loans)
    open_loans = Loan.objects.filter(user=user, is_closed=False)
    current_invested_amount = (
        open_loans.aggregate(current_invested_amount=Sum("invested_amount"))["current_invested_amount"] or 0
    )

    # Total repaid amount (all loans)
    total_repaid_amount = (
        Loan.objects.filter(user=user)
        .annotate(
            total_cash_flows_amount=Sum(
                "cashflows__amount",
                filter=django_filters.Q(cashflows__type=Cashflow.REPAYMENT),
            ),
            total_expected_amount=F("invested_amount") + F("expected_interest_amount"),
        )
        .aggregate(
            total_repaid_amount=Sum(
                "total_cash_flows_amount",
                filter=django_filters.Q(total_cash_flows_amount__gte=F("total_expected_amount")),
            )
        )["total_repaid_amount"]
        or 0
    )

    # Average Realized IRR (weighted)
    closed_loans = Loan.objects.filter(user=user, is_closed=True)
    realized_irrs = []
    for loan in closed_loans:
        cash_flows = [(cf.date, -cf.amount) for cf in loan.cashflows.filter(type=Cashflow.FUNDING)] + [
            (cf.date, cf.amount) for cf in loan.cashflows.filter(type=Cashflow.REPAYMENT)
        ]
        realized_irrs.append(
            {
                "loan": loan.id,
                "realized_irr": XIRR(cash_flows) * 100,
                "invested_amount": loan.invested_amount,
            }
        )
    average_realized_irr = (
        sum([(irr["realized_irr"] * irr["invested_amount"]) for irr in realized_irrs]) / total_invested_amount
        if total_invested_amount > 0
        else 0
    )

    # Create stats dict
    stats = {
        "num_loans": num_loans,
        "total_invested_amount": total_invested_amount,
        "current_invested_amount": current_invested_amount,
        "total_repaid_amount": total_repaid_amount,
        "average_realized_irr": average_realized_irr,
    }

    # Store stats in cache
    redis_conn.set(cache_key, stats)

    return stats
