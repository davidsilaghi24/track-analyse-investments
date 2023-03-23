from rest_framework import serializers

from .models import Cashflow, Loan


class CashflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cashflow
        fields = "__all__"


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = "__all__"


class LoanCsvUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class CashFlowCsvUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class InvestmentStatisticsSerializer(serializers.Serializer):
    total_investments = serializers.IntegerField()
    total_invested_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2)
    total_expected_interest_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2)
    total_realized_interest_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2)
    realized_irr = serializers.DecimalField(max_digits=10, decimal_places=6)
    expected_irr = serializers.DecimalField(max_digits=10, decimal_places=6)
