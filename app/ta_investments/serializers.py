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
