import django_filters

from .models import Cashflow, Loan


class LoanFilter(django_filters.FilterSet):
    class Meta:
        model = Loan
        fields = {
            # Add fields to filter loans by, for example:
            "investment_date": [
                "exact",
                "lt",
                "gt",
                "lte",
                "gte",
                "year",
                "year__lt",
                "year__gt",
            ],
            "invested_amount": ["exact", "lt", "gt", "lte", "gte"],
            "is_closed": ["exact"],
            "expected_irr": ["exact", "lt", "gt", "lte", "gte"],
            "realized_irr": ["exact", "lt", "gt", "lte", "gte"],
        }


class CashFlowFilter(django_filters.FilterSet):
    class Meta:
        model = Cashflow
        fields = {
            # Add fields to filter cash flows by, for example:
            "loan_identifier": ["exact"],
            "reference_date": [
                "exact",
                "lt",
                "gt",
                "lte",
                "gte",
                "year",
                "year__lt",
                "year__gt",
            ],
            "amount": ["exact", "lt", "gt", "lte", "gte"],
            "type": ["exact"],
        }
